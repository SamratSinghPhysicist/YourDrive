import { Storage } from 'megajs';

export async function uploadToMega(email: string, password: string, fileBuffer: Buffer): Promise<string> {
  const storage = await Storage.login(email, password);
  const upload = await storage.upload({
    name: `chunk_${Date.now()}`,
    buffer: fileBuffer,
  });
  return upload.handle;
}

export async function downloadFromMega(email: string, password: string, fileId: string): Promise<Buffer> {
  const storage = await Storage.login(email, password);
  const file = storage.files.find((f: any) => f.handle === fileId);
  if (!file) throw new Error('File not found');
  return file.downloadBuffer();
}

export async function deleteFromMega(email: string, password: string, fileId: string): Promise<void> {
  const storage = await Storage.login(email, password);
  const file = storage.files.find((f: any) => f.handle === fileId);
  if (!file) throw new Error('File not found');
  await file.delete();
}