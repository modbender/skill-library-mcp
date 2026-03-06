import { NextRequest } from 'next/server'
import { authenticateAgent, extractApiKey } from '@/lib/auth'
import { db } from '@/lib/db'
import { success, handleError, notFound, forbidden } from '@/lib/api-response'

/**
 * GET /api/v1/agents/me
 * Get current authenticated agent's profile
 */
export async function GET(request: NextRequest) {
  try {
    const agent = await authenticateAgent(request)
    
    if (!agent) {
      // DIAGNOSTIC BLOCK
      const key = extractApiKey(request)
      if (key) {
        const prefix = key.substring(0, 8)
        const count = await db.agent.count({
          where: { apiKeyPrefix: prefix }
        })
        return forbidden(`Authentication failed. Debug info: Prefix '${prefix}' found ${count} records.`)
      }
      return forbidden('Authentication required')
    }
    
    return success({
      ...agent,
      isClaimed: !!agent.claimedAt,
    })
    
  } catch (err) {
    return handleError(err)
  }
}
