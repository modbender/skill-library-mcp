import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { requireAgent } from '@/lib/auth'
import { sendDmSchema } from '@/lib/validation'
import { checkRateLimit } from '@/lib/rate-limit'
import { sanitizeMarkdown, flagSuspiciousContent } from '@/lib/sanitize'
import { success, handleError, rateLimitExceeded, notFound, forbidden } from '@/lib/api-response'

/**
 * POST /api/v1/dm/send
 * Send a direct message
 */
export async function POST(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    
    // Check rate limit
    const rateCheck = await checkRateLimit(agent.id, 'dm/send')
    if (!rateCheck.allowed) {
      return rateLimitExceeded(rateCheck.resetAt)
    }
    
    const body = await request.json()
    const data = sendDmSchema.parse(body)
    
    // Can't message yourself
    if (data.recipientId === agent.id) {
      return handleError(new Error('Cannot message yourself'))
    }
    
    // Check recipient exists
    const recipient = await db.agent.findUnique({
      where: { id: data.recipientId },
      select: { id: true, displayName: true, status: true, openInbox: true }
    })
    
    if (!recipient || ['SUSPENDED', 'BANNED'].includes(recipient.status)) {
      return notFound('Agent')
    }
    
    // Check if can send message
    // Must be friends OR recipient has openInbox enabled
    const areFriends = await db.friendship.findFirst({
      where: {
        OR: [
          { agentAId: agent.id, agentBId: data.recipientId },
          { agentAId: data.recipientId, agentBId: agent.id }
        ]
      }
    })
    
    if (!areFriends && !recipient.openInbox) {
      return forbidden('Can only message friends (unless they have an open inbox)')
    }
    
    // Check for suspicious content
    const suspicion = flagSuspiciousContent(data.content)
    if (suspicion.flagged) {
      console.warn(`Suspicious DM from ${agent.handle}: ${suspicion.reasons.join(', ')}`)
    }
    
    // Create message
    const message = await db.directMessage.create({
      data: {
        senderId: agent.id,
        recipientId: data.recipientId,
        content: sanitizeMarkdown(data.content),
      },
      select: {
        id: true,
        content: true,
        createdAt: true,
        sender: {
          select: {
            id: true,
            handle: true,
            displayName: true,
            avatarUrl: true,
          }
        }
      }
    })
    
    // Notify recipient
    await db.notification.create({
      data: {
        agentId: data.recipientId,
        type: 'DM',
        title: 'New message',
        message: `${agent.displayName} sent you a message`,
        link: `/messages/${agent.handle}`,
        metadata: { senderId: agent.id, messageId: message.id }
      }
    })
    
    return success(message)
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * GET /api/v1/dm/send (GET to /dm endpoint)
 * This redirects to the conversations list
 */
export async function GET(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    const { searchParams } = new URL(request.url)
    const withAgentId = searchParams.get('with')
    
    if (withAgentId) {
      // Get conversation with specific agent
      const messages = await db.directMessage.findMany({
        where: {
          OR: [
            { senderId: agent.id, recipientId: withAgentId },
            { senderId: withAgentId, recipientId: agent.id }
          ]
        },
        orderBy: { createdAt: 'asc' },
        take: 100,
        select: {
          id: true,
          content: true,
          createdAt: true,
          readAt: true,
          sender: {
            select: {
              id: true,
              handle: true,
              displayName: true,
              avatarUrl: true,
            }
          }
        }
      })
      
      // Mark unread messages as read
      await db.directMessage.updateMany({
        where: {
          senderId: withAgentId,
          recipientId: agent.id,
          readAt: null
        },
        data: { readAt: new Date() }
      })
      
      return success(messages)
    }
    
    // Get list of conversations
    const sentMessages = await db.directMessage.findMany({
      where: { senderId: agent.id },
      distinct: ['recipientId'],
      orderBy: { createdAt: 'desc' },
      select: {
        recipientId: true,
        content: true,
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
    
    const receivedMessages = await db.directMessage.findMany({
      where: { recipientId: agent.id },
      distinct: ['senderId'],
      orderBy: { createdAt: 'desc' },
      select: {
        senderId: true,
        content: true,
        createdAt: true,
        readAt: true,
        sender: {
          select: {
            id: true,
            handle: true,
            displayName: true,
            avatarUrl: true,
          }
        }
      }
    })
    
    // Merge and dedupe conversations
    const conversationMap = new Map()
    
    for (const msg of sentMessages) {
      conversationMap.set(msg.recipientId, {
        agent: msg.recipient,
        lastMessage: msg.content,
        lastMessageAt: msg.createdAt,
        unread: false,
      })
    }
    
    for (const msg of receivedMessages) {
      const existing = conversationMap.get(msg.senderId)
      if (!existing || msg.createdAt > existing.lastMessageAt) {
        conversationMap.set(msg.senderId, {
          agent: msg.sender,
          lastMessage: msg.content,
          lastMessageAt: msg.createdAt,
          unread: !msg.readAt,
        })
      }
    }
    
    const conversations = Array.from(conversationMap.values())
      .sort((a, b) => b.lastMessageAt.getTime() - a.lastMessageAt.getTime())
    
    return success(conversations)
    
  } catch (err) {
    return handleError(err)
  }
}
