import { NextRequest, NextResponse } from 'next/server'
import { authenticate } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import type { ApiResponse, MemoryResponse, MemoryType } from '@/types'

export async function GET(request: NextRequest): Promise<NextResponse<ApiResponse<MemoryResponse[]>>> {
  try {
    // Authenticate (supports both JWT and legacy auth)
    const auth = await authenticate(request)

    if (!auth.success || !auth.agent) {
      return NextResponse.json(
        { success: false, error: auth.error },
        { status: 401 }
      )
    }

    // Parse query params
    const { searchParams } = new URL(request.url)
    const type = searchParams.get('type') as MemoryType | null
    const limit = Math.min(parseInt(searchParams.get('limit') || '20', 10), 100)
    const offset = parseInt(searchParams.get('offset') || '0', 10)

    // Build query
    const where: { agentId: string; type?: string } = { agentId: auth.agent.id }
    if (type) {
      where.type = type
    }

    // Fetch memories
    const memories = await prisma.memory.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: limit,
      skip: offset,
    })

    const response: MemoryResponse[] = memories.map((m) => ({
      id: m.id,
      content: m.content,
      type: m.type as MemoryType,
      tags: m.tags,
      createdAt: m.createdAt.toISOString(),
    }))

    return NextResponse.json({
      success: true,
      data: response,
      usage: {
        memoriesStored: auth.agent.memoriesStored,
        recallsToday: auth.agent.recallsToday,
        tier: auth.agent.tier,
      },
    })
  } catch (error) {
    console.error('List memories error:', error instanceof Error ? error.message : 'Unknown error')
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
