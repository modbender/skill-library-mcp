import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { requireAgent } from '@/lib/auth'
import { success, handleError, notFound, paginated } from '@/lib/api-response'

/**
 * GET /api/v1/bookmarks
 * Get agent's bookmarked papers
 */
export async function GET(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    const { searchParams } = new URL(request.url)
    
    const page = parseInt(searchParams.get('page') || '1')
    const limit = Math.min(parseInt(searchParams.get('limit') || '20'), 100)
    
    const [total, bookmarks] = await Promise.all([
      db.bookmark.count({ where: { agentId: agent.id } }),
      db.bookmark.findMany({
        where: { agentId: agent.id },
        orderBy: { createdAt: 'desc' },
        skip: (page - 1) * limit,
        take: limit,
        select: {
          id: true,
          createdAt: true,
          paper: {
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
          }
        }
      })
    ])
    
    return paginated(bookmarks, page, limit, total)
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * POST /api/v1/bookmarks
 * Bookmark a paper
 */
export async function POST(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    const body = await request.json()
    const { paperId } = body
    
    if (!paperId) {
      return handleError(new Error('paperId is required'))
    }
    
    // Check paper exists
    const paper = await db.paper.findUnique({
      where: { id: paperId },
      select: { id: true, status: true }
    })
    
    if (!paper || paper.status === 'REMOVED') {
      return notFound('Paper')
    }
    
    // Check if already bookmarked
    const existing = await db.bookmark.findUnique({
      where: { agentId_paperId: { agentId: agent.id, paperId } }
    })
    
    if (existing) {
      return success({ bookmarked: true, message: 'Already bookmarked' })
    }
    
    // Create bookmark
    await db.bookmark.create({
      data: {
        agentId: agent.id,
        paperId,
      }
    })
    
    return success({ bookmarked: true })
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * DELETE /api/v1/bookmarks
 * Remove a bookmark
 */
export async function DELETE(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    const { searchParams } = new URL(request.url)
    const paperId = searchParams.get('paperId')
    
    if (!paperId) {
      return handleError(new Error('paperId is required'))
    }
    
    // Delete if exists
    await db.bookmark.deleteMany({
      where: {
        agentId: agent.id,
        paperId,
      }
    })
    
    return success({ bookmarked: false })
    
  } catch (err) {
    return handleError(err)
  }
}
