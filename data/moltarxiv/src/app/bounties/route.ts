import { NextRequest } from 'next/server'
import { handleError } from '@/lib/api-response'

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
 * GET /bounties
 * Legacy wrapper for /api/v1/bounties
 */
export async function GET(request: NextRequest) {
  try {
    const incoming = new URL(request.url)
    const forwardUrl = new URL('/api/v1/bounties', request.url)

    incoming.searchParams.forEach((value, key) => {
      forwardUrl.searchParams.set(key, value)
    })

    return fetch(forwardUrl, {
      method: 'GET',
      headers: buildAuthHeaders(request),
    })
  } catch (err) {
    return handleError(err)
  }
}

/**
 * POST /bounties
 * Legacy wrapper for /api/v1/bounties
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}))
    const forwardUrl = new URL('/api/v1/bounties', request.url)

    return fetch(forwardUrl, {
      method: 'POST',
      headers: buildAuthHeaders(request, true),
      body: JSON.stringify(body),
    })
  } catch (err) {
    return handleError(err)
  }
}
