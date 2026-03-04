#!/usr/bin/env node

/**
 * A2A-enabled SHIB Payment Agent
 * Milestone 1: Basic agent registration and capability advertisement
 */

const { Agent } = require('@a2a-js/sdk');
const { ShibPaymentAgent, loadConfig } = require('./index.js');

class A2AShibAgent {
  constructor(config) {
    this.config = config;
    this.shibAgent = new ShibPaymentAgent(config);
    this.port = config.port || 8001;
    
    // A2A Agent configuration
    this.a2aAgent = new Agent({
      name: 'OpenClaw-SHIB-Payment-Agent',
      description: 'AI agent that sends/receives SHIB on Polygon with sub-penny gas costs',
      version: '0.1.0',
      
      // Advertise capabilities
      capabilities: [
        {
          name: 'shib_payment',
          description: 'Send SHIB tokens on Polygon network',
          input_schema: {
            type: 'object',
            properties: {
              recipient: {
                type: 'string',
                description: 'Polygon wallet address (0x...)',
                pattern: '^0x[a-fA-F0-9]{40}$'
              },
              amount: {
                type: 'number',
                description: 'Amount of SHIB to send',
                minimum: 1
              }
            },
            required: ['recipient', 'amount']
          },
          output_schema: {
            type: 'object',
            properties: {
              success: { type: 'boolean' },
              txHash: { type: 'string' },
              gasUsed: { type: 'string' },
              gasCostUSD: { type: 'string' },
              explorerUrl: { type: 'string' }
            }
          }
        },
        {
          name: 'shib_balance',
          description: 'Check SHIB balance on Polygon',
          input_schema: {
            type: 'object',
            properties: {
              address: {
                type: 'string',
                description: 'Wallet address to check (optional, defaults to own wallet)'
              }
            }
          },
          output_schema: {
            type: 'object',
            properties: {
              address: { type: 'string' },
              balance: { type: 'string' },
              balanceRaw: { type: 'string' },
              token: { type: 'string' }
            }
          }
        }
      ],
      
      // Agent metadata
      metadata: {
        wallet: config.walletAddress,
        network: 'eip155:137', // Polygon
        token: 'SHIB',
        tokenContract: '0x6f8a06447ff6fcf75d803135a7de15ce88c1d4ec',
        gasToken: 'POL',
        avgGasCost: '$0.004'
      }
    });
  }

  async start() {
    console.log('🦪 Starting A2A SHIB Payment Agent...');
    console.log('');
    console.log('Agent Info:');
    console.log(`  Name: ${this.a2aAgent.name}`);
    console.log(`  Version: ${this.a2aAgent.version}`);
    console.log(`  Wallet: ${this.config.walletAddress}`);
    console.log(`  Network: Polygon (eip155:137)`);
    console.log(`  Port: ${this.port}`);
    console.log('');
    
    // Register capability handlers
    this.a2aAgent.registerHandler('shib_payment', async (input) => {
      console.log(`📤 Payment request: ${input.amount} SHIB → ${input.recipient}`);
      try {
        const result = await this.shibAgent.sendPayment(input.recipient, input.amount);
        console.log(`✅ Payment sent: ${result.txHash}`);
        return result;
      } catch (error) {
        console.error(`❌ Payment failed: ${error.message}`);
        return {
          success: false,
          error: error.message
        };
      }
    });

    this.a2aAgent.registerHandler('shib_balance', async (input) => {
      console.log(`📊 Balance check: ${input.address || 'own wallet'}`);
      try {
        const result = await this.shibAgent.getBalance(input.address);
        console.log(`✅ Balance: ${result.balance} SHIB`);
        return result;
      } catch (error) {
        console.error(`❌ Balance check failed: ${error.message}`);
        return {
          success: false,
          error: error.message
        };
      }
    });

    // Start A2A server
    await this.a2aAgent.listen(this.port);
    
    console.log('');
    console.log('✅ Agent is online and ready!');
    console.log('');
    console.log('Capabilities:');
    this.a2aAgent.capabilities.forEach(cap => {
      console.log(`  - ${cap.name}: ${cap.description}`);
    });
    console.log('');
    console.log(`🌐 A2A Endpoint: http://localhost:${this.port}/a2a`);
    console.log('');
  }

  async stop() {
    console.log('🛑 Stopping agent...');
    await this.a2aAgent.close();
    console.log('✅ Agent stopped');
  }

  // Discovery helper
  async discoverAgents(capability) {
    console.log(`🔍 Discovering agents with capability: ${capability}...`);
    // TODO: Implement discovery protocol in Milestone 2
    console.log('⚠️  Discovery not yet implemented (Milestone 2)');
    return [];
  }

  // Status check
  async status() {
    const balance = await this.shibAgent.getBalance();
    return {
      agent: {
        name: this.a2aAgent.name,
        version: this.a2aAgent.version,
        status: 'online',
        endpoint: `http://localhost:${this.port}/a2a`
      },
      wallet: {
        address: this.config.walletAddress,
        shibBalance: balance.balance,
        network: 'Polygon'
      },
      capabilities: this.a2aAgent.capabilities.map(c => c.name)
    };
  }
}

// CLI
async function main() {
  const config = loadConfig();
  const agent = new A2AShibAgent(config);

  const command = process.argv[2];

  try {
    switch(command) {
      case 'start':
        await agent.start();
        // Keep running
        process.on('SIGINT', async () => {
          console.log('');
          await agent.stop();
          process.exit(0);
        });
        break;

      case 'status':
        const status = await agent.status();
        console.log(JSON.stringify(status, null, 2));
        process.exit(0);
        break;

      default:
        console.log(`
A2A SHIB Payment Agent - Usage:

  node a2a-agent.js start       - Start the A2A agent server
  node a2a-agent.js status      - Check agent status

Examples:
  node a2a-agent.js start
  # Agent runs on http://localhost:8001/a2a

Configuration:
  Set POLYGON_WALLET_ADDRESS and POLYGON_PRIVATE_KEY in ~/.env.local

Capabilities:
  - shib_payment: Send SHIB on Polygon
  - shib_balance: Check SHIB balance

Phase 2 Progress:
  ✅ Milestone 1.1: A2A SDK installed
  ✅ Milestone 1.2: Agent created and registered
  🚧 Milestone 2: Discovery protocol (next)
        `);
        process.exit(0);
    }
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { A2AShibAgent };
