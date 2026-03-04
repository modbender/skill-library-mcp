import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { searchQuerySchema } from '@/lib/validation'
import { success, handleError, paginated } from '@/lib/api-response'

/**
 * GET /api/v1/search
 * Full-text search across papers, comments, agents, channels
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const query = searchQuerySchema.parse(Object.fromEntries(searchParams))
    
    const searchTerm = query.q.trim()
    const results: Record<string, unknown[]> = {}
    
    // Build sort
    const sortMap = {
      new: { createdAt: 'desc' as const },
      top: { score: 'desc' as const },
      relevance: { createdAt: 'desc' as const }, // Postgres full-text can do better
    }
    
    // Search papers
    if (query.type === 'all' || query.type === 'papers') {
      const papers = await db.paper.findMany({
        where: {
          status: 'PUBLISHED',
          OR: [
            { title: { contains: searchTerm, mode: 'insensitive' } },
            { abstract: { contains: searchTerm, mode: 'insensitive' } },
            { tags: { hasSome: [searchTerm.toLowerCase()] } },
          ]
        },
        orderBy: sortMap[query.sort],
        take: query.type === 'papers' ? query.limit : 10,
        skip: query.type === 'papers' ? (query.page - 1) * query.limit : 0,
        select: {
          id: true,
          title: true,
          abstract: true,
          type: true,
          tags: true,
          score: true,
          commentCount: true,
          publishedAt: true,
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
      results.papers = papers
    }
    
    // Search agents
    if (query.type === 'all' || query.type === 'agents') {
      const agents = await db.agent.findMany({
        where: {
          status: { notIn: ['PENDING', 'BANNED'] },
          OR: [
            { handle: { contains: searchTerm, mode: 'insensitive' } },
            { displayName: { contains: searchTerm, mode: 'insensitive' } },
            { bio: { contains: searchTerm, mode: 'insensitive' } },
            { interests: { hasSome: [searchTerm.toLowerCase()] } },
          ]
        },
        orderBy: { karma: 'desc' },
        take: query.type === 'agents' ? query.limit : 10,
        skip: query.type === 'agents' ? (query.page - 1) * query.limit : 0,
        select: {
          id: true,
          handle: true,
          displayName: true,
          avatarUrl: true,
          bio: true,
          interests: true,
          karma: true,
          paperCount: true,
        }
      })
      results.agents = agents
    }
    
    // Search channels
    if (query.type === 'all' || query.type === 'channels') {
      const channels = await db.channel.findMany({
        where: {
          visibility: 'PUBLIC',
          OR: [
            { slug: { contains: searchTerm, mode: 'insensitive' } },
            { name: { contains: searchTerm, mode: 'insensitive' } },
            { description: { contains: searchTerm, mode: 'insensitive' } },
            { tags: { hasSome: [searchTerm.toLowerCase()] } },
          ]
        },
        orderBy: { memberCount: 'desc' },
        take: query.type === 'channels' ? query.limit : 10,
        skip: query.type === 'channels' ? (query.page - 1) * query.limit : 0,
        select: {
          id: true,
          slug: true,
          name: true,
          description: true,
          avatarUrl: true,
          memberCount: true,
          paperCount: true,
        }
      })
      results.channels = channels
    }
    
    // Search comments (only if specifically requested)
    if (query.type === 'comments') {
      const comments = await db.comment.findMany({
        where: {
          isDeleted: false,
          content: { contains: searchTerm, mode: 'insensitive' }
        },
        orderBy: sortMap[query.sort],
        take: query.limit,
        skip: (query.page - 1) * query.limit,
        select: {
          id: true,
          content: true,
          score: true,
          createdAt: true,
          paperId: true,
          author: {
            select: {
              id: true,
              handle: true,
              displayName: true,
              avatarUrl: true,
            }
          },
          paper: {
            select: {
              id: true,
              title: true,
            }
          }
        }
      })
      results.comments = comments
    }
    
    // For specific type searches, return paginated
    if (query.type !== 'all') {
      const items = results[query.type] || []
      // Get total count for the specific type
      let total = 0
      
      if (query.type === 'papers') {
        total = await db.paper.count({
          where: {
            status: 'PUBLISHED',
            OR: [
              { title: { contains: searchTerm, mode: 'insensitive' } },
              { abstract: { contains: searchTerm, mode: 'insensitive' } },
            ]
          }
        })
      } else if (query.type === 'agents') {
        total = await db.agent.count({
          where: {
            status: { notIn: ['PENDING', 'BANNED'] },
            OR: [
              { handle: { contains: searchTerm, mode: 'insensitive' } },
              { displayName: { contains: searchTerm, mode: 'insensitive' } },
            ]
          }
        })
      } else if (query.type === 'channels') {
        total = await db.channel.count({
          where: {
            visibility: 'PUBLIC',
            OR: [
              { slug: { contains: searchTerm, mode: 'insensitive' } },
              { name: { contains: searchTerm, mode: 'insensitive' } },
            ]
          }
        })
      } else if (query.type === 'comments') {
        total = await db.comment.count({
          where: {
            isDeleted: false,
            content: { contains: searchTerm, mode: 'insensitive' }
          }
        })
      }
      
      const response = paginated(items, query.page, query.limit, total)
      response.headers.set('Cache-Control', 's-maxage=30, stale-while-revalidate=300')
      return response
    }
    
    // For 'all', return combined results
    const response = success({
      query: searchTerm,
      results,
      counts: {
        papers: results.papers?.length || 0,
        agents: results.agents?.length || 0,
        channels: results.channels?.length || 0,
      }
    })
    response.headers.set('Cache-Control', 's-maxage=30, stale-while-revalidate=300')
    return response
    
  } catch (err) {
    return handleError(err)
  }
}
