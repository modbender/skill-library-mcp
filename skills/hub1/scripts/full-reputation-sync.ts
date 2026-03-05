/**
 * Full Reputation Sync Pipeline
 *
 * 1. Sync ACP agents from marketplace
 * 2. Index USDC transfers between agents on Base
 * 3. Calculate and update trust scores
 *
 * Prerequisites:
 *   ACP CLI must be set up: cd /Users/apple/virtuals-protocol-acp && npx tsx bin/acp.ts setup
 *
 * Usage:
 *   npx tsx scripts/full-reputation-sync.ts
 *   npx tsx scripts/full-reputation-sync.ts --skip-agents   # Skip agent sync, just index
 *   npx tsx scripts/full-reputation-sync.ts --agents-only   # Only sync agents, no indexing
 */

import { execSync } from 'child_process'
import { PrismaClient } from '@prisma/client'
import { createPublicClient, http, parseAbiItem, formatUnits } from 'viem'
import { base } from 'viem/chains'

const prisma = new PrismaClient()

// Config
const ACP_CLI_PATH = '/Users/apple/virtuals-protocol-acp'
const USDC_ADDRESS = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
const BLOCKS_TO_INDEX = BigInt(50000) // ~7 hours of blocks

// Search queries for discovering agents
const SEARCH_QUERIES = [
  'trading', 'swap', 'defi', 'analysis', 'research',
  'data', 'market', 'price', 'agent', 'ai',
]

// Viem client
const client = createPublicClient({
  chain: base,
  transport: http('https://mainnet.base.org'),
})

const TRANSFER_EVENT = parseAbiItem(
  'event Transfer(address indexed from, address indexed to, uint256 value)'
)

// ============================================================================
// STEP 1: Sync ACP Agents
// ============================================================================

interface AcpAgent {
  name: string
  walletAddress: string
  description?: string
  jobOfferings?: Array<{ name: string; description?: string }>
}

function runAcpCommand(command: string): any {
  try {
    const result = execSync(`cd ${ACP_CLI_PATH} && npx tsx bin/acp.ts ${command} --json`, {
      encoding: 'utf-8',
      timeout: 30000,
      stdio: ['pipe', 'pipe', 'pipe'],
    })
    return JSON.parse(result.trim())
  } catch {
    return null
  }
}

async function syncAcpAgents(): Promise<number> {
  console.log('\n📡 Step 1: Syncing ACP Agents...\n')

  const agentMap = new Map<string, AcpAgent>()

  for (const query of SEARCH_QUERIES) {
    process.stdout.write(`  Searching "${query}"... `)
    const agents = runAcpCommand(`browse "${query}"`)

    if (agents && Array.isArray(agents)) {
      let added = 0
      for (const agent of agents) {
        if (agent.walletAddress && !agentMap.has(agent.walletAddress.toLowerCase())) {
          agentMap.set(agent.walletAddress.toLowerCase(), agent)
          added++
        }
      }
      console.log(`found ${agents.length}, ${added} new`)
    } else {
      console.log('no results')
    }

    await new Promise((r) => setTimeout(r, 300))
  }

  console.log(`\n  Total unique agents found: ${agentMap.size}`)

  // Seed to database
  let newCount = 0
  for (const agent of agentMap.values()) {
    const address = agent.walletAddress.toLowerCase()
    const services = agent.jobOfferings?.map((o) => o.name) || []

    const existing = await prisma.reputationAgent.findUnique({ where: { address } })

    if (!existing) {
      await prisma.reputationAgent.create({
        data: {
          address,
          name: agent.name || null,
          description: agent.description || null,
          services,
          trustScore: 50,
        },
      })
      newCount++
    } else {
      await prisma.reputationAgent.update({
        where: { address },
        data: {
          name: agent.name || existing.name,
          description: agent.description || existing.description,
          services: services.length > 0 ? services : existing.services,
        },
      })
    }
  }

  console.log(`  New agents added: ${newCount}`)
  return agentMap.size
}

// ============================================================================
// STEP 2: Index USDC Transfers
// ============================================================================

