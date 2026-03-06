import { NextRequest, NextResponse } from 'next/server'
import { authenticate, TIER_LIMITS } from '@/lib/auth'
import type { ApiResponse } from '@/types'

interface AgentStats {
  address: string
  tier: string
  memoriesStored: number
  recallsToday: number
  limits: {
    maxMemories: number
    maxRecallsPerDay: number
  }
}

export async function GET(request: NextRequest): Promise<NextResponse<ApiResponse<AgentStats>>> {
  try {
    // Authenticate (supports both JWT and legacy auth)
    const auth = await authenticate(request)

    if (!auth.success || !auth.agent) {
      return NextResponse.json(
        { success: false, error: auth.error },
        { status: 401 }
      )
    }

    const limits = TIER_LIMITS[auth.agent.tier as keyof typeof TIER_LIMITS] || TIER_LIMITS.free

    return NextResponse.json({
      success: true,
      data: {
        address: auth.agent.address,
        tier: auth.agent.tier,
        memoriesStored: auth.agent.memoriesStored,
        recallsToday: auth.agent.recallsToday,
        limits: {
          maxMemories: limits.maxMemories,
          maxRecallsPerDay: limits.maxRecallsPerDay === Infinity ? -1 : limits.maxRecallsPerDay,
        },
      },
    })
  } catch (error) {
    console.error('Agent stats error:', error instanceof Error ? error.message : 'Unknown error')
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
