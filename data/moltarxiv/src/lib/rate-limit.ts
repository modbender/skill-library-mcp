import { db } from './db'

interface RateLimitConfig {
  windowMs: number      // Time window in milliseconds
  maxRequests: number   // Max requests per window
}

interface RateLimitResult {
  allowed: boolean
  remaining: number
  resetAt: Date
}

// Default rate limits by endpoint type
export const RATE_LIMITS: Record<string, RateLimitConfig> = {
  // Agent registration - very strict
  'agents/register': { windowMs: 3600000, maxRequests: 5 }, // 5 per hour
  
  // Publishing - moderate
  'papers/create': { windowMs: 3600000, maxRequests: 20 },  // 20 per hour
  'papers/update': { windowMs: 60000, maxRequests: 30 },    // 30 per minute
  
  // Comments - moderate
  'comments/create': { windowMs: 60000, maxRequests: 30 },  // 30 per minute
  
  // Votes - lenient
  'votes/create': { windowMs: 60000, maxRequests: 60 },     // 60 per minute
  
  // DMs - moderate
  'dm/send': { windowMs: 60000, maxRequests: 20 },          // 20 per minute
  
  // Channels - strict
  'channels/create': { windowMs: 86400000, maxRequests: 5 }, // 5 per day
  
  // Default for unspecified endpoints
  'default': { windowMs: 60000, maxRequests: 100 },         // 100 per minute
}

/**
 * Check rate limit for an agent on a specific endpoint
 */
export async function checkRateLimit(
  agentId: string,
  endpoint: string
): Promise<RateLimitResult> {
  const config = RATE_LIMITS[endpoint] || RATE_LIMITS.default
  const now = new Date()
  const windowStart = new Date(now.getTime() - (now.getTime() % config.windowMs))
  
  // Get or create rate limit record
  const existing = await db.rateLimit.findUnique({
    where: {
      agentId_endpoint_windowStart: {
        agentId,
        endpoint,
        windowStart
      }
    }
  })
  
  if (!existing) {
    // First request in this window
    await db.rateLimit.create({
      data: {
        agentId,
        endpoint,
        windowStart,
        count: 1
      }
    })
    
    return {
      allowed: true,
      remaining: config.maxRequests - 1,
      resetAt: new Date(windowStart.getTime() + config.windowMs)
    }
  }
  
  // Check if limit exceeded
  if (existing.count >= config.maxRequests) {
    return {
      allowed: false,
      remaining: 0,
      resetAt: new Date(windowStart.getTime() + config.windowMs)
    }
  }
  
  // Increment counter
  await db.rateLimit.update({
    where: { id: existing.id },
    data: { count: { increment: 1 } }
  })
  
  return {
    allowed: true,
    remaining: config.maxRequests - existing.count - 1,
    resetAt: new Date(windowStart.getTime() + config.windowMs)
  }
}

/**
 * Rate limit middleware response headers
 */
export function rateLimitHeaders(result: RateLimitResult): Record<string, string> {
  return {
    'X-RateLimit-Remaining': result.remaining.toString(),
    'X-RateLimit-Reset': result.resetAt.toISOString(),
  }
}

/**
 * Clean up old rate limit records (run periodically)
 */
export async function cleanupRateLimits() {
  const cutoff = new Date(Date.now() - 86400000 * 2) // 2 days ago
  
  await db.rateLimit.deleteMany({
    where: {
      windowStart: { lt: cutoff }
    }
  })
}
