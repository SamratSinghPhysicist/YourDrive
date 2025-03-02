"""
Command-Line Interface (CLI) for Mega.co.nz Cloud Storage Manager
"""


#!/usr/bin/env python
import argparse
import getpass
import os
import sys
import asyncio
import functools
import time

# Add back the coroutine decorator that was removed in Python 3.11
if not hasattr(asyncio, 'coroutine'):
    asyncio.coroutine = functools.wraps(lambda f: f)

# Import Mega after fixing the coroutine decorator
from mega import Mega

# Initialize Mega instance
mega = Mega()

def print_separator(title):
    """Print a separator with a title for better readability"""
    print("\n" + "=" * 50)
    print(f" {title} ")
    print("=" * 50)

def login(args):
    """Login to Mega with provided credentials or anonymously"""
    print_separator("LOGIN")
    
    if args.email:
        if not args.password:
            args.password = getpass.getpass("Enter your Mega password: ")
        print(f"Logging in with account: {args.email}")
        try:
            m = mega.login(args.email, args.password)
            print("Login successful!")
            return m
        except Exception as e:
            print(f"Login failed: {e}")
            sys.exit(1)
    else:
        print("Logging in anonymously")
        try:
            m = mega.login()
            print("Anonymous login successful!")
            return m
        except Exception as e:
            print(f"Anonymous login failed: {e}")
            sys.exit(1)

def get_account_info(m):
    """Get and display account information"""
    print_separator("ACCOUNT INFORMATION")
    
    # Get user details
    details = m.get_user()
    print(f"User details: {details}")
    
    # Get account quota
    quota = m.get_quota()
    print(f"Account quota: {quota} bytes")
    
    # Get storage space in different units
    space_bytes = m.get_storage_space()
    space_mega = m.get_storage_space(mega=True)
    space_giga = m.get_storage_space(giga=True)
    
    print(f"Storage space used: {space_bytes['used']} bytes / {space_bytes['total']} bytes")
    print(f"Storage space used: {space_mega['used']:.2f} MB / {space_mega['total']} MB")
    print(f"Storage space used: {space_giga['used']:.4f} GB / {space_giga['total']} GB")
    
    # Try to get balance (Pro accounts only)
    try:
        balance = m.get_balance()
        print(f"Account balance: {balance}")
    except Exception as e:
        print(f"Could not get balance (Pro accounts only): {e}")

def list_files(m, args):
    """List all files in the account or in a specific folder"""
    print_separator("FILE LISTING")
    
    files = m.get_files()
    
    if args.folder:
        # Find the folder
        folder = m.find(args.folder)
        if not folder:
            print(f"Folder '{args.folder}' not found")
            return
        
        folder_id = folder[0]
        print(f"Listing contents of folder: {args.folder} (ID: {folder_id})")
        
        # Filter files by parent folder
        folder_files = {k: v for k, v in files.items() if v.get('p') == folder_id}
        files_count = sum(1 for v in folder_files.values() if v.get('t') == 0)
        folders_count = sum(1 for v in folder_files.values() if v.get('t') == 1)
        
        print(f"Total items: {len(folder_files)} ({files_count} files, {folders_count} folders)")
        
        # Display file information
        for file_id, file_data in folder_files.items():
            if file_data.get('t') == 0:  # Type 0 is file
                print(f"File: {file_data.get('a', {}).get('n', 'Unnamed')} (ID: {file_id})")
            elif file_data.get('t') == 1:  # Type 1 is folder
                print(f"Folder: {file_data.get('a', {}).get('n', 'Unnamed')} (ID: {file_id})")
    else:
        # List all files and folders
        files_count = sum(1 for v in files.values() if v.get('t') == 0)
        folders_count = sum(1 for v in files.values() if v.get('t') == 1)
        
        print(f"Total items: {len(files)} ({files_count} files, {folders_count} folders)")
        
        # Display file information
        for file_id, file_data in files.items():
            if file_data.get('t') == 0:  # Type 0 is file
                print(f"File: {file_data.get('a', {}).get('n', 'Unnamed')} (ID: {file_id})")
            elif file_data.get('t') == 1:  # Type 1 is folder
                print(f"Folder: {file_data.get('a', {}).get('n', 'Unnamed')} (ID: {file_id})")

def upload_file(m, args):
    """Upload a file to Mega"""
    print_separator("FILE UPLOAD")
    
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' does not exist")
        return
    
    print(f"Uploading file: {args.file}")
    
    try:
        # If destination folder is specified
        if args.folder:
            folder = m.find(args.folder)
            if not folder:
                print(f"Folder '{args.folder}' not found")
                return
            
            folder_id = folder[0]
            print(f"Uploading to folder: {args.folder} (ID: {folder_id})")
            uploaded_file = m.upload(args.file, dest=folder_id)
        else:
            uploaded_file = m.upload(args.file)
        
        print(f"File uploaded successfully. File handle: {uploaded_file}")
        
        # Get upload link if requested
        if args.get_link:
            upload_link = m.get_upload_link(uploaded_file)
            print(f"Upload link: {upload_link}")
    except Exception as e:
        print(f"Error during file upload: {e}")

def download_file(m, args):
    """Download a file from Mega"""
    print_separator("FILE DOWNLOAD")
    
    print(f"Searching for file: {args.file}")
    found_file = m.find(args.file)
    
    if not found_file:
        print(f"File '{args.file}' not found")
        return
    
    file_handle = found_file[0]
    print(f"Found file: {args.file} (ID: {file_handle})")
    
    # Set download path
    download_path = args.destination if args.destination else args.file
    
    print(f"Downloading to: {download_path}")
    try:
        m.download(file_handle, download_path)
        print(f"File downloaded successfully to: {download_path}")
    except Exception as e:
        print(f"Error downloading file: {e}")

