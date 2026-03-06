import { NextRequest } from 'next/server'
import { handleError } from '@/lib/api-response'

interface RouteContext {
  params: Promise<{ id: string }>
}

function buildAuthHeaders(request: NextRequest) {
  const headers = new Headers()
  const auth = request.headers.get('authorization')
  const apiKey = request.headers.get('x-api-key')

  if (auth) headers.set('authorization', auth)
  if (apiKey) headers.set('x-api-key', apiKey)
  headers.set('content-type', 'application/json')

  return headers
}

/**
 * POST /papers/[id]/downvote
 * Legacy wrapper for /api/v1/votes (DOWN)
 */
export async function POST(request: NextRequest, context: RouteContext) {
  try {
    const { id } = await context.params
    const forwardUrl = new URL('/api/v1/votes', request.url)

    return fetch(forwardUrl, {
      method: 'POST',
      headers: buildAuthHeaders(request),
      body: JSON.stringify({
        paperId: id,
        type: 'DOWN',
      }),
    })
  } catch (err) {
    return handleError(err)
  }
}
