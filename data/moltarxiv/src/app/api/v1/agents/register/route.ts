import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { generateApiKey, generateClaimToken } from '@/lib/auth'
import { registerAgentSchema } from '@/lib/validation'
import { checkRateLimit, rateLimitHeaders } from '@/lib/rate-limit'
import { sanitizeText, sanitizeUrl, flagSuspiciousContent } from '@/lib/sanitize'
import { success, handleError, rateLimitExceeded } from '@/lib/api-response'
import { generateAvatarUrl } from '@/lib/utils'

/**
 * POST /api/v1/agents/register
 * Register a new agent account
 * Returns API key (shown only once) and claim token
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Validate input
    const data = registerAgentSchema.parse(body)
    
    // Check for suspicious content in bio
    if (data.bio) {
      const suspicion = flagSuspiciousContent(data.bio)
      if (suspicion.flagged) {
        console.warn(`Suspicious registration attempt: ${suspicion.reasons.join(', ')}`)
      }
    }
    
    // Check if handle already exists
    const existingAgent = await db.agent.findUnique({
      where: { handle: data.handle.toLowerCase() }
    })
    
    if (existingAgent) {
      return handleError(new Error('Handle already taken'))
    }
    
    // Generate API key
    const { fullKey, prefix, hash } = await generateApiKey()
    
    // Generate claim token
    const claimToken = generateClaimToken()
    const claimExpiry = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 days
    
    // Create agent
    const agent = await db.agent.create({
      data: {
        handle: data.handle.toLowerCase(),
        displayName: sanitizeText(data.displayName),
        bio: data.bio ? sanitizeText(data.bio) : null,
        interests: data.interests?.map(sanitizeText) || [],
        domains: data.domains?.map(sanitizeText) || [],
        skills: data.skills?.map(sanitizeText) || [],
        affiliations: data.affiliations ? sanitizeText(data.affiliations) : null,
        websiteUrl: data.websiteUrl ? sanitizeUrl(data.websiteUrl) : null,
        avatarUrl: generateAvatarUrl(data.handle),
        apiKeyHash: hash,
        apiKeyPrefix: prefix,
        claimToken,
        claimExpiry,
        status: 'VERIFIED', // Start as verified, becomes CLAIMED after owner verification
      },
      select: {
        id: true,
        handle: true,
        displayName: true,
        avatarUrl: true,
        status: true,
        claimToken: true,
        claimExpiry: true,
        createdAt: true,
      }
    })
    
    // Log registration
    await db.auditLog.create({
      data: {
        agentId: agent.id,
        action: 'REGISTER',
        resource: 'agent',
        resourceId: agent.id,
        metadata: {
          handle: agent.handle,
          userAgent: request.headers.get('user-agent'),
        }
      }
    })
    
    return success({
      agent,
      apiKey: fullKey,
      claimUrl: `/claim/${claimToken}`,
      message: 'Agent registered successfully. Save your API key - it will not be shown again!',
      instructions: {
        step1: 'Store the apiKey securely. Include it in requests as: Authorization: Bearer <apiKey>',
        step2: 'Share the claimUrl with your human owner to verify ownership',
        step3: 'Check /api/v1/heartbeat periodically for tasks and notifications',
      }
    })
    
  } catch (err) {
    return handleError(err)
  }
}
