import boto3
import os
from pdf2docx import Converter
import logging

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# AWS clients
s3_client = boto3.client('s3')
translate_client = boto3.client('translate')
dynamodb = boto3.client('dynamodb')

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def update_file_status(file_id, status, job_id=None):
    """
    Updates the status and JobId of a file in the DynamoDB table.
    """
    table_name = os.getenv('DYNAMODB_TABLE', 'FileMetadata')  # Replace with your table name
    try:
        # Build update expression dynamically
        update_expression = "SET #s = :status"
        expression_values = {':status': {'S': status}}
        expression_names = {'#s': 'status'}

        if job_id:
            update_expression += ", #j = :jobId"
            expression_values[':jobId'] = {'S': job_id}
            expression_names['#j'] = 'jobId'

        response = dynamodb.update_item(
            TableName=table_name,
            Key={
                'fileId': {'S': file_id}  # Ensure fileId is passed when invoking this function
            },
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values
        )
        logger.info(f"Updated status for file ID {file_id} to '{status}' with JobId: {job_id}")
    except Exception as e:
        logger.error(f"Failed to update status for file ID {file_id}: {e}")



def send_email_via_ses(to_email, subject, body):
    """
    Sends an email using Amazon SES via SMTP.
    """
    smtp_server = os.getenv('SES_SMTP_SERVER', 'email-smtp.us-west-1.amazonaws.com')
    smtp_port = int(os.getenv('SES_SMTP_PORT', 587))
    smtp_user = os.getenv('SES_SMTP_USER')
    smtp_password = os.getenv('SES_SMTP_PASSWORD')
    from_email = os.getenv('SES_FROM_EMAIL','omkarnagarkar53@gmail.com')

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
        logger.info(f"Email sent successfully to {to_email}.")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")


# Translation Job Function
def translation_job(bucket_name, input_prefix, output_bucket, output_prefix, data_access_role_arn, file_extension, target_language, fileId):
    content_type = 'text/plain' if file_extension == 'txt' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    try:
        response = translate_client.start_text_translation_job(
            JobName="My-Lambda-Translation-Job",
            InputDataConfig={
                'S3Uri': f's3://{bucket_name}/input/{fileId}',
                'ContentType': content_type
            },
            OutputDataConfig={
                'S3Uri': f's3://{output_bucket}/output'
            },
            DataAccessRoleArn=data_access_role_arn,
            SourceLanguageCode='en',
            TargetLanguageCodes=[target_language]
        )
        jobId = response['JobId']
        logger.info(f"Translation job started: {jobId}")

        # Update file status in DynamoDB
        update_file_status(fileId, 'IN_PROGRESS', jobId)
        return {
            'statusCode': 200,
            'body': f"Translation job initiated successfully with Job ID: {jobId}"
        }
    except Exception as e:
        logger.error(f"Error starting translation job: {e}")
        update_file_status(fileId, 'FAILED', jobId)
        return {
            'statusCode': 500,
            'body': f"Error starting translation job: {str(e)}"
        }

# Function to handle TXT files
def handle_txt(bucket_name, file_key, target_language ,fileId):
    update_file_status(fileId, 'IN_PROGRESS', fileId)
    file_name = os.path.basename(file_key)
    local_path = f"/tmp/{file_name}"
    s3_client.download_file(bucket_name, file_key, local_path)

    with open(local_path, 'r', encoding='utf-8') as file:
        content = file.read()

    response = translate_client.translate_text(
        Text=content,
        SourceLanguageCode='en',
        TargetLanguageCode=target_language
    )
    translated_text = response['TranslatedText']

    output_bucket = os.getenv('OUTPUT_BUCKET', 'outputbucket-dev')
    output_key = f"output/Translated-{file_name}"
    s3_client.put_object(Body=translated_text.encode('utf-8'), Bucket=output_bucket, Key=output_key)
    logger.info(f"TXT file translated and saved to {output_bucket}/{output_key}")

    # Update file status in DynamoDB
    update_file_status(fileId, 'COMPLETED')

    # generate presigned URL
    presigned_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': output_bucket, 'Key': output_key}, ExpiresIn=3600)
    logger.info(f"Presigned URL: {presigned_url}")

    # Send email notification after successful translation
    to_email = os.getenv('SES_RECIPIENT_EMAIL', 'omkarnagarkar53@gmail.com')
    send_email_via_ses(to_email=to_email, subject=f"Translation Completed - {fileId}", body=f"""
    <html>
    <body>
        <p>Your translated file for file {file_name} is ready for download. You can download it using the following link:</p>
        <p><a href="{presigned_url}">Download Translated File</a></p>
        <p>The link will expire in 1 hour.</p>
    </body>
    </html>
    """)

# Function to handle PDF files
def handle_pdf(bucket_name, file_key, data_access_role_arn, target_language, fileId):
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
    intermediate_key = f"input/{fileId}/{new_file_name}"
    s3_client.upload_file(local_docx_path, intermediate_bucket, intermediate_key)

    handle_docx(intermediate_bucket, intermediate_key, data_access_role_arn, target_language, fileId)

# Function to handle DOCX files
def handle_docx(bucket_name, file_key, data_access_role_arn, target_language, fileId):
    output_bucket = os.getenv('OUTPUT_BUCKET', 'outputbucket-dev')
    output_prefix = f"Translated-{file_key}"
    translation_job(bucket_name, file_key, output_bucket, output_prefix, data_access_role_arn, 'docx', target_language, fileId)

# Lambda Handler
def lambda_handler(event, context):
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']
        logger.info(f"Processing file: {file_key} from bucket: {bucket_name}")
        data_access_role_arn = os.getenv('DATA_ACCESS_ROLE_ARN','arn:aws:iam::867344435459:role/TranslateDataAccessRole')

        response = s3_client.head_object(Bucket=bucket_name, Key=file_key)
        logger.info(f"Head Object Response: {response}")
        metadata = response.get('Metadata', {})
        
        # Extract language metadata
        language = metadata.get('languagecode', 'en')  # Default to English if not provided
        fileId = metadata.get('fileid', None)
        print(f"Processing file '{file_key}' with language: {language}")


        # Determine the file type
        if file_key.endswith('.txt'):
            handle_txt(bucket_name, file_key, language, fileId)
        elif file_key.endswith('.docx'):
            handle_docx(bucket_name, file_key, data_access_role_arn, language, fileId)
        elif file_key.endswith('.pdf'):
            handle_pdf(bucket_name, file_key, data_access_role_arn, language, fileId)
        else:
            logger.error(f"Unsupported file type for file: {file_key}")
            return {
                'statusCode': 400,
                'body': f"Unsupported file type for file: {file_key}"
            }
        
        # Send email notification after successful translation
        #to_email = os.getenv('SES_RECIPIENT_EMAIL', 'omkarnagarkar53@gmail.com')
        #send_email_via_ses(to_email=to_email, subject="Translation Completed", body=f"The translation of '{os.path.basename(file_key)}' has been completed successfully and uploaded to outputbucket-dev'.")
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
