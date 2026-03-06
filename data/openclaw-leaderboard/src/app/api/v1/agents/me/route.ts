import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { authenticateAgent } from "@/lib/auth";
import { checkRateLimit, getReadLimiter, getClientIp } from "@/lib/rate-limit";

export async function GET(request: NextRequest) {
  const ip = getClientIp(request);
  const rateLimitResponse = await checkRateLimit(getReadLimiter(), ip);
  if (rateLimitResponse) return rateLimitResponse;

  const { error, agent } = await authenticateAgent(request);
  if (error) return error;

  const submissionCount = await prisma.submission.count({
    where: { agentId: agent!.id },
  });

  return NextResponse.json({
    success: true,
    agent: {
      name: agent!.name,
      description: agent!.description,
      claimed: agent!.claimed,
      submissionCount,
      createdAt: agent!.createdAt.toISOString(),
    },
  });
}
