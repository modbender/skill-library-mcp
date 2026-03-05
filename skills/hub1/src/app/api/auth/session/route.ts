import { NextRequest, NextResponse } from 'next/server'
import { verifyMessage } from 'viem'
import { SignJWT, jwtVerify } from 'jose'
import { prisma } from '@/lib/prisma'

const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || 'openclawdy-secret-key-change-in-production'
)
const SESSION_DURATION = 24 * 60 * 60 // 24 hours in seconds

// POST - Create new session (login)
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { address, signature, timestamp } = body

    if (!address || !signature || !timestamp) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields' },
        { status: 400 }
      )
    }

    // Validate timestamp (allow 5 minutes for initial sign)
    const ts = parseInt(timestamp, 10)
    const now = Date.now()
    if (isNaN(ts) || now - ts > 5 * 60 * 1000) {
      return NextResponse.json(
        { success: false, error: 'Timestamp expired. Please try again.' },
        { status: 401 }
      )
    }

    // Verify signature
    const message = `OpenClawdy Auth\nTimestamp: ${timestamp}`

    try {
      const isValid = await verifyMessage({
        address: address as `0x${string}`,
        message,
        signature: signature as `0x${string}`,
      })

      if (!isValid) {
        return NextResponse.json(
          { success: false, error: 'Invalid signature' },
          { status: 401 }
        )
      }
    } catch {
      return NextResponse.json(
        { success: false, error: 'Signature verification failed' },
        { status: 401 }
      )
    }

    // Get or create agent
    const normalizedAddress = address.toLowerCase()
    let agent = await prisma.agent.findUnique({
      where: { address: normalizedAddress },
    })

    if (!agent) {
      agent = await prisma.agent.create({
        data: { address: normalizedAddress },
      })
    }

    // Reset daily recall counter if needed
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    if (agent.recallsResetAt < today) {
      agent = await prisma.agent.update({
        where: { id: agent.id },
        data: {
          recallsToday: 0,
          recallsResetAt: today,
        },
      })
    }

    // Create JWT
    const token = await new SignJWT({
      agentId: agent.id,
      address: normalizedAddress,
    })
      .setProtectedHeader({ alg: 'HS256' })
      .setIssuedAt()
      .setExpirationTime(`${SESSION_DURATION}s`)
      .sign(JWT_SECRET)

    return NextResponse.json({
      success: true,
      data: {
        token,
        expiresAt: Date.now() + SESSION_DURATION * 1000,
        agent: {
          id: agent.id,
          address: agent.address,
          tier: agent.tier,
          memoriesStored: agent.memoriesStored,
          recallsToday: agent.recallsToday,
        },
      },
    })
  } catch (error) {
    console.error('Session creation error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// GET - Validate session and get agent info
export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization')
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json(
        { success: false, error: 'Missing authorization header' },
        { status: 401 }
      )
    }

    const token = authHeader.slice(7)

    try {
      const { payload } = await jwtVerify(token, JWT_SECRET)
      const agentId = payload.agentId as string

      const agent = await prisma.agent.findUnique({
        where: { id: agentId },
      })

      if (!agent) {
        return NextResponse.json(
          { success: false, error: 'Agent not found' },
          { status: 404 }
        )
      }

      return NextResponse.json({
        success: true,
        data: {
          id: agent.id,
          address: agent.address,
          tier: agent.tier,
          memoriesStored: agent.memoriesStored,
          recallsToday: agent.recallsToday,
        },
      })
    } catch {
      return NextResponse.json(
        { success: false, error: 'Invalid or expired session' },
        { status: 401 }
      )
    }
  } catch (error) {
    console.error('Session validation error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
