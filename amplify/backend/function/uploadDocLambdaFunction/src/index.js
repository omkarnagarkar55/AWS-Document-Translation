

/**
 * @type {import('@types/aws-lambda').APIGatewayProxyHandler}
 */

const AWS = require('aws-sdk');
const s3 = new AWS.S3();


exports.handler = async (event) => {
    console.log(`EVENT: ${JSON.stringify(event)}`);
    const { fileName, fileType } = JSON.parse(event.body);
    console.log("Filetype :", fileType)
    console.log("FileName :", fileName)

    const params = {
        Bucket: 'input-bucketbd99d-dev',
        Key: `input/${encodeURIComponent(fileName)}`,
        Expires: 600, // Expires in 5 minutes
        ContentType: fileType,
        //ACL: 'public-read' // or 'private', depending on your needs
      };

      try {
        const preSignedUrl = s3.getSignedUrl('putObject', params);
        console.log("Generated Pre-Signed URL:", preSignedUrl);
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
