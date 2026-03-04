import { db as prisma } from '@/lib/db';
import { NextResponse } from 'next/server';
import { PaperType } from '@prisma/client';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const briefing = await prisma.paper.findFirst({
      where: {
        author: { handle: 'daily-briefing' },
        type: PaperType.IDEA_NOTE,
      },
      orderBy: { createdAt: 'desc' },
      include: {
        author: {
          select: { handle: true, displayName: true, avatarUrl: true }
        }
      }
    });

    if (!briefing) {
      return NextResponse.json({ success: false, message: "No briefing found." }, { status: 404 });
    }

    return NextResponse.json({ success: true, data: briefing });
  } catch (error) {
    return NextResponse.json({ success: false, error: String(error) }, { status: 500 });
  }
}
