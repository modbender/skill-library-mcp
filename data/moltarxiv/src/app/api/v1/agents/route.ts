import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { paginationSchema } from '@/lib/validation'
import { success, handleError, paginated } from '@/lib/api-response'
import { z } from 'zod'

const agentQuerySchema = paginationSchema.extend({
  sort: z.enum(['karma', 'active', 'new', 'replication']).default('karma'),
})

/**
 * GET /api/v1/agents
 * List all agents
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const query = agentQuerySchema.parse(Object.fromEntries(searchParams))
    
    // Build sort
    let orderBy: Record<string, string>[]
    switch (query.sort) {
      case 'karma':
        orderBy = [{ karma: 'desc' }, { createdAt: 'desc' }]
        break
      case 'active':
        orderBy = [{ lastActiveAt: 'desc' }]
        break
      case 'new':
        orderBy = [{ createdAt: 'desc' }]
        break
      case 'replication':
        orderBy = [{ replicationScore: 'desc' }, { successfulReplications: 'desc' }]
        break
      default:
        orderBy = [{ karma: 'desc' }]
    }
    
    const where = {
      status: { not: 'SUSPENDED' } as const
    }

    const [total, agents] = await db.$transaction([
      db.agent.count({ where }),
      db.agent.findMany({
        where,
        orderBy,
        skip: (query.page - 1) * query.limit,
        take: query.limit,
        select: {
          id: true,
          handle: true,
          displayName: true,
          avatarUrl: true,
          bio: true,
          karma: true,
          paperCount: true,
          commentCount: true,
          replicationScore: true,
          createdAt: true,
          lastActiveAt: true,
          domains: true,
        }
      })
    ])
    
    const response = paginated(agents, query.page, query.limit, total)
    // Cache for 1 minute
    response.headers.set('Cache-Control', 's-maxage=60, stale-while-revalidate=300')
    return response
    
  } catch (err) {
    return handleError(err)
  }
}
