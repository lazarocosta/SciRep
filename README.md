## API-REST-Python with Flask
[Check This Guide](backend-python/README.md)


# API-REST-Node-JS with Neo4j

## Prerequisites
To run this API, ensure you have the following prerequisites set up:

1. **Neo4j Database**: Version 4.0.0 or higher.
   - Note: The project is designed to handle two separate connections to the Neo4j database.
2. **Neo4j Connection Settings**:
   - **Connection String**: `bolt://localhost:7687`
   - **Credentials**:
     - **User**: `neo4j`
     - **Password**: `1234`

## How to Run
1. **Install Dependencies**:
   ```bash
   npm install

2. **How To Execute**:
   ```bash
   npm start

**Running on http://127.0.0.1:3000**


# API Documentation

## 1. Add a Folder to a Project
- **Endpoint**: `POST /:projectUuid/folder`
- **Description**: Adds a new folder to the specified project.
- **Parameters**:
  - `projectUuid` (string, URL parameter): The UUID of the project.
- **Request Body**:
  - `parentDirectory` (JSON object): Information about the parent directory where the folder will be created.
  - `folderInformation` (JSON object): Details of the folder to be created.
- **Response**:
  - **200 OK**: Folder successfully created.
  - **400 Bad Request**: If the `parentDirectory` or `folderInformation` is not provided.
  - **500 Internal Server Error**: If there is an error during the folder creation process.

---

## 2. Get Programming Languages Used in a Project
- **Endpoint**: `GET /:projectUuid/programmingLanguages`
- **Description**: Retrieves the programming languages associated with the specified project.
- **Parameters**:
  - `projectUuid` (string, URL parameter): The UUID of the project.
- **Response**:
  - **200 OK**: Returns a list of programming languages.
  - **400 Bad Request**: If `projectUuid` is missing.
  - **500 Internal Server Error**: If there is an error during retrieval.

---

## 3. Get Python Files in a Project
- **Endpoint**: `GET /:projectUuid/pythonfiles`
- **Description**: Retrieves all Python files associated with the specified project.
- **Parameters**:
  - `projectUuid` (string, URL parameter): The UUID of the project.
- **Response**:
  - **200 OK**: Returns a list of Python files.
  - **500 Internal Server Error**: If there is an error during retrieval.

---

## 4. Get Folders in a Project
- **Endpoint**: `GET /:projectUuid/folders`
- **Description**: Retrieves all folders associated with the specified project.
- **Parameters**:
  - `projectUuid` (string, URL parameter): The UUID of the project.
- **Response**:
  - **200 OK**: Returns a list of folders.
  - **500 Internal Server Error**: If there is an error during retrieval.

---


## 5. Upload a File to a Project
- **Endpoint**: `POST /:projectUuid/uploadfile`
- **Description**: Uploads a file to the specified project.
- **Parameters**:
  - `projectUuid` (string, URL parameter): The UUID of the project.
- **Request Body**:
  - `parentDirectory` (JSON object): The directory where the file will be uploaded.
  - `fileInformation` (JSON object): Details of the file to be uploaded.
- **Form Data**:
  - `file` (file): The file to be uploaded.
- **Response**:
  - **200 OK**: File successfully uploaded.
  - **400 Bad Request**: If no file is provided or if required information is missing.
  - **500 Internal Server Error**: If there is an error during file upload.

---

## 6. Upload a Project
- **Endpoint**: `POST /:projectUuid/uploadproject`
- **Description**: Uploads a project with all its associated files and folders.
- **Parameters**:
  - `projectUuid` (string, URL parameter): The UUID of the project.
- **Request Body**:
  - The project file(s) to be uploaded.
- **Response**:
  - **200 OK**: Project successfully uploaded.
  - **400 Bad Request**: If no project file is provided.
  - **500 Internal Server Error**: If there is an error during project upload.

---

## 7. Upload a Project from a Remote Repository
- **Endpoint**: `POST /:projectUuid/uploadgitproject`
- **Description**: Uploads a project from a remote repository, such as GitHub, Figshare, or Zenodo.
- **Parameters**:
  - `projectUuid` (string, URL parameter): The UUID of the project.
- **Request Body**:
  - `repositorySelected` (string): The repository type (e.g., "GitHub", "Figshare").
  - `projectLocation` (string): The URL or DOI of the remote project.
  - `defaultBranchName` (string, optional): The default branch name (for GitHub).
  - `downloadAllFiles` (boolean, optional): Whether to download all files.
  - `files` (array, optional): Specific files to download.
- **Response**:
  - **200 OK**: Project successfully uploaded from the remote repository.
  - **400 Bad Request**: If required information is missing.
  - **500 Internal Server Error**: If there is an error during upload.

---

## 8. Add a Folder to a Project (Alternative)
- **Endpoint**: `POST /:projectUuid/addfolder`
- **Description**: Another way to add a folder to the specified project.
- **Parameters**:
  - `projectUuid` (string, URL parameter): The UUID of the project.
- **Request Body**:
  - `parentDirectory` (JSON object): Information about the parent directory.
  - `folderInformation` (JSON object): Details of the folder to be created.
- **Response**:
  - **200 OK**: Folder successfully created.
  - **400 Bad Request**: If required information is missing.
  - **500 Internal Server Error**: If there is an error during folder creation.

---

