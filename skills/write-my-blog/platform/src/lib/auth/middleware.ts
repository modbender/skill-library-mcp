/**
 * API Key Authentication & Security Middleware
 *
 * Validates API keys, enforces rate limits, and adds security headers.
 */

import { NextRequest, NextResponse } from "next/server";
import { getDatabase } from "@/lib/db";

// ── Rate Limiter (Token Bucket) ──────────────────────────────────

interface RateBucket {
    tokens: number;
    lastRefill: number;
}

const rateBuckets = new Map<string, RateBucket>();
const RATE_LIMIT = parseInt(process.env.RATE_LIMIT_RPM || "100", 10);
const RATE_WINDOW_MS = 60_000; // 1 minute

function checkRateLimit(ip: string): boolean {
    const now = Date.now();
    let bucket = rateBuckets.get(ip);

    if (!bucket) {
        bucket = { tokens: RATE_LIMIT, lastRefill: now };
        rateBuckets.set(ip, bucket);
    }

    // Refill tokens based on elapsed time
    const elapsed = now - bucket.lastRefill;
    const refill = Math.floor((elapsed / RATE_WINDOW_MS) * RATE_LIMIT);
    if (refill > 0) {
        bucket.tokens = Math.min(RATE_LIMIT, bucket.tokens + refill);
        bucket.lastRefill = now;
    }

    if (bucket.tokens <= 0) return false;

    bucket.tokens--;
    return true;
}

// ── API Key Validation ───────────────────────────────────────────

export async function validateRequest(
    request: NextRequest,
): Promise<NextResponse | null> {
    const ip =
        request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
        request.headers.get("x-real-ip") ||
        "unknown";

    // Rate limit check
    if (!checkRateLimit(ip)) {
        return NextResponse.json(
            { error: "Rate limit exceeded. Try again later." },
            {
                status: 429,
                headers: { "Retry-After": "60" },
            },
        );
    }

    // API key check
    const apiKey = request.headers.get("x-api-key");
    if (!apiKey) {
        return NextResponse.json(
            { error: "Missing X-API-Key header" },
            { status: 401 },
        );
    }

    // Check against env var first (fast path)
    const envKey = process.env.API_KEY;
    if (envKey && apiKey === envKey) return null;

    // Check against database keys
    try {
        const db = await getDatabase();
        const valid = await db.validateApiKey(apiKey);
        if (!valid) {
            return NextResponse.json(
                { error: "Invalid API key" },
                { status: 403 },
            );
        }
    } catch {
        return NextResponse.json(
            { error: "Authentication service unavailable" },
            { status: 503 },
        );
    }

    return null; // Request is valid
}

// ── Input Sanitization ───────────────────────────────────────────

export function sanitizeHtml(dirty: string): string {
    // Basic sanitization — strip script tags and event handlers
    return dirty
        .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
        .replace(/on\w+\s*=\s*"[^"]*"/gi, "")
        .replace(/on\w+\s*=\s*'[^']*'/gi, "")
        .replace(/javascript\s*:/gi, "")
        .replace(/data\s*:\s*text\/html/gi, "");
}

export function sanitizeInput(obj: Record<string, unknown>): Record<string, unknown> {
    const sanitized: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj)) {
        if (typeof value === "string") {
            sanitized[key] = sanitizeHtml(value);
        } else if (Array.isArray(value)) {
            sanitized[key] = value.map((v) =>
                typeof v === "string" ? sanitizeHtml(v) : v,
            );
        } else {
            sanitized[key] = value;
        }
    }
    return sanitized;
}

// ── Security Headers ─────────────────────────────────────────────

export function addSecurityHeaders(response: NextResponse): NextResponse {
    response.headers.set("X-Content-Type-Options", "nosniff");
    response.headers.set("X-Frame-Options", "DENY");
    response.headers.set("X-XSS-Protection", "1; mode=block");
    response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
    response.headers.set(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self'",
    );
    return response;
}
