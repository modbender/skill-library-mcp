import { generateDailyBriefing } from '@/lib/daily-briefing';
import { NextRequest, NextResponse } from 'next/server';

export const maxDuration = 300; // 5 minutes (Vercel max for pro)
export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  // Verify Cron Secret (Vercel automatically sets CRON_SECRET)
  const authHeader = req.headers.get('authorization');
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    // Also allow manual trigger with ADMIN_KEY for debugging
    if (authHeader !== `Bearer ${process.env.ADMIN_KEY}`) {
      return new NextResponse('Unauthorized', { status: 401 });
    }
  }

  try {
    const paper = await generateDailyBriefing();
    return NextResponse.json({ success: true, paperId: paper?.id });
  } catch (error) {
    console.error('Deep Research Cron Failed:', error);
    return NextResponse.json({ success: false, error: String(error) }, { status: 500 });
  }
}
