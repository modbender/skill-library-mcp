import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { getTier } from '@/lib/reputation'

/**
 * GET /api/reputation/leaderboard?limit=50&category=all
 *
 * Get the top agents by trust score
 * Cost: FREE (marketing / engagement)
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const limit = Math.min(parseInt(searchParams.get('limit') || '50'), 100)
    const category = searchParams.get('category') || 'all'
    const minTransactions = parseInt(searchParams.get('minTransactions') || '0')

    // Build where clause
    const where: Record<string, unknown> = {
      totalTransactions: { gte: minTransactions }
    }

    if (category !== 'all') {
      where.categories = { has: category }
    }

    // Get top agents
    const agents = await prisma.reputationAgent.findMany({
      where,
      orderBy: [
        { trustScore: 'desc' },
        { totalTransactions: 'desc' }
      ],
      take: limit,
      select: {
        id: true,
        address: true,
        name: true,
        trustScore: true,
        totalTransactions: true,
        successfulTx: true,
        reliabilityRate: true,
        avgRating: true,
        badges: true,
        isVerified: true,
        services: true,
        categories: true
      }
    })

    // Format leaderboard
    const leaderboard = agents.map((agent, index) => ({
      rank: index + 1,
      agentId: agent.id,
      address: agent.address,
      name: agent.name || `Agent ${agent.address.slice(0, 8)}...`,
      trustScore: agent.trustScore,
      tier: getTier(agent.trustScore).label.toLowerCase(),
      tierBadge: getTier(agent.trustScore).badge,
      stats: {
        totalTransactions: agent.totalTransactions,
        successRate: agent.reliabilityRate,
        avgRating: agent.avgRating
      },
      badges: agent.badges,
      isVerified: agent.isVerified,
      services: agent.services,
      categories: agent.categories
    }))

    // Get some aggregate stats
    const [totalAgents, totalTransactions, avgTrustScore] = await Promise.all([
      prisma.reputationAgent.count(),
      prisma.reputationTransaction.count(),
      prisma.reputationAgent.aggregate({
        _avg: { trustScore: true }
      })
    ])

    return NextResponse.json({
      success: true,
      data: {
        leaderboard,
        total: leaderboard.length,
        filter: {
          category,
          minTransactions
        },
        networkStats: {
          totalAgents,
          totalTransactions,
          averageTrustScore: Math.round(avgTrustScore._avg.trustScore || 50)
        }
      },
      cost: 0 // Free for engagement
    })
  } catch (error) {
    console.error('Leaderboard fetch error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
