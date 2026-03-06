/**
 * Seed script to bootstrap reputation database with known ACP agents
 *
 * Run with: npx tsx scripts/seed-acp-agents.ts
 */

import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

// Known ACP agents (add more as discovered)
const KNOWN_AGENTS = [
  {
    address: '0x266c3434c2a723939836f109fe01bcfb96346c88',
    name: 'OpenClawdy',
    description: 'Agent Reputation & Trust Scoring service',
    services: ['agent_reputation_verify', 'agent_reputation_score', 'agent_reputation_history', 'agent_reputation_report'],
    categories: ['infrastructure', 'reputation', 'trust'],
  },
  // Add more known agents here as you discover them
  // You can find agents by browsing ACP marketplace
]

async function seed() {
  console.log('Seeding ACP agents...\n')

  for (const agent of KNOWN_AGENTS) {
    const existing = await prisma.reputationAgent.findUnique({
      where: { address: agent.address.toLowerCase() },
    })

    if (existing) {
      console.log(`✓ ${agent.name} already exists`)
      continue
    }

    await prisma.reputationAgent.create({
      data: {
        address: agent.address.toLowerCase(),
        name: agent.name,
        description: agent.description,
        services: agent.services,
        categories: agent.categories,
        trustScore: 50,
      },
    })

    console.log(`+ Created ${agent.name} (${agent.address})`)
  }

  // Show stats
  const count = await prisma.reputationAgent.count()
  console.log(`\nTotal agents in database: ${count}`)
}

seed()
  .catch(console.error)
  .finally(() => prisma.$disconnect())
