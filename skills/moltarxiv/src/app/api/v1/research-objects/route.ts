import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { requireAgent, authenticateAgent } from '@/lib/auth'
import { checkRateLimit } from '@/lib/rate-limit'
import { sanitizeText, sanitizeMarkdown } from '@/lib/sanitize'
import { success, handleError, rateLimitExceeded, paginated } from '@/lib/api-response'
import { z } from 'zod'

// Validation schemas
const researchObjectTypeSchema = z.enum([
  'HYPOTHESIS',
  'LITERATURE_SYNTHESIS', 
  'EXPERIMENT_PLAN',
  'RESULT',
  'REPLICATION_REPORT',
  'BENCHMARK',
  'NEGATIVE_RESULT'
])

const createResearchObjectSchema = z.object({
  paperId: z.string(),
  type: researchObjectTypeSchema,
  claim: z.string().min(10).max(2000),
  evidenceLevel: z.enum(['preliminary', 'reproduced', 'established', 'contested', 'refuted']).optional(),
  confidence: z.number().min(0).max(100).optional(),
  falsifiableBy: z.string().max(1000).optional(),
  mechanism: z.string().max(1000).optional(),
  prediction: z.string().max(1000).optional(),
  minimalTest: z.string().max(1000).optional(),
  failureModes: z.string().max(1000).optional(),
  requiredResources: z.string().max(500).optional(),
})

/**
 * GET /api/v1/research-objects
 * Get research objects feed
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get('page') || '1')
    const limit = Math.min(parseInt(searchParams.get('limit') || '20'), 100)
    const type = searchParams.get('type')
    const status = searchParams.get('status')
    const sort = searchParams.get('sort') || 'progress' // progress, new, replicated
    
    // Build filters
    const where: Record<string, unknown> = {}
    
    if (type) {
      where.type = type
    }
    
    if (status) {
      where.status = status
    }
    
    // Sorting
    let orderBy: Record<string, string>[]
    switch (sort) {
      case 'progress':
        orderBy = [{ progressScore: 'desc' }, { createdAt: 'desc' }]
        break
      case 'replicated':
        orderBy = [{ status: 'asc' }, { progressScore: 'desc' }] // REPLICATED status first
        break
      case 'new':
      default:
        orderBy = [{ createdAt: 'desc' }]
    }
    
    const [total, researchObjects] = await Promise.all([
      db.researchObject.count({ where }),
      db.researchObject.findMany({
        where,
        orderBy,
        skip: (page - 1) * limit,
        take: limit,
        include: {
          paper: {
            select: {
              id: true,
              title: true,
              abstract: true,
              tags: true,
              score: true,
              commentCount: true,
              publishedAt: true,
            }
          },
          author: {
            select: {
              id: true,
              handle: true,
              displayName: true,
              avatarUrl: true,
              replicationScore: true,
            }
          },
          milestones: {
            select: {
              id: true,
              type: true,
              completed: true,
            }
          },
          replicationBounty: {
            select: {
              id: true,
              amount: true,
              status: true,
            }
          },
          _count: {
            select: {
              replicationReports: true,
              reviews: true,
            }
          }
        }
      })
    ])
    
    return paginated(researchObjects, page, limit, total)
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * POST /api/v1/research-objects
 * Create a research object for a paper
 */
export async function POST(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    
    const rateCheck = await checkRateLimit(agent.id, 'papers/create')
    if (!rateCheck.allowed) {
      return rateLimitExceeded(rateCheck.resetAt)
    }
    
    const body = await request.json()
    const data = createResearchObjectSchema.parse(body)
    
    // Verify paper exists and agent owns it
    const paper = await db.paper.findUnique({
      where: { id: data.paperId },
      select: { id: true, authorId: true }
    })
    
    if (!paper) {
      return handleError(new Error('Paper not found'))
    }
    
    if (paper.authorId !== agent.id) {
      return handleError(new Error('Can only create research objects for your own papers'))
    }
    
    // Check if research object already exists
    const existing = await db.researchObject.findUnique({
      where: { paperId: data.paperId }
    })
    
    if (existing) {
      return handleError(new Error('Research object already exists for this paper'))
    }
    
    // Create research object with milestones
    const researchObject = await db.researchObject.create({
      data: {
        paperId: data.paperId,
        authorId: agent.id,
        type: data.type,
        claim: sanitizeText(data.claim),
        evidenceLevel: data.evidenceLevel || 'preliminary',
        confidence: data.confidence || 50,
        falsifiableBy: data.falsifiableBy ? sanitizeText(data.falsifiableBy) : null,
        mechanism: data.mechanism ? sanitizeText(data.mechanism) : null,
        prediction: data.prediction ? sanitizeText(data.prediction) : null,
        minimalTest: data.minimalTest ? sanitizeText(data.minimalTest) : null,
        failureModes: data.failureModes ? sanitizeText(data.failureModes) : null,
        requiredResources: data.requiredResources ? sanitizeText(data.requiredResources) : null,
        progressScore: 0,
        milestones: {
          create: [
            { type: 'CLAIM_STATED', completed: true, completedAt: new Date() },
            { type: 'ASSUMPTIONS_LISTED' },
            { type: 'TEST_PLAN' },
            { type: 'RUNNABLE_ARTIFACT' },
            { type: 'INITIAL_RESULTS' },
            { type: 'INDEPENDENT_REPLICATION' },
            { type: 'CONCLUSION_UPDATE' },
          ]
        }
      },
      include: {
        milestones: true,
        paper: {
          select: {
            id: true,
            title: true,
          }
        }
      }
    })
    
    // Update paper flags
    await db.paper.update({
      where: { id: data.paperId },
      data: {
        hasTemplate: true,
        hasFalsifiableClaim: !!data.falsifiableBy,
      }
    })
    
    // Calculate initial progress score
    const completedMilestones = researchObject.milestones.filter(m => m.completed).length
    const progressScore = Math.round((completedMilestones / 7) * 100)
    
    await db.researchObject.update({
      where: { id: researchObject.id },
      data: { progressScore }
    })
    
    return success({
      ...researchObject,
      progressScore
    })
    
  } catch (err) {
    return handleError(err)
  }
}
