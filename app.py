import asyncio
import functools
import os
import time

# Add back the coroutine decorator that was removed in Python 3.11
if not hasattr(asyncio, 'coroutine'):
    asyncio.coroutine = functools.wraps(lambda f: f)

from mega import Mega

# Initialize Mega instance
mega = Mega()

# List of Mega accounts
mega_accounts = [{ 'email': 'ysuni4@edny.net', 'password': 'Study@123' }, { 'email': 'buv55@edny.net', 'password': 'Study@123' }, { 'email': 'jbk8a@edny.net', 'password': 'Study@123' }, { 'email': 'sezsec@edny.net', 'password': 'Study@123' }, { 'email': 'areklu@edny.net', 'password': 'Study@123' }, { 'email': 'at9q2@edny.net', 'password': 'Study@123' }, { 'email': 'r2nwir@edny.net', 'password': 'Study@123' }, { 'email': 'urac0p@edny.net', 'password': 'Study@123' }, { 'email': 'jaez9h@edny.net', 'password': 'Study@123' }, { 'email': 'm574z@edny.net', 'password': 'Study@123' },]

def print_separator(title):
    """Print a separator with a title for better readability"""
    print("\n" + "=" * 50)
    print(f" {title} ")
    print("=" * 50)

def login_to_mega(email=None, password=None):
    """Login to Mega with provided credentials or anonymously"""
    print_separator("LOGIN")
    if email and password:
        print(f"Logging in with account: {email}")
        m = mega.login(email, password)
    else:
        print("Logging in anonymously")
        m = mega.login()
    return m

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
    space_kilo = m.get_storage_space(kilo=True)
    space_mega = m.get_storage_space(mega=True)
    space_giga = m.get_storage_space(giga=True)
    
    print(f"Storage space in bytes: {space_bytes}")
    print(f"Storage space in kilobytes: {space_kilo}")
    print(f"Storage space in megabytes: {space_mega}")
    print(f"Storage space in gigabytes: {space_giga}")
    
    # Try to get balance (Pro accounts only)
    try:
        balance = m.get_balance()
        print(f"Account balance: {balance}")
    except Exception as e:
        print(f"Could not get balance (Pro accounts only): {e}")

def list_files(m):
    """List all files in the account"""
    print_separator("FILE LISTING")
    files = m.get_files()
    print(f"Total files: {len(files)}")
    
    # Display file information
    for file_id, file_data in files.items():
        if file_data['t'] == 0:  # Type 0 is file
            print(f"File: {file_data.get('a', {}).get('n', 'Unnamed')} (ID: {file_id})")
        elif file_data['t'] == 1:  # Type 1 is folder
            print(f"Folder: {file_data.get('a', {}).get('n', 'Unnamed')} (ID: {file_id})")

def file_operations(m):
    """Demonstrate file operations: upload, download, find, rename, etc."""
    print_separator("FILE OPERATIONS")
    
    # Create a test file
    test_file_path = "test_upload.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file for Mega.py demonstration.")
    
    print(f"Created test file: {test_file_path}")
    
    # Upload the file
    print("\nUploading file...")
    try:
        uploaded_file = m.upload(test_file_path)
        print(f"File uploaded successfully. File handle: {uploaded_file}")
        
        # Get upload link
        upload_link = m.get_upload_link(uploaded_file)
        print(f"Upload link: {upload_link}")
        
        # Find the file
        print("\nSearching for the uploaded file...")
        found_file = m.find(os.path.basename(test_file_path))
        if found_file:
            print(f"Found file: {found_file}")
            
            # Rename the file
            print("\nRenaming the file...")
            new_name = "renamed_test_file.txt"
            # Fix: Extract the file handle from the found_file tuple
            file_handle = found_file[0]
            try:
                m.rename(file_handle, new_name)
                print(f"File renamed to: {new_name}")
            except Exception as e:
                print(f"Error renaming file: {e}")
            
            # Export (get public link)
            print("\nExporting file (generating public link)...")
            try:
                public_link = m.export(file_handle)
                print(f"Public link: {public_link}")
            except Exception as e:
                print(f"Error exporting file: {e}")
            
            # Download the file
            print("\nDownloading the file...")
            download_path = "downloaded_test_file.txt"
            try:
                m.download(file_handle, download_path)
                print(f"File downloaded to: {download_path}")
            except Exception as e:
                print(f"Error downloading file: {e}")
            
            # Delete the file
            print("\nDeleting the file...")
            try:
                m.delete(file_handle)
                print("File deleted successfully")
            except Exception as e:
                print(f"Error deleting file: {e}")
    except Exception as e:
        print(f"Error during file operations: {e}")
    
    # Clean up local test files
    try:
        os.remove(test_file_path)
        if os.path.exists("downloaded_test_file.txt"):
            os.remove("downloaded_test_file.txt")
    except Exception as e:
        print(f"Error cleaning up test files: {e}")

def folder_operations(m):
    """Demonstrate folder operations: create, find, rename, etc."""
    print_separator("FOLDER OPERATIONS")
    
    # Create folders
    print("Creating folders...")
    try:
        folder_structure = m.create_folder("test_folder/subfolder/subsubfolder")
        print(f"Created folder structure: {folder_structure}")
        
        # Find the main folder
        print("\nFinding the created folder...")
        found_folder = m.find("test_folder")
        if found_folder:
            print(f"Found folder: {found_folder}")
            
            # Rename the folder
            print("\nRenaming the folder...")
            # Fix: Extract the folder handle from the found_folder tuple
            folder_handle = found_folder[0]
            try:
                m.rename(folder_handle, "renamed_test_folder")
                print("Folder renamed successfully")
            except Exception as e:
                print(f"Error renaming folder: {e}")
            
            # Export the folder (get public link)
            print("\nExporting folder (generating public link)...")
            try:
                public_link = m.export(folder_handle)
                print(f"Public link for folder: {public_link}")
            except Exception as e:
                print(f"Error exporting folder: {e}")
            
            # Delete the folder
            print("\nDeleting the folder...")
            try:
                m.delete(folder_handle)
                print("Folder deleted successfully")
            except Exception as e:
                print(f"Error deleting folder: {e}")
    except Exception as e:
        print(f"Error during folder operations: {e}")

def import_from_url(m):
    """Demonstrate importing files from public URLs"""
    print_separator("IMPORT FROM URL")
    
    # Note: This requires a valid Mega public URL
    print("To import from a URL, you would use:")
    print("m.import_public_url('https://mega.co.nz/#!valid_url_here')")
    print("\nOr to import to a specific folder:")
    print("folder_node = m.find('Documents')[0]")
    print("m.import_public_url('https://mega.co.nz/#!valid_url_here', dest_node=folder_node)")

def main():
    """Main function to demonstrate Mega.py functionality"""
    # Login with the first account from the list
    m = login_to_mega(mega_accounts[0]['email'], mega_accounts[0]['password'])
    
    # Get account information
    get_account_info(m)
    
    # List files
    list_files(m)
    
    # Demonstrate file operations
    file_operations(m)
    
    # Demonstrate folder operations
    folder_operations(m)
    
    # Demonstrate import from URL
    import_from_url(m)
    
    print_separator("DEMO COMPLETED")

if __name__ == "__main__":
    main()
