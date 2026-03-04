import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import {
  calculateTrustScore,
  getTier,
  getRecommendation,
  recordQuery,
  REPUTATION_QUERY_COST
} from '@/lib/reputation'

/**
 * POST /api/reputation/verify
 *
 * Verify an agent's reputation before transacting
 * Cost: $0.50 per query
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { agentAddress, agentId, minScore, querierAddress } = body

    if (!agentAddress && !agentId) {
      return NextResponse.json(
        { success: false, error: 'agentAddress or agentId required' },
        { status: 400 }
      )
    }

    // Find the agent
    const agent = await prisma.reputationAgent.findFirst({
      where: agentId
        ? { id: agentId }
        : { address: agentAddress.toLowerCase() }
    })

    if (!agent) {
      return NextResponse.json(
        {
          success: true,
          data: {
            found: false,
            agentAddress: agentAddress || null,
            agentId: agentId || null,
            trustScore: 0,
            tier: 'unknown',
            recommendation: 'not_found',
            message: 'Agent not registered in reputation system'
          },
          cost: REPUTATION_QUERY_COST
        }
      )
    }

    // Calculate trust score
    const { trustScore, breakdown } = await calculateTrustScore(agent.id)
    const tier = getTier(trustScore)
    const recommendation = getRecommendation(trustScore)
    const meetsMinScore = minScore ? trustScore >= minScore : true

    // Record the query (for billing/analytics)
    if (querierAddress) {
      await recordQuery(querierAddress, agent.id, 'verify', trustScore, recommendation)
    }

    return NextResponse.json({
      success: true,
      data: {
        found: true,
        agentId: agent.id,
        agentAddress: agent.address,
        name: agent.name,

        // Trust Score
        trustScore,
        tier: tier.label.toLowerCase(),
        tierBadge: tier.badge,

        // Quick Stats
        reliabilityRate: agent.reliabilityRate,
        totalTransactions: agent.totalTransactions,
        avgRating: agent.avgRating,
        isVerified: agent.isVerified,

        // Recommendation
        recommendation,
        meetsMinScore,

        // Badges
        badges: agent.badges,

        // Breakdown (for transparency)
        scoreBreakdown: breakdown,
      },
      cost: REPUTATION_QUERY_COST
    })
  } catch (error) {
    console.error('Reputation verify error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
