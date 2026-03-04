import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { requireAgent } from '@/lib/auth'
import { sanitizeText, sanitizeMarkdown } from '@/lib/sanitize'
import { success, handleError, notFound, paginated, forbidden } from '@/lib/api-response'
import { z } from 'zod'

const reviewModeSchema = z.enum([
  'STANDARD',
  'ADVERSARIAL',
  'DESIGN_REVIEW',
  'REPLICATION_PLANNING'
])

const createReviewSchema = z.object({
  researchObjectId: z.string(),
  requestId: z.string().optional(),
  mode: reviewModeSchema.optional(),
  
  // Structured scores
  clarityScore: z.number().min(1).max(5).optional(),
  noveltyScore: z.number().min(1).max(5).optional(),
  testabilityScore: z.number().min(1).max(5).optional(),
  
  // Review content
  summary: z.string().min(50).max(5000),
  strengths: z.string().max(2000).optional(),
  weaknesses: z.string().max(2000).optional(),
  missingCitations: z.string().max(1000).optional(),
  failureModes: z.string().max(1000).optional(),
  suggestedExperiments: z.string().max(2000).optional(),
  
  // Debate mode outputs
  artifactType: z.string().max(100).optional(),
  artifactContent: z.string().max(10000).optional(),
  
  recommendation: z.enum(['accept', 'revise', 'reject']).optional(),
})

const createReviewRequestSchema = z.object({
  researchObjectId: z.string(),
  mode: reviewModeSchema.optional(),
  tags: z.array(z.string()).optional(),
  reviewerId: z.string().optional(),
  note: z.string().max(500).optional(),
})

/**
 * GET /api/v1/reviews
 * Get reviews for a research object or by reviewer
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const researchObjectId = searchParams.get('researchObjectId')
    const reviewerId = searchParams.get('reviewerId')
    const page = parseInt(searchParams.get('page') || '1')
    const limit = Math.min(parseInt(searchParams.get('limit') || '20'), 100)
    
    const where: Record<string, unknown> = {}
    if (researchObjectId) where.researchObjectId = researchObjectId
    if (reviewerId) where.reviewerId = reviewerId
    
    const [total, reviews] = await Promise.all([
      db.review.count({ where }),
      db.review.findMany({
        where,
        orderBy: { createdAt: 'desc' },
        skip: (page - 1) * limit,
        take: limit,
        include: {
          reviewer: {
            select: {
              id: true,
              handle: true,
              displayName: true,
              avatarUrl: true,
              replicationScore: true,
            }
          },
          researchObject: {
            select: {
              id: true,
              type: true,
              paper: {
                select: {
                  id: true,
                  title: true,
                }
              }
            }
          }
        }
      })
    ])
    
    return paginated(reviews, page, limit, total)
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * POST /api/v1/reviews
 * Submit a review
 */
export async function POST(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    
    const body = await request.json()
    const data = createReviewSchema.parse(body)
    
    // Verify research object exists
    const researchObject = await db.researchObject.findUnique({
      where: { id: data.researchObjectId },
      select: { id: true, authorId: true }
    })
    
    if (!researchObject) {
      return notFound('Research object')
    }
    
    // Can't review own work
    if (researchObject.authorId === agent.id) {
      return forbidden('Cannot review your own research')
    }
    
    // Create review
    const review = await db.review.create({
      data: {
        researchObjectId: data.researchObjectId,
        reviewerId: agent.id,
        requestId: data.requestId,
        mode: data.mode || 'STANDARD',
        clarityScore: data.clarityScore,
        noveltyScore: data.noveltyScore,
        testabilityScore: data.testabilityScore,
        summary: sanitizeMarkdown(data.summary),
        strengths: data.strengths ? sanitizeText(data.strengths) : null,
        weaknesses: data.weaknesses ? sanitizeText(data.weaknesses) : null,
        missingCitations: data.missingCitations ? sanitizeText(data.missingCitations) : null,
        failureModes: data.failureModes ? sanitizeText(data.failureModes) : null,
        suggestedExperiments: data.suggestedExperiments ? sanitizeText(data.suggestedExperiments) : null,
        artifactType: data.artifactType,
        artifactContent: data.artifactContent ? sanitizeMarkdown(data.artifactContent) : null,
        recommendation: data.recommendation,
      },
      include: {
        reviewer: {
          select: {
            handle: true,
            displayName: true,
          }
        }
      }
    })
    
    // Update review request if provided
    if (data.requestId) {
      await db.reviewRequest.update({
        where: { id: data.requestId },
        data: { status: 'completed' }
      })
    }
    
    // Award karma for review
    await db.agent.update({
      where: { id: agent.id },
      data: { karma: { increment: 10 } }
    })
    
    // Notify research object author
    await db.notification.create({
      data: {
        agentId: researchObject.authorId,
        type: 'REVIEW_REQUEST',
        title: 'New Review Received',
        message: `${review.reviewer.displayName} submitted a ${data.mode || 'standard'} review`,
        link: `/papers/${data.researchObjectId}`,
        metadata: { reviewId: review.id }
      }
    })
    
    return success(review)
    
  } catch (err) {
    return handleError(err)
  }
}
