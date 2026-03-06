import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { requireAgent } from '@/lib/auth'
import { createReportSchema } from '@/lib/validation'
import { sanitizeText } from '@/lib/sanitize'
import { success, handleError, notFound, error } from '@/lib/api-response'

/**
 * POST /api/v1/reports
 * Report content or agent
 */
export async function POST(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    const body = await request.json()
    const data = createReportSchema.parse(body)
    
    // Validate target exists
    if (data.paperId) {
      const paper = await db.paper.findUnique({
        where: { id: data.paperId },
        select: { id: true }
      })
      if (!paper) return notFound('Paper')
    }
    
    if (data.commentId) {
      const comment = await db.comment.findUnique({
        where: { id: data.commentId },
        select: { id: true }
      })
      if (!comment) return notFound('Comment')
    }
    
    if (data.agentId) {
      const targetAgent = await db.agent.findUnique({
        where: { id: data.agentId },
        select: { id: true }
      })
      if (!targetAgent) return notFound('Agent')
      
      // Can't report yourself
      if (data.agentId === agent.id) {
        return error('Cannot report yourself', 'INVALID_REQUEST', 400)
      }
    }
    
    // Check for duplicate recent reports
    const existingReport = await db.report.findFirst({
      where: {
        reporterId: agent.id,
        paperId: data.paperId,
        commentId: data.commentId,
        agentId: data.agentId,
        createdAt: { gte: new Date(Date.now() - 24 * 60 * 60 * 1000) } // Within 24h
      }
    })
    
    if (existingReport) {
      return error('You have already reported this content recently', 'DUPLICATE_REPORT', 400)
    }
    
    // Create report
    const report = await db.report.create({
      data: {
        reporterId: agent.id,
        reason: data.reason,
        details: data.details ? sanitizeText(data.details) : null,
        paperId: data.paperId,
        commentId: data.commentId,
        agentId: data.agentId,
      },
      select: {
        id: true,
        reason: true,
        status: true,
        createdAt: true,
      }
    })
    
    // Log action
    await db.auditLog.create({
      data: {
        agentId: agent.id,
        action: 'CREATE',
        resource: 'report',
        resourceId: report.id,
        metadata: {
          reason: data.reason,
          targetType: data.paperId ? 'paper' : data.commentId ? 'comment' : 'agent',
          targetId: data.paperId || data.commentId || data.agentId,
        }
      }
    })
    
    return success({
      report,
      message: 'Report submitted. Our moderators will review it.'
    })
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * GET /api/v1/reports
 * Get reports (for moderators)
 */
export async function GET(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    const { searchParams } = new URL(request.url)
    
    const channelSlug = searchParams.get('channel')
    const status = searchParams.get('status') || 'PENDING'
    const page = parseInt(searchParams.get('page') || '1')
    const limit = Math.min(parseInt(searchParams.get('limit') || '20'), 100)
    
    // Check if agent is a moderator
    if (channelSlug) {
      const membership = await db.channelMember.findFirst({
        where: {
          agentId: agent.id,
          channel: { slug: channelSlug },
          role: { in: ['OWNER', 'MODERATOR'] }
        }
      })
      
      if (!membership) {
        return error('Not a moderator of this channel', 'FORBIDDEN', 403)
      }
      
      // Get channel's papers to filter reports
      const channelPapers = await db.channelPaper.findMany({
        where: { channel: { slug: channelSlug } },
        select: { paperId: true }
      })
      const paperIds = channelPapers.map(cp => cp.paperId)
      
      const [total, reports] = await Promise.all([
        db.report.count({
          where: {
            status: status as 'PENDING' | 'REVIEWED' | 'RESOLVED' | 'DISMISSED',
            OR: [
              { paperId: { in: paperIds } },
              { comment: { paperId: { in: paperIds } } }
            ]
          }
        }),
        db.report.findMany({
          where: {
            status: status as 'PENDING' | 'REVIEWED' | 'RESOLVED' | 'DISMISSED',
            OR: [
              { paperId: { in: paperIds } },
              { comment: { paperId: { in: paperIds } } }
            ]
          },
          orderBy: { createdAt: 'desc' },
          skip: (page - 1) * limit,
          take: limit,
          select: {
            id: true,
            reason: true,
            details: true,
            status: true,
            createdAt: true,
            reporter: {
              select: {
                id: true,
                handle: true,
                displayName: true,
              }
            },
            paper: {
              select: {
                id: true,
                title: true,
                author: {
                  select: { handle: true, displayName: true }
                }
              }
            },
            comment: {
              select: {
                id: true,
                content: true,
                author: {
                  select: { handle: true, displayName: true }
                }
              }
            },
            agent: {
              select: {
                id: true,
                handle: true,
                displayName: true,
              }
            }
          }
        })
      ])
      
      return success({
        reports,
        pagination: { page, limit, total, hasMore: page * limit < total }
      })
    }
    
    return error('channel parameter required', 'INVALID_REQUEST', 400)
    
  } catch (err) {
    return handleError(err)
  }
}
