import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { updateAgentScore } from '@/lib/reputation'

/**
 * POST /api/reputation/transaction
 *
 * Record a transaction between two agents
 * Cost: FREE (we want transaction data)
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const {
      buyerAddress,
      sellerAddress,
      serviceType,
      amount,
      acpTransactionId
    } = body

    if (!buyerAddress || !sellerAddress) {
      return NextResponse.json(
        { success: false, error: 'buyerAddress and sellerAddress required' },
        { status: 400 }
      )
    }

    // Get or create buyer agent
    let buyer = await prisma.reputationAgent.findUnique({
      where: { address: buyerAddress.toLowerCase() }
    })
    if (!buyer) {
      buyer = await prisma.reputationAgent.create({
        data: { address: buyerAddress.toLowerCase(), trustScore: 50 }
      })
    }

    // Get or create seller agent
    let seller = await prisma.reputationAgent.findUnique({
      where: { address: sellerAddress.toLowerCase() }
    })
    if (!seller) {
      seller = await prisma.reputationAgent.create({
        data: { address: sellerAddress.toLowerCase(), trustScore: 50 }
      })
    }

    // Check for duplicate ACP transaction
    if (acpTransactionId) {
      const existing = await prisma.reputationTransaction.findUnique({
        where: { acpTransactionId }
      })
      if (existing) {
        return NextResponse.json({
          success: true,
          data: {
            transactionId: existing.id,
            status: existing.status,
            message: 'Transaction already recorded'
          }
        })
      }
    }

    // Create transaction record
    const transaction = await prisma.reputationTransaction.create({
      data: {
        buyerId: buyer.id,
        sellerId: seller.id,
        serviceType: serviceType || 'unknown',
        amount: amount || 0,
        acpTransactionId: acpTransactionId || null,
        status: 'pending',
      }
    })

    // Update transaction counts
    await prisma.reputationAgent.update({
      where: { id: seller.id },
      data: { totalTransactions: { increment: 1 } }
    })

    return NextResponse.json({
      success: true,
      data: {
        transactionId: transaction.id,
        buyerId: buyer.id,
        sellerId: seller.id,
        status: 'pending',
        message: 'Transaction recorded. Submit outcome report when completed.'
      }
    })
  } catch (error) {
    console.error('Transaction record error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}

/**
 * PATCH /api/reputation/transaction
 *
 * Update transaction status (complete, dispute, refund)
 */
export async function PATCH(request: NextRequest) {
  try {
    const body = await request.json()
    const { transactionId, status, responseTimeMs } = body

    if (!transactionId || !status) {
      return NextResponse.json(
        { success: false, error: 'transactionId and status required' },
        { status: 400 }
      )
    }

    const validStatuses = ['completed', 'disputed', 'refunded']
    if (!validStatuses.includes(status)) {
      return NextResponse.json(
        { success: false, error: `status must be one of: ${validStatuses.join(', ')}` },
        { status: 400 }
      )
    }

    const transaction = await prisma.reputationTransaction.findUnique({
      where: { id: transactionId }
    })

    if (!transaction) {
      return NextResponse.json(
        { success: false, error: 'Transaction not found' },
        { status: 404 }
      )
    }

    // Update transaction
    const updated = await prisma.reputationTransaction.update({
      where: { id: transactionId },
      data: {
        status,
        completedAt: status === 'completed' ? new Date() : null,
        responseTimeMs: responseTimeMs || null,
      }
    })

    // Update seller stats
    if (status === 'completed') {
      await prisma.reputationAgent.update({
        where: { id: transaction.sellerId },
        data: {
          successfulTx: { increment: 1 },
          reliabilityRate: {
            // Will be recalculated properly by updateAgentScore
            set: 0
          }
        }
      })

      // Recalculate reliability rate
      const seller = await prisma.reputationAgent.findUnique({
        where: { id: transaction.sellerId }
      })
      if (seller && seller.totalTransactions > 0) {
        const reliabilityRate = seller.successfulTx / seller.totalTransactions
        await prisma.reputationAgent.update({
          where: { id: transaction.sellerId },
          data: { reliabilityRate }
        })
      }

      // Update trust score
      await updateAgentScore(transaction.sellerId)
    } else if (status === 'disputed') {
      await prisma.reputationAgent.update({
        where: { id: transaction.sellerId },
        data: { disputeCount: { increment: 1 } }
      })
      await updateAgentScore(transaction.sellerId)
    }

    return NextResponse.json({
      success: true,
      data: {
        transactionId: updated.id,
        status: updated.status,
        completedAt: updated.completedAt?.toISOString() || null
      }
    })
  } catch (error) {
    console.error('Transaction update error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
