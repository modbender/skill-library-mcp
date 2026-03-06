#!/usr/bin/env node

/**
 * A2A Discovery Client
 * Finds and connects to A2A agents via registry
 */

const { ClientFactory } = require('@a2a-js/sdk/client');
const fs = require('fs');
const path = require('path');

class DiscoveryClient {
  constructor(registryPath = './registry.json') {
    this.registryPath = registryPath;
    this.registry = null;
    this.clientFactory = new ClientFactory();
  }

  /**
   * Load agent registry
   */
  loadRegistry() {
    if (!fs.existsSync(this.registryPath)) {
      throw new Error(`Registry not found: ${this.registryPath}`);
    }
    
    const data = fs.readFileSync(this.registryPath, 'utf8');
    this.registry = JSON.parse(data);
    console.log(`📋 Loaded registry: ${this.registry.agents.length} agents`);
    return this.registry;
  }

  /**
   * Find agents by capability
   */
  findByCapability(capability) {
    if (!this.registry) this.loadRegistry();
    
    return this.registry.agents.filter(agent => 
      agent.capabilities.includes(capability)
    );
  }

  /**
   * Find agent by ID
   */
  findById(id) {
    if (!this.registry) this.loadRegistry();
    
    return this.registry.agents.find(agent => agent.id === id);
  }

  /**
   * List all agents
   */
  listAgents() {
    if (!this.registry) this.loadRegistry();
    
    return this.registry.agents;
  }

  /**
   * Connect to an agent and return A2A client
   */
  async connect(agentId) {
    const agent = this.findById(agentId);
    if (!agent) {
      throw new Error(`Agent not found: ${agentId}`);
    }

    console.log(`🔌 Connecting to ${agent.name}...`);
    const client = await this.clientFactory.createFromUrl(
      agent.agentCardUrl.replace('/.well-known/agent-card.json', '')
    );
    
    console.log(`✅ Connected to ${agent.name}`);
    return { agent, client };
  }

  /**
   * Send message to an agent
   */
  async sendMessage(agentId, messageText) {
    const { agent, client } = await this.connect(agentId);
    
    console.log(`💬 Sending: "${messageText}"`);
    
    const response = await client.sendMessage({
      message: {
        kind: 'message',
        messageId: require('crypto').randomUUID(),
        role: 'user',
        parts: [{ kind: 'text', text: messageText }]
      }
    });

    if (response.kind === 'message') {
      const reply = response.parts[0].text;
      console.log(`📨 Response:\n${reply}\n`);
      return reply;
    } else if (response.kind === 'task') {
      console.log(`📋 Task created: ${response.id}`);
      console.log(`Status: ${response.status.state}`);
      return response;
    }
  }
}

// CLI
async function main() {
  const [,, command, ...args] = process.argv;
  const client = new DiscoveryClient();

  try {
    switch (command) {
      case 'list':
        const agents = client.listAgents();
        console.log('\n📋 Available Agents:\n');
        agents.forEach(agent => {
          console.log(`  ${agent.id}`);
          console.log(`    Name: ${agent.name}`);
          console.log(`    Capabilities: ${agent.capabilities.join(', ')}`);
          console.log(`    Endpoint: ${agent.endpoints.jsonrpc}\n`);
        });
        break;

      case 'find':
        const capability = args[0];
        if (!capability) {
          console.error('Usage: node discovery-client.js find <capability>');
          process.exit(1);
        }
        const found = client.findByCapability(capability);
        console.log(`\n🔍 Agents with capability "${capability}":\n`);
        found.forEach(agent => {
          console.log(`  - ${agent.name} (${agent.id})`);
        });
        break;

      case 'send':
        const agentId = args[0];
        const message = args.slice(1).join(' ');
        if (!agentId || !message) {
          console.error('Usage: node discovery-client.js send <agent-id> <message>');
          process.exit(1);
        }
        await client.sendMessage(agentId, message);
        break;

      case 'info':
        const id = args[0];
        if (!id) {
          console.error('Usage: node discovery-client.js info <agent-id>');
          process.exit(1);
        }
        const agent = client.findById(id);
        if (!agent) {
          console.error(`Agent not found: ${id}`);
          process.exit(1);
        }
        console.log('\n📄 Agent Info:\n');
        console.log(JSON.stringify(agent, null, 2));
        break;

      default:
        console.log(`
A2A Discovery Client

Usage:
  node discovery-client.js list                    - List all agents
  node discovery-client.js find <capability>       - Find agents by capability
  node discovery-client.js info <agent-id>         - Show agent details
  node discovery-client.js send <agent-id> <msg>   - Send message to agent

Examples:
  node discovery-client.js list
  node discovery-client.js find crypto-payments
  node discovery-client.js send shib-payment-agent balance
  node discovery-client.js send shib-payment-agent "send 10 SHIB to 0x..."
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

module.exports = { DiscoveryClient };
