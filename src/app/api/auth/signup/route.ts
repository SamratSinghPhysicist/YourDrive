import { NextResponse } from 'next/server';
import prisma from '@/lib/prisma';
import bcrypt from 'bcryptjs';
import { encrypt } from '@/lib/crypto';

// Replace with real Mega credentials
const PRE_CREATED_MEGA_ACCOUNTS = [
  { email: 'mega1@example.com', password: 'mega_pass_1' },
  { email: 'mega2@example.com', password: 'mega_pass_2' },
  { email: 'mega3@example.com', password: 'mega_pass_3' },
  { email: 'mega4@example.com', password: 'mega_pass_4' },
  { email: 'mega5@example.com', password: 'mega_pass_5' },
];

export async function POST(request: Request) {
  try {
    const { username, password } = await request.json();
    const existingUser = await prisma.user.findUnique({ where: { username } });
    if (existingUser) return NextResponse.json({ error: 'Username exists' }, { status: 400 });
    const passwordHash = await bcrypt.hash(password, 10);
    const user = await prisma.user.create({ data: { username, passwordHash } });

    for (const account of PRE_CREATED_MEGA_ACCOUNTS) {
      await prisma.megaAccount.create({
        data: {
          userId: user.id,
          megaEmail: account.email,
          megaPasswordEncrypted: encrypt(account.password),
          availableSpace: 20 * 1024 * 1024 * 1024,
        },
      });
    }

    await prisma.folder.create({ data: { userId: user.id, name: 'Home', path: 'home' } });

    return NextResponse.json({ message: 'Signup successful' }, { status: 201 });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}