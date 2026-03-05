/**
 * Sync ALL ACP Agents to Reputation Database
 *
 * Queries the ACP API with every letter, number, and common terms
 * to discover as many agents as possible.
 *
 * Usage: npx tsx scripts/sync-all-acp-agents.ts
 */

import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

const ACP_API = 'https://claw-api.virtuals.io'
const API_KEY = 'acp-4e0e4e39028eda8e44a2'

// All letters A-Z
const LETTERS = 'abcdefghijklmnopqrstuvwxyz'.split('')

// Numbers
const NUMBERS = '0123456789'.split('')

// Common terms that might match agents
const COMMON_TERMS = [
  'agent', 'ai', 'bot', 'trading', 'swap', 'defi', 'nft', 'market',
  'price', 'data', 'analysis', 'research', 'token', 'crypto', 'wallet',
  'social', 'content', 'news', 'alpha', 'whale', 'degen', 'meme',
  'yield', 'farm', 'stake', 'bridge', 'oracle', 'index', 'fund',
  'hedge', 'arbitrage', 'sniper', 'copy', 'signal', 'alert', 'track',
  'monitor', 'scan', 'audit', 'security', 'risk', 'portfolio', 'manage',
  'assistant', 'helper', 'butler', 'luna', 'nova', 'max', 'pro',
  'smart', 'auto', 'fast', 'super', 'mega', 'ultra', 'hyper',
  'the', 'my', 'your', 'our', 'best', 'top', 'new', 'old',
]

interface AcpAgent {
  id: string
  name: string
  walletAddress: string
  description?: string
  jobOfferings?: Array<{ name: string; description?: string }>
  resources?: Array<{ name: string; description?: string }>
}

interface AcpResponse {
  data: AcpAgent[]
}

async function fetchAgents(query: string): Promise<AcpAgent[]> {
  try {
    const response = await fetch(
      `${ACP_API}/acp/agents?query=${encodeURIComponent(query)}`,
      {
        headers: {
          'x-api-key': API_KEY,
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      return []
    }

    const data: AcpResponse = await response.json()
    return data.data || []
  } catch {
    return []
  }
}

async function seedAgent(agent: AcpAgent): Promise<boolean> {
  if (!agent.walletAddress) return false

  const address = agent.walletAddress.toLowerCase()
  const services = agent.jobOfferings?.map((o) => o.name) || []
  const description =
    agent.description || agent.jobOfferings?.[0]?.description || null

  const existing = await prisma.reputationAgent.findUnique({
    where: { address },
  })

  if (existing) {
    await prisma.reputationAgent.update({
      where: { address },
      data: {
        name: agent.name || existing.name,
        description: description || existing.description,
        services: services.length > 0 ? services : existing.services,
      },
    })
    return false
  }

  await prisma.reputationAgent.create({
    data: {
      address,
      name: agent.name || null,
      description,
      services,
      categories: [],
      trustScore: 50,
    },
  })

  return true
}

async function main() {
  console.log('\n' + '='.repeat(60))
  console.log('🔍 SYNCING ALL ACP AGENTS')
  console.log('='.repeat(60) + '\n')

  const agentMap = new Map<string, AcpAgent>()
  const allQueries = [...LETTERS, ...NUMBERS, ...COMMON_TERMS]

  console.log(`Running ${allQueries.length} queries...\n`)

  let queryCount = 0
  for (const query of allQueries) {
    queryCount++
    process.stdout.write(
      `  [${queryCount}/${allQueries.length}] "${query}" ... `
    )

    const agents = await fetchAgents(query)
    let newFound = 0

    for (const agent of agents) {
      if (
        agent.walletAddress &&
        !agentMap.has(agent.walletAddress.toLowerCase())
      ) {
        agentMap.set(agent.walletAddress.toLowerCase(), agent)
        newFound++
      }
    }

    console.log(`${agents.length} results, ${newFound} new (total: ${agentMap.size})`)

    // Small delay to avoid rate limiting
    await new Promise((r) => setTimeout(r, 200))
  }

  console.log('\n' + '='.repeat(60))
  console.log(`\n📊 Found ${agentMap.size} unique agents\n`)

  // Seed to database
  let newCount = 0
  let updatedCount = 0

  for (const agent of agentMap.values()) {
    const isNew = await seedAgent(agent)
    if (isNew) {
      console.log(`  ✅ NEW: ${agent.name || 'Unknown'} (${agent.walletAddress.slice(0, 10)}...)`)
      newCount++
    } else {
      updatedCount++
    }
  }

  // Final stats
  const totalAgents = await prisma.reputationAgent.count()

  console.log('\n' + '='.repeat(60))
  console.log('\n📈 SYNC COMPLETE\n')
  console.log(`  Queries run:    ${allQueries.length}`)
  console.log(`  Agents found:   ${agentMap.size}`)
  console.log(`  New agents:     ${newCount}`)
  console.log(`  Updated:        ${updatedCount}`)
  console.log(`  Total in DB:    ${totalAgents}`)
  console.log('')
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect())
