'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface FileExplorerProps {
  token: string;
  setToken: (token: string | null) => void;
}

interface Folder {
  id: number;
  path: string;
}

interface File {
  id: number;
  path: string;
  size: string;
}

export default function FileExplorer({ token, setToken }: FileExplorerProps) {
  const [folders, setFolders] = useState<Folder[]>([]);
  const [files, setFiles] = useState<File[]>([]);
  const [currentPath, setCurrentPath] = useState('home');
  const [newFolder, setNewFolder] = useState('');
  const router = useRouter();

  useEffect(() => {
    fetchFilesAndFolders();
  }, [token]);

  const fetchFilesAndFolders = async () => {
    try {
      const res = await fetch('/api/list', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await res.json();
      if (res.ok) {
        setFolders(data.folders);
        setFiles(data.files);
      } else {
        setToken(null);
        localStorage.removeItem('token');
        router.push('/login');
      }
    } catch (err) {
      setToken(null);
      localStorage.removeItem('token');
      router.push('/login');
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('folderPath', currentPath);
    try {
      const res = await fetch('/api/files/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData,
      });
      if (res.ok) fetchFilesAndFolders();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDownload = async (fileId: number) => {
    const res = await fetch(`/api/files/download/${fileId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = files.find(f => f.id === fileId)?.path.split('/').pop() || 'file';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const handleDelete = async (fileId: number) => {
    try {
      const res = await fetch(`/api/files/${fileId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (res.ok) fetchFilesAndFolders();
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateFolder = async () => {
    try {
      const res = await fetch('/api/folders', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ parentPath: currentPath, name: newFolder }),
      });
      if (res.ok) {
        setNewFolder('');
        fetchFilesAndFolders();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem('token');
    router.push('/login');
  };

  const navigateFolder = (path: string) => setCurrentPath(path);

  const currentFolders = folders.filter(f => f.path.startsWith(currentPath) && f.path.split('/').length === currentPath.split('/').length + 1);
  const currentFiles = files.filter(f => f.path.startsWith(currentPath) && f.path.split('/').length === currentPath.split('/').length + 1);

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-white shadow-md p-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-blue-600">YourDrive</h1>
        <button onClick={handleLogout} className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
          Logout
        </button>
      </nav>
      <div className="flex flex-1">
        <div className="w-1/4 bg-gray-200 p-4">
          <h2 className="text-lg font-semibold mb-4">Folders</h2>
          <ul>
            <li
              onClick={() => navigateFolder('home')}
              className={`cursor-pointer p-2 rounded ${currentPath === 'home' ? 'bg-blue-100' : 'hover:bg-gray-300'}`}
            >
              Home
            </li>
            {currentFolders.map(folder => (
              <li
                key={folder.id}
                onClick={() => navigateFolder(folder.path)}
                className={`cursor-pointer p-2 rounded ${currentPath === folder.path ? 'bg-blue-100' : 'hover:bg-gray-300'}`}
              >
                {folder.path.split('/').pop()}
              </li>
            ))}
          </ul>
          <div className="mt-4">
            <input
              type="text"
              placeholder="New Folder"
              value={newFolder}
              onChange={e => setNewFolder(e.target.value)}
              className="w-full p-2 border rounded mb-2"
            />
            <button onClick={handleCreateFolder} className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
              Create Folder
            </button>
          </div>
        </div>
        <div className="w-3/4 p-4">
          <h2 className="text-lg font-semibold mb-4">Files in {currentPath}</h2>
          <label className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 cursor-pointer">
            Upload File
            <input type="file" onChange={handleUpload} className="hidden" />
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
            {currentFiles.map(file => (
              <div key={file.id} className="bg-white p-4 rounded shadow-md flex justify-between items-center">
                <span>{file.path.split('/').pop()}</span>
                <div>
                  <button
                    onClick={() => handleDownload(file.id)}
                    className="text-blue-500 hover:underline mr-2"
                  >
                    Download
                  </button>
                  <button
                    onClick={() => handleDelete(file.id)}
                    className="text-red-500 hover:underline"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}