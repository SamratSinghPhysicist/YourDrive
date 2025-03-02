import os
import time
import uuid
import json
from functools import wraps
from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import asyncio
import functools

# Add back the coroutine decorator that was removed in Python 3.11
if not hasattr(asyncio, 'coroutine'):
    asyncio.coroutine = functools.wraps(lambda f: f)

from mega import Mega

app = Flask(__name__)
CORS(app)

# Configure Flask app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'yourdrive_secret_key')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_uploads')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB max upload size

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Mega instance
mega = Mega()

# List of Mega accounts for rotation
mega_accounts = [
    {'email': 'ysuni4@edny.net', 'password': 'Study@123'},
    {'email': 'buv55@edny.net', 'password': 'Study@123'},
    {'email': 'jbk8a@edny.net', 'password': 'Study@123'},
    {'email': 'sezsec@edny.net', 'password': 'Study@123'},
    {'email': 'areklu@edny.net', 'password': 'Study@123'},
    {'email': 'at9q2@edny.net', 'password': 'Study@123'},
    {'email': 'r2nwir@edny.net', 'password': 'Study@123'},
    {'email': 'urac0p@edny.net', 'password': 'Study@123'},
    {'email': 'jaez9h@edny.net', 'password': 'Study@123'},
    {'email': 'm574z@edny.net', 'password': 'Study@123'},
]

# Account rotation index
current_account_index = 0

# Active sessions storage
active_sessions = {}

