// YourDrive Frontend JavaScript

// API Base URL
const API_BASE_URL = '/api';

// Global state
let currentFolder = '';
let authToken = localStorage.getItem('authToken') || null;
let selectedFile = null;

// DOM Elements
const loginContainer = document.getElementById('loginContainer');
const appContainer = document.getElementById('appContainer');
const filesList = document.getElementById('filesList');
const breadcrumb = document.getElementById('breadcrumb');
const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const createFolderBtn = document.getElementById('createFolderBtn');
const logoutBtn = document.getElementById('logoutBtn');
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');
const uploadProgress = document.getElementById('uploadProgress');
const progressBar = uploadProgress.querySelector('.progress-bar');

// Bootstrap modals
const fileActionsModal = new bootstrap.Modal(document.getElementById('fileActionsModal'));
const createFolderModal = new bootstrap.Modal(document.getElementById('createFolderModal'));
const renameModal = new bootstrap.Modal(document.getElementById('renameModal'));
const shareLinkModal = new bootstrap.Modal(document.getElementById('shareLinkModal'));

// Initialize the app
function init() {
    // Check if user is logged in
    if (authToken) {
        showApp();
        loadFiles();
    } else {
        showLogin();
    }

    // Set up event listeners
    setupEventListeners();
}

// Set up event listeners
function setupEventListeners() {
    // Login and register buttons
    loginBtn.addEventListener('click', handleLogin);
    registerBtn.addEventListener('click', handleRegister);
    logoutBtn.addEventListener('click', handleLogout);

    // File operations
    uploadBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileUpload);
    createFolderBtn.addEventListener('click', () => createFolderModal.show());
    document.getElementById('confirmCreateFolderBtn').addEventListener('click', handleCreateFolder);

    // File action buttons
    document.getElementById('downloadBtn').addEventListener('click', handleDownload);
    document.getElementById('renameBtn').addEventListener('click', showRenameModal);
    document.getElementById('shareBtn').addEventListener('click', handleGetShareLink);
    document.getElementById('deleteBtn').addEventListener('click', handleDelete);
    document.getElementById('confirmRenameBtn').addEventListener('click', handleRename);
    document.getElementById('copyLinkBtn').addEventListener('click', copyShareLink);
}

// Show login screen
function showLogin() {
    loginContainer.style.display = 'block';
    appContainer.style.display = 'none';
}

// Show app screen
function showApp() {
    loginContainer.style.display = 'none';
    appContainer.style.display = 'block';
}

// API request helper
async function apiRequest(endpoint, method = 'GET', data = null, isFormData = false) {
    const headers = {
        'Authorization': authToken
    };

    if (!isFormData && method !== 'GET' && data) {
        headers['Content-Type'] = 'application/json';
    }

    const options = {
        method,
        headers
    };

    if (data) {
        if (isFormData) {
            options.body = data;
        } else if (method !== 'GET') {
            options.body = JSON.stringify(data);
        }
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        
        // Handle file downloads
        if (endpoint.startsWith('/files/download/') && response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = endpoint.split('/').pop();
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            return { status: 'success' };
        }

        // For other requests, parse JSON
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'API request failed');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        alert(`Error: ${error.message}`);
        throw error;
    }
}

// Handle login
async function handleLogin() {
    try {
        const result = await apiRequest('/login', 'POST');
        authToken = result.token;
        localStorage.setItem('authToken', authToken);
        showApp();
        loadFiles();
    } catch (error) {
        console.error('Login failed:', error);
    }
}

// Handle register
async function handleRegister() {
    try {
        const result = await apiRequest('/register', 'POST');
        authToken = result.token;
        localStorage.setItem('authToken', authToken);
        showApp();
        loadFiles();
    } catch (error) {
        console.error('Registration failed:', error);
    }
}

// Handle logout
async function handleLogout() {
    try {
        await apiRequest('/logout', 'POST');
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        // Clear local storage and reset UI
        localStorage.removeItem('authToken');
        authToken = null;
        showLogin();
    }
}

