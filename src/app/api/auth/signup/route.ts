import { NextResponse } from 'next/server';
import prisma from '@/lib/prisma';
import bcrypt from 'bcryptjs';
import { encrypt } from '@/lib/crypto';

// Replace with real Mega credentials
const PRE_CREATED_MEGA_ACCOUNTS = [
  { email: 'ysuni4@edny.net', password: 'Study@123' },
  { email: 'buv55@edny.net', password: 'Study@123' },
  { email: 'jbk8a@edny.net', password: 'Study@123' },
  { email: 'sezsec@edny.net', password: 'Study@123' },
  { email: 'areklu@edny.net', password: 'Study@123' },
  { email: 'at9q2@edny.net', password: 'Study@123' },
  { email: 'r2nwir@edny.net', password: 'Study@123' },
  { email: 'urac0p@edny.net', password: 'Study@123' },
  { email: 'jaez9h@edny.net', password: 'Study@123' },
  { email: 'm574z@edny.net', password: 'Study@123' },
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