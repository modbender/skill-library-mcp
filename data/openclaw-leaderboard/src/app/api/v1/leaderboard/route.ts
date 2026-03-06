import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { leaderboardQuerySchema } from "@/lib/validators";
import { checkRateLimit, getReadLimiter, getClientIp } from "@/lib/rate-limit";

export async function GET(request: NextRequest) {
  const ip = getClientIp(request);
  const rateLimitResponse = await checkRateLimit(getReadLimiter(), ip);
  if (rateLimitResponse) return rateLimitResponse;

  const searchParams = Object.fromEntries(request.nextUrl.searchParams);
  const parsed = leaderboardQuerySchema.safeParse(searchParams);

  if (!parsed.success) {
    return NextResponse.json(
      { error: "Invalid query parameters", details: parsed.error.issues },
      { status: 400 }
    );
  }

  const { page, pageSize, currency, period } = parsed.data;

  // Calculate date filter
  let dateFilter: Date | undefined;
  const now = new Date();
  switch (period) {
    case "day":
      dateFilter = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      break;
    case "week":
      dateFilter = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      break;
    case "month":
      dateFilter = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      break;
    case "year":
      dateFilter = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
      break;
  }

  const where = {
    status: { in: ["PENDING" as const, "VERIFIED" as const] },
    ...(currency && { currency }),
    ...(dateFilter && { createdAt: { gte: dateFilter } }),
  };

  // Get grouped data
  const grouped = await prisma.submission.groupBy({
    by: ["openclawInstanceId"],
    where,
    _sum: { amountCents: true },
    _count: { id: true },
    _max: { createdAt: true },
    orderBy: { _sum: { amountCents: "desc" } },
  });

  const total = grouped.length;
  const paginated = grouped.slice((page - 1) * pageSize, page * pageSize);

  // Get the display names for each instance
  const instanceIds = paginated.map((g) => g.openclawInstanceId);
  const latestSubmissions = await prisma.submission.findMany({
    where: {
      openclawInstanceId: { in: instanceIds },
      ...where,
    },
    orderBy: { createdAt: "desc" },
    distinct: ["openclawInstanceId"],
    select: {
      openclawInstanceId: true,
      openclawName: true,
      currency: true,
    },
  });

  const nameMap = new Map(
    latestSubmissions.map((s) => [s.openclawInstanceId, s])
  );

  const data = paginated.map((g, i) => {
    const info = nameMap.get(g.openclawInstanceId);
    return {
      rank: (page - 1) * pageSize + i + 1,
      openclawInstanceId: g.openclawInstanceId,
      openclawName: info?.openclawName ?? "Unknown",
      totalEarningsCents: g._sum.amountCents ?? 0,
      currency: info?.currency ?? "USD",
      submissionCount: g._count.id,
      latestSubmission: g._max.createdAt?.toISOString() ?? "",
    };
  });

  return NextResponse.json({
    data,
    meta: { page, pageSize, total },
  });
}
