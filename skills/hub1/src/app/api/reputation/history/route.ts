import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { REPUTATION_QUERY_COST, recordQuery } from '@/lib/reputation'

/**
 * GET /api/reputation/history?address=0x...&limit=20&offset=0
 *
 * Get transaction history for an agent
 * Cost: $0.50 per query
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const address = searchParams.get('address')
    const agentId = searchParams.get('agentId')
    const querierAddress = searchParams.get('querierAddress')
    const limit = Math.min(parseInt(searchParams.get('limit') || '20'), 100)
    const offset = parseInt(searchParams.get('offset') || '0')

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
        : { address: address!.toLowerCase() }
    })

    if (!agent) {
      return NextResponse.json({
        success: true,
        data: {
          found: false,
          transactions: [],
          total: 0,
          message: 'Agent not found in reputation system'
        },
        cost: REPUTATION_QUERY_COST
      })
    }

    // Get transactions where agent is buyer or seller
    const [transactions, total] = await Promise.all([
      prisma.reputationTransaction.findMany({
        where: {
          OR: [
            { buyerId: agent.id },
            { sellerId: agent.id }
          ]
        },
        include: {
          buyer: { select: { id: true, address: true, name: true, trustScore: true } },
          seller: { select: { id: true, address: true, name: true, trustScore: true } },
          reports: {
            select: { outcome: true, rating: true, createdAt: true }
          }
        },
        orderBy: { createdAt: 'desc' },
        take: limit,
        skip: offset
      }),
      prisma.reputationTransaction.count({
        where: {
          OR: [
            { buyerId: agent.id },
            { sellerId: agent.id }
          ]
        }
      })
    ])

    // Format transactions
    const formattedTransactions = transactions.map(tx => ({
      id: tx.id,
      role: tx.buyerId === agent.id ? 'buyer' : 'seller',
      counterparty: tx.buyerId === agent.id
        ? { id: tx.seller.id, address: tx.seller.address, name: tx.seller.name, trustScore: tx.seller.trustScore }
        : { id: tx.buyer.id, address: tx.buyer.address, name: tx.buyer.name, trustScore: tx.buyer.trustScore },
      serviceType: tx.serviceType,
      amount: tx.amount,
      status: tx.status,
      ratings: tx.reports.map(r => ({ outcome: r.outcome, rating: r.rating })),
      createdAt: tx.createdAt.toISOString(),
      completedAt: tx.completedAt?.toISOString() || null,
      responseTimeMs: tx.responseTimeMs
    }))

    // Record the query (for billing)
    if (querierAddress) {
      await recordQuery(querierAddress, agent.id, 'history', agent.trustScore, 'history_query')
    }

    return NextResponse.json({
      success: true,
      data: {
        found: true,
        agentId: agent.id,
        agentAddress: agent.address,
        transactions: formattedTransactions,
        total,
        limit,
        offset,
        hasMore: offset + limit < total
      },
      cost: REPUTATION_QUERY_COST
    })
  } catch (error) {
    console.error('History fetch error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
