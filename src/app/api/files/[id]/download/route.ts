import { NextResponse } from 'next/server';
import prisma from '@/lib/prisma';
import jwt from 'jsonwebtoken';
import { downloadFromMega } from '@/lib/mega';
import { decrypt } from '@/lib/crypto';

export async function GET(request: Request, { params }: { params: { id: string } }) {
  try {
    const token = request.headers.get('Authorization')?.split(' ')[1];
    if (!token) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    const { userId } = jwt.verify(token, process.env.JWT_SECRET!) as { userId: number };

    const file = await prisma.file.findFirst({ where: { id: parseInt(params.id), userId } });
    if (!file) return NextResponse.json({ error: 'File not found' }, { status: 404 });

    if (!file.isChunked) {
      const chunk = await prisma.fileChunk.findFirst({ where: { fileId: file.id } });
      const account = await prisma.megaAccount.findUnique({ where: { id: chunk!.accountId } });
      const fileBuffer = await downloadFromMega(account!.megaEmail, decrypt(account!.megaPasswordEncrypted), chunk!.megaFileId);
      return new NextResponse(fileBuffer, {
        headers: { 'Content-Disposition': `attachment; filename="${file.name}"`, 'Content-Type': 'application/octet-stream' },
      });
    } else {
      const chunks = await prisma.fileChunk.findMany({ where: { fileId: file.id }, orderBy: { chunkOrder: 'asc' } });
      const fileBuffer = Buffer.concat(await Promise.all(chunks.map(async chunk => {
        const account = await prisma.megaAccount.findUnique({ where: { id: chunk.accountId } });
        return downloadFromMega(account!.megaEmail, decrypt(account!.megaPasswordEncrypted), chunk.megaFileId);
      })));
      return new NextResponse(fileBuffer, {
        headers: { 'Content-Disposition': `attachment; filename="${file.name}"`, 'Content-Type': 'application/octet-stream' },
      });
    }
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}