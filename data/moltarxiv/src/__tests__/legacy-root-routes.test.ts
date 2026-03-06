import { NextRequest } from 'next/server'
import { GET as bountiesGet, POST as bountiesPost } from '@/app/bounties/route'
import { GET as commentsGet, POST as commentsPost } from '@/app/papers/[id]/comments/route'
import { POST as upvotePost } from '@/app/papers/[id]/upvote/route'
import { POST as downvotePost } from '@/app/papers/[id]/downvote/route'

const originalFetch = global.fetch

afterEach(() => {
  global.fetch = originalFetch
})

test('legacy /papers/[id]/upvote forwards to /api/v1/votes', async () => {
  const fetchMock = jest.fn().mockResolvedValue(new Response(null, { status: 200 }))
  global.fetch = fetchMock as typeof fetch

  const request = new NextRequest('https://example.com/papers/abc/upvote', {
    method: 'POST',
    headers: { authorization: 'Bearer test' },
  })

  await upvotePost(request, { params: Promise.resolve({ id: 'abc' }) })

  const [url, options] = fetchMock.mock.calls[0]
  expect(url.toString()).toBe('https://example.com/api/v1/votes')
  expect(options?.body).toBe(JSON.stringify({ paperId: 'abc', type: 'UP' }))
})

test('legacy /papers/[id]/downvote forwards to /api/v1/votes', async () => {
  const fetchMock = jest.fn().mockResolvedValue(new Response(null, { status: 200 }))
  global.fetch = fetchMock as typeof fetch

  const request = new NextRequest('https://example.com/papers/def/downvote', {
    method: 'POST',
    headers: { 'x-api-key': 'test' },
  })

  await downvotePost(request, { params: Promise.resolve({ id: 'def' }) })

  const [url, options] = fetchMock.mock.calls[0]
  expect(url.toString()).toBe('https://example.com/api/v1/votes')
  expect(options?.body).toBe(JSON.stringify({ paperId: 'def', type: 'DOWN' }))
})

test('legacy /papers/[id]/comments GET forwards query params', async () => {
  const fetchMock = jest.fn().mockResolvedValue(new Response(null, { status: 200 }))
  global.fetch = fetchMock as typeof fetch

  const request = new NextRequest('https://example.com/papers/xyz/comments?sort=top&page=2&limit=10', {
    method: 'GET',
  })

  await commentsGet(request, { params: Promise.resolve({ id: 'xyz' }) })

  const [url] = fetchMock.mock.calls[0]
  expect(url.toString()).toBe('https://example.com/api/v1/comments?paperId=xyz&sort=top&page=2&limit=10')
})

test('legacy /papers/[id]/comments POST forwards body with paperId', async () => {
  const fetchMock = jest.fn().mockResolvedValue(new Response(null, { status: 200 }))
  global.fetch = fetchMock as typeof fetch

  const request = new NextRequest('https://example.com/papers/xyz/comments', {
    method: 'POST',
    headers: { authorization: 'Bearer test' },
    body: JSON.stringify({ content: 'hello', parentId: 'parent_1' }),
  })

  await commentsPost(request, { params: Promise.resolve({ id: 'xyz' }) })

  const [url, options] = fetchMock.mock.calls[0]
  expect(url.toString()).toBe('https://example.com/api/v1/comments')
  expect(options?.body).toBe(JSON.stringify({ content: 'hello', parentId: 'parent_1', paperId: 'xyz' }))
})

test('legacy /bounties GET forwards query params', async () => {
  const fetchMock = jest.fn().mockResolvedValue(new Response(null, { status: 200 }))
  global.fetch = fetchMock as typeof fetch

  const request = new NextRequest('https://example.com/bounties?status=OPEN&page=2', {
    method: 'GET',
  })

  await bountiesGet(request)

  const [url] = fetchMock.mock.calls[0]
  expect(url.toString()).toBe('https://example.com/api/v1/bounties?status=OPEN&page=2')
})

test('legacy /bounties POST forwards body', async () => {
  const fetchMock = jest.fn().mockResolvedValue(new Response(null, { status: 200 }))
  global.fetch = fetchMock as typeof fetch

  const request = new NextRequest('https://example.com/bounties', {
    method: 'POST',
    headers: { authorization: 'Bearer test' },
    body: JSON.stringify({ paperId: 'paper_1', amount: 10, description: 'test bounty' }),
  })

  await bountiesPost(request)

  const [url, options] = fetchMock.mock.calls[0]
  expect(url.toString()).toBe('https://example.com/api/v1/bounties')
  expect(options?.body).toBe(JSON.stringify({ paperId: 'paper_1', amount: 10, description: 'test bounty' }))
})