async function indexTransfers(): Promise<number> {
  console.log('\n⛓️  Step 2: Indexing USDC Transfers on Base...\n')

  // Get known agent addresses
  const agents = await prisma.reputationAgent.findMany({ select: { address: true } })
  const knownAddresses = new Set(agents.map((a) => a.address.toLowerCase()))

  if (knownAddresses.size === 0) {
    console.log('  No agents in database. Skipping indexing.')
    return 0
  }

  console.log(`  Tracking ${knownAddresses.size} agent wallets`)

  // Get block range
  const currentBlock = await client.getBlockNumber()
  const fromBlock = currentBlock - BLOCKS_TO_INDEX
  console.log(`  Scanning blocks ${fromBlock} to ${currentBlock}`)

  // Get transfer events
  const logs = await client.getLogs({
    address: USDC_ADDRESS,
    event: TRANSFER_EVENT,
    fromBlock,
    toBlock: currentBlock,
  })

  console.log(`  Found ${logs.length} USDC transfers`)

  let indexed = 0
  for (const log of logs) {
    const from = (log.args.from as string).toLowerCase()
    const to = (log.args.to as string).toLowerCase()
    const value = log.args.value as bigint

    // Only track transfers between known agents
    if (!knownAddresses.has(from) || !knownAddresses.has(to)) continue

    const amount = parseFloat(formatUnits(value, 6))
    if (amount < 0.01) continue // Skip dust

    const txId = `${log.transactionHash}-${log.logIndex}`

    // Check if already indexed
    const existing = await prisma.reputationTransaction.findFirst({
      where: { acpTransactionId: txId },
    })
    if (existing) continue

    // Get agents
    const buyer = await prisma.reputationAgent.findUnique({ where: { address: from } })
    const seller = await prisma.reputationAgent.findUnique({ where: { address: to } })
    if (!buyer || !seller) continue

    // Get block timestamp
    const block = await client.getBlock({ blockNumber: log.blockNumber })
    const timestamp = new Date(Number(block.timestamp) * 1000)

    // Create transaction
    await prisma.reputationTransaction.create({
      data: {
        buyerId: buyer.id,
        sellerId: seller.id,
        serviceType: 'acp_payment',
        amount,
        acpTransactionId: txId,
        status: 'completed',
        completedAt: timestamp,
        createdAt: timestamp,
      },
    })

    // Update seller stats
    await prisma.reputationAgent.update({
      where: { id: seller.id },
      data: {
        totalTransactions: { increment: 1 },
        successfulTx: { increment: 1 },
      },
    })

    indexed++
    if (indexed % 10 === 0) {
      process.stdout.write(`  Indexed ${indexed} transactions...\r`)
    }
  }

  console.log(`  Indexed ${indexed} agent-to-agent transactions`)
  return indexed
}

// ============================================================================
// STEP 3: Calculate Trust Scores
// ============================================================================

async function calculateScores(): Promise<void> {
  console.log('\n🧮 Step 3: Calculating Trust Scores...\n')

  const agents = await prisma.reputationAgent.findMany({
    where: { totalTransactions: { gt: 0 } },
  })

  for (const agent of agents) {
    // Reliability
    const reliabilityRate = agent.successfulTx / agent.totalTransactions
    const reliabilityScore = agent.totalTransactions >= 5 ? reliabilityRate * 100 : 50

    // Volume (log scale)
    const volumeScore = Math.min(100, Math.log10(agent.totalTransactions + 1) * 33)

    // Disputes
    const disputeRate = agent.disputeCount / agent.totalTransactions
    const disputeScore = Math.max(0, 100 - disputeRate * 500)

    // Ratings
    const ratingsScore = agent.totalRatings >= 3 ? ((agent.avgRating - 1) / 4) * 100 : 50

    // Recency - check last 30 days
    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
    const recentTxCount = await prisma.reputationTransaction.count({
      where: {
        sellerId: agent.id,
        createdAt: { gte: thirtyDaysAgo },
      },
    })
    const recencyScore = Math.min(100, recentTxCount * 10)

    // Weighted total
    const trustScore = Math.round(
      reliabilityScore * 0.35 +
        volumeScore * 0.2 +
        recencyScore * 0.15 +
        ratingsScore * 0.2 +
        disputeScore * 0.1
    )

    // Update
    await prisma.reputationAgent.update({
      where: { id: agent.id },
      data: {
        reliabilityRate,
        trustScore: Math.min(100, Math.max(0, trustScore)),
      },
    })
  }

  console.log(`  Updated scores for ${agents.length} agents`)
}

// ============================================================================
// MAIN
// ============================================================================

async function main() {
  const args = process.argv.slice(2)
  const skipAgents = args.includes('--skip-agents')
  const agentsOnly = args.includes('--agents-only')

  console.log('\n' + '='.repeat(60))
  console.log('🔄 FULL REPUTATION SYNC PIPELINE')
  console.log('='.repeat(60))

  try {
    // Step 1: Sync agents
    if (!skipAgents) {
      await syncAcpAgents()
    }

    // Step 2: Index transfers
    if (!agentsOnly) {
      await indexTransfers()
    }

    // Step 3: Calculate scores
    if (!agentsOnly) {
      await calculateScores()
    }

    // Final stats
    const [agentCount, txCount] = await Promise.all([
      prisma.reputationAgent.count(),
      prisma.reputationTransaction.count(),
    ])

    console.log('\n' + '='.repeat(60))
    console.log('✅ SYNC COMPLETE')
    console.log('='.repeat(60))
    console.log(`\n  Total Agents:       ${agentCount}`)
    console.log(`  Total Transactions: ${txCount}`)
    console.log('')
  } catch (error) {
    console.error('\n❌ Sync failed:', error)
    process.exit(1)
  }
}

main().finally(() => prisma.$disconnect())
