import { NextResponse } from 'next/server';
import prisma from '@/lib/prisma';
import jwt from 'jsonwebtoken';

export async function GET(request: Request) {
  try {
    const token = request.headers.get('Authorization')?.split(' ')[1];
    if (!token) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    const { userId } = jwt.verify(token, process.env.JWT_SECRET!) as { userId: number };

    const folders = await prisma.folder.findMany({ where: { userId } });
    const files = await prisma.file.findMany({ where: { userId } });

    return NextResponse.json({
      folders: folders.map(f => ({ id: f.id, path: f.path })),
      files: files.map(f => ({ id: f.id, path: f.path, size: f.size.toString() })),
    }, { status: 200 });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}