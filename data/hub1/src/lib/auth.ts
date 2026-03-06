import { verifyMessage } from 'viem'
import { jwtVerify } from 'jose'
import { prisma } from './prisma'

const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || 'openclawdy-secret-key-change-in-production'
)

// Legacy constants (for backward compatibility)
const AUTH_MESSAGE_PREFIX = 'OpenClawdy Auth\nTimestamp: '
const MAX_TIMESTAMP_AGE = 5 * 60 * 1000 // 5 minutes

export interface AuthResult {
  success: boolean
  agent?: {
    id: string
    address: string
    tier: string
    memoriesStored: number
    recallsToday: number
  }
  error?: string
}

// New JWT-based auth (preferred)
export async function verifySession(authHeader: string | null): Promise<AuthResult> {
  if (!authHeader?.startsWith('Bearer ')) {
    return { success: false, error: 'Missing or invalid authorization header' }
  }

  const token = authHeader.slice(7)

  try {
    const { payload } = await jwtVerify(token, JWT_SECRET)
    const agentId = payload.agentId as string

    const agent = await prisma.agent.findUnique({
      where: { id: agentId },
    })

    if (!agent) {
      return { success: false, error: 'Agent not found' }
    }

    // Reset daily recall counter if needed
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    let updatedAgent = agent
    if (agent.recallsResetAt < today) {
      updatedAgent = await prisma.agent.update({
        where: { id: agent.id },
        data: {
          recallsToday: 0,
          recallsResetAt: today,
        },
      })
    }

    return {
      success: true,
      agent: {
        id: updatedAgent.id,
        address: updatedAgent.address,
        tier: updatedAgent.tier,
        memoriesStored: updatedAgent.memoriesStored,
        recallsToday: updatedAgent.recallsToday,
      },
    }
  } catch {
    return { success: false, error: 'Invalid or expired session' }
  }
}

// Legacy signature-based auth (for backward compatibility with external agents)
export async function verifyAgent(
  address: string | null,
  signature: string | null,
  timestamp: string | null
): Promise<AuthResult> {
  if (!address || !signature || !timestamp) {
    return { success: false, error: 'Missing authentication headers' }
  }

  // Validate timestamp
  const ts = parseInt(timestamp, 10)
  if (isNaN(ts)) {
    return { success: false, error: 'Invalid timestamp' }
  }

  const now = Date.now()
  if (now - ts > MAX_TIMESTAMP_AGE) {
    return { success: false, error: 'Timestamp expired' }
  }

  // Verify signature
  const message = `${AUTH_MESSAGE_PREFIX}${timestamp}`

  try {
    const isValid = await verifyMessage({
      address: address as `0x${string}`,
      message,
      signature: signature as `0x${string}`,
    })

    if (!isValid) {
      return { success: false, error: 'Invalid signature' }
    }
  } catch {
    return { success: false, error: 'Signature verification failed' }
  }

  // Get or create agent
  let agent = await prisma.agent.findUnique({
    where: { address: address.toLowerCase() },
  })

  if (!agent) {
    agent = await prisma.agent.create({
      data: { address: address.toLowerCase() },
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

  return {
    success: true,
    agent: {
      id: agent.id,
      address: agent.address,
      tier: agent.tier,
      memoriesStored: agent.memoriesStored,
      recallsToday: agent.recallsToday,
    },
  }
}

// Combined auth - tries JWT first, falls back to legacy
export async function authenticate(request: Request): Promise<AuthResult> {
  // Try JWT auth first (preferred)
  const authHeader = request.headers.get('Authorization')
  if (authHeader?.startsWith('Bearer ')) {
    return verifySession(authHeader)
  }

  // Fall back to legacy signature auth
  return verifyAgent(
    request.headers.get('x-agent-address'),
    request.headers.get('x-agent-signature'),
    request.headers.get('x-agent-timestamp')
  )
}

// Tier limits
export const TIER_LIMITS = {
  free: {
    maxMemories: 1000,
    maxRecallsPerDay: 100,
  },
  pro: {
    maxMemories: 50000,
    maxRecallsPerDay: Infinity,
  },
  enterprise: {
    maxMemories: Infinity,
    maxRecallsPerDay: Infinity,
  },
}

export function checkMemoryLimit(tier: string, currentCount: number): boolean {
  const limits = TIER_LIMITS[tier as keyof typeof TIER_LIMITS] || TIER_LIMITS.free
  return currentCount < limits.maxMemories
}

export function checkRecallLimit(tier: string, currentCount: number): boolean {
  const limits = TIER_LIMITS[tier as keyof typeof TIER_LIMITS] || TIER_LIMITS.free
  return currentCount < limits.maxRecallsPerDay
}
