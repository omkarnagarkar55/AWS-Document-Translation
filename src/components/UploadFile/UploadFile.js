// FILE: UploadFile.js
import React, { useState } from 'react';
import {  post} from 'aws-amplify/api';
import { fetchAuthSession } from 'aws-amplify/auth'

function UploadFile() {
  const [file, setFile] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!file) {
      alert('Please select a file to upload');
      return;
    }

    try {
        const authToken = (await fetchAuthSession()).tokens?.idToken?.toString();
        console.log('authToken:', authToken);
      const response = await post({
        apiName: 'uploadAPI',
        path: '/upload',
        options: {
            headers: {
                Authorization: `Bearer ${authToken}`,
                }
        }
      }).response;
      console.log('File uploaded successfully:', response);
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div>
      <h2>Upload File</h2>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
}

export default UploadFile;