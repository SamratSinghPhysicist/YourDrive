# YourDrive - Usage Guide

## Overview
YourDrive is a cloud storage solution that provides a simple and intuitive interface for storing, managing, and sharing your files. It's built with a Flask backend API and a simple frontend interface for easy interaction.

## Setup Instructions

### Prerequisites
- Python 3.x
- Required Python packages (install using `pip install -r requirements.txt`):
  - Flask
  - Flask-CORS
  - mega.py (version 1.0.8 or higher)
  - Werkzeug
  - pathlib
  - pycryptodome
  - requests
  - tenacity

### Installation
1. Clone or download the YourDrive repository
2. Navigate to the project directory
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
1. Start the Flask API server:
   ```bash
   python api.py
   ```
   This will start the server at `http://localhost:5000`

2. Open your web browser and navigate to:
   ```
   http://localhost:5000/static/index.html
   ```

## Using the Web Interface

### Authentication
- **Login**: Click the "Login to YourDrive" button to authenticate with a Mega account (the application uses account rotation)
- **Register**: Click the "Register" button to create a new session with a Mega account

### File Management
- **View Files**: After logging in, you'll see your files and folders listed
- **Navigate Folders**: Click on a folder to view its contents
- **Upload Files**: Click the "Upload File" button and select a file from your computer
- **Create Folders**: Click the "Create Folder" button, enter a name, and click "Create"

### File Operations
Click the three dots button next to any file or folder to access these operations:

- **Download**: Download the selected file to your computer
- **Rename**: Change the name of the selected file or folder
- **Get Sharing Link**: Generate a public link to share the file or folder
- **Delete**: Remove the file or folder from your storage

### Navigation
- Use the breadcrumb navigation at the top to move back to parent folders
- Click "Home" to return to the root directory

## Using the API Directly

YourDrive provides a RESTful API that you can use to interact with the service programmatically.

### Authentication Endpoints

#### Register a New User
```
POST /api/register
```
Response: Returns a session token to use for subsequent requests

#### Login
```
POST /api/login
```
Response: Returns a session token to use for subsequent requests

#### Logout
```
POST /api/logout
Headers: Authorization: <session_token>
```

### Account Information
```
GET /api/account/info
Headers: Authorization: <session_token>
```
Returns user details and storage information

### File Operations

#### List Files
```
GET /api/files
Headers: Authorization: <session_token>
Query Parameters (optional): folder=<folder_name>
```

#### Upload File
```
POST /api/files/upload
Headers: Authorization: <session_token>
Body: multipart/form-data with 'file' field and optional 'folder' field
```

#### Download File
```
GET /api/files/download/<file_name>
Headers: Authorization: <session_token>
```

#### Delete File or Folder
```
DELETE /api/files/delete/<file_name>
Headers: Authorization: <session_token>
```

#### Rename File or Folder
```
PUT /api/files/rename/<file_name>
Headers: Authorization: <session_token>
Body: {"new_name": "new_file_name"}
```

#### Create Folder
```
POST /api/folders
Headers: Authorization: <session_token>
Body: {"folder_path": "folder_name/subfolder"}
```

#### Get Public Link
```
GET /api/files/link/<file_name>
Headers: Authorization: <session_token>
```

#### Import from URL
```
POST /api/files/import
Headers: Authorization: <session_token>
Body: {"url": "mega_public_url", "folder": "optional_destination_folder"}
```

## Using the Command Line Interface

YourDrive also includes a command-line interface for managing your files:

```bash
python cli.py --email <email> --password <password> <command> [options]
```

Available commands:
- `info`: Get account information
- `list`: List files and folders (use `--folder` to specify a folder)
- `upload`: Upload a file (specify file path and optional `--folder` destination)
- `download`: Download a file (specify file name and optional `--destination` path)
- `create-folder`: Create a folder structure
- `delete`: Delete a file or folder
- `rename`: Rename a file or folder
- `get-link`: Get a public link for a file or folder
- `import`: Import a file from a public Mega URL

Example:
```bash
python cli.py --email user@example.com --password mypassword upload myfile.txt --folder Documents
```

## Troubleshooting

- **Authentication Issues**: If you encounter login problems, try using the register function to create a new session
- **File Upload Failures**: Ensure your file is under the 500MB size limit
- **API Errors**: Check the error message returned in the response for specific details

## Security Notes

- The application uses a rotation of Mega accounts for demonstration purposes
- In a production environment, you would implement proper user authentication
- API tokens are stored in browser localStorage and should be handled securely
- Temporary files are created during upload/download operations and automatically cleaned up