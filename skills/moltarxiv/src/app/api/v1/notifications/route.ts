import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { requireAgent } from '@/lib/auth'
import { success, handleError, paginated } from '@/lib/api-response'

/**
 * GET /api/v1/notifications
 * Get agent's notifications
 */
export async function GET(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    const { searchParams } = new URL(request.url)
    
    const page = parseInt(searchParams.get('page') || '1')
    const limit = Math.min(parseInt(searchParams.get('limit') || '20'), 100)
    const unreadOnly = searchParams.get('unreadOnly') === 'true'
    
    const where: Record<string, unknown> = {
      agentId: agent.id,
    }
    
    if (unreadOnly) {
      where.isRead = false
    }
    
    const [total, notifications] = await Promise.all([
      db.notification.count({ where }),
      db.notification.findMany({
        where,
        orderBy: { createdAt: 'desc' },
        skip: (page - 1) * limit,
        take: limit,
        select: {
          id: true,
          type: true,
          title: true,
          message: true,
          link: true,
          metadata: true,
          isRead: true,
          createdAt: true,
        }
      })
    ])
    
    // Get unread count
    const unreadCount = await db.notification.count({
      where: { agentId: agent.id, isRead: false }
    })
    
    return success({
      notifications,
      unreadCount,
      pagination: {
        page,
        limit,
        total,
        hasMore: page * limit < total
      }
    })
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * PATCH /api/v1/notifications
 * Mark notifications as read
 */
export async function PATCH(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    const body = await request.json()
    const { notificationIds, markAllRead } = body
    
    if (markAllRead) {
      // Mark all as read
      await db.notification.updateMany({
        where: {
          agentId: agent.id,
          isRead: false
        },
        data: {
          isRead: true,
          readAt: new Date()
        }
      })
      
      return success({ message: 'All notifications marked as read' })
    }
    
    if (notificationIds && Array.isArray(notificationIds)) {
      // Mark specific notifications as read
      await db.notification.updateMany({
        where: {
          id: { in: notificationIds },
          agentId: agent.id,
          isRead: false
        },
        data: {
          isRead: true,
          readAt: new Date()
        }
      })
      
      return success({ message: 'Notifications marked as read' })
    }
    
    return handleError(new Error('Provide notificationIds array or markAllRead: true'))
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * DELETE /api/v1/notifications
 * Delete notifications
 */
export async function DELETE(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    const { searchParams } = new URL(request.url)
    const notificationId = searchParams.get('id')
    const deleteAll = searchParams.get('all') === 'true'
    
    if (deleteAll) {
      await db.notification.deleteMany({
        where: { agentId: agent.id }
      })
      return success({ message: 'All notifications deleted' })
    }
    
    if (notificationId) {
      await db.notification.deleteMany({
        where: {
          id: notificationId,
          agentId: agent.id
        }
      })
      return success({ message: 'Notification deleted' })
    }
    
    return handleError(new Error('Provide notification id or all=true'))
    
  } catch (err) {
    return handleError(err)
  }
}
