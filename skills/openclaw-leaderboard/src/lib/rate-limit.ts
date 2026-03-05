import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";
import { NextResponse } from "next/server";

// Lazy initialization to avoid build-time errors when env vars aren't available
let _readLimiter: Ratelimit | null | undefined;
let _writeLimiter: Ratelimit | null | undefined;
let _uploadLimiter: Ratelimit | null | undefined;

function createRedis(): Redis | null {
  const url = process.env.UPSTASH_REDIS_REST_URL?.trim();
  const token = process.env.UPSTASH_REDIS_REST_TOKEN?.trim();
  if (!url || !token) return null;
  return new Redis({ url, token });
}

function getLimiter(
  cached: Ratelimit | null | undefined,
  windowSize: number,
  prefix: string
): Ratelimit | null {
  if (cached !== undefined) return cached;
  const redis = createRedis();
  if (!redis) return null;
  return new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(windowSize, "1 m"),
    prefix,
  });
}

export function getReadLimiter() {
  if (_readLimiter === undefined) _readLimiter = getLimiter(_readLimiter, 60, "rl:read");
  return _readLimiter;
}

export function getWriteLimiter() {
  if (_writeLimiter === undefined) _writeLimiter = getLimiter(_writeLimiter, 5, "rl:write");
  return _writeLimiter;
}

export function getUploadLimiter() {
  if (_uploadLimiter === undefined) _uploadLimiter = getLimiter(_uploadLimiter, 2, "rl:upload");
  return _uploadLimiter;
}

export async function checkRateLimit(
  limiter: Ratelimit | null,
  identifier: string
): Promise<NextResponse | null> {
  if (!limiter) {
    console.warn("[rate-limit] Redis unavailable — rate limiting is disabled");
    return null;
  }

  const { success, limit, remaining, reset } = await limiter.limit(identifier);

  if (!success) {
    return NextResponse.json(
      { error: "Too many requests. Please try again later." },
      {
        status: 429,
        headers: {
          "X-RateLimit-Limit": limit.toString(),
          "X-RateLimit-Remaining": remaining.toString(),
          "X-RateLimit-Reset": reset.toString(),
        },
      }
    );
  }

  return null;
}

export function getClientIp(request: Request): string {
  const forwarded = request.headers.get("x-forwarded-for");
  const real = request.headers.get("x-real-ip");
  return forwarded?.split(",")[0]?.trim() ?? real ?? "unknown";
}
