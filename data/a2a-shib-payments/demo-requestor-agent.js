#!/usr/bin/env node

/**
 * Demo Requestor Agent
 * Uses A2A discovery to find and interact with the SHIB Payment Agent
 * 
 * This demonstrates agent-to-agent communication:
 * - Agent A (requestor) needs to send SHIB
 * - Agent A discovers Agent B (SHIB payment agent) via registry
 * - Agent A requests service from Agent B via A2A protocol
 */

const { DiscoveryClient } = require('./discovery-client.js');

class RequestorAgent {
  constructor() {
    this.discovery = new DiscoveryClient();
    this.name = 'Demo Requestor Agent';
  }

  /**
   * Find a payment agent that supports SHIB
   */
  async findPaymentAgent() {
    console.log(`🤖 [${this.name}] Looking for a SHIB payment agent...`);
    
    const agents = this.discovery.findByCapability('shib');
    if (agents.length === 0) {
      throw new Error('No SHIB payment agents found in registry');
    }

    const paymentAgent = agents[0];
    console.log(`✅ Found: ${paymentAgent.name} (${paymentAgent.id})`);
    
    return paymentAgent.id;
  }

  /**
   * Request payment via discovered agent
   */
  async requestPayment(recipient, amount) {
    console.log(`\n💼 [${this.name}] Task: Send ${amount} SHIB to ${recipient}`);
    
    // Step 1: Discover payment agent
    const agentId = await this.findPaymentAgent();
    
    // Step 2: Check balance first
    console.log(`\n📊 Checking balance via ${agentId}...`);
    const balanceResponse = await this.discovery.sendMessage(agentId, 'balance');
    
    // Step 3: Send payment
    console.log(`\n💸 Requesting payment of ${amount} SHIB...`);
    const paymentResponse = await this.discovery.sendMessage(
      agentId,
      `send ${amount} SHIB to ${recipient}`
    );
    
    console.log(`✅ [${this.name}] Payment completed!`);
    return paymentResponse;
  }

  /**
   * Demonstrate multi-agent workflow
   */
  async runWorkflow() {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`🦪 Agent-to-Agent Communication Demo`);
    console.log(`${'='.repeat(60)}\n`);

    try {
      // Scenario: Requestor agent needs to send SHIB but doesn't know how
      // Solution: Discover and delegate to payment specialist agent
      
      await this.requestPayment(
        '0xDBD846593c1C89014a64bf0ED5802126912Ba99A', // Coinbase Polygon wallet
        5 // 5 SHIB
      );

      console.log(`\n${'='.repeat(60)}`);
      console.log(`✅ Workflow Complete!`);
      console.log(`${'='.repeat(60)}\n`);
      
      console.log(`📝 What just happened:`);
      console.log(`   1. Requestor agent needed to send SHIB`);
      console.log(`   2. Discovered payment agent via registry`);
      console.log(`   3. Checked balance via A2A protocol`);
      console.log(`   4. Delegated payment to specialist agent`);
      console.log(`   5. Received confirmation via A2A response\n`);

    } catch (error) {
      console.error(`❌ [${this.name}] Workflow failed:`, error.message);
      throw error;
    }
  }
}

// CLI
async function main() {
  const [,, command] = process.argv;

  const agent = new RequestorAgent();

  try {
    switch (command) {
      case 'workflow':
        await agent.runWorkflow();
        break;

      case 'find':
        await agent.findPaymentAgent();
        break;

      default:
        console.log(`
Demo Requestor Agent - Agent-to-Agent Communication

Usage:
  node demo-requestor-agent.js workflow   - Run full A2A demo workflow
  node demo-requestor-agent.js find       - Just discover payment agent

Example:
  node demo-requestor-agent.js workflow

This demonstrates:
- Agent discovery via registry
- Agent-to-agent communication via A2A protocol
- Delegating specialized tasks to specialist agents
- Multi-agent workflows (check balance → send payment)
        `);
    }
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { RequestorAgent };
