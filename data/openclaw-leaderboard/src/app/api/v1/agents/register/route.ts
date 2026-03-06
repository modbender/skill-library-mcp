import { NextRequest, NextResponse } from "next/server";
import { z } from "zod/v4";
import { prisma } from "@/lib/prisma";
import { generateApiKey, generateClaimToken } from "@/lib/auth";
import { checkRateLimit, getWriteLimiter, getClientIp } from "@/lib/rate-limit";
import { SITE_URL } from "@/lib/constants";

const registerSchema = z.object({
  name: z
    .string()
    .min(2, "Name must be at least 2 characters")
    .max(50, "Name must be under 50 characters")
    .regex(
      /^[a-zA-Z0-9_-]+$/,
      "Name can only contain letters, numbers, hyphens, and underscores"
    ),
  description: z.string().max(500).optional(),
});

export async function POST(request: NextRequest) {
  const ip = getClientIp(request);
  const rateLimitResponse = await checkRateLimit(getWriteLimiter(), ip);
  if (rateLimitResponse) return rateLimitResponse;

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const parsed = registerSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { error: "Validation failed", details: parsed.error.issues },
      { status: 400 }
    );
  }

  // Check if name is taken
  const existing = await prisma.agent.findUnique({
    where: { name: parsed.data.name },
  });
  if (existing) {
    return NextResponse.json(
      {
        error: "Name already taken",
        hint: "Choose a different name for your agent.",
      },
      { status: 409 }
    );
  }

  const apiKey = generateApiKey();
  const claimToken = generateClaimToken();
  const claimUrl = `${SITE_URL}/claim/${claimToken}`;

  const agent = await prisma.agent.create({
    data: {
      name: parsed.data.name,
      description: parsed.data.description ?? null,
      apiKey,
      claimUrl,
    },
  });

  return NextResponse.json(
    {
      agent: {
        name: agent.name,
        api_key: apiKey,
        claim_url: claimUrl,
      },
      important:
        "Save your api_key! You need it for all authenticated requests.",
    },
    { status: 201 }
  );
}
