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
 * GET /api/reputation/score?address=0x...
 *
 * Get detailed score breakdown for an agent
 * Cost: $0.50 per query
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const address = searchParams.get('address')
    const agentId = searchParams.get('agentId')
    const querierAddress = searchParams.get('querierAddress')

    if (!address && !agentId) {
      return NextResponse.json(
        { success: false, error: 'address or agentId query param required' },
        { status: 400 }
      )
    }

    // Find the agent
    const agent = await prisma.reputationAgent.findFirst({
      where: agentId
        ? { id: agentId }
        : { address: address!.toLowerCase() },
      include: {
        transactionsAsSeller: {
          select: { status: true, createdAt: true },
          orderBy: { createdAt: 'desc' },
          take: 100
        },
        transactionsAsBuyer: {
          select: { status: true, createdAt: true },
          orderBy: { createdAt: 'desc' },
          take: 100
        },
        reportsReceived: {
          select: { outcome: true, rating: true, createdAt: true },
          orderBy: { createdAt: 'desc' },
          take: 50
        }
      }
    })

    if (!agent) {
      return NextResponse.json({
        success: true,
        data: {
          found: false,
          address: address || null,
          agentId: agentId || null,
          message: 'Agent not found in reputation system'
        },
        cost: REPUTATION_QUERY_COST
      })
    }

    // Calculate detailed score
    const { trustScore, breakdown } = await calculateTrustScore(agent.id)
    const tier = getTier(trustScore)
    const recommendation = getRecommendation(trustScore)

    // Calculate trends (last 30 days vs previous 30 days)
    const now = new Date()
    const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
    const sixtyDaysAgo = new Date(now.getTime() - 60 * 24 * 60 * 60 * 1000)

    const recentTx = agent.transactionsAsSeller.filter(
      tx => new Date(tx.createdAt) >= thirtyDaysAgo
    )
    const previousTx = agent.transactionsAsSeller.filter(
      tx => new Date(tx.createdAt) >= sixtyDaysAgo && new Date(tx.createdAt) < thirtyDaysAgo
    )

    const recentSuccessRate = recentTx.length > 0
      ? recentTx.filter(tx => tx.status === 'completed').length / recentTx.length
      : 0
    const previousSuccessRate = previousTx.length > 0
      ? previousTx.filter(tx => tx.status === 'completed').length / previousTx.length
      : 0

    const trend = recentSuccessRate > previousSuccessRate ? 'improving'
      : recentSuccessRate < previousSuccessRate ? 'declining'
      : 'stable'

    // Recent activity summary
    const recentActivity = {
      transactionsLast30Days: recentTx.length,
      successfulLast30Days: recentTx.filter(tx => tx.status === 'completed').length,
      disputesLast30Days: recentTx.filter(tx => tx.status === 'disputed').length,
      reportsReceivedLast30Days: agent.reportsReceived.filter(
        r => new Date(r.createdAt) >= thirtyDaysAgo
      ).length
    }

    // Record the query
    if (querierAddress) {
      await recordQuery(querierAddress, agent.id, 'detailed', trustScore, recommendation)
    }

    return NextResponse.json({
      success: true,
      data: {
        found: true,
        agentId: agent.id,
        agentAddress: agent.address,
        name: agent.name,
        description: agent.description,
        services: agent.services,
        categories: agent.categories,
        website: agent.website,

        // Trust Score Details
        trustScore,
        tier: tier.label.toLowerCase(),
        tierBadge: tier.badge,
        recommendation,

        // Detailed Breakdown
        scoreBreakdown: {
          reliability: {
            score: breakdown.reliability,
            weight: '35%',
            description: 'Success rate of transactions'
          },
          volume: {
            score: breakdown.volume,
            weight: '20%',
            description: 'Total transaction volume (log scale)'
          },
          recency: {
            score: breakdown.recency,
            weight: '15%',
            description: 'Activity in the last 30 days'
          },
          ratings: {
            score: breakdown.ratings,
            weight: '20%',
            description: 'Average rating from counterparties'
          },
          disputes: {
            score: breakdown.disputes,
            weight: '10%',
            description: 'Dispute rate (lower is better)'
          }
        },

        // Stats
        stats: {
          totalTransactions: agent.totalTransactions,
          successfulTransactions: agent.successfulTx,
          reliabilityRate: agent.reliabilityRate,
          avgRating: agent.avgRating,
          totalRatings: agent.totalRatings,
          disputeCount: agent.disputeCount,
          avgResponseTimeMs: agent.avgResponseTimeMs
        },

        // Verification
        isVerified: agent.isVerified,
        verifiedAt: agent.verifiedAt?.toISOString() || null,
        badges: agent.badges,

        // Trends
        trend,
        recentActivity,

        // Timestamps
        registeredAt: agent.registeredAt.toISOString(),
        updatedAt: agent.updatedAt.toISOString()
      },
      cost: REPUTATION_QUERY_COST
    })
  } catch (error) {
    console.error('Score fetch error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