def create_folder(m, args):
    """Create a folder or folder structure in Mega"""
    print_separator("FOLDER CREATION")
    
    print(f"Creating folder structure: {args.folder}")
    try:
        folder_structure = m.create_folder(args.folder)
        print(f"Created folder structure: {folder_structure}")
    except Exception as e:
        print(f"Error creating folder: {e}")

def delete_item(m, args):
    """Delete a file or folder from Mega"""
    print_separator("DELETE OPERATION")
    
    print(f"Searching for item: {args.item}")
    found_item = m.find(args.item)
    
    if not found_item:
        print(f"Item '{args.item}' not found")
        return
    
    item_handle = found_item[0]
    print(f"Found item: {args.item} (ID: {item_handle})")
    
    if args.confirm or input(f"Are you sure you want to delete '{args.item}'? (y/n): ").lower() == 'y':
        try:
            m.delete(item_handle)
            print(f"Item '{args.item}' deleted successfully")
        except Exception as e:
            print(f"Error deleting item: {e}")
    else:
        print("Delete operation cancelled")

def rename_item(m, args):
    """Rename a file or folder in Mega"""
    print_separator("RENAME OPERATION")
    
    print(f"Searching for item: {args.item}")
    found_item = m.find(args.item)
    
    if not found_item:
        print(f"Item '{args.item}' not found")
        return
    
    item_handle = found_item[0]
    print(f"Found item: {args.item} (ID: {item_handle})")
    
    try:
        m.rename(item_handle, args.new_name)
        print(f"Item renamed from '{args.item}' to '{args.new_name}' successfully")
    except Exception as e:
        print(f"Error renaming item: {e}")

def get_public_link(m, args):
    """Get a public link for a file or folder"""
    print_separator("PUBLIC LINK GENERATION")
    
    print(f"Searching for item: {args.item}")
    found_item = m.find(args.item)
    
    if not found_item:
        print(f"Item '{args.item}' not found")
        return
    
    item_handle = found_item[0]
    print(f"Found item: {args.item} (ID: {item_handle})")
    
    try:
        public_link = m.export(item_handle)
        print(f"Public link for '{args.item}': {public_link}")
    except Exception as e:
        print(f"Error generating public link: {e}")

def import_from_url(m, args):
    """Import a file from a public Mega URL"""
    print_separator("IMPORT FROM URL")
    
    print(f"Importing from URL: {args.url}")
    
    try:
        # If destination folder is specified
        if args.folder:
            folder = m.find(args.folder)
            if not folder:
                print(f"Folder '{args.folder}' not found")
                return
            
            folder_id = folder[0]
            print(f"Importing to folder: {args.folder} (ID: {folder_id})")
            imported_file = m.import_public_url(args.url, dest_node=folder_id)
        else:
            imported_file = m.import_public_url(args.url)
        
        print(f"File imported successfully: {imported_file}")
    except Exception as e:
        print(f"Error importing from URL: {e}")

def main():
    parser = argparse.ArgumentParser(description="YourDrive - Mega.co.nz Cloud Storage Manager")
    parser.add_argument('--email', help='Mega account email')
    parser.add_argument('--password', help='Mega account password')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Account info command
    info_parser = subparsers.add_parser('info', help='Get account information')
    
    # List files command
    list_parser = subparsers.add_parser('list', help='List files and folders')
    list_parser.add_argument('--folder', help='List files in a specific folder')
    
    # Upload file command
    upload_parser = subparsers.add_parser('upload', help='Upload a file')
    upload_parser.add_argument('file', help='File to upload')
    upload_parser.add_argument('--folder', help='Destination folder')
    upload_parser.add_argument('--get-link', action='store_true', help='Get upload link after upload')
    
    # Download file command
    download_parser = subparsers.add_parser('download', help='Download a file')
    download_parser.add_argument('file', help='File to download')
    download_parser.add_argument('--destination', help='Destination path')
    
    # Create folder command
    folder_parser = subparsers.add_parser('create-folder', help='Create a folder')
    folder_parser.add_argument('folder', help='Folder path to create (can include subfolders like "folder/subfolder")')
    
    # Delete item command
    delete_parser = subparsers.add_parser('delete', help='Delete a file or folder')
    delete_parser.add_argument('item', help='File or folder to delete')
    delete_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    
    # Rename item command
    rename_parser = subparsers.add_parser('rename', help='Rename a file or folder')
    rename_parser.add_argument('item', help='File or folder to rename')
    rename_parser.add_argument('new_name', help='New name')
    
    # Get public link command
    link_parser = subparsers.add_parser('get-link', help='Get a public link for a file or folder')
    link_parser.add_argument('item', help='File or folder to get link for')
    
    # Import from URL command
    import_parser = subparsers.add_parser('import', help='Import a file from a public Mega URL')
    import_parser.add_argument('url', help='Public Mega URL')
    import_parser.add_argument('--folder', help='Destination folder')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Login to Mega
    m = login(args)
    
    # Execute the requested command
    if args.command == 'info':
        get_account_info(m)
    elif args.command == 'list':
        list_files(m, args)
    elif args.command == 'upload':
        upload_file(m, args)
    elif args.command == 'download':
        download_file(m, args)
    elif args.command == 'create-folder':
        create_folder(m, args)
    elif args.command == 'delete':
        delete_item(m, args)
    elif args.command == 'rename':
        rename_item(m, args)
    elif args.command == 'get-link':
        get_public_link(m, args)
    elif args.command == 'import':
        import_from_url(m, args)

if __name__ == "__main__":
    main()