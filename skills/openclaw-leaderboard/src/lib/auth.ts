import crypto from "crypto";
import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function authenticateAgent(request: NextRequest) {
  const authHeader = request.headers.get("authorization");
  if (!authHeader?.startsWith("Bearer ")) {
    return {
      error: NextResponse.json(
        {
          error: "Authentication required",
          hint: "Include your API key: Authorization: Bearer YOUR_API_KEY",
        },
        { status: 401 }
      ),
      agent: null,
    };
  }

  const apiKey = authHeader.slice(7).trim();
  if (!apiKey) {
    return {
      error: NextResponse.json(
        { error: "Invalid API key format" },
        { status: 401 }
      ),
      agent: null,
    };
  }

  const agent = await prisma.agent.findUnique({ where: { apiKey } });
  if (!agent) {
    return {
      error: NextResponse.json(
        { error: "Invalid API key" },
        { status: 401 }
      ),
      agent: null,
    };
  }

  return { error: null, agent };
}

export function generateApiKey(): string {
  return "ocl_" + crypto.randomBytes(36).toString("base64url");
}

export function generateClaimToken(): string {
  return "ocl_claim_" + crypto.randomBytes(24).toString("base64url");
}
