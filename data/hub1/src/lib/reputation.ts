import { prisma } from './prisma'

// Pricing
export const REPUTATION_QUERY_COST = 0.50 // $0.50 per query

// Score tiers
export const SCORE_TIERS = {
  excellent: { min: 90, label: 'Excellent', badge: 'gold' },
  good: { min: 75, label: 'Good', badge: 'silver' },
  average: { min: 50, label: 'Average', badge: 'bronze' },
  belowAverage: { min: 25, label: 'Below Average', badge: 'none' },
  poor: { min: 0, label: 'Poor', badge: 'warning' },
}

export function getTier(score: number) {
  if (score >= 90) return SCORE_TIERS.excellent
  if (score >= 75) return SCORE_TIERS.good
  if (score >= 50) return SCORE_TIERS.average
  if (score >= 25) return SCORE_TIERS.belowAverage
  return SCORE_TIERS.poor
}

export function getRecommendation(score: number): string {
  if (score >= 80) return 'highly_recommended'
  if (score >= 60) return 'safe_to_transact'
  if (score >= 40) return 'proceed_with_caution'
  if (score >= 20) return 'high_risk'
  return 'not_recommended'
}

/**
 * Calculate trust score for an agent
 *
 * Formula:
 * Trust Score = (
 *   Reliability × 0.35 +
 *   Volume × 0.20 +
 *   Recency × 0.15 +
 *   Ratings × 0.20 +
 *   Disputes × 0.10
 * )
 */
export async function calculateTrustScore(agentId: string): Promise<{
  trustScore: number
  breakdown: {
    reliability: number
    volume: number
    recency: number
    ratings: number
    disputes: number
  }
}> {
  const agent = await prisma.reputationAgent.findUnique({
    where: { id: agentId },
    include: {
      transactionsAsSeller: {
        where: {
          createdAt: { gte: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000) } // Last 90 days
        }
      },
      reportsReceived: {
        where: {
          createdAt: { gte: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000) }
        }
      }
    }
  })

  if (!agent) {
    return {
      trustScore: 50,
      breakdown: { reliability: 50, volume: 0, recency: 0, ratings: 50, disputes: 100 }
    }
  }

  // 1. Reliability Score (35%) - Success rate
  let reliabilityScore = 50 // Default for new agents
  if (agent.totalTransactions >= 5) {
    reliabilityScore = agent.totalTransactions > 0
      ? (agent.successfulTx / agent.totalTransactions) * 100
      : 50
  }

  // 2. Volume Score (20%) - Logarithmic scale
  const volumeScore = Math.min(100, Math.log10(agent.totalTransactions + 1) * 33)

  // 3. Recency Score (15%) - Activity in last 30 days
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
  const recentTransactions = agent.transactionsAsSeller.filter(
    tx => new Date(tx.createdAt) >= thirtyDaysAgo
  ).length
  const recencyScore = Math.min(100, recentTransactions * 10)

  // 4. Ratings Score (20%) - Average rating converted to 0-100
  let ratingsScore = 50 // Default
  if (agent.totalRatings >= 3) {
    ratingsScore = ((agent.avgRating - 1) / 4) * 100 // Convert 1-5 to 0-100
  }

  // 5. Dispute Score (10%) - Lower is better
  const disputeRate = agent.totalTransactions > 0
    ? agent.disputeCount / agent.totalTransactions
    : 0
  const disputeScore = Math.max(0, 100 - (disputeRate * 500))

  // Calculate weighted total
  const trustScore = Math.round(
    reliabilityScore * 0.35 +
    volumeScore * 0.20 +
    recencyScore * 0.15 +
    ratingsScore * 0.20 +
    disputeScore * 0.10
  )

  return {
    trustScore: Math.min(100, Math.max(0, trustScore)),
    breakdown: {
      reliability: Math.round(reliabilityScore),
      volume: Math.round(volumeScore),
      recency: Math.round(recencyScore),
      ratings: Math.round(ratingsScore),
      disputes: Math.round(disputeScore),
    }
  }
}

/**
 * Update agent's trust score (call after transactions/reports)
 */
export async function updateAgentScore(agentId: string): Promise<void> {
  const { trustScore } = await calculateTrustScore(agentId)

  // Update badges based on score and activity
  const agent = await prisma.reputationAgent.findUnique({ where: { id: agentId } })
  if (!agent) return

  const badges: string[] = []
  if (trustScore >= 90) badges.push('top_rated')
  if (agent.totalTransactions >= 100) badges.push('high_volume')
  if (agent.totalTransactions >= 1000) badges.push('power_seller')
  if (agent.avgResponseTimeMs > 0 && agent.avgResponseTimeMs < 2000) badges.push('fast_responder')
  if (agent.isVerified) badges.push('verified')
  if (agent.disputeCount === 0 && agent.totalTransactions >= 10) badges.push('dispute_free')

  await prisma.reputationAgent.update({
    where: { id: agentId },
    data: { trustScore, badges }
  })
}

/**
 * Record a query and charge for it
 */
export async function recordQuery(
  querierAddress: string,
  queriedId: string,
  queryType: string,
  trustScore: number,
  recommendation: string
): Promise<void> {
  await prisma.reputationQuery.create({
    data: {
      querierAddress,
      queriedId,
      queryType,
      cost: REPUTATION_QUERY_COST,
      trustScore,
      recommendation,
    }
  })
}
