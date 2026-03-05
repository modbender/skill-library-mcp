import { NextRequest } from 'next/server'
import { handleError } from '@/lib/api-response'
import { createComment, GET as getComments } from '../../../comments/route'
import { requireAgent } from '@/lib/auth'
import { createCommentSchema } from '@/lib/validation'

interface RouteContext {
  params: Promise<{ id: string }>
}

/**
 * GET /api/v1/papers/[id]/comments
 * Convenience wrapper for /api/v1/comments?paperId=...
 */
export async function GET(request: NextRequest, context: RouteContext) {
  try {
    const { id } = await context.params
    const url = new URL(request.url)
    url.searchParams.set('paperId', id)
    
    // Construct a new request with the updated URL parameters to invoke the handler directly
    const newReq = new NextRequest(url, request)
    return await getComments(newReq)
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * POST /api/v1/papers/[id]/comments
 * Convenience wrapper for /api/v1/comments
 */
export async function POST(request: NextRequest, context: RouteContext) {
  try {
    const agent = await requireAgent(request)
    const { id } = await context.params
    const body = await request.json().catch(() => ({}))
    
    const rawData = {
        ...body,
        paperId: id
    }
    
    // Validate data using the shared schema
    const data = createCommentSchema.parse(rawData)
    
    // Call logic directly
    return await createComment(agent, data)
    
  } catch (err) {
    return handleError(err)
  }
}
