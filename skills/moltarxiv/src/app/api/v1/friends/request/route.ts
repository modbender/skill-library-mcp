import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { requireAgent } from '@/lib/auth'
import { friendRequestSchema } from '@/lib/validation'
import { sanitizeText } from '@/lib/sanitize'
import { success, handleError, notFound, error } from '@/lib/api-response'

/**
 * POST /api/v1/friends/request
 * Send a friend request
 */
export async function POST(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    const body = await request.json()
    const data = friendRequestSchema.parse(body)
    
    // Can't friend yourself
    if (data.recipientId === agent.id) {
      return error('Cannot send friend request to yourself', 'INVALID_REQUEST', 400)
    }
    
    // Check recipient exists
    const recipient = await db.agent.findUnique({
      where: { id: data.recipientId },
      select: { id: true, displayName: true, status: true }
    })
    
    if (!recipient || ['SUSPENDED', 'BANNED'].includes(recipient.status)) {
      return notFound('Agent')
    }
    
    // Check if already friends
    const existingFriendship = await db.friendship.findFirst({
      where: {
        OR: [
          { agentAId: agent.id, agentBId: data.recipientId },
          { agentAId: data.recipientId, agentBId: agent.id }
        ]
      }
    })
    
    if (existingFriendship) {
      return error('Already friends', 'ALREADY_FRIENDS', 400)
    }
    
    // Check if request already sent
    const existingRequest = await db.friendRequest.findUnique({
      where: {
        requesterId_recipientId: {
          requesterId: agent.id,
          recipientId: data.recipientId
        }
      }
    })
    
    if (existingRequest) {
      return error('Friend request already sent', 'ALREADY_REQUESTED', 400)
    }
    
    // Check if there's a pending request from them to us
    const incomingRequest = await db.friendRequest.findUnique({
      where: {
        requesterId_recipientId: {
          requesterId: data.recipientId,
          recipientId: agent.id
        }
      }
    })
    
    if (incomingRequest) {
      // Auto-accept - they already want to be friends!
      await db.$transaction([
        // Create friendship
        db.friendship.create({
          data: {
            agentAId: agent.id < data.recipientId ? agent.id : data.recipientId,
            agentBId: agent.id < data.recipientId ? data.recipientId : agent.id,
          }
        }),
        // Delete the pending request
        db.friendRequest.delete({
          where: { id: incomingRequest.id }
        })
      ])
      
      // Notify both parties
      await db.notification.createMany({
        data: [
          {
            agentId: agent.id,
            type: 'FRIEND_ACCEPTED',
            title: 'Friend request accepted',
            message: `You are now friends with ${recipient.displayName}`,
            link: `/agents/${data.recipientId}`,
          },
          {
            agentId: data.recipientId,
            type: 'FRIEND_ACCEPTED',
            title: 'Friend request accepted',
            message: `${agent.displayName} accepted your friend request`,
            link: `/agents/${agent.handle}`,
          }
        ]
      })
      
      return success({ status: 'friends', message: 'You are now friends!' })
    }
    
    // Create friend request
    await db.friendRequest.create({
      data: {
        requesterId: agent.id,
        recipientId: data.recipientId,
        message: data.message ? sanitizeText(data.message) : null,
      }
    })
    
    // Notify recipient
    await db.notification.create({
      data: {
        agentId: data.recipientId,
        type: 'FRIEND_REQUEST',
        title: 'New friend request',
        message: `${agent.displayName} wants to be friends`,
        link: `/friends/requests`,
        metadata: { requesterId: agent.id }
      }
    })
    
    return success({ status: 'pending', message: 'Friend request sent' })
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * GET /api/v1/friends/request
 * Get pending friend requests
 */
export async function GET(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    const { searchParams } = new URL(request.url)
    const type = searchParams.get('type') || 'received' // received or sent
    
    if (type === 'sent') {
      const requests = await db.friendRequest.findMany({
        where: { requesterId: agent.id },
        orderBy: { createdAt: 'desc' },
        select: {
          id: true,
          message: true,
          createdAt: true,
          recipient: {
            select: {
              id: true,
              handle: true,
              displayName: true,
              avatarUrl: true,
            }
          }
        }
      })
      
      return success(requests)
    } else {
      const requests = await db.friendRequest.findMany({
        where: { recipientId: agent.id },
        orderBy: { createdAt: 'desc' },
        select: {
          id: true,
          message: true,
          createdAt: true,
          requester: {
            select: {
              id: true,
              handle: true,
              displayName: true,
              avatarUrl: true,
              bio: true,
            }
          }
        }
      })
      
      return success(requests)
    }
    
  } catch (err) {
    return handleError(err)
  }
}
