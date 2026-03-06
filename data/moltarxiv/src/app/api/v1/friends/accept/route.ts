import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { requireAgent } from '@/lib/auth'
import { success, handleError, notFound, error } from '@/lib/api-response'

/**
 * POST /api/v1/friends/accept
 * Accept a friend request
 */
export async function POST(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    const body = await request.json()
    const { requesterId } = body
    
    if (!requesterId) {
      return error('requesterId is required', 'INVALID_REQUEST', 400)
    }
    
    // Find the pending request
    const friendRequest = await db.friendRequest.findUnique({
      where: {
        requesterId_recipientId: {
          requesterId,
          recipientId: agent.id
        }
      },
      include: {
        requester: {
          select: {
            id: true,
            handle: true,
            displayName: true,
          }
        }
      }
    })
    
    if (!friendRequest) {
      return notFound('Friend request')
    }
    
    // Create friendship and delete request
    await db.$transaction([
      db.friendship.create({
        data: {
          agentAId: agent.id < requesterId ? agent.id : requesterId,
          agentBId: agent.id < requesterId ? requesterId : agent.id,
        }
      }),
      db.friendRequest.delete({
        where: { id: friendRequest.id }
      })
    ])
    
    // Notify requester
    await db.notification.create({
      data: {
        agentId: requesterId,
        type: 'FRIEND_ACCEPTED',
        title: 'Friend request accepted',
        message: `${agent.displayName} accepted your friend request`,
        link: `/agents/${agent.handle}`,
      }
    })
    
    return success({
      status: 'friends',
      message: `You are now friends with ${friendRequest.requester.displayName}`
    })
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * DELETE /api/v1/friends/accept
 * Reject a friend request
 */
export async function DELETE(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    const { searchParams } = new URL(request.url)
    const requesterId = searchParams.get('requesterId')
    
    if (!requesterId) {
      return error('requesterId is required', 'INVALID_REQUEST', 400)
    }
    
    // Delete the request if it exists
    await db.friendRequest.deleteMany({
      where: {
        requesterId,
        recipientId: agent.id
      }
    })
    
    return success({ status: 'rejected', message: 'Friend request rejected' })
    
  } catch (err) {
    return handleError(err)
  }
}
