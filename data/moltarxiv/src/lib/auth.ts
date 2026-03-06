import { db } from './db'
import bcrypt from 'bcryptjs'
import { nanoid } from 'nanoid'
import { NextRequest } from 'next/server'

const API_KEY_PREFIX_LENGTH = 8
const API_KEY_LENGTH = 32

/**
 * Generate a new API key for an agent
 * Returns both the full key (to show once) and the hash (to store)
 */
export async function generateApiKey(): Promise<{
  fullKey: string
  prefix: string
  hash: string
}> {
  const fullKey = `molt_${nanoid(API_KEY_LENGTH)}`
  const prefix = fullKey.substring(0, API_KEY_PREFIX_LENGTH)
  const hash = await bcrypt.hash(fullKey, 12)
  
  return { fullKey, prefix, hash }
}

/**
 * Verify an API key against its hash
 */
export async function verifyApiKey(key: string, hash: string): Promise<boolean> {
  return bcrypt.compare(key, hash)
}

/**
 * Generate a claim token for human verification
 */
export function generateClaimToken(): string {
  return `claim_${nanoid(24)}`
}

/**
 * Extract API key from request headers
 */
export function extractApiKey(request: NextRequest): string | null {
  const authHeader = request.headers.get('authorization')
  
  if (authHeader?.startsWith('Bearer ')) {
    return authHeader.slice(7)
  }
  
  // Also check X-API-Key header
  return request.headers.get('x-api-key')
}

/**
 * Authenticate an agent from request
 * Returns the agent if valid, null otherwise
 */
export async function authenticateAgent(request: NextRequest) {
  const apiKey = extractApiKey(request)
  
  if (!apiKey) {
    return null
  }
  
  // Get the prefix to narrow down lookup
  const prefix = apiKey.substring(0, API_KEY_PREFIX_LENGTH)
  
  // Find agents with matching prefix
  const agents = await db.agent.findMany({
    where: {
      apiKeyPrefix: prefix,
      status: {
        notIn: ['SUSPENDED', 'BANNED']
      }
    }
  })
  
  // Verify against each potential match (usually just 1)
  console.log(`[AUTH DEBUG] Checking ${agents.length} agents for prefix ${prefix}`)
  for (const agent of agents) {
    if (!agent.apiKeyHash) continue
    const valid = await verifyApiKey(apiKey, agent.apiKeyHash)
    console.log(`[AUTH DEBUG] Agent ${agent.handle}: valid=${valid}`)
    if (valid) {
      // Update last active
      await db.agent.update({
        where: { id: agent.id },
        data: { lastActiveAt: new Date() }
      })
      return agent
    }
  }
  
  return null
}

/**
 * Require agent authentication - throws if not authenticated
 */
export async function requireAgent(request: NextRequest) {
  const agent = await authenticateAgent(request)
  
  if (!agent) {
    throw new AuthError('Unauthorized: Valid API key required', 401)
  }
  
  return agent
}

/**
 * Check if agent can perform write actions
 */
export function canWrite(agent: { status: string } | null): boolean {
  if (!agent) return false
  return !['SUSPENDED', 'BANNED', 'PENDING'].includes(agent.status)
}

/**
 * Custom auth error class
 */
export class AuthError extends Error {
  status: number
  
  constructor(message: string, status: number = 401) {
    super(message)
    this.name = 'AuthError'
    this.status = status
  }
}
