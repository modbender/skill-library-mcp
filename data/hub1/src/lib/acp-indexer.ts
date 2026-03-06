/**
 * ACP On-Chain Indexer
 *
 * Indexes USDC transfers between ACP agent wallets on Base
 * to build reputation data from actual transaction history.
 */

import { createPublicClient, http, parseAbiItem, formatUnits } from 'viem'
import { base } from 'viem/chains'
import { prisma } from './prisma'

// USDC on Base
const USDC_ADDRESS = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'

// ACP API
const ACP_API = 'https://claw-api.virtuals.io'

// Viem client for Base
const client = createPublicClient({
  chain: base,
  transport: http('https://mainnet.base.org'),
})

// USDC Transfer event signature
const TRANSFER_EVENT = parseAbiItem(
  'event Transfer(address indexed from, address indexed to, uint256 value)'
)

interface AcpAgent {
  id: string
  name: string
  walletAddress: string
  description?: string
  jobOfferings?: Array<{
    name: string
    description?: string
    price: number
    priceType: string
  }>
}

/**
 * Fetch all ACP agents from the API
 * Note: This requires an API key, so we'll need to handle auth
 */
export async function fetchAcpAgents(apiKey: string): Promise<AcpAgent[]> {
  try {
    // Search for all agents (empty query returns all)
    const response = await fetch(`${ACP_API}/acp/agents?query=`, {
      headers: {
        'x-api-key': apiKey,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`ACP API error: ${response.status}`)
    }

    const data = await response.json()
    return data.data || []
  } catch (error) {
    console.error('Failed to fetch ACP agents:', error)
    return []
  }
}

/**
 * Sync ACP agents to our reputation database
 */
export async function syncAcpAgents(agents: AcpAgent[]): Promise<number> {
  let synced = 0

  for (const agent of agents) {
    if (!agent.walletAddress) continue

    const address = agent.walletAddress.toLowerCase()

    // Upsert agent in reputation system
    await prisma.reputationAgent.upsert({
      where: { address },
      update: {
        name: agent.name || null,
        description: agent.description || null,
        services: agent.jobOfferings?.map(o => o.name) || [],
      },
      create: {
        address,
        name: agent.name || null,
        description: agent.description || null,
        services: agent.jobOfferings?.map(o => o.name) || [],
        trustScore: 50,
      },
    })

    synced++
  }

  return synced
}

/**
 * Get all known ACP agent addresses from our database
 */
export async function getKnownAgentAddresses(): Promise<Set<string>> {
  const agents = await prisma.reputationAgent.findMany({
    select: { address: true },
  })
  return new Set(agents.map(a => a.address.toLowerCase()))
}

/**
 * Index USDC transfers between ACP agents
 */
export async function indexUsdcTransfers(
  fromBlock: bigint,
  toBlock: bigint
): Promise<number> {
  const knownAgents = await getKnownAgentAddresses()

  if (knownAgents.size === 0) {
    console.log('No agents in database yet. Sync agents first.')
    return 0
  }

  console.log(`Indexing USDC transfers from block ${fromBlock} to ${toBlock}`)
  console.log(`Tracking ${knownAgents.size} known agent wallets`)

  // Get USDC Transfer events
  const logs = await client.getLogs({
    address: USDC_ADDRESS,
    event: TRANSFER_EVENT,
    fromBlock,
    toBlock,
  })

  let indexed = 0

  for (const log of logs) {
    const from = (log.args.from as string).toLowerCase()
    const to = (log.args.to as string).toLowerCase()
    const value = log.args.value as bigint

    // Check if both sender and receiver are known ACP agents
    if (knownAgents.has(from) && knownAgents.has(to)) {
      const amount = parseFloat(formatUnits(value, 6)) // USDC has 6 decimals

      // Skip dust amounts (likely not real transactions)
      if (amount < 0.01) continue

      // Get block timestamp
      const block = await client.getBlock({ blockNumber: log.blockNumber })
      const timestamp = new Date(Number(block.timestamp) * 1000)

      // Create unique transaction ID from tx hash + log index
      const txId = `${log.transactionHash}-${log.logIndex}`

      // Check if already indexed
      const existing = await prisma.reputationTransaction.findFirst({
        where: { acpTransactionId: txId },
      })

      if (existing) continue

      // Get or create agents
      const buyer = await prisma.reputationAgent.findUnique({
        where: { address: from },
      })
      const seller = await prisma.reputationAgent.findUnique({
        where: { address: to },
      })

      if (!buyer || !seller) continue

      // Create transaction record
      await prisma.reputationTransaction.create({
        data: {
          buyerId: buyer.id,
          sellerId: seller.id,
          serviceType: 'acp_payment', // Generic - we can't know the exact service
          amount,
          acpTransactionId: txId,
          status: 'completed', // If payment happened, job was likely completed
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
      console.log(
        `Indexed: ${from.slice(0, 8)}... -> ${to.slice(0, 8)}... : ${amount} USDC`
      )
    }
  }

  // Recalculate reliability rates
  const agents = await prisma.reputationAgent.findMany({
    where: { totalTransactions: { gt: 0 } },
  })

  for (const agent of agents) {
    const reliabilityRate =
      agent.totalTransactions > 0
        ? agent.successfulTx / agent.totalTransactions
        : 0

    await prisma.reputationAgent.update({
      where: { id: agent.id },
      data: { reliabilityRate },
    })
  }

  return indexed
}

/**
 * Get the latest indexed block
 */
export async function getLatestIndexedBlock(): Promise<bigint> {
  // Store this in a simple key-value or use the latest transaction
  const latest = await prisma.reputationTransaction.findFirst({
    where: { acpTransactionId: { startsWith: '0x' } },
    orderBy: { createdAt: 'desc' },
  })

  if (!latest?.acpTransactionId) {
    // Start from a reasonable block (about 30 days ago on Base)
    // Base produces ~2 blocks/second, so 30 days ≈ 5,184,000 blocks
    const currentBlock = await client.getBlockNumber()
    return currentBlock - BigInt(5184000)
  }

  // Extract block number from transaction hash (would need to query)
  // For now, just continue from a reasonable recent point
  const currentBlock = await client.getBlockNumber()
  return currentBlock - BigInt(100000) // Last ~14 hours
}

/**
 * Run the indexer
 */
export async function runIndexer(apiKey?: string): Promise<{
  agentsSynced: number
  transactionsIndexed: number
}> {
  let agentsSynced = 0
  let transactionsIndexed = 0

  // Step 1: Sync ACP agents if we have an API key
  if (apiKey) {
    console.log('Fetching ACP agents...')
    const agents = await fetchAcpAgents(apiKey)
    agentsSynced = await syncAcpAgents(agents)
    console.log(`Synced ${agentsSynced} agents`)
  }

  // Step 2: Index USDC transfers
  const fromBlock = await getLatestIndexedBlock()
  const toBlock = await client.getBlockNumber()

  // Index in chunks to avoid rate limits
  const CHUNK_SIZE = BigInt(10000)

  for (let start = fromBlock; start < toBlock; start += CHUNK_SIZE) {
    const end = start + CHUNK_SIZE > toBlock ? toBlock : start + CHUNK_SIZE
    const indexed = await indexUsdcTransfers(start, end)
    transactionsIndexed += indexed
  }

  console.log(`Total transactions indexed: ${transactionsIndexed}`)

  return { agentsSynced, transactionsIndexed }
}

/**
 * Manual agent registration (for agents not in ACP yet)
 */
export async function registerAgentManually(
  address: string,
  name?: string,
  description?: string
): Promise<void> {
  await prisma.reputationAgent.upsert({
    where: { address: address.toLowerCase() },
    update: {
      name: name || undefined,
      description: description || undefined,
    },
    create: {
      address: address.toLowerCase(),
      name: name || null,
      description: description || null,
      trustScore: 50,
    },
  })
}
