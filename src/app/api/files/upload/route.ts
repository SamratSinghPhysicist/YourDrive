import { NextResponse } from 'next/server';
import prisma from '@/lib/prisma';
import jwt from 'jsonwebtoken';
import { uploadToMega } from '@/lib/mega';
import { decrypt } from '@/lib/crypto';

const CHUNK_SIZE = 5 * 1024 * 1024 * 1024; // 5GB

export async function POST(request: Request) {
  try {
    const token = request.headers.get('Authorization')?.split(' ')[1];
    if (!token) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    const { userId } = jwt.verify(token, process.env.JWT_SECRET!) as { userId: number };

    const formData = await request.formData();
    const file = formData.get('file') as File;
    const folderPath = (formData.get('folderPath') as string) || 'home';

    if (!file) return NextResponse.json({ error: 'No file provided' }, { status: 400 });

    const folder = await prisma.folder.findFirst({ where: { userId, path: folderPath } });
    if (!folder) return NextResponse.json({ error: 'Folder not found' }, { status: 404 });

    const fileBuffer = Buffer.from(await file.arrayBuffer());
    const fileSize = fileBuffer.length;
    const filePath = `${folderPath}/${file.name}`;

    const fileEntry = await prisma.file.create({
      data: { userId, folderId: folder.id, name: file.name, size: BigInt(fileSize), path: filePath },
    });

    const megaAccounts = await prisma.megaAccount.findMany({ where: { userId } });

    if (fileSize <= CHUNK_SIZE) {
      const account = megaAccounts.find(acc => acc.availableSpace >= fileSize);
      if (!account) return NextResponse.json({ error: 'No space available' }, { status: 400 });
      const megaFileId = await uploadToMega(account.megaEmail, decrypt(account.megaPasswordEncrypted), fileBuffer);
      await prisma.fileChunk.create({
        data: { fileId: fileEntry.id, accountId: account.id, chunkOrder: 0, megaFileId, chunkSize: BigInt(fileSize) },
      });
      await prisma.megaAccount.update({
        where: { id: account.id },
        data: { availableSpace: account.availableSpace - BigInt(fileSize) },
      });
    } else {
      await prisma.file.update({ where: { id: fileEntry.id }, data: { isChunked: true } });
      const chunks = [];
      for (let i = 0; i < fileSize; i += CHUNK_SIZE) {
        chunks.push(fileBuffer.subarray(i, i + CHUNK_SIZE));
      }
      for (let i = 0; i < chunks.length; i++) {
        const chunk = chunks[i];
        const chunkSize = chunk.length;
        const account = megaAccounts.find(acc => acc.availableSpace >= chunkSize);
        if (!account) return NextResponse.json({ error: 'No space available' }, { status: 400 });
        const megaFileId = await uploadToMega(account.megaEmail, decrypt(account.megaPasswordEncrypted), chunk);
        await prisma.fileChunk.create({
          data: { fileId: fileEntry.id, accountId: account.id, chunkOrder: i, megaFileId, chunkSize: BigInt(chunkSize) },
        });
        await prisma.megaAccount.update({
          where: { id: account.id },
          data: { availableSpace: account.availableSpace - BigInt(chunkSize) },
        });
      }
    }

    return NextResponse.json({ message: 'File uploaded successfully' }, { status: 200 });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}