# Helper function to get next account for rotation
def get_next_account():
    global current_account_index
    account = mega_accounts[current_account_index]
    current_account_index = (current_account_index + 1) % len(mega_accounts)
    return account

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_token = request.headers.get('Authorization')
        if not auth_token or auth_token not in active_sessions:
            return jsonify({'error': 'Unauthorized access'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Error handling
@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({
        'error': str(e),
        'status': 'error'
    }), 500

# Routes
@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user (in this case, just create a session with a Mega account)"""
    try:
        # In a real app, you would create a user account here
        # For this demo, we'll just create a session with a Mega account
        account = get_next_account()
        m = mega.login(account['email'], account['password'])
        
        # Generate a session token
        session_token = str(uuid.uuid4())
        
        # Store the session
        active_sessions[session_token] = {
            'mega_instance': m,
            'account': account['email'],
            'created_at': time.time()
        }
        
        return jsonify({
            'token': session_token,
            'message': 'Registration successful',
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login to YourDrive (creates a session with a Mega account)"""
    try:
        # In a real app, you would verify user credentials here
        # For this demo, we'll just create a session with a Mega account
        account = get_next_account()
        m = mega.login(account['email'], account['password'])
        
        # Generate a session token
        session_token = str(uuid.uuid4())
        
        # Store the session
        active_sessions[session_token] = {
            'mega_instance': m,
            'account': account['email'],
            'created_at': time.time()
        }
        
        return jsonify({
            'token': session_token,
            'message': 'Login successful',
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Logout from YourDrive (removes the session)"""
    try:
        auth_token = request.headers.get('Authorization')
        if auth_token in active_sessions:
            del active_sessions[auth_token]
        
        return jsonify({
            'message': 'Logout successful',
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/account/info', methods=['GET'])
@login_required
def account_info():
    """Get account information"""
    try:
        auth_token = request.headers.get('Authorization')
        m = active_sessions[auth_token]['mega_instance']
        
        # Get user details
        details = m.get_user()
        
        # Get storage space
        space_bytes = m.get_storage_space()
        space_mega = m.get_storage_space(mega=True)
        space_giga = m.get_storage_space(giga=True)
        
        return jsonify({
            'user_details': details,
            'storage': {
                'used_bytes': space_bytes['used'],
                'total_bytes': space_bytes['total'],
                'used_mb': space_mega['used'],
                'total_mb': space_mega['total'],
                'used_gb': space_giga['used'],
                'total_gb': space_giga['total'],
            },
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/files', methods=['GET'])
@login_required
def list_files():
    """List all files or files in a specific folder"""
    try:
        auth_token = request.headers.get('Authorization')
        m = active_sessions[auth_token]['mega_instance']
        
        # Get all files
        files = m.get_files()
        
        # Check if folder parameter is provided
        folder_name = request.args.get('folder')
        
        if folder_name:
            # Find the folder
            folder = m.find(folder_name)
            if not folder:
                return jsonify({
                    'error': f"Folder '{folder_name}' not found",
                    'status': 'error'
                }), 404
            
            folder_id = folder[0]
            
            # Filter files by parent folder
            folder_files = {k: v for k, v in files.items() if v.get('p') == folder_id}
            files_to_return = folder_files
        else:
            files_to_return = files
        
        # Format the response
        formatted_files = []
        for file_id, file_data in files_to_return.items():
            file_type = 'file' if file_data.get('t') == 0 else 'folder'
            name = file_data.get('a', {}).get('n', 'Unnamed')
            
            formatted_files.append({
                'id': file_id,
                'name': name,
                'type': file_type,
                'size': file_data.get('s', 0) if file_type == 'file' else None,
                'parent_id': file_data.get('p'),
                'created_at': file_data.get('ts', 0)
            })
        
        return jsonify({
            'files': formatted_files,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/files/upload', methods=['POST'])
@login_required
def upload_file():
    """Upload a file"""
    try:
        auth_token = request.headers.get('Authorization')
        m = active_sessions[auth_token]['mega_instance']
        
        # Check if file is in the request
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file part in the request',
                'status': 'error'
            }), 400
        
        file = request.files['file']
        
        # Check if a file was selected
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'status': 'error'
            }), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Save the file temporarily
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        # Check if destination folder is specified
        folder_name = request.form.get('folder')
        
        if folder_name:
            # Find the folder
            folder = m.find(folder_name)
            if not folder:
                # Clean up the temporary file
                os.remove(temp_path)
                return jsonify({
                    'error': f"Folder '{folder_name}' not found",
                    'status': 'error'
                }), 404
            
            folder_id = folder[0]
            
            # Upload the file to the specified folder
            uploaded_file = m.upload(temp_path, dest=folder_id)
        else:
            # Upload the file to the root folder
            uploaded_file = m.upload(temp_path)
        
        # Clean up the temporary file
        os.remove(temp_path)
        
        return jsonify({
            'file_id': uploaded_file,
            'message': 'File uploaded successfully',
            'status': 'success'
        })
    except Exception as e:
        # Clean up the temporary file if it exists
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(request.files['file'].filename))
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/files/download/<file_name>', methods=['GET'])
@login_required
def download_file(file_name):
    """Download a file"""
    try:
        auth_token = request.headers.get('Authorization')
        m = active_sessions[auth_token]['mega_instance']
        
        # Find the file
        found_file = m.find(file_name)
        
        if not found_file:
            return jsonify({
                'error': f"File '{file_name}' not found",
                'status': 'error'
            }), 404
        
        file_handle = found_file[0]
        
        # Set download path
        download_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file_name))
        
        # Download the file
        m.download(file_handle, download_path)
        
        # Send the file to the client
        response = send_file(
            download_path,
            as_attachment=True,
            download_name=file_name
        )
        
        # Clean up the file after sending (using a callback)
        @response.call_on_close
        def cleanup():
            if os.path.exists(download_path):
                os.remove(download_path)
        
        return response
    except Exception as e:
        # Clean up the temporary file if it exists
        download_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file_name))
        if os.path.exists(download_path):
            os.remove(download_path)
        
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/files/delete/<file_name>', methods=['DELETE'])
@login_required
def delete_file(file_name):
    """Delete a file or folder"""
    try:
        auth_token = request.headers.get('Authorization')
        m = active_sessions[auth_token]['mega_instance']
        
        # Find the item
        found_item = m.find(file_name)
        
        if not found_item:
            return jsonify({
                'error': f"Item '{file_name}' not found",
                'status': 'error'
            }), 404
        
        item_handle = found_item[0]
        
        # Delete the item
        m.delete(item_handle)
        
        return jsonify({
            'message': f"Item '{file_name}' deleted successfully",
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/files/rename/<file_name>', methods=['PUT'])
@login_required
def rename_file(file_name):
    """Rename a file or folder"""
    try:
        auth_token = request.headers.get('Authorization')
        m = active_sessions[auth_token]['mega_instance']
        
        # Get the new name from request data
        data = request.get_json()
        if not data or 'new_name' not in data:
            return jsonify({
                'error': 'New name not provided',
                'status': 'error'
            }), 400
        
        new_name = data['new_name']
        
        # Find the item
        found_item = m.find(file_name)
        
        if not found_item:
            return jsonify({
                'error': f"Item '{file_name}' not found",
                'status': 'error'
            }), 404
        
        item_handle = found_item[0]
        
        # Rename the item
        m.rename(item_handle, new_name)
        
        return jsonify({
            'message': f"Item renamed from '{file_name}' to '{new_name}' successfully",
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/folders', methods=['POST'])
@login_required
def create_folder():
    """Create a folder or folder structure"""
    try:
        auth_token = request.headers.get('Authorization')
        m = active_sessions[auth_token]['mega_instance']
        
        # Get folder path from request data
        data = request.get_json()
        if not data or 'folder_path' not in data:
            return jsonify({
                'error': 'Folder path not provided',
                'status': 'error'
            }), 400
        
        folder_path = data['folder_path']
        
        # Create the folder structure
        folder_structure = m.create_folder(folder_path)
        
        return jsonify({
            'folder_structure': folder_structure,
            'message': f"Folder '{folder_path}' created successfully",
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/files/link/<file_name>', methods=['GET'])
@login_required
def get_public_link(file_name):
    """Get a public link for a file or folder"""
    try:
        auth_token = request.headers.get('Authorization')
        m = active_sessions[auth_token]['mega_instance']
        
        # Find the item
        found_item = m.find(file_name)
        
        if not found_item:
            return jsonify({
                'error': f"Item '{file_name}' not found",
                'status': 'error'
            }), 404
        
        item_handle = found_item[0]
        
        # Generate public link
        public_link = m.export(item_handle)
        
        return jsonify({
            'public_link': public_link,
            'message': f"Public link generated for '{file_name}'",
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/files/import', methods=['POST'])
@login_required
def import_from_url():
    """Import a file from a public Mega URL"""
    try:
        auth_token = request.headers.get('Authorization')
        m = active_sessions[auth_token]['mega_instance']
        
        # Get URL from request data
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({
                'error': 'URL not provided',
                'status': 'error'
            }), 400
        
        url = data['url']
        folder_name = data.get('folder')
        
        # If destination folder is specified
        if folder_name:
            folder = m.find(folder_name)
            if not folder:
                return jsonify({
                    'error': f"Folder '{folder_name}' not found",
                    'status': 'error'
                }), 404
            
            folder_id = folder[0]
            imported_file = m.import_public_url(url, dest_node=folder_id)
        else:
            imported_file = m.import_public_url(url)
        
        return jsonify({
            'file_id': imported_file,
            'message': 'File imported successfully',
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)