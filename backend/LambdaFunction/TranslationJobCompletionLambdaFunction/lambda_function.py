import json
import logging
import smtplib
import os
import boto3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

s3_client = boto3.client('s3')
dynamodb = boto3.client('dynamodb')

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_file_id_by_job_id(job_id):
    """
    Retrieves the fileId and associated metadata from the DynamoDB table using the jobId index.
    """
    table_name = os.getenv('DYNAMODB_TABLE', 'FileMetadata') 
    job_index_name = os.getenv('DYNAMODB_JOB_INDEX', 'jobId-index') 
    try:
        # Query the table using the job-index
        response = dynamodb.query(
            TableName=table_name,
            IndexName=job_index_name,
            KeyConditionExpression="jobId = :jobId",
            ExpressionAttributeValues={
                ":jobId": {"S": job_id}
            }
        )

        # Check if items are returned
        if 'Items' in response and len(response['Items']) > 0:
            item = response['Items'][0]  # Get the first item
            logger.info(f"Item found: {item}")
            file_id = item['fileId']['S']  # Extract fileId
            logger.info(f"Found fileId '{file_id}' for jobId '{job_id}'.")
            return item  # Return the entire item if needed
        else:
            logger.error(f"No metadata found for jobId '{job_id}'.")
            return None

    except Exception as e:
        logger.error(f"Error querying DynamoDB for jobId '{job_id}': {e}")
        return None


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


def lambda_handler(event, context):
    try:
        output_bucket = os.getenv('OUTPUT_BUCKET', 'outputbucket-dev')
        # Log the event details
        logger.info(f"Received event: {json.dumps(event)}")

        # Extract details about the job
        jobId = event['detail']['jobId']
        job_status = event['detail']['jobStatus']
        accountid = event['account']
        logger.info(f"Job Name: {jobId}, Job Status: {job_status}")

        # Retrieve the fileId associated with the jobId
        item = get_file_id_by_job_id(jobId)
        file_id = item['fileId']['S']
        fileName = item['fileName']['S']
        languageCode = item['languageCode']['S']

        #If file name has .pdf extension, then replace it with .docx
        if fileName.endswith('.pdf'):
            fileName = fileName.replace('.pdf', '.docx')
        outfile_location = f"output/{accountid}-TranslateText-{jobId}/{languageCode}.{fileName}"
        logger.info(f"Output file location: {outfile_location}")

        # Process the event based on status
        if job_status == "COMPLETED":
            logger.info(f"Translation job '{jobId}' completed successfully.")
            update_file_status(file_id, 'COMPLETED')

            # generate presigned URL
            presigned_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': output_bucket, 'Key': outfile_location}, ExpiresIn=3600)
            logger.info(f"Presigned URL generated: {presigned_url}")

            # Add logic for successful job completion (e.g., send notification, move files, etc.)
            to_email = os.getenv('SES_RECIPIENT_EMAIL', 'omkarnagarkar53@gmail.com')
            send_email_via_ses(to_email=to_email, subject=f"Translation Completed-{jobId}", body=f"""
                <html>
                <body>
                    <p>Your translated file {fileName} is ready for download. You can download it using the following link:</p>
                    <p><a href="{presigned_url}">Download Translated File</a></p>
                    <p>The link will expire in 1 hour.</p>
                </body>
                </html>
            """)
            
        elif job_status == "FAILED":
            logger.error(f"Translation job '{jobId}' failed.")
            update_file_status(file_id, 'FAILED')
            # Add logic for failure (e.g., alert admin)
            send_email_via_ses(to_email=to_email, subject=f"Translation Failed -{jobId}", body=f"""
                <html>
                <body>
                    <p>Your document Translation Failed</p>
                </body>
                </html>
            """)

        return {
            'statusCode': 200,
            'body': 'Event processed successfully'
        }

    except Exception as e:
        logger.error(f"Error processing event: {e}")
        update_file_status(file_id, 'FAILED')
        return {
            'statusCode': 500,
            'body': f"Error processing event: {str(e)}"
        }
