import { NextRequest, NextResponse } from 'next/server'
import { verifyAgent } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { deleteAgentVectors } from '@/lib/qdrant'
import type { ApiResponse, MemoryResponse, MemoryType } from '@/types'

// GET - Export all memories
export async function GET(request: NextRequest): Promise<NextResponse<ApiResponse<MemoryResponse[]>>> {
  try {
    // Authenticate
    const auth = await verifyAgent(
      request.headers.get('x-agent-address'),
      request.headers.get('x-agent-signature'),
      request.headers.get('x-agent-timestamp')
    )

    if (!auth.success || !auth.agent) {
      return NextResponse.json(
        { success: false, error: auth.error },
        { status: 401 }
      )
    }

    // Fetch all memories
    const memories = await prisma.memory.findMany({
      where: { agentId: auth.agent.id },
      orderBy: { createdAt: 'desc' },
    })

    const response: MemoryResponse[] = memories.map((m) => ({
      id: m.id,
      content: m.content,
      type: m.type as MemoryType,
      tags: m.tags,
      createdAt: m.createdAt.toISOString(),
    }))

    // Log usage
    await prisma.usageLog.create({
      data: {
        agentId: auth.agent.id,
        action: 'export',
        cost: 0.02,
      },
    })

    return NextResponse.json({
      success: true,
      data: response,
    })
  } catch (error) {
    console.error('Export vault error:', error instanceof Error ? error.message : 'Unknown error')
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// DELETE - Clear entire vault
export async function DELETE(request: NextRequest): Promise<NextResponse<ApiResponse>> {
  try {
    // Authenticate
    const auth = await verifyAgent(
      request.headers.get('x-agent-address'),
      request.headers.get('x-agent-signature'),
      request.headers.get('x-agent-timestamp')
    )

    if (!auth.success || !auth.agent) {
      return NextResponse.json(
        { success: false, error: auth.error },
        { status: 401 }
      )
    }

    // Delete all vectors from Qdrant
    await deleteAgentVectors(auth.agent.id)

    // Delete all memories from Postgres
    await prisma.memory.deleteMany({
      where: { agentId: auth.agent.id },
    })

    // Reset agent stats
    await prisma.agent.update({
      where: { id: auth.agent.id },
      data: { memoriesStored: 0 },
    })

    // Log usage
    await prisma.usageLog.create({
      data: {
        agentId: auth.agent.id,
        action: 'clear_vault',
        cost: 0,
      },
    })

    return NextResponse.json({
      success: true,
      usage: {
        memoriesStored: 0,
        recallsToday: auth.agent.recallsToday,
        tier: auth.agent.tier,
      },
    })
  } catch (error) {
    console.error('Clear vault error:', error instanceof Error ? error.message : 'Unknown error')
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
