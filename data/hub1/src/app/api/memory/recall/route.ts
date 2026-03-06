import { NextRequest, NextResponse } from 'next/server'
import { authenticate, checkRecallLimit } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { createEmbedding } from '@/lib/embeddings'
import { searchVectors } from '@/lib/qdrant'
import type { RecallMemoryRequest, ApiResponse, MemoryResponse } from '@/types'

export async function POST(request: NextRequest): Promise<NextResponse<ApiResponse<MemoryResponse[]>>> {
  try {
    // Authenticate (supports both JWT and legacy auth)
    const auth = await authenticate(request)

    if (!auth.success || !auth.agent) {
      return NextResponse.json(
        { success: false, error: auth.error },
        { status: 401 }
      )
    }

    // Check limits
    if (!checkRecallLimit(auth.agent.tier, auth.agent.recallsToday)) {
      return NextResponse.json(
        { success: false, error: 'Daily recall limit reached. Upgrade to Pro for unlimited recalls.' },
        { status: 402 }
      )
    }

    // Parse body
    const body: RecallMemoryRequest = await request.json()

    if (!body.query || typeof body.query !== 'string') {
      return NextResponse.json(
        { success: false, error: 'Query is required' },
        { status: 400 }
      )
    }

    // Validate query length (max 1KB)
    if (body.query.length > 1000) {
      return NextResponse.json(
        { success: false, error: 'Query too long. Maximum 1,000 characters.' },
        { status: 400 }
      )
    }

    const limit = Math.min(body.limit || 5, 20) // Max 20 results

    // Create embedding for query
    const queryEmbedding = await createEmbedding(body.query)

    // Search Qdrant
    const results = await searchVectors(
      queryEmbedding,
      auth.agent.id,
      limit,
      body.type ? { type: body.type } : undefined
    )

    // Get full memory data from Postgres
    const vectorIds = results.map((r) => r.id)
    const memories = await prisma.memory.findMany({
      where: { vectorId: { in: vectorIds } },
    })

    // Map with relevance scores
    const memoriesWithScores: MemoryResponse[] = results.map((result) => {
      const memory = memories.find((m) => m.vectorId === result.id)
      return {
        id: memory?.id || result.id,
        content: (result.payload.content as string) || memory?.content || '',
        type: (result.payload.type as MemoryResponse['type']) || 'fact',
        tags: (result.payload.tags as string[]) || memory?.tags || [],
        relevance: result.score,
        createdAt: memory?.createdAt.toISOString() || new Date().toISOString(),
      }
    })

    // Update agent stats
    await prisma.agent.update({
      where: { id: auth.agent.id },
      data: { recallsToday: { increment: 1 } },
    })

    // Log usage
    await prisma.usageLog.create({
      data: {
        agentId: auth.agent.id,
        action: 'recall',
        cost: 0.005,
      },
    })

    return NextResponse.json({
      success: true,
      data: memoriesWithScores,
      usage: {
        memoriesStored: auth.agent.memoriesStored,
        recallsToday: auth.agent.recallsToday + 1,
        tier: auth.agent.tier,
      },
    })
  } catch (error) {
    console.error('Recall memory error:', error instanceof Error ? error.message : 'Unknown error')
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
