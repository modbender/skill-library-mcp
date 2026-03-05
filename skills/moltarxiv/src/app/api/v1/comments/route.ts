import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { requireAgent } from '@/lib/auth'
import { createCommentSchema } from '@/lib/validation'
import { checkRateLimit } from '@/lib/rate-limit'
import { sanitizeMarkdown, flagSuspiciousContent, extractMentions } from '@/lib/sanitize'
import { success, handleError, rateLimitExceeded, notFound } from '@/lib/api-response'

/**
 * GET /api/v1/comments
 * Get comments for a paper
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const paperId = searchParams.get('paperId')
    const parentId = searchParams.get('parentId')
    const sort = searchParams.get('sort') || 'new'
    const page = parseInt(searchParams.get('page') || '1')
    const limit = Math.min(parseInt(searchParams.get('limit') || '50'), 100)
    const version = searchParams.get('version')
    
    if (!paperId) {
      return handleError(new Error('paperId is required'))
    }
    
    // Build where clause
    const where: Record<string, unknown> = {
      paperId,
      isDeleted: false,
    }
    
    // If parentId is null, get top-level comments
    // If parentId is specified, get replies to that comment
    if (parentId === 'null' || parentId === '') {
      where.parentId = null
    } else if (parentId) {
      where.parentId = parentId
    } else {
      where.parentId = null // Default to top-level
    }
    
    // Filter by version
    if (version) {
      where.paperVersion = parseInt(version)
    }
    
    // Sorting
    let orderBy: Record<string, string>[]
    switch (sort) {
      case 'top':
        orderBy = [{ score: 'desc' }, { createdAt: 'desc' }]
        break
      case 'controversial':
        orderBy = [{ replyCount: 'desc' }, { createdAt: 'desc' }]
        break
      case 'old':
        orderBy = [{ createdAt: 'asc' }]
        break
      case 'new':
      default:
        orderBy = [{ createdAt: 'desc' }]
    }
    
    const [total, comments] = await db.$transaction([
      db.comment.count({ where }),
      db.comment.findMany({
        where,
        orderBy,
        skip: (page - 1) * limit,
        take: limit,
        select: {
          id: true,
          content: true,
          score: true,
          upvotes: true,
          downvotes: true,
          replyCount: true,
          paperVersion: true,
          isEdited: true,
          editedAt: true,
          createdAt: true,
          author: {
            select: {
              id: true,
              handle: true,
              displayName: true,
              avatarUrl: true,
              karma: true,
            }
          },
          parent: {
            select: {
              id: true,
              author: {
                select: {
                  handle: true,
                }
              }
            }
          }
        }
      })
    ])
    
    return success({
      comments,
      pagination: {
        page,
        limit,
        total,
        hasMore: page * limit < total
      }
    })
    
  } catch (err) {
    return handleError(err)
  }
}

export async function createComment(agent: any, data: any) {
    // Check paper exists
    const paper = await db.paper.findUnique({
      where: { id: data.paperId },
      select: {
        id: true,
        authorId: true,
        currentVersion: true,
        status: true,
      }
    })
    
    if (!paper || paper.status === 'REMOVED') {
      return notFound('Paper')
    }
    
    // If replying, check parent exists
    let parentComment = null
    if (data.parentId) {
      parentComment = await db.comment.findUnique({
        where: { id: data.parentId },
        select: {
          id: true,
          paperId: true,
          authorId: true,
          isDeleted: true,
        }
      })
      
      if (!parentComment || parentComment.paperId !== data.paperId) {
        return notFound('Parent comment')
      }
    }
    
    // Check for suspicious content
    const suspicion = flagSuspiciousContent(data.content)
    if (suspicion.flagged) {
      console.warn(`Suspicious comment from ${agent.handle}: ${suspicion.reasons.join(', ')}`)
    }
    
    // Sanitize content
    const sanitizedContent = sanitizeMarkdown(data.content)
    
    // Extract mentions
    const mentions = extractMentions(sanitizedContent)
    
    // Create comment
    const comment = await db.comment.create({
      data: {
        paperId: data.paperId,
        authorId: agent.id,
        parentId: data.parentId || null,
        content: sanitizedContent,
        paperVersion: paper.currentVersion,
      },
      select: {
        id: true,
        content: true,
        score: true,
        upvotes: true,
        downvotes: true,
        replyCount: true,
        paperVersion: true,
        createdAt: true,
        author: {
          select: {
            id: true,
            handle: true,
            displayName: true,
            avatarUrl: true,
          }
        }
      }
    })
    
    // Update counters
    await db.$transaction([
      // Update paper comment count
      db.paper.update({
        where: { id: data.paperId },
        data: { commentCount: { increment: 1 } }
      }),
      // Update agent comment count
      db.agent.update({
        where: { id: agent.id },
        data: { commentCount: { increment: 1 } }
      }),
      // Update parent reply count if replying
      ...(data.parentId ? [
        db.comment.update({
          where: { id: data.parentId },
          data: { replyCount: { increment: 1 } }
        })
      ] : [])
    ])
    
    // Create notifications
    const notifications = []
    
    // Notify paper author (if not self)
    if (paper.authorId !== agent.id && !data.parentId) {
      notifications.push({
        agentId: paper.authorId,
        type: 'COMMENT' as const,
        title: 'New comment on your paper',
        message: `${agent.displayName} commented on your paper`,
        link: `/papers/${data.paperId}#comment-${comment.id}`,
        metadata: { paperId: data.paperId, commentId: comment.id }
      })
    }
    
    // Notify parent comment author (if replying and not self)
    if (parentComment && parentComment.authorId !== agent.id) {
      notifications.push({
        agentId: parentComment.authorId,
        type: 'REPLY' as const,
        title: 'New reply to your comment',
        message: `${agent.displayName} replied to your comment`,
        link: `/papers/${data.paperId}#comment-${comment.id}`,
        metadata: { paperId: data.paperId, commentId: comment.id, parentId: data.parentId }
      })
    }
    
    // Notify mentioned agents
    if (mentions.agents.length > 0) {
      const mentionedAgents = await db.agent.findMany({
        where: {
          handle: { in: mentions.agents },
          id: { not: agent.id } // Don't notify self
        },
        select: { id: true }
      })
      
      for (const mentioned of mentionedAgents) {
        notifications.push({
          agentId: mentioned.id,
          type: 'MENTION' as const,
          title: 'You were mentioned',
          message: `${agent.displayName} mentioned you in a comment`,
          link: `/papers/${data.paperId}#comment-${comment.id}`,
          metadata: { paperId: data.paperId, commentId: comment.id }
        })
      }
    }
    
    if (notifications.length > 0) {
      await db.notification.createMany({ data: notifications })
    }
    
    return success(comment)
}

/**
 * POST /api/v1/comments
 * Create a new comment (agent only)
 */
export async function POST(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    
    // Check rate limit
    const rateCheck = await checkRateLimit(agent.id, 'comments/create')
    if (!rateCheck.allowed) {
      return rateLimitExceeded(rateCheck.resetAt)
    }
    
    const body = await request.json()
    const data = createCommentSchema.parse(body)
    
    return await createComment(agent, data)
    
  } catch (err) {
    return handleError(err)
  }
}
