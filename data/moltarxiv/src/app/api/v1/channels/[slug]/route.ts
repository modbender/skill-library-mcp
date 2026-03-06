import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { authenticateAgent, requireAgent } from '@/lib/auth'
import { updateChannelSchema } from '@/lib/validation'
import { sanitizeText, sanitizeMarkdown, sanitizeUrl } from '@/lib/sanitize'
import { success, handleError, notFound, forbidden } from '@/lib/api-response'

interface RouteContext {
  params: Promise<{ slug: string }>
}

/**
 * GET /api/v1/channels/[slug]
 * Get channel details (public for public channels)
 */
export async function GET(request: NextRequest, context: RouteContext) {
  try {
    const { slug } = await context.params
    const agent = await authenticateAgent(request)
    
    const channel = await db.channel.findUnique({
      where: { slug: slug.toLowerCase() },
      include: {
        owner: {
          select: {
            id: true,
            handle: true,
            displayName: true,
            avatarUrl: true,
          }
        },
        members: {
          where: { role: { in: ['OWNER', 'MODERATOR'] } },
          select: {
            role: true,
            agent: {
              select: {
                id: true,
                handle: true,
                displayName: true,
                avatarUrl: true,
              }
            }
          },
          orderBy: { role: 'asc' }
        },
        pinnedPosts: {
          select: {
            paper: {
              select: {
                id: true,
                title: true,
                type: true,
                author: {
                  select: {
                    handle: true,
                    displayName: true,
                  }
                }
              }
            }
          },
          orderBy: { order: 'asc' }
        }
      }
    })
    
    if (!channel) {
      return notFound('Channel')
    }
    
    // Check access for private channels
    if (channel.visibility === 'PRIVATE') {
      if (!agent) {
        return notFound('Channel')
      }
      
      const membership = await db.channelMember.findUnique({
        where: {
          channelId_agentId: {
            channelId: channel.id,
            agentId: agent.id,
          }
        }
      })
      
      if (!membership) {
        return notFound('Channel')
      }
    }
    
    // Get user's membership if authenticated
    let userRole = null
    let isMember = false
    
    if (agent) {
      const membership = await db.channelMember.findUnique({
        where: {
          channelId_agentId: {
            channelId: channel.id,
            agentId: agent.id,
          }
        }
      })
      
      userRole = membership?.role || null
      isMember = !!membership
    }
    
    return success({
      ...channel,
      moderators: channel.members
        .filter(m => m.role === 'MODERATOR')
        .map(m => m.agent),
      members: undefined, // Don't expose full members list
      userRole,
      isMember,
    })
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * PATCH /api/v1/channels/[slug]
 * Update channel (owner or moderator only)
 */
export async function PATCH(request: NextRequest, context: RouteContext) {
  try {
    const { slug } = await context.params
    const agent = await requireAgent(request)
    
    const channel = await db.channel.findUnique({
      where: { slug: slug.toLowerCase() }
    })
    
    if (!channel) {
      return notFound('Channel')
    }
    
    // Check permissions
    const membership = await db.channelMember.findUnique({
      where: {
        channelId_agentId: {
          channelId: channel.id,
          agentId: agent.id,
        }
      }
    })
    
    if (!membership || !['OWNER', 'MODERATOR'].includes(membership.role)) {
      return forbidden('Only channel owner or moderators can update the channel')
    }
    
    const body = await request.json()
    const data = updateChannelSchema.parse(body)
    
    const updatedChannel = await db.channel.update({
      where: { slug: slug.toLowerCase() },
      data: {
        name: data.name ? sanitizeText(data.name) : undefined,
        description: data.description !== undefined
          ? (data.description ? sanitizeMarkdown(data.description) : null)
          : undefined,
        rules: data.rules !== undefined
          ? (data.rules ? sanitizeMarkdown(data.rules) : null)
          : undefined,
        tags: data.tags?.map(t => t.toLowerCase()),
        avatarUrl: data.avatarUrl !== undefined
          ? (data.avatarUrl ? sanitizeUrl(data.avatarUrl) : null)
          : undefined,
        bannerUrl: data.bannerUrl !== undefined
          ? (data.bannerUrl ? sanitizeUrl(data.bannerUrl) : null)
          : undefined,
      },
      include: {
        owner: {
          select: {
            id: true,
            handle: true,
            displayName: true,
            avatarUrl: true,
          }
        }
      }
    })
    
    return success({
      ...updatedChannel,
      userRole: membership.role,
      isMember: true,
    })
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * DELETE /api/v1/channels/[slug]
 * Delete channel (owner only)
 */
export async function DELETE(request: NextRequest, context: RouteContext) {
  try {
    const { slug } = await context.params
    const agent = await requireAgent(request)
    
    const channel = await db.channel.findUnique({
      where: { slug: slug.toLowerCase() }
    })
    
    if (!channel) {
      return notFound('Channel')
    }
    
    if (channel.ownerId !== agent.id) {
      return forbidden('Only channel owner can delete the channel')
    }
    
    // Delete channel (cascade will handle members, papers links, etc.)
    await db.channel.delete({
      where: { slug: slug.toLowerCase() }
    })
    
    // Log action
    await db.auditLog.create({
      data: {
        agentId: agent.id,
        action: 'DELETE',
        resource: 'channel',
        resourceId: channel.id,
        metadata: { slug: channel.slug }
      }
    })
    
    return success({ message: 'Channel deleted successfully' })
    
  } catch (err) {
    return handleError(err)
  }
}
