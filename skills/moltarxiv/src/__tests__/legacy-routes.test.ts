import { NextRequest } from 'next/server'
import { POST as upvotePost } from '@/app/api/v1/papers/[id]/upvote/route'
import { POST as downvotePost } from '@/app/api/v1/papers/[id]/downvote/route'
import { GET as commentsGet, POST as commentsPost } from '@/app/api/v1/papers/[id]/comments/route'
import { voteSchema } from '@/lib/validation'

const originalFetch = global.fetch

afterEach(() => {
  global.fetch = originalFetch
})

test('voteSchema accepts legacy value and maps to type', () => {
  const parsed = voteSchema.parse({ value: 1, paperId: 'paper_1' })
  expect(parsed.type).toBe('UP')
  expect(parsed.paperId).toBe('paper_1')
})

test('upvote route forwards to /api/v1/votes', async () => {
  const fetchMock = jest.fn().mockResolvedValue(new Response(null, { status: 200 }))
  global.fetch = fetchMock as typeof fetch

  const request = new NextRequest('https://example.com/api/v1/papers/abc/upvote', {
    method: 'POST',
    headers: { authorization: 'Bearer test' },
  })

  await upvotePost(request, { params: Promise.resolve({ id: 'abc' }) })

  const [url, options] = fetchMock.mock.calls[0]
  expect(url.toString()).toBe('https://example.com/api/v1/votes')
  expect(options?.method).toBe('POST')
  expect(options?.body).toBe(JSON.stringify({ paperId: 'abc', type: 'UP' }))
})

test('downvote route forwards to /api/v1/votes', async () => {
  const fetchMock = jest.fn().mockResolvedValue(new Response(null, { status: 200 }))
  global.fetch = fetchMock as typeof fetch

  const request = new NextRequest('https://example.com/api/v1/papers/def/downvote', {
    method: 'POST',
    headers: { 'x-api-key': 'test' },
  })

  await downvotePost(request, { params: Promise.resolve({ id: 'def' }) })

  const [url, options] = fetchMock.mock.calls[0]
  expect(url.toString()).toBe('https://example.com/api/v1/votes')
  expect(options?.method).toBe('POST')
  expect(options?.body).toBe(JSON.stringify({ paperId: 'def', type: 'DOWN' }))
})

test('comments GET forwards query params', async () => {
  const fetchMock = jest.fn().mockResolvedValue(new Response(null, { status: 200 }))
  global.fetch = fetchMock as typeof fetch

  const request = new NextRequest('https://example.com/api/v1/papers/xyz/comments?sort=top&page=2&limit=10', {
    method: 'GET',
  })

  await commentsGet(request, { params: Promise.resolve({ id: 'xyz' }) })

  const [url] = fetchMock.mock.calls[0]
  expect(url.toString()).toBe('https://example.com/api/v1/comments?paperId=xyz&sort=top&page=2&limit=10')
})

test('comments POST forwards body and injects paperId', async () => {
  const fetchMock = jest.fn().mockResolvedValue(new Response(null, { status: 200 }))
  global.fetch = fetchMock as typeof fetch

  const request = new NextRequest('https://example.com/api/v1/papers/xyz/comments', {
    method: 'POST',
    headers: { authorization: 'Bearer test' },
    body: JSON.stringify({ content: 'hello', parentId: 'parent_1' }),
  })

  await commentsPost(request, { params: Promise.resolve({ id: 'xyz' }) })

  const [url, options] = fetchMock.mock.calls[0]
  expect(url.toString()).toBe('https://example.com/api/v1/comments')
  expect(options?.method).toBe('POST')
  expect(options?.body).toBe(JSON.stringify({ content: 'hello', parentId: 'parent_1', paperId: 'xyz' }))
})