// Load files from current folder
async function loadFiles() {
    try {
        // Show loading indicator
        filesList.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p>Loading files...</p>
            </div>
        `;

        // Fetch files from API
        const endpoint = currentFolder ? `/files?folder=${encodeURIComponent(currentFolder)}` : '/files';
        const result = await apiRequest(endpoint);
        
        // Update breadcrumb
        updateBreadcrumb();
        
        // Display files
        displayFiles(result.files);
    } catch (error) {
        console.error('Error loading files:', error);
        filesList.innerHTML = `<div class="alert alert-danger">Error loading files: ${error.message}</div>`;
    }
}

// Display files in the UI
function displayFiles(files) {
    if (!files || files.length === 0) {
        filesList.innerHTML = '<div class="alert alert-info">No files found in this folder.</div>';
        return;
    }

    // Sort files: folders first, then files, both alphabetically
    files.sort((a, b) => {
        if (a.type !== b.type) {
            return a.type === 'folder' ? -1 : 1;
        }
        return a.name.localeCompare(b.name);
    });

    // Create HTML for file list
    let html = '';
    files.forEach(file => {
        const icon = file.type === 'folder' ? 'bi-folder' : 'bi-file';
        const fileClass = file.type === 'folder' ? 'folder' : 'file';
        const fileSize = file.size ? `(${formatFileSize(file.size)})` : '';
        
        html += `
            <div class="file-item list-group-item d-flex justify-content-between align-items-center ${fileClass}" 
                 data-id="${file.id}" 
                 data-name="${file.name}" 
                 data-type="${file.type}">
                <div>
                    <i class="bi ${icon} me-2"></i>
                    ${file.name} ${fileSize}
                </div>
                <button class="btn btn-sm btn-outline-secondary file-actions-btn">
                    <i class="bi bi-three-dots"></i>
                </button>
            </div>
        `;
    });

    filesList.innerHTML = html;

    // Add event listeners to file items
    document.querySelectorAll('.file-item').forEach(item => {
        item.addEventListener('click', (e) => {
            // Ignore clicks on the actions button
            if (e.target.closest('.file-actions-btn')) {
                e.stopPropagation();
                return;
            }
            
            const fileType = item.getAttribute('data-type');
            const fileName = item.getAttribute('data-name');
            
            if (fileType === 'folder') {
                // Navigate into folder
                currentFolder = fileName;
                loadFiles();
            }
        });
    });

    // Add event listeners to file action buttons
    document.querySelectorAll('.file-actions-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const fileItem = btn.closest('.file-item');
            selectedFile = {
                id: fileItem.getAttribute('data-id'),
                name: fileItem.getAttribute('data-name'),
                type: fileItem.getAttribute('data-type')
            };
            
            // Update modal title and show it
            document.getElementById('selectedFileName').textContent = selectedFile.name;
            fileActionsModal.show();
        });
    });
}

// Update breadcrumb navigation
function updateBreadcrumb() {
    // Clear existing breadcrumb except Home
    while (breadcrumb.children.length > 1) {
        breadcrumb.removeChild(breadcrumb.lastChild);
    }

    // If we're in a folder, add it to breadcrumb
    if (currentFolder) {
        const item = document.createElement('li');
        item.className = 'breadcrumb-item active';
        item.setAttribute('data-folder', currentFolder);
        item.textContent = currentFolder;
        breadcrumb.appendChild(item);
    }

    // Add click event to Home breadcrumb
    breadcrumb.querySelector('[data-folder=""]').addEventListener('click', () => {
        currentFolder = '';
        loadFiles();
    });
}

// Handle file upload
async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    try {
        // Create FormData
        const formData = new FormData();
        formData.append('file', file);
        
        // Add folder if we're in one
        if (currentFolder) {
            formData.append('folder', currentFolder);
        }

        // Show progress bar
        uploadProgress.style.display = 'block';
        progressBar.style.width = '0%';
        progressBar.textContent = '0%';

        // Simulate progress (since fetch doesn't provide upload progress)
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 5;
            if (progress > 90) {
                clearInterval(progressInterval);
                return;
            }
            progressBar.style.width = `${progress}%`;
            progressBar.textContent = `${progress}%`;
        }, 300);

        // Upload file
        const result = await apiRequest('/files/upload', 'POST', formData, true);
        
        // Complete progress
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        progressBar.textContent = '100%';
        
        // Hide progress after a delay
        setTimeout(() => {
            uploadProgress.style.display = 'none';
        }, 1000);

        // Reset file input
        fileInput.value = '';

        // Reload files
        loadFiles();
        
        alert('File uploaded successfully!');
    } catch (error) {
        console.error('Upload failed:', error);
        uploadProgress.style.display = 'none';
    }
}

// Handle folder creation
async function handleCreateFolder() {
    const folderNameInput = document.getElementById('folderNameInput');
    const folderName = folderNameInput.value.trim();
    
    if (!folderName) {
        alert('Please enter a folder name');
        return;
    }

    try {
        // Create folder path (include current folder if we're in one)
        const folderPath = currentFolder ? `${currentFolder}/${folderName}` : folderName;
        
        await apiRequest('/folders', 'POST', { folder_path: folderPath });
        
        // Reset input and close modal
        folderNameInput.value = '';
        createFolderModal.hide();
        
        // Reload files
        loadFiles();
    } catch (error) {
        console.error('Error creating folder:', error);
    }
}

// Handle file download
async function handleDownload() {
    if (!selectedFile || selectedFile.type !== 'file') {
        alert('Please select a file to download');
        return;
    }

    try {
        await apiRequest(`/files/download/${encodeURIComponent(selectedFile.name)}`);
        fileActionsModal.hide();
    } catch (error) {
        console.error('Download failed:', error);
    }
}

// Show rename modal
function showRenameModal() {
    if (!selectedFile) return;
    
    document.getElementById('newNameInput').value = selectedFile.name;
    fileActionsModal.hide();
    renameModal.show();
}

// Handle rename
async function handleRename() {
    const newNameInput = document.getElementById('newNameInput');
    const newName = newNameInput.value.trim();
    
    if (!newName) {
        alert('Please enter a new name');
        return;
    }

    try {
        await apiRequest(`/files/rename/${encodeURIComponent(selectedFile.name)}`, 'PUT', { new_name: newName });
        
        // Close modal and reload files
        renameModal.hide();
        loadFiles();
    } catch (error) {
        console.error('Rename failed:', error);
    }
}

// Handle get sharing link
async function handleGetShareLink() {
    if (!selectedFile) return;

    try {
        const result = await apiRequest(`/files/link/${encodeURIComponent(selectedFile.name)}`);
        
        // Display the link in the modal
        document.getElementById('shareLinkInput').value = result.public_link;
        fileActionsModal.hide();
        shareLinkModal.show();
    } catch (error) {
        console.error('Error getting share link:', error);
    }
}

// Copy share link to clipboard
function copyShareLink() {
    const linkInput = document.getElementById('shareLinkInput');
    linkInput.select();
    document.execCommand('copy');
    alert('Link copied to clipboard!');
}

// Handle delete
async function handleDelete() {
    if (!selectedFile) return;
    
    if (confirm(`Are you sure you want to delete ${selectedFile.name}?`)) {
        try {
            await apiRequest(`/files/delete/${encodeURIComponent(selectedFile.name)}`, 'DELETE');
            
            // Close modal and reload files
            fileActionsModal.hide();
            loadFiles();
        } catch (error) {
            console.error('Delete failed:', error);
        }
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', init);