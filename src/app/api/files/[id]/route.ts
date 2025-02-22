import { NextResponse } from 'next/server';
import prisma from '@/lib/prisma';
import jwt from 'jsonwebtoken';
import { deleteFromMega } from '@/lib/mega';
import { decrypt } from '@/lib/crypto';

export async function DELETE(request: Request, { params }: { params: { id: string } }) {
  try {
    const token = request.headers.get('Authorization')?.split(' ')[1];
    if (!token) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    const { userId } = jwt.verify(token, process.env.JWT_SECRET!) as { userId: number };

    const file = await prisma.file.findFirst({ where: { id: parseInt(params.id), userId } });
    if (!file) return NextResponse.json({ error: 'File not found' }, { status: 404 });

    const chunks = await prisma.fileChunk.findMany({ where: { fileId: file.id } });
    for (const chunk of chunks) {
      const account = await prisma.megaAccount.findUnique({ where: { id: chunk.accountId } });
      await deleteFromMega(account!.megaEmail, decrypt(account!.megaPasswordEncrypted), chunk.megaFileId);
      await prisma.megaAccount.update({
        where: { id: chunk.accountId },
        data: { availableSpace: account!.availableSpace + BigInt(chunk.chunkSize) },
      });
      await prisma.fileChunk.delete({ where: { id: chunk.id } });
    }
    await prisma.file.delete({ where: { id: file.id } });

    return NextResponse.json({ message: 'File deleted successfully' }, { status: 200 });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}