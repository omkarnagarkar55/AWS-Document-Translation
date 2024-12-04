import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { post } from "aws-amplify/api";
import { fetchAuthSession } from "aws-amplify/auth";
import "./UploadFile.css";

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

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

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

      const result = await fetch(url, {
        method: "PUT",
        headers: {
          "Content-Type": file.type,
        },
        body: file,
      });

      if (result.ok) {
        console.log("Upload successful!");
      } else {
        console.log("Upload failed.");
      }
    } catch (error) {
      console.error("Error uploading file:", error);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    <div className="upload-container">
      <div className="drag-and-dropdown-container">
        <div
          {...getRootProps()}
          className={`dropzone ${isDragActive ? "active" : ""}`}
        >
          <input
            {...getInputProps()}
            onChange={handleFileChange}
          />
          <div className="drag-and-drop-content">
            <i className="bi bi-upload icon"></i>
            <p>
              {isDragActive
                ? "Drop the file here..."
                : "Drag and drop a file here, or click to select one"}
            </p>
          </div>
        </div>

        <div className="dropdown-container">
          <div className="btn-group">
            <button type="button" className="btn btn-secondary">
              {languages.find((lang) => lang.code === language)?.name ||
                "Select Language"}
            </button>
            <button
              type="button"
              className="btn btn-secondary dropdown-toggle dropdown-toggle-split"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <span className="visually-hidden">Toggle Dropdown</span>
            </button>
            <ul className="dropdown-menu">
              {languages.map((lang) => (
                <li key={lang.code}>
                  <button
                    className="dropdown-item"
                    onClick={() =>
                      handleLanguageChange({ target: { value: lang.code } })
                    }
                  >
                    {lang.name}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="file-info-container">
        <p className="file-info">
          <strong>Selected file:</strong>{" "}
          {file ? file.name : "No file selected"}
        </p>
      </div>

      <div className="button-container">
        <button
          className="btn btn-outline-success upload-button"
          onClick={uploadFile}
        >
          Upload and Translate
        </button>
      </div>
    </div>
  );
}

export default UploadFile;
