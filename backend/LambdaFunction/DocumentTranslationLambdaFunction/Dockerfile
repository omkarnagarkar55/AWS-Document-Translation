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
ENV OUTPUT_BUCKET_NAME=default-bucket
ENV IAM_ROLE_ARN=default-role

# Define the Lambda function handler
CMD ["lambda_function.lambda_handler"]
