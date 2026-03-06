import { NextResponse } from 'next/server';
import { exportToCsv } from '@/lib/storage';

export async function GET() {
  try {
    const csv = exportToCsv();
    return new NextResponse(csv, {
      headers: {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename="portfolio.csv"',
      },
    });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to export CSV' }, { status: 500 });
  }
}
