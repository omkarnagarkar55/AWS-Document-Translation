import json
import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
    msg.attach(MIMEText(body, 'plain'))

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
        # Log the event details
        logger.info(f"Received event: {json.dumps(event)}")

        # Extract details about the job
        job_name = event['detail']['JobName']
        job_status = event['detail']['Status']
        logger.info(f"Job Name: {job_name}, Job Status: {job_status}")

        # Process the event based on status
        if job_status == "COMPLETED":
            logger.info(f"Translation job '{job_name}' completed successfully.")
            # Add logic for successful job completion (e.g., send notification, move files, etc.)
            
            to_email = os.getenv('SES_RECIPIENT_EMAIL', 'omkarnagarkar53@gmail.com')
            send_email_via_ses(to_email=to_email, subject="Translation Completed", body=f"The translation has been completed successfully.")
        elif job_status == "FAILED":
            logger.error(f"Translation job '{job_name}' failed.")
            # Add logic for failure (e.g., alert admin)
            send_email_via_ses(to_email=to_email, subject="Translation Failed", body=f"The translation has Failed.")

        return {
            'statusCode': 200,
            'body': 'Event processed successfully'
        }

    except Exception as e:
        logger.error(f"Error processing event: {e}")
        return {
            'statusCode': 500,
            'body': f"Error processing event: {str(e)}"
        }
