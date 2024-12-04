# Use the AWS Lambda Python 3.8 base image
FROM public.ecr.aws/lambda/python:3.8

# Set the working directory inside the container
WORKDIR /var/task

# Copy the application code into the container
COPY lambda_function.py .

# If additional Python libraries are needed, include a requirements.txt file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org -r requirements.txt

# Set the environment variables
ENV OUTPUT_BUCKET_NAME=
ENV IAM_ROLE_ARN=
ENV SES_RECIPIENT_EMAIL=
ENV SES_SMTP_SERVER=
ENV SES_SMTP_PORT=
ENV SES_SMTP_USER=
ENV SES_SMTP_PASSWORD=
ENV SES_FROM_EMAIL=

# Define the Lambda function handler
CMD ["lambda_function.lambda_handler"]
