# YourDrive - Mega.co.nz Cloud Storage Manager

YourDrive is a Python application that demonstrates the functionality of the Mega.py library for interacting with Mega.co.nz cloud storage. This application allows you to manage your Mega.co.nz account, including file and folder operations, account information retrieval, and more.

## Features

- **Account Management**: Login with credentials or anonymously
- **Account Information**: View user details, storage quota, and space usage
- **File Operations**: Upload, download, find, rename, export (public link), and delete files
- **Folder Operations**: Create, find, rename, export, and delete folders
- **Import from URL**: Import files from public Mega.co.nz URLs
- **Multiple Account Support**: Manage multiple Mega accounts

## Requirements

- Python 3.x
- mega.py library (version 1.0.8 or higher)
- pathlib
- pycryptodome
- requests
- tenacity

## Installation

```bash
pip install mega.py
```

## Usage

Run the application using Python:

```bash
python app.py
```

## Known Issues

- There are issues with the rename operations for both files and folders, showing "string indices must be integers" errors.
- The application currently uses hardcoded account credentials for demonstration purposes.

## Security Note

This application contains hardcoded Mega account credentials for demonstration purposes. In a production environment, it's recommended to:

1. Store credentials securely (e.g., environment variables or a secure configuration file)
2. Implement proper authentication mechanisms
3. Handle exceptions appropriately

## License

This project is provided as-is for educational purposes.

## Contributing

Contributions to fix bugs or add features are welcome. Please feel free to submit a pull request or open an issue to discuss potential improvements.