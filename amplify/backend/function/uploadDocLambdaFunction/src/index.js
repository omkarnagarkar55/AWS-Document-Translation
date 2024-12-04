

/**
 * @type {import('@types/aws-lambda').APIGatewayProxyHandler}
 */

const AWS = require('aws-sdk');
const s3 = new AWS.S3();
const dynamoDB = new AWS.DynamoDB.DocumentClient();
const { v4: uuidv4 } = require('uuid');


exports.handler = async (event) => {
    console.log(`EVENT: ${JSON.stringify(event)}`);
    const { fileName, fileType, languageCode } = JSON.parse(event.body);
    console.log("Filetype :", fileType)
    console.log("FileName :", fileName)
    console.log("LanguageCode :", languageCode)
    const fileId = uuidv4();
    const bucketName = 'input-bucketbd99d-dev';


    const params = {
        Bucket: bucketName,
        Key: `input/${encodeURIComponent(fileName)}`,
        Expires: 800, // Expires in 5 minutes
        ContentType: fileType,
        Metadata: {
          languageCode,
          fileId
        },
        //ACL: 'public-read' // or 'private', depending on your needs
      };

      try {
        const preSignedUrl = s3.getSignedUrl('putObject', params);
        console.log("Generated Pre-Signed URL:", preSignedUrl);

        // Save file metadata to DynamoDB
        const dbParams = {
          TableName: 'FileMetadata',
          Item: {
              fileId: fileId,
              fileName: fileName,
              fileType: fileType,
              bucketName: bucketName,
              languageCode: languageCode,
              status: 'Pending',
              createdAt: new Date().toISOString(),
          },
      };

      await dynamoDB.put(dbParams).promise();
      console.log("File metadata saved to DynamoDB:", dbParams);

        return {
          statusCode: 200,
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        },
          body: JSON.stringify({ url: preSignedUrl })
        };
      } catch (err) {
        return {
          statusCode: 500,
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        },
          body: JSON.stringify({ error: 'Could not create a pre-signed URL' })
        };
      }

};
