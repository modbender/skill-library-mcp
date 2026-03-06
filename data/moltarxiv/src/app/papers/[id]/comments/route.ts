import { NextRequest } from 'next/server'
import { handleError } from '@/lib/api-response'

interface RouteContext {
  params: Promise<{ id: string }>
}

function buildAuthHeaders(request: NextRequest, withJson = false) {
  const headers = new Headers()
  const auth = request.headers.get('authorization')
  const apiKey = request.headers.get('x-api-key')

  if (auth) headers.set('authorization', auth)
  if (apiKey) headers.set('x-api-key', apiKey)
  if (withJson) headers.set('content-type', 'application/json')

  return headers
}

/**
 * GET /papers/[id]/comments
 * Legacy wrapper for /api/v1/comments?paperId=...
 */
export async function GET(request: NextRequest, context: RouteContext) {
  try {
    const { id } = await context.params
    const incoming = new URL(request.url)
    const forwardUrl = new URL('/api/v1/comments', request.url)

    forwardUrl.searchParams.set('paperId', id)

    const passthroughParams = ['parentId', 'sort', 'page', 'limit', 'version']
    for (const key of passthroughParams) {
      const value = incoming.searchParams.get(key)
      if (value !== null) {
        forwardUrl.searchParams.set(key, value)
      }
    }

    return fetch(forwardUrl, {
      method: 'GET',
      headers: buildAuthHeaders(request),
    })
  } catch (err) {
    return handleError(err)
  }
}

/**
 * POST /papers/[id]/comments
 * Legacy wrapper for /api/v1/comments
 */
export async function POST(request: NextRequest, context: RouteContext) {
  try {
    const { id } = await context.params
    const body = await request.json().catch(() => ({}))
    const forwardUrl = new URL('/api/v1/comments', request.url)

    return fetch(forwardUrl, {
      method: 'POST',
      headers: buildAuthHeaders(request, true),
      body: JSON.stringify({
        ...body,
        paperId: id,
      }),
    })
  } catch (err) {
    return handleError(err)
  }
}
