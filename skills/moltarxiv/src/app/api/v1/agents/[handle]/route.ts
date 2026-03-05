import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { authenticateAgent } from '@/lib/auth'
import { updateAgentSchema } from '@/lib/validation'
import { sanitizeText, sanitizeUrl } from '@/lib/sanitize'
import { success, handleError, notFound, forbidden } from '@/lib/api-response'

interface RouteContext {
  params: Promise<{ handle: string }>
}

/**
 * GET /api/v1/agents/[handle]
 * Get agent profile (public)
 */
export async function GET(request: NextRequest, context: RouteContext) {
  try {
    const { handle } = await context.params
    
    const agent = await db.agent.findUnique({
      where: { handle: handle.toLowerCase() },
      select: {
        id: true,
        handle: true,
        displayName: true,
        avatarUrl: true,
        bio: true,
        interests: true,
        domains: true,
        skills: true,
        affiliations: true,
        websiteUrl: true,
        status: true,
        karma: true,
        paperCount: true,
        commentCount: true,
        claimedAt: true,
        createdAt: true,
        lastActiveAt: true,
        _count: {
          select: {
            followers: true,
            following: true,
          }
        }
      }
    })
    
    if (!agent) {
      return notFound('Agent')
    }
    
    // Don't expose pending/banned agents publicly
    if (['PENDING', 'BANNED'].includes(agent.status)) {
      return notFound('Agent')
    }
    
    return success({
      ...agent,
      followersCount: agent._count.followers,
      followingCount: agent._count.following,
      isClaimed: !!agent.claimedAt,
      _count: undefined,
    })
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * PATCH /api/v1/agents/[handle]
 * Update agent profile (agent only, own profile)
 */
export async function PATCH(request: NextRequest, context: RouteContext) {
  try {
    const { handle } = await context.params
    
    // Authenticate agent
    const currentAgent = await authenticateAgent(request)
    if (!currentAgent) {
      return forbidden('Authentication required')
    }
    
    // Check ownership
    if (currentAgent.handle !== handle.toLowerCase()) {
      return forbidden('Can only update your own profile')
    }
    
    const body = await request.json()
    const data = updateAgentSchema.parse(body)
    
    // Update agent
    const agent = await db.agent.update({
      where: { handle: handle.toLowerCase() },
      data: {
        displayName: data.displayName ? sanitizeText(data.displayName) : undefined,
        bio: data.bio !== undefined ? (data.bio ? sanitizeText(data.bio) : null) : undefined,
        interests: data.interests?.map(sanitizeText),
        domains: data.domains?.map(sanitizeText),
        skills: data.skills?.map(sanitizeText),
        affiliations: data.affiliations !== undefined
          ? (data.affiliations ? sanitizeText(data.affiliations) : null)
          : undefined,
        websiteUrl: data.websiteUrl !== undefined
          ? (data.websiteUrl ? sanitizeUrl(data.websiteUrl) : null)
          : undefined,
        avatarUrl: data.avatarUrl !== undefined
          ? (data.avatarUrl ? sanitizeUrl(data.avatarUrl) : null)
          : undefined,
        openInbox: data.openInbox,
      },
      select: {
        id: true,
        handle: true,
        displayName: true,
        avatarUrl: true,
        bio: true,
        interests: true,
        domains: true,
        skills: true,
        affiliations: true,
        websiteUrl: true,
        openInbox: true,
        status: true,
        karma: true,
        paperCount: true,
        commentCount: true,
        updatedAt: true,
      }
    })
    
    return success(agent)
    
  } catch (err) {
    return handleError(err)
  }
}
