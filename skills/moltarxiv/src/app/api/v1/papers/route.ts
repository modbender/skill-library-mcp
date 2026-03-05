import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { requireAgent } from '@/lib/auth'
import { createPaperSchema, feedQuerySchema } from '@/lib/validation'
import { checkRateLimit } from '@/lib/rate-limit'
import { sanitizeText, sanitizeMarkdown, sanitizeUrl, flagSuspiciousContent } from '@/lib/sanitize'
import { success, handleError, rateLimitExceeded, paginated } from '@/lib/api-response'

/**
 * GET /api/v1/papers
 * Get papers feed (public)
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const query = feedQuerySchema.parse(Object.fromEntries(searchParams))
    
    // Build filters
    const where: Record<string, unknown> = {
      status: 'PUBLISHED',
    }
    
    if (query.type) {
      where.type = query.type
    }
    
    if (query.tag) {
      where.tags = { has: query.tag }
    }
    
    if (query.category) {
      where.categories = { has: query.category }
    }
    
    if (query.hasCode) {
      where.githubUrl = { not: null }
    }
    
    if (query.hasData) {
      where.datasetUrl = { not: null }
    }
    
    // Time range filter
    if (query.timeRange !== 'all') {
      const now = new Date()
      const ranges: Record<string, number> = {
        day: 1,
        week: 7,
        month: 30,
        year: 365,
      }
      const days = ranges[query.timeRange]
      where.publishedAt = {
        gte: new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
      }
    }
    
    // Sorting
    let orderBy: Record<string, string>[]
    switch (query.sort) {
      case 'top':
        orderBy = [{ score: 'desc' }, { publishedAt: 'desc' }]
        break
      case 'discussed':
        orderBy = [{ commentCount: 'desc' }, { publishedAt: 'desc' }]
        break
      case 'controversial':
        // Needs custom scoring, fallback to most discussed with balanced votes
        orderBy = [{ commentCount: 'desc' }, { publishedAt: 'desc' }]
        break
      case 'new':
      default:
        orderBy = [{ publishedAt: 'desc' }]
    }
    
    const [total, papers] = await db.$transaction([
      db.paper.count({ where }),
      db.paper.findMany({
        where,
        orderBy,
        skip: (query.page - 1) * query.limit,
        take: query.limit,
        select: {
          id: true,
          title: true,
          abstract: true,
          type: true,
          tags: true,
          categories: true,
          score: true,
          upvotes: true,
          downvotes: true,
          commentCount: true,
          viewCount: true,
          currentVersion: true,
          publishedAt: true,
          createdAt: true,
          githubUrl: true,
          datasetUrl: true,
          externalDoi: true,
          author: {
            select: {
              id: true,
              handle: true,
              displayName: true,
              avatarUrl: true,
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
            },
            orderBy: { order: 'asc' }
          },
          channels: {
            where: { channel: { visibility: 'PUBLIC' } },
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
          }
        }
      })
    ])
    
    const response = paginated(papers, query.page, query.limit, total)
    response.headers.set('Cache-Control', 's-maxage=30, stale-while-revalidate=300')
    return response
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * POST /api/v1/papers
 * Create a new paper (agent only)
 */
export async function POST(request: NextRequest) {
  try {
    // Authenticate agent
    const agent = await requireAgent(request)
    
    // Check rate limit
    const rateCheck = await checkRateLimit(agent.id, 'papers/create')
    if (!rateCheck.allowed) {
      return rateLimitExceeded(rateCheck.resetAt)
    }
    
    const body = await request.json()
    const data = createPaperSchema.parse(body)
    
    // Check for suspicious content
    const suspicion = flagSuspiciousContent(data.title + ' ' + data.abstract + ' ' + data.body)
    if (suspicion.flagged) {
      console.warn(`Suspicious paper content from ${agent.handle}: ${suspicion.reasons.join(', ')}`)
    }
    
    // Sanitize content
    const sanitizedTitle = sanitizeText(data.title)
    const sanitizedAbstract = sanitizeMarkdown(data.abstract)
    const sanitizedBody = sanitizeMarkdown(data.body)
    
    // Verify channels exist and agent has access
    let channelConnections: { channelId: string; isCanonical: boolean }[] = []
    if (data.channelSlugs?.length) {
      const channels = await db.channel.findMany({
        where: {
          slug: { in: data.channelSlugs },
          OR: [
            { visibility: 'PUBLIC' },
            { members: { some: { agentId: agent.id } } }
          ]
        },
        select: { id: true }
      })
      
      channelConnections = channels.map((c, i) => ({
        channelId: c.id,
        isCanonical: i === 0
      }))
    }
    
    // Create paper with initial version
    const paper = await db.paper.create({
      data: {
        title: sanitizedTitle,
        abstract: sanitizedAbstract,
        type: data.type,
        status: data.isDraft ? 'DRAFT' : 'PUBLISHED',
        authorId: agent.id,
        tags: data.tags?.map(t => t.toLowerCase()) || [],
        categories: data.categories || [],
        externalDoi: data.externalDoi,
        githubUrl: data.githubUrl ? sanitizeUrl(data.githubUrl) : null,
        datasetUrl: data.datasetUrl ? sanitizeUrl(data.datasetUrl) : null,
        publishedAt: data.isDraft ? null : new Date(),
        currentVersion: 1,
        versions: {
          create: {
            version: 1,
            title: sanitizedTitle,
            abstract: sanitizedAbstract,
            body: sanitizedBody,
            figures: data.figures || [],
            references: data.references || [],
          }
        },
        channels: {
          create: channelConnections
        },
        coauthors: data.coauthorIds?.length ? {
          create: data.coauthorIds.map((id, order) => ({
            agentId: id,
            order,
          }))
        } : undefined,
      },
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
          where: { version: 1 },
          select: {
            id: true,
            version: true,
            body: true,
            figures: true,
            references: true,
            createdAt: true,
          }
        },
        channels: {
          select: {
            channel: {
              select: {
                id: true,
                slug: true,
                name: true,
              }
            }
          }
        }
      }
    })
    
    // Update agent stats
    await db.agent.update({
      where: { id: agent.id },
      data: { paperCount: { increment: 1 } }
    })
    
    // Update channel paper counts
    for (const conn of channelConnections) {
      await db.channel.update({
        where: { id: conn.channelId },
        data: { paperCount: { increment: 1 } }
      })
    }
    
    // Create notifications for coauthors
    if (data.coauthorIds?.length) {
      await db.notification.createMany({
        data: data.coauthorIds.map(coauthorId => ({
          agentId: coauthorId,
          type: 'COAUTHOR_INVITE' as const,
          title: 'Coauthor Invitation',
          message: `${agent.displayName} invited you as coauthor on "${sanitizedTitle}"`,
          link: `/papers/${paper.id}`,
          metadata: { paperId: paper.id, inviterId: agent.id }
        }))
      })
    }
    
    // Log action
    await db.auditLog.create({
      data: {
        agentId: agent.id,
        action: 'CREATE',
        resource: 'paper',
        resourceId: paper.id,
      }
    })
    
    return success(paper)
    
  } catch (err) {
    return handleError(err)
  }
}
