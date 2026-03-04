#!/usr/bin/env node

/**
 * A2A-enabled SHIB Payment Agent (v2 - Correct SDK usage)
 * Milestone 1: Basic agent registration and capability advertisement
 */

const express = require('express');
const { AgentCard, AGENT_CARD_PATH } = require('@a2a-js/sdk');
const { AgentExecutor, DefaultRequestHandler, InMemoryTaskStore } = require('@a2a-js/sdk/server');
const { agentCardHandler, jsonRpcHandler, restHandler, UserBuilder } = require('@a2a-js/sdk/server/express');
const { ShibPaymentAgent, loadConfig } = require('./index.js');

const config = loadConfig();
const shibAgent = new ShibPaymentAgent(config);

// 1. Define Agent Card (identity)
const agentCard = {
  name: 'OpenClaw SHIB Payment Agent',
  description: 'AI agent that sends/receives SHIB on Polygon with sub-penny gas costs',
  protocolVersion: '0.3.0',
  version: '0.1.0',
  url: 'http://localhost:8001/a2a/jsonrpc',
  
  skills: [
    {
      id: 'shib_payment',
      name: 'SHIB Payment',
      description: 'Send SHIB tokens on Polygon network',
      tags: ['payment', 'crypto', 'shib', 'polygon']
    },
    {
      id: 'shib_balance',
      name: 'SHIB Balance',
      description: 'Check SHIB balance on Polygon',
      tags: ['query', 'balance', 'shib']
    }
  ],
  
  capabilities: {
    pushNotifications: false
  },
  
  defaultInputModes: ['text'],
  defaultOutputModes: ['text'],
  
  additionalInterfaces: [
    { url: 'http://localhost:8001/a2a/jsonrpc', transport: 'JSONRPC' },
    { url: 'http://localhost:8001/a2a/rest', transport: 'HTTP+JSON' }
  ],
  
  metadata: {
    wallet: config.walletAddress,
    network: 'eip155:137', // Polygon
    token: 'SHIB',
    tokenContract: '0x6f8a06447ff6fcf75d803135a7de15ce88c1d4ec',
    gasToken: 'POL',
    avgGasCost: '$0.004'
  }
};

// 2. Implement Agent Executor (logic)
class ShibPaymentExecutor {
  async execute(requestContext, eventBus) {
    const { userMessage, taskId, contextId } = requestContext;
    const text = userMessage.parts[0]?.text || '';
    const { v4: uuidv4 } = require('crypto');
    
    console.log(`📨 Received [${taskId}]: ${text}`);
    
    const createMessage = (text) => ({
      kind: 'message',
      messageId: require('crypto').randomUUID(),
      role: 'agent',
      parts: [{ kind: 'text', text }],
      contextId
    });
    
    // Parse command
    if (text.includes('send') || text.includes('pay')) {
      // Extract amount and recipient from message
      const match = text.match(/send (\d+) SHIB to (0x[a-fA-F0-9]{40})/i);
      if (match) {
        const amount = parseFloat(match[1]);
        const recipient = match[2];
        
        try {
          const result = await shibAgent.sendPayment(recipient, amount);
          eventBus.publish(createMessage(
            `✅ Payment sent!\n\nAmount: ${amount} SHIB\nTo: ${recipient}\nTx: ${result.txHash}\nGas: ${result.gasCostUSD}\n\n${result.explorerUrl}`
          ));
        } catch (error) {
          eventBus.publish(createMessage(`❌ Payment failed: ${error.message}`));
        }
      } else {
        eventBus.publish(createMessage('Usage: send <amount> SHIB to <0xaddress>'));
      }
    } else if (text.includes('balance')) {
      try {
        const balance = await shibAgent.getBalance();
        eventBus.publish(createMessage(
          `💰 SHIB Balance\n\nAddress: ${balance.address}\nBalance: ${balance.balance} SHIB\nNetwork: Polygon`
        ));
      } catch (error) {
        eventBus.publish(createMessage(`❌ Balance check failed: ${error.message}`));
      }
    } else {
      eventBus.publish(createMessage(
        `🦪 SHIB Payment Agent\n\nCommands:\n- send <amount> SHIB to <address>\n- balance\n\nExample: send 100 SHIB to 0xDBD846593c1C89014a64bf0ED5802126912Ba99A`
      ));
    }
    
    eventBus.finished();
  }
  
  async cancelTask(taskId, eventBus) {
    console.log(`🛑 Task ${taskId} cancellation requested (not implemented)`);
  }
}

// 3. Start Server
async function startServer() {
  const app = express();
  const port = 8001;
  
  // Set up agent executor
  const executor = new ShibPaymentExecutor();
  const taskStore = new InMemoryTaskStore();
  const requestHandler = new DefaultRequestHandler(agentCard, taskStore, executor);
  
  // Register routes
  app.use(`/${AGENT_CARD_PATH}`, agentCardHandler({ agentCardProvider: requestHandler }));
  app.use('/a2a/jsonrpc', express.json(), jsonRpcHandler({ requestHandler, userBuilder: UserBuilder.noAuthentication }));
  app.use('/a2a/rest', express.json(), restHandler({ requestHandler, userBuilder: UserBuilder.noAuthentication }));
  
  // Start listening
  app.listen(port, () => {
    console.log('🦪 OpenClaw SHIB Payment Agent');
    console.log('');
    console.log('✅ Agent is online and ready!');
    console.log('');
    console.log('Agent Info:');
    console.log(`  Name: ${agentCard.name}`);
    console.log(`  Version: ${agentCard.version}`);
    console.log(`  Wallet: ${config.walletAddress}`);
    console.log(`  Network: Polygon (eip155:137)`);
    console.log('');
    console.log('Endpoints:');
    console.log(`  Agent Card: http://localhost:${port}${AGENT_CARD_PATH}`);
    console.log(`  JSON-RPC:   http://localhost:${port}/a2a/jsonrpc`);
    console.log(`  REST API:   http://localhost:${port}/a2a/rest`);
    console.log('');
    console.log('Skills:');
    agentCard.skills.forEach(skill => {
      console.log(`  - ${skill.name}: ${skill.description}`);
    });
    console.log('');
    console.log('Try: curl http://localhost:8001/.well-known/agent.json');
    console.log('');
  });
  
  // Graceful shutdown
  process.on('SIGINT', () => {
    console.log('');
    console.log('🛑 Shutting down agent...');
    process.exit(0);
  });
}

// CLI
const command = process.argv[2];

if (command === 'start' || !command) {
  startServer().catch(err => {
    console.error('Failed to start agent:', err);
    process.exit(1);
  });
} else {
  console.log(`
A2A SHIB Payment Agent - Usage:

  node a2a-agent-v2.js start    - Start the A2A agent server

Examples:
  node a2a-agent-v2.js start
  # Agent runs on http://localhost:8001

  # Test with curl:
  curl http://localhost:8001/.well-known/agent.json

Configuration:
  Set POLYGON_WALLET_ADDRESS and POLYGON_PRIVATE_KEY in ~/.env.local

Phase 2 Progress:
  ✅ Milestone 1.1: A2A SDK installed
  ✅ Milestone 1.2: Agent created with proper SDK structure
  🚧 Milestone 2: Discovery protocol (next)
  `);
}
