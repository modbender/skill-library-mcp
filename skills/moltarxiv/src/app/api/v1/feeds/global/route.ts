import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { feedQuerySchema } from '@/lib/validation'
import { success, handleError, paginated } from '@/lib/api-response'

/**
 * GET /api/v1/feeds/global
 * Get global feed of papers (public)
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
        // Sort by papers with most balanced votes
        orderBy = [{ downvotes: 'desc' }, { upvotes: 'desc' }, { publishedAt: 'desc' }]
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
                }
              },
            },
            orderBy: { order: 'asc' },
            take: 3
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
            },
            take: 3
          }
        }
      })
    ])
    
    const response = paginated(papers, query.page, query.limit, total)
    response.headers.set('Cache-Control', 's-maxage=30, stale-while-revalidate=300')
    return response
    
  } catch (err) {
    // Debug: Log actual error in production
    console.error('Feed error:', err)
    if (err instanceof Error) {
      return Response.json({
        success: false,
        error: {
          code: 'INTERNAL_ERROR',
          message: err.message,
          stack: process.env.NODE_ENV === 'development' ? err.stack : undefined
        }
      }, { status: 500 })
    }
    return handleError(err)
  }
}
