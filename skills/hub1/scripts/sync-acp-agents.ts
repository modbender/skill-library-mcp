/**
 * Sync ACP Agents to Reputation Database
 *
 * Uses the ACP CLI to browse agents and seeds them into our reputation database.
 *
 * Prerequisites:
 * 1. ACP CLI must be set up: cd /Users/apple/virtuals-protocol-acp && npx tsx bin/acp.ts setup
 * 2. Must have valid session token
 *
 * Usage:
 *   npx tsx scripts/sync-acp-agents.ts [search_queries...]
 *
 * Examples:
 *   npx tsx scripts/sync-acp-agents.ts                    # Search common terms
 *   npx tsx scripts/sync-acp-agents.ts trading analysis   # Search specific terms
 */

import { execSync } from 'child_process'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

const ACP_CLI_PATH = '/Users/apple/virtuals-protocol-acp'

// Default search queries to discover agents
const DEFAULT_QUERIES = [
  'trading',
  'analysis',
  'data',
  'research',
  'swap',
  'defi',
  'nft',
  'social',
  'content',
  'agent',
  'ai',
  'assistant',
  'market',
  'price',
  'token',
]

interface AcpOffering {
  name: string
  description?: string
  price: number
  priceType: string
  requiredFunds?: boolean
}

interface AcpResource {
  name: string
  description?: string
  url?: string
}

interface AcpAgent {
  id: string
  name: string
  walletAddress: string
  description?: string
  jobOfferings?: AcpOffering[]
  resources?: AcpResource[]
}

/**
 * Run ACP CLI command and return JSON output
 */
function runAcpCommand(command: string): any {
  try {
    const result = execSync(`cd ${ACP_CLI_PATH} && npx tsx bin/acp.ts ${command} --json`, {
      encoding: 'utf-8',
      timeout: 30000,
      stdio: ['pipe', 'pipe', 'pipe'],
    })

    // Parse JSON output
    return JSON.parse(result.trim())
  } catch (error: any) {
    if (error.stderr?.includes('LITE_AGENT_API_KEY')) {
      console.error('\n❌ ACP CLI not set up. Run:')
      console.error(`   cd ${ACP_CLI_PATH} && npx tsx bin/acp.ts setup\n`)
      process.exit(1)
    }
    if (error.stderr?.includes('Session expired')) {
      console.error('\n❌ ACP session expired. Run:')
      console.error(`   cd ${ACP_CLI_PATH} && npx tsx bin/acp.ts login\n`)
      process.exit(1)
    }
    // Return null for other errors (e.g., no results)
    return null
  }
}

/**
 * Browse ACP agents with a search query
 */
function browseAgents(query: string): AcpAgent[] {
  console.log(`  Searching: "${query}"...`)

  const result = runAcpCommand(`browse "${query}"`)

  if (!result || !Array.isArray(result)) {
    return []
  }

  return result
}

/**
 * Seed an agent into the reputation database
 */
async function seedAgent(agent: AcpAgent): Promise<boolean> {
  if (!agent.walletAddress) {
    return false
  }

  const address = agent.walletAddress.toLowerCase()

  // Check if already exists
  const existing = await prisma.reputationAgent.findUnique({
    where: { address },
  })

  const services = agent.jobOfferings?.map((o) => o.name) || []
  const description = agent.description || agent.jobOfferings?.[0]?.description || null

  if (existing) {
    // Update with any new info
    await prisma.reputationAgent.update({
      where: { address },
      data: {
        name: agent.name || existing.name,
        description: description || existing.description,
        services: services.length > 0 ? services : existing.services,
      },
    })
    return false // Not new
  }

  // Create new agent
  await prisma.reputationAgent.create({
    data: {
      address,
      name: agent.name || null,
      description,
      services,
      categories: [],
      trustScore: 50, // Start neutral
    },
  })

  return true // New agent
}

/**
 * Main sync function
 */
async function syncAgents(queries: string[]) {
  console.log('\n🔍 Syncing ACP Agents to Reputation Database\n')
  console.log('=' .repeat(50))

  // Collect all unique agents
  const agentMap = new Map<string, AcpAgent>()

  for (const query of queries) {
    const agents = browseAgents(query)

    for (const agent of agents) {
      if (agent.walletAddress && !agentMap.has(agent.walletAddress.toLowerCase())) {
        agentMap.set(agent.walletAddress.toLowerCase(), agent)
      }
    }

    // Small delay to avoid rate limiting
    await new Promise((r) => setTimeout(r, 500))
  }

  console.log('\n' + '=' .repeat(50))
  console.log(`\n📊 Found ${agentMap.size} unique agents\n`)

  // Seed agents
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

  console.log('\n' + '=' .repeat(50))
  console.log('\n📈 Sync Complete!\n')
  console.log(`  New agents:     ${newCount}`)
  console.log(`  Updated:        ${updatedCount}`)
  console.log(`  Total in DB:    ${totalAgents}`)
  console.log('')
}

// Main
const args = process.argv.slice(2)
const queries = args.length > 0 ? args : DEFAULT_QUERIES

syncAgents(queries)
  .catch((error) => {
    console.error('Sync failed:', error)
    process.exit(1)
  })
  .finally(() => prisma.$disconnect())
