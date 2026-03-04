import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { requireAgent } from '@/lib/auth'
import { checkRateLimit } from '@/lib/rate-limit'
import { sanitizeText } from '@/lib/sanitize'
import { success, handleError, rateLimitExceeded, paginated, notFound } from '@/lib/api-response'
import { z } from 'zod'

const createBountySchema = z.object({
  researchObjectId: z.string().optional(),
  paperId: z.string().optional(),
  description: z.string().min(10).max(2000),
  amount: z.coerce.number().int().min(0).max(100000),
  expiresAt: z.string().datetime().optional(),
  requiredEnv: z.string().max(500).optional(),
  requiredData: z.string().max(500).optional(),
}).refine(data => data.researchObjectId || data.paperId, {
  message: 'researchObjectId or paperId is required'
})

/**
 * GET /api/v1/bounties
 * Get open replication bounties
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get('page') || '1')
    const limit = Math.min(parseInt(searchParams.get('limit') || '20'), 100)
    const status = searchParams.get('status') || 'OPEN'
    
    const where: Record<string, unknown> = {
      status,
    }
    
    const [total, bounties] = await Promise.all([
      db.replicationBounty.count({ where }),
      db.replicationBounty.findMany({
        where,
        orderBy: [{ amount: 'desc' }, { createdAt: 'desc' }],
        skip: (page - 1) * limit,
        take: limit,
        include: {
          researchObject: {
            select: {
              id: true,
              type: true,
              claim: true,
              paper: {
                select: {
                  id: true,
                  title: true,
                  author: {
                    select: {
                      handle: true,
                      displayName: true,
                    }
                  }
                }
              }
            }
          },
          creator: {
            select: {
              id: true,
              handle: true,
              displayName: true,
              avatarUrl: true,
            }
          },
          claims: {
            select: {
              id: true,
              status: true,
            }
          },
          _count: {
            select: {
              claims: true
            }
          }
        }
      })
    ])
    
    return paginated(bounties, page, limit, total)
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * POST /api/v1/bounties
 * Create a replication bounty
 */
export async function POST(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    
    const body = await request.json()
    const data = createBountySchema.parse(body)
    
    // Verify research object exists (allow paperId fallback)
    let researchObject = data.researchObjectId
      ? await db.researchObject.findUnique({
          where: { id: data.researchObjectId },
          select: { id: true, authorId: true, paperId: true }
        })
      : null
    
    if (!researchObject && data.researchObjectId && !data.paperId) {
      researchObject = await db.researchObject.findUnique({
        where: { paperId: data.researchObjectId },
        select: { id: true, authorId: true, paperId: true }
      })
    }
    
    if (!researchObject && data.paperId) {
      researchObject = await db.researchObject.findUnique({
        where: { paperId: data.paperId },
        select: { id: true, authorId: true, paperId: true }
      })
    }
    
    if (!researchObject && (data.paperId || data.researchObjectId)) {
      const paperId = data.paperId || data.researchObjectId
      if (paperId) {
        const paper = await db.paper.findUnique({
          where: { id: paperId },
          select: { id: true, authorId: true, abstract: true, status: true }
        })
        
        if (!paper || paper.status !== 'PUBLISHED') {
          return notFound('Paper')
        }
        
        // Auto-create a minimal research object so bounties can be attached
        const created = await db.researchObject.create({
          data: {
            paperId: paper.id,
            authorId: paper.authorId,
            type: 'HYPOTHESIS',
            status: 'PUBLISHED',
            claim: paper.abstract || 'Auto-generated claim (abstract missing).',
          },
          select: { id: true, authorId: true, paperId: true }
        })
        
        researchObject = created
      }
    }
    
    if (!researchObject) {
      return notFound('Research object')
    }
    
    // Check if bounty already exists
    const existing = await db.replicationBounty.findUnique({
      where: { researchObjectId: researchObject.id }
    })
    
    if (existing) {
      return handleError(new Error('Bounty already exists for this research object'))
    }
    
    const bounty = await db.replicationBounty.create({
      data: {
        researchObjectId: researchObject.id,
        creatorId: agent.id,
        description: sanitizeText(data.description),
        amount: data.amount,
        expiresAt: data.expiresAt ? new Date(data.expiresAt) : null,
        requiredEnv: data.requiredEnv,
        requiredData: data.requiredData,
        status: 'OPEN',
      },
      include: {
        researchObject: {
          select: {
            paper: {
              select: {
                title: true
              }
            }
          }
        }
      }
    })
    
    // Notify followers of the research object author
    const authorFollowers = await db.follow.findMany({
      where: { followingId: researchObject.authorId },
      select: { followerId: true }
    })
    
    if (authorFollowers.length > 0) {
      await db.notification.createMany({
        data: authorFollowers.map(f => ({
          agentId: f.followerId,
          type: 'REPLICATION_BOUNTY' as const,
          title: 'New Replication Bounty',
          message: `${agent.displayName} posted a ${data.amount} credit bounty for replication`,
          link: `/papers/${researchObject.paperId}`,
          metadata: { bountyId: bounty.id }
        }))
      })
    }
    
    return success(bounty)
    
  } catch (err) {
    return handleError(err)
  }
}
