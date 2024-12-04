// FILE: UploadFile.js
import React, { useState } from "react";
import { post } from "aws-amplify/api";
import { fetchAuthSession } from "aws-amplify/auth";

function UploadFile() {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState("en");

  const languages = [
    { code: "en", name: "English" },
    { code: "es", name: "Spanish" },
    { code: "de", name: "German" },
    { code: "fr", name: "French" },
    { code: "zh", name: "Chinese" },
  ];

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleLanguageChange = (event) => {
    setLanguage(event.target.value);
  };

  const uploadFile = async () => {
    if (!file) {
      alert("Please select a file to upload");
      return;
    }

    try {
      const authToken = (await fetchAuthSession()).tokens?.idToken?.toString();
      console.log("authToken:", authToken);
      const { body } = await post({
        apiName: "uploadAPI",
        path: "/upload",
        options: {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
          body: {
            fileName: file.name,
            fileType: file.type,
          },
        },
      }).response;
      console.log("File uploaded successfully:", body);
      const { url } = await body.json();
      console.log("Presigned URL:", url);

      // Upload the file using the pre-signed URL
      const result = await fetch(url, {
        method: "PUT",
        headers: {
          "Content-Type": file.type, // important to match the ContentType specified in Lambda
        },
        body: file,
      });

      if (result.ok) {
        alert("Upload successful!");
      } else {
        alert("Upload failed.");
      }
    } catch (error) {
      console.error("Error uploading file:", error);
    }
  };

  return (
    <div>
      <input type="file" onChange={handleFileChange} />
      <select value={language} onChange={handleLanguageChange}>
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.name}
          </option>
        ))}
      </select>
      <button onClick={uploadFile}>Upload and Translate</button>
    </div>
  );
}

export default UploadFile;
