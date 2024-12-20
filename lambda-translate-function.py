import boto3
import os
#from pdftodocx import Converter
import logging

# AWS clients
s3_client = boto3.client('s3')
translate_client = boto3.client('translate')

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Translation Job Function
def translation_job(bucket_name, input_prefix, output_bucket, output_prefix, data_access_role_arn, file_extension):
    content_type = 'text/plain' if file_extension == 'txt' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    try:
        response = translate_client.start_text_translation_job(
            JobName="My-Lambda-Translation-Job",
            InputDataConfig={
                'S3Uri': f's3://{bucket_name}/input',
                'ContentType': content_type
            },
            OutputDataConfig={
                'S3Uri': f's3://{output_bucket}/output'
            },
            DataAccessRoleArn=data_access_role_arn,
            SourceLanguageCode='en',
            TargetLanguageCodes=[os.getenv('TARGET_LANGUAGE', 'hi')]
        )
        logger.info(f"Translation job started: {response['JobId']}")
        return {
            'statusCode': 200,
            'body': f"Translation job initiated successfully with Job ID: {response['JobId']}"
        }
    except Exception as e:
        logger.error(f"Error starting translation job: {e}")
        return {
            'statusCode': 500,
            'body': f"Error starting translation job: {str(e)}"
        }

# Function to handle TXT files
def handle_txt(bucket_name, file_key):
    file_name = os.path.basename(file_key)
    local_path = f"/tmp/{file_name}"
    s3_client.download_file(bucket_name, file_key, local_path)

    with open(local_path, 'r', encoding='utf-8') as file:
        content = file.read()

    target_language = os.getenv('TARGET_LANGUAGE', 'hi')  # Default to English
    response = translate_client.translate_text(
        Text=content,
        SourceLanguageCode='en',
        TargetLanguageCode=target_language
    )
    translated_text = response['TranslatedText']

    output_bucket = os.getenv('OUTPUT_BUCKET', 'outputbucket-dev')
    output_key = f"Translated-{file_name}"
    s3_client.put_object(Body=translated_text.encode('utf-8'), Bucket=output_bucket, Key=output_key)
    logger.info(f"TXT file translated and saved to {output_bucket}/{output_key}")

# Function to handle PDF files
def handle_pdf(bucket_name, file_key, data_access_role_arn):
    file_name = os.path.basename(file_key)
    local_pdf_path = f"/tmp/{file_name}"
    s3_client.download_file(bucket_name, file_key, local_pdf_path)
    new_file_name = file_name.replace('.pdf', '.docx')
    # Convert PDF to DOCX
    local_docx_path = f"/tmp/{new_file_name}"
    converter = Converter(local_pdf_path)
    converter.convert(local_docx_path, start=0, end=None)
    converter.close()

    intermediate_bucket = os.getenv('INTERMEDIATE_BUCKET', 'outputbucket-dev')
    intermediate_key = f"input/Converted-{file_key}.docx"
    s3_client.upload_file(local_docx_path, intermediate_bucket, intermediate_key)

    handle_docx(intermediate_bucket, intermediate_key, data_access_role_arn)

# Function to handle DOCX files
def handle_docx(bucket_name, file_key, data_access_role_arn):
    output_bucket = os.getenv('OUTPUT_BUCKET', 'outputbucket-dev')
    output_prefix = f"Translated-{file_key}"
    translation_job(bucket_name, file_key, output_bucket, output_prefix, data_access_role_arn, 'docx')

# Lambda Handler
def lambda_handler(event, context):
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']
        logger.info(f"Processing file: {file_key} from bucket: {bucket_name}")

        data_access_role_arn = os.getenv('DATA_ACCESS_ROLE_ARN','arn:aws:iam::867344435459:role/TranslateDataAccessRole')

        # Determine the file type
        if file_key.endswith('.txt'):
            handle_txt(bucket_name, file_key)
        elif file_key.endswith('.docx'):
            handle_docx(bucket_name, file_key, data_access_role_arn)
        elif file_key.endswith('.pdf'):
            handle_pdf(bucket_name, file_key, data_access_role_arn)
        else:
            logger.error(f"Unsupported file type for file: {file_key}")
            return {
                'statusCode': 400,
                'body': f"Unsupported file type for file: {file_key}"
            }

        return {
            'statusCode': 200,
            'body': f"File {file_key} processed successfully"
        }

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return {
            'statusCode': 500,
            'body': f"Error processing file: {e}"
        }
