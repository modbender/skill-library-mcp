import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { requireAgent, authenticateAgent } from '@/lib/auth'
import { createChannelSchema } from '@/lib/validation'
import { checkRateLimit } from '@/lib/rate-limit'
import { sanitizeText, sanitizeMarkdown } from '@/lib/sanitize'
import { success, handleError, rateLimitExceeded, paginated } from '@/lib/api-response'
import { generateAvatarUrl } from '@/lib/utils'

/**
 * GET /api/v1/channels
 * List channels (public)
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get('page') || '1')
    const limit = Math.min(parseInt(searchParams.get('limit') || '20'), 100)
    const sort = searchParams.get('sort') || 'popular'
    const search = searchParams.get('q')
    
    const agent = await authenticateAgent(request)
    
    // Build where clause
    const where: Record<string, unknown> = {}
    
    // Non-authenticated users only see public channels
    if (!agent) {
      where.visibility = 'PUBLIC'
    } else {
      // Authenticated agents see public + their private channels
      where.OR = [
        { visibility: 'PUBLIC' },
        { members: { some: { agentId: agent.id } } }
      ]
    }
    
    // Search
    if (search) {
      where.AND = [
        where.OR ? { OR: where.OR } : {},
        {
          OR: [
            { name: { contains: search, mode: 'insensitive' } },
            { slug: { contains: search, mode: 'insensitive' } },
            { description: { contains: search, mode: 'insensitive' } }
          ]
        }
      ]
      delete where.OR
    }
    
    // Sorting
    let orderBy: Record<string, string>[]
    switch (sort) {
      case 'new':
        orderBy = [{ createdAt: 'desc' }]
        break
      case 'alphabetical':
        orderBy = [{ name: 'asc' }]
        break
      case 'active':
        orderBy = [{ paperCount: 'desc' }, { memberCount: 'desc' }]
        break
      case 'popular':
      default:
        orderBy = [{ memberCount: 'desc' }, { paperCount: 'desc' }]
    }
    
    const [total, channels] = await Promise.all([
      db.channel.count({ where }),
      db.channel.findMany({
        where,
        orderBy,
        skip: (page - 1) * limit,
        take: limit,
        select: {
          id: true,
          slug: true,
          name: true,
          description: true,
          avatarUrl: true,
          visibility: true,
          memberCount: true,
          paperCount: true,
          tags: true,
          createdAt: true,
          owner: {
            select: {
              id: true,
              handle: true,
              displayName: true,
              avatarUrl: true,
            }
          },
          members: agent ? {
            where: { agentId: agent.id },
            select: { role: true }
          } : undefined,
        }
      })
    ])
    
    // Transform to include membership info
    const transformed = channels.map(c => ({
      ...c,
      userRole: c.members?.[0]?.role || null,
      isMember: !!c.members?.length,
      members: undefined,
    }))
    
    return paginated(transformed, page, limit, total)
    
  } catch (err) {
    return handleError(err)
  }
}

/**
 * POST /api/v1/channels
 * Create a new channel (agent only)
 */
export async function POST(request: NextRequest) {
  try {
    const agent = await requireAgent(request)
    
    // Check rate limit
    const rateCheck = await checkRateLimit(agent.id, 'channels/create')
    if (!rateCheck.allowed) {
      return rateLimitExceeded(rateCheck.resetAt)
    }
    
    const body = await request.json()
    const data = createChannelSchema.parse(body)
    
    // Check if slug is taken
    const existing = await db.channel.findUnique({
      where: { slug: data.slug.toLowerCase() }
    })
    
    if (existing) {
      return handleError(new Error('Channel slug already taken'))
    }
    
    // Create channel
    const channel = await db.channel.create({
      data: {
        slug: data.slug.toLowerCase(),
        name: sanitizeText(data.name),
        description: data.description ? sanitizeMarkdown(data.description) : null,
        rules: data.rules ? sanitizeMarkdown(data.rules) : null,
        tags: data.tags?.map(t => t.toLowerCase()) || [],
        visibility: data.visibility,
        ownerId: agent.id,
        avatarUrl: generateAvatarUrl(`channel-${data.slug}`),
        memberCount: 1, // Owner is first member
        members: {
          create: {
            agentId: agent.id,
            role: 'OWNER',
          }
        }
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
    
    // Log action
    await db.auditLog.create({
      data: {
        agentId: agent.id,
        action: 'CREATE',
        resource: 'channel',
        resourceId: channel.id,
        metadata: { slug: channel.slug }
      }
    })
    
    return success({
      ...channel,
      userRole: 'OWNER',
      isMember: true,
    })
    
  } catch (err) {
    return handleError(err)
  }
}
