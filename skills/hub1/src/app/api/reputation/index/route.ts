import { NextRequest, NextResponse } from 'next/server'
import { runIndexer, registerAgentManually } from '@/lib/acp-indexer'

/**
 * POST /api/reputation/index
 *
 * Trigger the ACP indexer to sync agents and index transactions
 * This should be called periodically (cron job) or manually
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}))
    const { apiKey, manualAgent } = body

    // Option 1: Register a manual agent
    if (manualAgent) {
      await registerAgentManually(
        manualAgent.address,
        manualAgent.name,
        manualAgent.description
      )
      return NextResponse.json({
        success: true,
        data: {
          message: 'Agent registered manually',
          address: manualAgent.address,
        },
      })
    }

    // Option 2: Run the full indexer
    const result = await runIndexer(apiKey)

    return NextResponse.json({
      success: true,
      data: {
        agentsSynced: result.agentsSynced,
        transactionsIndexed: result.transactionsIndexed,
        message: 'Indexer completed successfully',
      },
    })
  } catch (error) {
    console.error('Indexer error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Indexer failed',
      },
      { status: 500 }
    )
  }
}

/**
 * GET /api/reputation/index/status
 *
 * Get indexer status and stats
 */
export async function GET() {
  try {
    const { prisma } = await import('@/lib/prisma')

    const [agentCount, transactionCount, latestTransaction] = await Promise.all(
      [
        prisma.reputationAgent.count(),
        prisma.reputationTransaction.count(),
        prisma.reputationTransaction.findFirst({
          orderBy: { createdAt: 'desc' },
          select: { createdAt: true, acpTransactionId: true },
        }),
      ]
    )

    return NextResponse.json({
      success: true,
      data: {
        totalAgents: agentCount,
        totalTransactions: transactionCount,
        latestTransaction: latestTransaction
          ? {
              timestamp: latestTransaction.createdAt.toISOString(),
              txId: latestTransaction.acpTransactionId,
            }
          : null,
      },
    })
  } catch (error) {
    console.error('Status error:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to get status' },
      { status: 500 }
    )
  }
}
