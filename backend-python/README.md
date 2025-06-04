# How To configure the Environment
`pip install -r requirements.txt`

# How To Execute
`python ./main.py`

**Running on http://127.0.0.1:5000**



# Endpoints Overview

## Build Docker Image
**URL**: `/<projectUuid>/build-docker-image`  
**Method**: `POST`  
**Description**: Builds a Docker image based on provided configurations and optional database configurations.  
**Request Body**:
- **configurationForm**: Includes Dockerfile, database Dockerfile, and configuration details.
- **projectUuid**: Unique identifier for the project.
- **DBhas**, **dbConfiguration**: Optional fields for database configuration.

**Response**: Returns the Docker image ID or an error message if the build fails.

---

## Build Dockerfile
**URL**: `/<projectUuid>/build-docker-file`  
**Method**: `POST`  
**Description**: Constructs a Dockerfile based on the provided request data.  
**Request Body**: JSON containing project UUID, programming languages, operating system, and dependencies.

**Response**: Returns the generated Dockerfile content or an error message.

---

## Get Configuration
**URL**: `/<projectUuid>/get-configuration`  
**Method**: `GET`  
**Description**: Retrieves the saved configuration for a given project UUID.

**Response**: The project configuration or an error message.

---

## Validate Docker Image
**URL**: `/<projectUuid>/validates-docker-image`  
**Method**: `POST`  
**Description**: Validates a Docker image with the specified Python dependencies.  
**Request Body**:
- **pythondependencies**: List of Python dependencies to validate.
- **tagId**: Tag ID of the Docker image to validate.

**Response**: The new Docker image ID if successful or an error message.

---

## Run Docker Container
**URL**: `/<projectUuid>/run-container`  
**Method**: `POST`  
**Description**: Runs a Docker container using the specified image and command. Supports running containers with database configurations.  
**Request Body**:
- **command**: Command to execute within the container.
- **tagId**: Docker image tag ID.
- **Optional**: Configuration form details for databases.

**Response**: The container logs or a message indicating that the container is running.

---

## Package Research Artifact
**URL**: `/<projectUuid>/package`  
**Method**: `GET`  
**Description**: Packages project files and Docker images into a zip file for research artifact purposes.  
**Request Body**: Contains information about commands to run, Docker tag ID, and optional database configurations.

**Response**: A downloadable zip file containing all the necessary files and scripts.
