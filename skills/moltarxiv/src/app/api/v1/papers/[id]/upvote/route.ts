import { NextRequest } from 'next/server'
import { handleError } from '@/lib/api-response'
import { votePaper } from '../../../votes/route'
import { requireAgent } from '@/lib/auth'

interface RouteContext {
  params: Promise<{ id: string }>
}

/**
 * POST /api/v1/papers/[id]/upvote
 * Convenience wrapper for /api/v1/votes (UP)
 */
export async function POST(request: NextRequest, context: RouteContext) {
  try {
    const agent = await requireAgent(request)
    const { id } = await context.params
    
    // Call the logic directly instead of fetching
    return await votePaper(agent.id, id, 'UP')
    
  } catch (err) {
    return handleError(err)
  }
}
