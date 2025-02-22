import { NextResponse } from 'next/server';
import prisma from '@/lib/prisma';
import jwt from 'jsonwebtoken';

export async function POST(request: Request) {
  try {
    const token = request.headers.get('Authorization')?.split(' ')[1];
    if (!token) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    const { userId } = jwt.verify(token, process.env.JWT_SECRET!) as { userId: number };

    const { parentPath, name } = await request.json();
    const parentFolder = await prisma.folder.findFirst({ where: { userId, path: parentPath } });
    if (!parentFolder) return NextResponse.json({ error: 'Parent folder not found' }, { status: 404 });

    const folderPath = `${parentPath}/${name}`;
    const existingFolder = await prisma.folder.findFirst({ where: { userId, path: folderPath } });
    if (existingFolder) return NextResponse.json({ error: 'Folder already exists' }, { status: 400 });

    await prisma.folder.create({
      data: { userId, parentFolderId: parentFolder.id, name, path: folderPath },
    });

    return NextResponse.json({ message: 'Folder created', path: folderPath }, { status: 201 });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}