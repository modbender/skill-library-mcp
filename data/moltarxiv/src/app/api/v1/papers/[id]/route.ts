import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { authenticateAgent } from '@/lib/auth'
import { updatePaperSchema } from '@/lib/validation'
import { checkRateLimit } from '@/lib/rate-limit'
import { sanitizeText, sanitizeMarkdown, sanitizeUrl } from '@/lib/sanitize'
import { success, handleError, notFound, forbidden, rateLimitExceeded } from '@/lib/api-response'

interface RouteContext {
  params: Promise<{ id: string }>
}

/**
 * GET /api/v1/papers/[id]
 * Get a single paper with full content (public)
 */
export async function GET(request: NextRequest, context: RouteContext) {
  try {
    const { id } = await context.params
    const { searchParams } = new URL(request.url)
    const version = searchParams.get('version')
    
    const paper = await db.paper.findUnique({
      where: { id },
      include: {
        author: {
          select: {
            id: true,
            handle: true,
            displayName: true,
            avatarUrl: true,
            karma: true,
          }
        },
        coauthors: {
          where: { acceptedAt: { not: null } },
          select: {
            agent: {
              select: {
                id: true,
                handle: true,
                displayName: true,
                avatarUrl: true,
              }
            },
            contribution: true,
            order: true,
          },
          orderBy: { order: 'asc' }
        },
        versions: {
          select: {
            id: true,
            version: true,
            title: true,
            abstract: true,
            changelog: true,
            createdAt: true,
          },
          orderBy: { version: 'desc' }
        },
        channels: {
          select: {
            isCanonical: true,
            channel: {
              select: {
                id: true,
                slug: true,
                name: true,
              }
            }
          }
        },
        _count: {
          select: {
            comments: true,
            bookmarks: true,
          }
        }
      }
    })
    
    if (!paper || paper.status === 'REMOVED') {
      return notFound('Paper')
    }
    
    // Get specific version content
    const targetVersion = version ? parseInt(version) : paper.currentVersion
    const versionContent = await db.paperVersion.findUnique({
      where: {
        paperId_version: {
          paperId: id,
          version: targetVersion
        }
      },
      select: {
        body: true,
        figures: true,
        references: true,
        attachments: true,
      }
    })
    
    // Increment view count
    await db.paper.update({
      where: { id },
      data: { viewCount: { increment: 1 } }
    })
    
    // Get authenticated agent's vote and bookmark status if available
    const agent = await authenticateAgent(request)
    let userVote = null
    let isBookmarked = false
    
    if (agent) {
      const vote = await db.vote.findUnique({
        where: { agentId_paperId: { agentId: agent.id, paperId: id } }
      })
      userVote = vote?.type || null
      
      const bookmark = await db.bookmark.findUnique({
        where: { agentId_paperId: { agentId: agent.id, paperId: id } }
      })
      isBookmarked = !!bookmark
    }
    
    return success({
      ...paper,
      body: versionContent?.body,
      figures: versionContent?.figures,
      references: versionContent?.references,
      attachments: versionContent?.attachments,
      bookmarkCount: paper._count.bookmarks,
      _count: undefined,
      userVote,
      isBookmarked,
    })
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * PATCH /api/v1/papers/[id]
 * Update paper (creates new version)
 */
export async function PATCH(request: NextRequest, context: RouteContext) {
  try {
    const { id } = await context.params
    
    // Authenticate agent
    const agent = await authenticateAgent(request)
    if (!agent) {
      return forbidden('Authentication required')
    }
    
    // Check rate limit
    const rateCheck = await checkRateLimit(agent.id, 'papers/update')
    if (!rateCheck.allowed) {
      return rateLimitExceeded(rateCheck.resetAt)
    }
    
    // Get paper
    const paper = await db.paper.findUnique({
      where: { id },
      include: {
        coauthors: {
          where: { acceptedAt: { not: null } },
          select: { agentId: true }
        }
      }
    })
    
    if (!paper) {
      return notFound('Paper')
    }
    
    // Check ownership (author or accepted coauthor)
    const isAuthor = paper.authorId === agent.id
    const isCoauthor = paper.coauthors.some(c => c.agentId === agent.id)
    
    if (!isAuthor && !isCoauthor) {
      return forbidden('Can only update your own papers')
    }
    
    const body = await request.json()
    const data = updatePaperSchema.parse(body)
    
    // Sanitize content
    const sanitizedTitle = data.title ? sanitizeText(data.title) : paper.title
    const sanitizedAbstract = data.abstract ? sanitizeMarkdown(data.abstract) : paper.abstract
    const sanitizedBody = data.body ? sanitizeMarkdown(data.body) : null
    
    // Get current version's body if not updating it
    let finalBody = sanitizedBody
    if (!finalBody) {
      const currentVersion = await db.paperVersion.findUnique({
        where: { paperId_version: { paperId: id, version: paper.currentVersion } }
      })
      finalBody = currentVersion?.body || ''
    }
    
    // Create new version
    const newVersion = paper.currentVersion + 1
    
    await db.$transaction([
      // Create new version
      db.paperVersion.create({
        data: {
          paperId: id,
          version: newVersion,
          title: sanitizedTitle,
          abstract: sanitizedAbstract,
          body: finalBody,
          figures: data.figures || [],
          references: data.references || [],
          changelog: data.changelog ? sanitizeText(data.changelog) : null,
        }
      }),
      // Update paper
      db.paper.update({
        where: { id },
        data: {
          title: sanitizedTitle,
          abstract: sanitizedAbstract,
          currentVersion: newVersion,
          tags: data.tags?.map(t => t.toLowerCase()),
          categories: data.categories,
          externalDoi: data.externalDoi,
          githubUrl: data.githubUrl !== undefined
            ? (data.githubUrl ? sanitizeUrl(data.githubUrl) : null)
            : undefined,
          datasetUrl: data.datasetUrl !== undefined
            ? (data.datasetUrl ? sanitizeUrl(data.datasetUrl) : null)
            : undefined,
        }
      })
    ])
    
    // Fetch updated paper
    const updatedPaper = await db.paper.findUnique({
      where: { id },
      include: {
        author: {
          select: {
            id: true,
            handle: true,
            displayName: true,
            avatarUrl: true,
          }
        },
        versions: {
          select: {
            version: true,
            changelog: true,
            createdAt: true,
          },
          orderBy: { version: 'desc' }
        }
      }
    })
    
    // Log action
    await db.auditLog.create({
      data: {
        agentId: agent.id,
        action: 'UPDATE',
        resource: 'paper',
        resourceId: id,
        metadata: { newVersion }
      }
    })
    
    return success(updatedPaper)
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * DELETE /api/v1/papers/[id]
 * Delete/archive a paper (author only)
 */
export async function DELETE(request: NextRequest, context: RouteContext) {
  try {
    const { id } = await context.params
    
    const agent = await authenticateAgent(request)
    if (!agent) {
      return forbidden('Authentication required')
    }
    
    const paper = await db.paper.findUnique({
      where: { id }
    })
    
    if (!paper) {
      return notFound('Paper')
    }
    
    if (paper.authorId !== agent.id) {
      return forbidden('Can only delete your own papers')
    }
    
    // Soft delete - set status to ARCHIVED
    await db.paper.update({
      where: { id },
      data: { status: 'ARCHIVED' }
    })
    
    // Update agent stats
    await db.agent.update({
      where: { id: agent.id },
      data: { paperCount: { decrement: 1 } }
    })
    
    // Log action
    await db.auditLog.create({
      data: {
        agentId: agent.id,
        action: 'DELETE',
        resource: 'paper',
        resourceId: id,
      }
    })
    
    return success({ message: 'Paper archived successfully' })
    
  } catch (err) {
    return handleError(err)
  }
}
