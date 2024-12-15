# AWS Document Translation

This repository provides a comprehensive solution for translating documents using AWS services. It includes a web user interface and backend workflow that leverage Amazon Translate to convert documents from one language to another.

## Features

- **Web Interface**: A user-friendly web application for uploading documents and initiating translations.
- **Backend Workflow**: Automated processing of documents using AWS Lambda functions and Amazon Translate.
- **Document Support**: Handles various document formats, ensuring accurate translation while preserving formatting.

## Architecture

The solution is built on a serverless architecture utilizing the following AWS services:

- **Amazon S3**: Stores the original and translated documents.
- **AWS Lambda**: Processes documents and interacts with translation services.
- **Amazon Translate**: Performs the actual text translation.
- **Amazon API Gateway**: Facilitates communication between the web interface and backend services.
- **Amazon Cognito**: Provides user authentication and authorization.
- **Amazon CloudWatch**: Monitors Lambda functions and logs events.
- **Amazon SES**: Sends email notifications upon job completion.

### Architecture Overview

Refer to the following architecture diagram for the overall flow of the application:
![AWS-Translate-Diagram drawio (1)](https://github.com/user-attachments/assets/867b27e0-d0b8-4604-9a18-cc47ae623c21)


### Key Components

1. **Translation Lambda Function**:
   - **Path**: `backend/LambdaFunction/DocumentTranslationLambdaFunction`
   - This Lambda function handles the translation process by leveraging Amazon Translate.
   - The function is dockerized to handle large dependencies efficiently.

   #### Steps to Dockerize and Deploy Lambda Function:
   - Navigate to the Lambda function directory:
     ```bash
     cd backend/LambdaFunction/DocumentTranslationLambdaFunction
     ```
   - Build the Docker image:
     ```bash
     docker build -t document-translation-lambda .
     ```
   - Tag the Docker image:
     ```bash
     docker tag document-translation-lambda:latest <your-aws-account-id>.dkr.ecr.<region>.amazonaws.com/document-translation-lambda:latest
     ```
   - Push the image to Amazon ECR:
     ```bash
     docker push <your-aws-account-id>.dkr.ecr.<region>.amazonaws.com/document-translation-lambda:latest
     ```
   - Deploy the Lambda function using the container image in AWS Lambda Console or CLI.

2. **Notification Lambda Function**:
   - **Path**: `backend/LambdaFunction/TranslationJobCompletionLambdaFunction`
   - This Lambda function sends email notifications to the user using Amazon SES when the translation job is completed.
   - The function is triggered by CloudWatch Events, which monitors the completion of translation jobs.

## Installation

To deploy this solution, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/omkarnagarkar55/AWS-Document-Translation.git
   cd AWS-Document-Translation
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Install and Configure Amplify CLI**:
   - Install the Amplify CLI globally:
     ```bash
     npm install -g @aws-amplify/cli
     ```
   - Configure the Amplify CLI:
     ```bash
     amplify configure
     ```
     Follow the on-screen instructions to set up an AWS IAM user with the necessary permissions and configure the CLI.

4. **Initialize Amplify in the Project**:
   ```bash
   amplify init
   ```
   Follow the prompts to initialize the Amplify project.

5. **Deploy Backend Services**:
   Utilize AWS Amplify or the Serverless Framework to deploy the backend infrastructure:
   ```bash
   amplify push
   ```

6. **Configure Frontend**:
   Update the frontend configuration to point to the deployed backend services.

7. **Run the Application**:
   ```bash
   npm start
   ```

## Deleting Amplify Resources

To delete the Amplify resources associated with this project, follow these steps:

1. **Delete Amplify Backend Resources**:
   ```bash
   amplify delete
   ```
   This command will remove all the Amplify resources created during the project setup, including S3 buckets, Lambda functions, and other associated services. Follow the prompts to confirm the deletion.

2. **Clean Up AWS Services Manually** (if necessary):
   - Log in to the AWS Management Console.
   - Navigate to the services (e.g., S3, Lambda, DynamoDB) and ensure all resources related to this project are deleted.

3. **Remove Local Amplify Files**:
   Delete the `.amplify` directory and associated configuration files from your local project directory:
   ```bash
   rm -rf amplify/.config amplify/backend amplify/team-provider-info.json
   ```

## Usage

1. **Access the Web Interface**: Open your browser and navigate to the application's URL.
2. **Upload Document**: Use the upload feature to select the document you wish to translate.
3. **Select Target Language**: Choose the language into which you want the document translated.
4. **Initiate Translation**: Click the translate button to start the process.
5. **Download Translated Document**: Once the translation is complete, download the translated document from the interface.

## Contributing

Contributions are welcome! Please fork this repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

This solution is inspired by AWS samples and utilizes AWS services for document translation.

For more information, refer to the [AWS Documentation](https://aws.amazon.com/documentation/).
