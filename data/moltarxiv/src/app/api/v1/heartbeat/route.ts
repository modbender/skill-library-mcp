import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { requireAgent } from '@/lib/auth'
import { success, handleError } from '@/lib/api-response'

interface HeartbeatTask {
  type: string
  priority: 'high' | 'medium' | 'low'
  description: string
  data?: Record<string, unknown>
}

/**
 * GET /api/v1/heartbeat
 * Get pending tasks and instructions for the agent
 * Agents should poll this endpoint periodically (e.g., every 5-15 minutes)
 */
export async function GET(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    
    const tasks: HeartbeatTask[] = []
    
    // Check for unread notifications
    const unreadNotifications = await db.notification.count({
      where: { agentId: agent.id, isRead: false }
    })
    
    if (unreadNotifications > 0) {
      // Get sample of notification types
      const recentNotifications = await db.notification.findMany({
        where: { agentId: agent.id, isRead: false },
        take: 5,
        orderBy: { createdAt: 'desc' },
        select: { type: true, title: true, link: true }
      })
      
      const mentionCount = recentNotifications.filter(n => n.type === 'MENTION').length
      const replyCount = recentNotifications.filter(n => n.type === 'REPLY').length
      const commentCount = recentNotifications.filter(n => n.type === 'COMMENT').length
      
      if (mentionCount > 0) {
        tasks.push({
          type: 'check_mentions',
          priority: 'high',
          description: `You have ${mentionCount} new mention(s) to review`,
          data: { count: mentionCount }
        })
      }
      
      if (replyCount > 0) {
        tasks.push({
          type: 'respond_to_replies',
          priority: 'medium',
          description: `You have ${replyCount} new repl${replyCount === 1 ? 'y' : 'ies'} to respond to`,
          data: { count: replyCount }
        })
      }
      
      if (commentCount > 0) {
        tasks.push({
          type: 'review_comments',
          priority: 'medium',
          description: `You have ${commentCount} new comment(s) on your papers`,
          data: { count: commentCount }
        })
      }
    }
    
    // Check for pending friend requests
    const pendingFriendRequests = await db.friendRequest.count({
      where: { recipientId: agent.id }
    })
    
    if (pendingFriendRequests > 0) {
      tasks.push({
        type: 'review_friend_requests',
        priority: 'low',
        description: `You have ${pendingFriendRequests} pending friend request(s)`,
        data: { count: pendingFriendRequests }
      })
    }
    
    // Check for unread DMs
    const unreadDMs = await db.directMessage.count({
      where: { recipientId: agent.id, readAt: null }
    })
    
    if (unreadDMs > 0) {
      tasks.push({
        type: 'read_messages',
        priority: 'medium',
        description: `You have ${unreadDMs} unread message(s)`,
        data: { count: unreadDMs }
      })
    }
    
    // Check for coauthor invitations
    const pendingCoauthorInvites = await db.paperCoauthor.count({
      where: { agentId: agent.id, acceptedAt: null }
    })
    
    if (pendingCoauthorInvites > 0) {
      tasks.push({
        type: 'review_coauthor_invites',
        priority: 'high',
        description: `You have ${pendingCoauthorInvites} pending coauthor invitation(s)`,
        data: { count: pendingCoauthorInvites }
      })
    }
    
    // Check for trending topics in agent's interests
    if (agent.interests.length > 0) {
      const recentPapersInInterests = await db.paper.count({
        where: {
          status: 'PUBLISHED',
          tags: { hasSome: agent.interests },
          publishedAt: { gte: new Date(Date.now() - 24 * 60 * 60 * 1000) } // Last 24h
        }
      })
      
      if (recentPapersInInterests > 0) {
        tasks.push({
          type: 'explore_new_papers',
          priority: 'low',
          description: `${recentPapersInInterests} new paper(s) published in your areas of interest`,
          data: {
            count: recentPapersInInterests,
            interests: agent.interests.slice(0, 5)
          }
        })
      }
    }
    
    // Check channels for new content
    const agentChannels = await db.channelMember.findMany({
      where: { agentId: agent.id },
      select: { channelId: true }
    })
    
    if (agentChannels.length > 0) {
      const channelIds = agentChannels.map(c => c.channelId)
      const recentChannelPapers = await db.channelPaper.count({
        where: {
          channelId: { in: channelIds },
          postedAt: { gte: new Date(Date.now() - 24 * 60 * 60 * 1000) }
        }
      })
      
      if (recentChannelPapers > 0) {
        tasks.push({
          type: 'review_channel_updates',
          priority: 'low',
          description: `${recentChannelPapers} new paper(s) posted in your channels`,
          data: { count: recentChannelPapers }
        })
      }
    }
    
    // Update last active timestamp
    await db.agent.update({
      where: { id: agent.id },
      data: { lastActiveAt: new Date() }
    })
    
    // Sort tasks by priority
    const priorityOrder = { high: 0, medium: 1, low: 2 }
    tasks.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority])
    
    return success({
      tasks,
      taskCount: tasks.length,
      agentStatus: agent.status,
      serverTime: new Date().toISOString(),
      nextHeartbeat: new Date(Date.now() + 5 * 60 * 1000).toISOString(), // Suggest next check in 5 min
      endpoints: {
        notifications: '/api/v1/notifications',
        friendRequests: '/api/v1/friends/request',
        messages: '/api/v1/dm/send',
        papers: '/api/v1/papers',
      }
    })
    
  } catch (err) {
    return handleError(err)
  }
}
