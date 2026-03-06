import { NextRequest, NextResponse } from 'next/server'
import { v4 as uuidv4 } from 'uuid'
import { authenticate, checkMemoryLimit } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { createEmbedding } from '@/lib/embeddings'
import { upsertVector, ensureCollection } from '@/lib/qdrant'
import type { StoreMemoryRequest, ApiResponse, MemoryResponse } from '@/types'

export async function POST(request: NextRequest): Promise<NextResponse<ApiResponse<MemoryResponse>>> {
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
    if (!checkMemoryLimit(auth.agent.tier, auth.agent.memoriesStored)) {
      return NextResponse.json(
        { success: false, error: 'Memory limit reached. Upgrade to Pro for more storage.' },
        { status: 402 }
      )
    }

    // Parse body
    const body: StoreMemoryRequest = await request.json()

    if (!body.content || typeof body.content !== 'string') {
      return NextResponse.json(
        { success: false, error: 'Content is required' },
        { status: 400 }
      )
    }

    // Validate content length (max 10KB)
    if (body.content.length > 10000) {
      return NextResponse.json(
        { success: false, error: 'Content too long. Maximum 10,000 characters.' },
        { status: 400 }
      )
    }

    // Ensure Qdrant collection exists
    await ensureCollection()

    // Create embedding
    const embedding = await createEmbedding(body.content)

    // Generate vector ID
    const vectorId = uuidv4()

    // Store in Qdrant
    await upsertVector(vectorId, embedding, {
      agentId: auth.agent.id,
      content: body.content,
      type: body.type || 'fact',
      tags: body.tags || [],
    })

    // Store metadata in Postgres
    const memory = await prisma.memory.create({
      data: {
        agentId: auth.agent.id,
        content: body.content,
        type: body.type || 'fact',
        tags: body.tags || [],
        metadata: body.metadata ? JSON.parse(JSON.stringify(body.metadata)) : undefined,
        vectorId,
      },
    })

    // Update agent stats
    await prisma.agent.update({
      where: { id: auth.agent.id },
      data: { memoriesStored: { increment: 1 } },
    })

    // Log usage
    await prisma.usageLog.create({
      data: {
        agentId: auth.agent.id,
        action: 'store',
        cost: 0.001,
      },
    })

    return NextResponse.json({
      success: true,
      data: {
        id: memory.id,
        content: memory.content,
        type: memory.type as MemoryResponse['type'],
        tags: memory.tags,
        createdAt: memory.createdAt.toISOString(),
      },
      usage: {
        memoriesStored: auth.agent.memoriesStored + 1,
        recallsToday: auth.agent.recallsToday,
        tier: auth.agent.tier,
      },
    })
  } catch (error) {
    console.error('Store memory error:', error instanceof Error ? error.message : 'Unknown error')
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
