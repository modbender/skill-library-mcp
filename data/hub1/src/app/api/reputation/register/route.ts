import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

/**
 * POST /api/reputation/register
 *
 * Register an agent in the reputation system
 * Cost: FREE (we want agents to register)
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { address, name, description, services, categories, website } = body

    if (!address) {
      return NextResponse.json(
        { success: false, error: 'address is required' },
        { status: 400 }
      )
    }

    const normalizedAddress = address.toLowerCase()

    // Check if already registered
    const existing = await prisma.reputationAgent.findUnique({
      where: { address: normalizedAddress }
    })

    if (existing) {
      // Update existing agent
      const updated = await prisma.reputationAgent.update({
        where: { address: normalizedAddress },
        data: {
          name: name || existing.name,
          description: description || existing.description,
          services: services || existing.services,
          categories: categories || existing.categories,
          website: website || existing.website,
        }
      })

      return NextResponse.json({
        success: true,
        data: {
          agentId: updated.id,
          address: updated.address,
          name: updated.name,
          trustScore: updated.trustScore,
          isNew: false,
          message: 'Agent profile updated'
        }
      })
    }

    // Create new agent
    const agent = await prisma.reputationAgent.create({
      data: {
        address: normalizedAddress,
        name: name || null,
        description: description || null,
        services: services || [],
        categories: categories || [],
        website: website || null,
        trustScore: 50, // Start neutral
      }
    })

    return NextResponse.json({
      success: true,
      data: {
        agentId: agent.id,
        address: agent.address,
        name: agent.name,
        trustScore: agent.trustScore,
        isNew: true,
        message: 'Agent registered successfully'
      }
    })
  } catch (error) {
    console.error('Reputation register error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}

/**
 * GET /api/reputation/register?address=0x...
 *
 * Check if an agent is registered
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const address = searchParams.get('address')

    if (!address) {
      return NextResponse.json(
        { success: false, error: 'address query param required' },
        { status: 400 }
      )
    }

    const agent = await prisma.reputationAgent.findUnique({
      where: { address: address.toLowerCase() }
    })

    if (!agent) {
      return NextResponse.json({
        success: true,
        data: {
          registered: false,
          address: address.toLowerCase()
        }
      })
    }

    return NextResponse.json({
      success: true,
      data: {
        registered: true,
        agentId: agent.id,
        address: agent.address,
        name: agent.name,
        trustScore: agent.trustScore,
        totalTransactions: agent.totalTransactions,
        isVerified: agent.isVerified,
        registeredAt: agent.registeredAt.toISOString()
      }
    })
  } catch (error) {
    console.error('Reputation check error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
