import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { updateAgentScore, REPUTATION_QUERY_COST } from '@/lib/reputation'

/**
 * POST /api/reputation/report
 *
 * Submit an outcome report for a completed transaction
 * Cost: $0.50 per report
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const {
      transactionId,
      reporterAddress,
      outcome,
      rating,
      feedback,
      evidenceHash
    } = body

    // Validate required fields
    if (!transactionId || !reporterAddress || !outcome || !rating) {
      return NextResponse.json(
        { success: false, error: 'transactionId, reporterAddress, outcome, and rating required' },
        { status: 400 }
      )
    }

    // Validate outcome
    const validOutcomes = ['success', 'partial', 'failure', 'fraud']
    if (!validOutcomes.includes(outcome)) {
      return NextResponse.json(
        { success: false, error: `outcome must be one of: ${validOutcomes.join(', ')}` },
        { status: 400 }
      )
    }

    // Validate rating
    if (rating < 1 || rating > 5) {
      return NextResponse.json(
        { success: false, error: 'rating must be between 1 and 5' },
        { status: 400 }
      )
    }

    // Find the transaction
    const transaction = await prisma.reputationTransaction.findUnique({
      where: { id: transactionId },
      include: { buyer: true, seller: true }
    })

    if (!transaction) {
      return NextResponse.json(
        { success: false, error: 'Transaction not found' },
        { status: 404 }
      )
    }

    // Find or create the reporter
    let reporter = await prisma.reputationAgent.findUnique({
      where: { address: reporterAddress.toLowerCase() }
    })
    if (!reporter) {
      reporter = await prisma.reputationAgent.create({
        data: { address: reporterAddress.toLowerCase(), trustScore: 50 }
      })
    }

    // Determine who is being reported (the other party)
    const isBuyer = transaction.buyer.address === reporterAddress.toLowerCase()
    const reportedAgent = isBuyer ? transaction.seller : transaction.buyer

    // Check for duplicate report from same reporter
    const existingReport = await prisma.outcomeReport.findFirst({
      where: {
        transactionId,
        reporterId: reporter.id
      }
    })

    if (existingReport) {
      return NextResponse.json({
        success: false,
        error: 'You have already submitted a report for this transaction'
      }, { status: 409 })
    }

    // Create the outcome report
    const report = await prisma.outcomeReport.create({
      data: {
        transactionId,
        reporterId: reporter.id,
        reportedId: reportedAgent.id,
        outcome,
        rating,
        feedback: feedback || null,
        evidenceHash: evidenceHash || null
      }
    })

    // Update the reported agent's ratings
    const allRatings = await prisma.outcomeReport.findMany({
      where: { reportedId: reportedAgent.id },
      select: { rating: true }
    })

    const totalRatings = allRatings.length
    const avgRating = allRatings.reduce((sum, r) => sum + r.rating, 0) / totalRatings

    await prisma.reputationAgent.update({
      where: { id: reportedAgent.id },
      data: {
        avgRating,
        totalRatings
      }
    })

    // Update trust score
    await updateAgentScore(reportedAgent.id)

    // If this is a fraud report, flag it for review
    const isFraudReport = outcome === 'fraud'
    if (isFraudReport) {
      // In a production system, this would trigger alerts/review process
      console.warn(`FRAUD REPORT: Transaction ${transactionId}, Reported Agent: ${reportedAgent.address}`)
    }

    return NextResponse.json({
      success: true,
      data: {
        reportId: report.id,
        transactionId,
        reportedAgentId: reportedAgent.id,
        outcome,
        rating,
        isFraudReport,
        message: 'Outcome report submitted successfully'
      },
      cost: REPUTATION_QUERY_COST
    })
  } catch (error) {
    console.error('Outcome report error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
