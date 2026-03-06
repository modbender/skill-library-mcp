import { NextRequest, NextResponse } from 'next/server'
import { authenticate } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { deleteVector } from '@/lib/qdrant'
import type { ApiResponse, MemoryResponse, MemoryType } from '@/types'

// GET single memory
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse<ApiResponse<MemoryResponse>>> {
  try {
    const { id } = await params

    // Authenticate (supports both JWT and legacy auth)
    const auth = await authenticate(request)

    if (!auth.success || !auth.agent) {
      return NextResponse.json(
        { success: false, error: auth.error },
        { status: 401 }
      )
    }

    // Fetch memory
    const memory = await prisma.memory.findFirst({
      where: {
        id,
        agentId: auth.agent.id,
      },
    })

    if (!memory) {
      return NextResponse.json(
        { success: false, error: 'Memory not found' },
        { status: 404 }
      )
    }

    return NextResponse.json({
      success: true,
      data: {
        id: memory.id,
        content: memory.content,
        type: memory.type as MemoryType,
        tags: memory.tags,
        createdAt: memory.createdAt.toISOString(),
      },
    })
  } catch (error) {
    console.error('Get memory error:', error instanceof Error ? error.message : 'Unknown error')
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// DELETE memory
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse<ApiResponse>> {
  try {
    const { id } = await params

    // Authenticate (supports both JWT and legacy auth)
    const auth = await authenticate(request)

    if (!auth.success || !auth.agent) {
      return NextResponse.json(
        { success: false, error: auth.error },
        { status: 401 }
      )
    }

    // Fetch memory to get vectorId
    const memory = await prisma.memory.findFirst({
      where: {
        id,
        agentId: auth.agent.id,
      },
    })

    if (!memory) {
      return NextResponse.json(
        { success: false, error: 'Memory not found' },
        { status: 404 }
      )
    }

    // Delete from Qdrant
    await deleteVector(memory.vectorId)

    // Delete from Postgres
    await prisma.memory.delete({
      where: { id },
    })

    // Update agent stats
    await prisma.agent.update({
      where: { id: auth.agent.id },
      data: { memoriesStored: { decrement: 1 } },
    })

    // Log usage
    await prisma.usageLog.create({
      data: {
        agentId: auth.agent.id,
        action: 'delete',
        cost: 0,
      },
    })

    return NextResponse.json({
      success: true,
      usage: {
        memoriesStored: auth.agent.memoriesStored - 1,
        recallsToday: auth.agent.recallsToday,
        tier: auth.agent.tier,
      },
    })
  } catch (error) {
    console.error('Delete memory error:', error instanceof Error ? error.message : 'Unknown error')
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
