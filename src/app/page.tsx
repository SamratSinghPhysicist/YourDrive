'use client';

import { useState, useEffect } from 'react';
import FileExplorer from '@/components/FileExplorer';
import Login from '@/app/login/page';

export default function Home() {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) setToken(storedToken);
  }, []);

  if (!token) return <Login setToken={setToken} />;
  return <FileExplorer token={token} setToken={setToken} />;
}