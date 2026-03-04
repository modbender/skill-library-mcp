#!/usr/bin/env node

/**
 * Full-Featured A2A SHIB Payment Agent
 * Includes: Payments, Escrow, Negotiation, Reputation
 */

const express = require('express');
const { AgentCard, AGENT_CARD_PATH } = require('@a2a-js/sdk');
const { AgentExecutor, DefaultRequestHandler, InMemoryTaskStore } = require('@a2a-js/sdk/server');
const { agentCardHandler, jsonRpcHandler, restHandler, UserBuilder } = require('@a2a-js/sdk/server/express');
const { ShibPaymentAgent, loadConfig } = require('./index.js');
const { EscrowSystem } = require('./escrow.js');
const { PaymentNegotiationSystem } = require('./payment-negotiation.js');
const { ReputationSystem } = require('./reputation.js');
const { AuditLogger } = require('./audit-logger.js');

const config = loadConfig();
const shibAgent = new ShibPaymentAgent(config);
const escrowSystem = new EscrowSystem();
const negotiationSystem = new PaymentNegotiationSystem(escrowSystem);
const reputationSystem = new ReputationSystem();
const auditLogger = new AuditLogger();

// Agent Card
const agentCard = {
  name: 'OpenClaw SHIB Payment Agent (Full-Featured)',
  description: 'Complete agent-to-agent payment system with escrow, negotiation, and reputation',
  protocolVersion: '0.3.0',
  version: '2.0.0',
  url: 'http://localhost:8003/a2a/jsonrpc',
  
  skills: [
    {
      id: 'payment',
      name: 'SHIB Payment',
      description: 'Send SHIB tokens on Polygon network',
      tags: ['payment', 'crypto', 'shib', 'polygon']
    },
    {
      id: 'balance',
      name: 'Balance Check',
      description: 'Check SHIB balance',
      tags: ['query', 'balance']
    },
    {
      id: 'escrow',
      name: 'Escrow Management',
      description: 'Create and manage trustless escrow payments',
      tags: ['escrow', 'trustless', 'secure']
    },
    {
      id: 'negotiation',
      name: 'Service Negotiation',
      description: 'Request quotes and negotiate prices for services',
      tags: ['negotiation', 'marketplace', 'quotes']
    },
    {
      id: 'reputation',
      name: 'Reputation System',
      description: 'Rate agents and view reputation scores',
      tags: ['reputation', 'trust', 'ratings']
    }
  ],
  
  capabilities: {
    pushNotifications: false,
    escrow: true,
    negotiation: true,
    reputation: true
  },
  
  defaultInputModes: ['text'],
  defaultOutputModes: ['text'],
  
  additionalInterfaces: [
    { url: 'http://localhost:8003/a2a/jsonrpc', transport: 'JSONRPC' },
    { url: 'http://localhost:8003/a2a/rest', transport: 'HTTP+JSON' }
  ],
  
  metadata: {
    wallet: config.walletAddress,
    network: 'eip155:137',
    token: 'SHIB',
    features: ['payments', 'escrow', 'negotiation', 'reputation']
  }
};

// Full-Featured Executor
class FullFeaturedExecutor {
  async execute(requestContext, eventBus) {
    const { userMessage, taskId, contextId } = requestContext;
    const text = userMessage.parts[0]?.text || '';
    
    console.log(`📨 Received [${taskId}]: ${text}`);
    
    const createMessage = (text) => ({
      kind: 'message',
      messageId: require('crypto').randomUUID(),
      role: 'agent',
      parts: [{ kind: 'text', text }],
      contextId
    });
    
    try {
      // Payment commands
      if (text.includes('balance')) {
        const balance = await shibAgent.getBalance();
        eventBus.publish(createMessage(
          `💰 SHIB Balance\n\nAddress: ${balance.address}\nBalance: ${balance.balance} SHIB\nNetwork: Polygon`
        ));
      }
      else if (text.match(/send (\d+(?:\.\d+)?) SHIB to (0x[a-fA-F0-9]{40})/i)) {
        const match = text.match(/send (\d+(?:\.\d+)?) SHIB to (0x[a-fA-F0-9]{40})/i);
        const amount = parseFloat(match[1]);
        const recipient = match[2];
        
        const result = await shibAgent.sendPayment(recipient, amount);
        auditLogger.log('payment_executed', { amount, recipient, txHash: result.txHash });
        
        eventBus.publish(createMessage(
          `✅ Payment sent!\n\nAmount: ${amount} SHIB\nTo: ${recipient}\nTx: ${result.txHash}\nGas: ${result.gasCostUSD}\n\n${result.explorerUrl}`
        ));
      }
      
      // Escrow commands
      else if (text.startsWith('escrow create')) {
        const match = text.match(/escrow create (\d+) SHIB for (.+?) payee ([\w-]+)/i);
        if (!match) {
          eventBus.publish(createMessage('Usage: escrow create <amount> SHIB for <purpose> payee <agentId>'));
        } else {
          const [, amount, purpose, payee] = match;
          const escrow = escrowSystem.create({
            payer: 'current-agent',
            payee,
            amount: parseFloat(amount),
            purpose,
            conditions: { requiresApproval: true, requiresDelivery: true },
            timeoutMinutes: 120
          });
          
          auditLogger.log('escrow_created', { escrowId: escrow.id, amount, payee });
          eventBus.publish(createMessage(
            `✅ Escrow created!\n\nID: ${escrow.id}\nAmount: ${amount} SHIB\nPayee: ${payee}\nPurpose: ${purpose}\nTimeout: 120 minutes\n\nNext: Use "escrow fund ${escrow.id} <txHash>" to fund it.`
          ));
        }
      }
      else if (text.startsWith('escrow fund')) {
        const match = text.match(/escrow fund (esc_\w+) (0x\w+)/i);
        if (!match) {
          eventBus.publish(createMessage('Usage: escrow fund <escrowId> <txHash>'));
        } else {
          const [, escrowId, txHash] = match;
          const escrow = escrowSystem.fund(escrowId, txHash);
          eventBus.publish(createMessage(
            `✅ Escrow funded!\n\nID: ${escrowId}\nState: ${escrow.state}\nTx: ${txHash}\n\nNext: Both parties must approve with "escrow approve ${escrowId}"`
          ));
        }
      }
      else if (text.startsWith('escrow approve')) {
        const match = text.match(/escrow approve (esc_\w+)/i);
        if (!match) {
          eventBus.publish(createMessage('Usage: escrow approve <escrowId>'));
        } else {
          const escrowId = match[1];
          const escrow = escrowSystem.approve(escrowId, 'current-agent');
          eventBus.publish(createMessage(
            `✅ Escrow approved!\n\nID: ${escrowId}\nState: ${escrow.state}\nApprovals: ${escrow.approvals.length}/2`
          ));
        }
      }
      else if (text.startsWith('escrow status')) {
        const match = text.match(/escrow status (esc_\w+)/i);
        if (!match) {
          eventBus.publish(createMessage('Usage: escrow status <escrowId>'));
        } else {
          const escrow = escrowSystem.get(match[1]);
          if (!escrow) {
            eventBus.publish(createMessage('Escrow not found'));
          } else {
            eventBus.publish(createMessage(
              `📋 Escrow Status\n\nID: ${escrow.id}\nState: ${escrow.state}\nAmount: ${escrow.amount} SHIB\nPayer: ${escrow.payer}\nPayee: ${escrow.payee}\nPurpose: ${escrow.purpose}\nApprovals: ${escrow.approvals.length}\nDelivery: ${escrow.deliveryProof ? '✅ Submitted' : '❌ Pending'}`
            ));
          }
        }
      }
      
      // Negotiation commands
      else if (text.startsWith('quote')) {
        const match = text.match(/quote (.+?) for (\d+) SHIB to ([\w-]+)/i);
        if (!match) {
          eventBus.publish(createMessage('Usage: quote <service description> for <price> SHIB to <clientId>'));
        } else {
          const [, service, price, clientId] = match;
          const quote = negotiationSystem.createQuote({
            providerId: 'current-agent',
            clientId,
            service,
            price: parseFloat(price),
            terms: { deliveryTimeMinutes: 60, escrowRequired: true },
            validForMinutes: 60
          });
          
          auditLogger.log('quote_created', { quoteId: quote.id, service, price, clientId });
          eventBus.publish(createMessage(
            `✅ Quote created!\n\nID: ${quote.id}\nService: ${service}\nPrice: ${price} SHIB\nClient: ${clientId}\nValid for: 60 minutes\n\nClient can accept with: accept quote ${quote.id}`
          ));
        }
      }
      else if (text.startsWith('accept quote')) {
        const match = text.match(/accept quote (quote_\w+)/i);
        if (!match) {
          eventBus.publish(createMessage('Usage: accept quote <quoteId>'));
        } else {
          const quote = negotiationSystem.accept(match[1], 'current-agent');
          eventBus.publish(createMessage(
            `✅ Quote accepted!\n\nID: ${quote.id}\nPrice: ${quote.agreedPrice} SHIB\nEscrow: ${quote.escrowId}\n\nNext: Fund escrow with "escrow fund ${quote.escrowId} <txHash>"`
          ));
        }
      }
      else if (text.startsWith('counter offer')) {
        const match = text.match(/counter offer (quote_\w+) (\d+) SHIB/i);
        if (!match) {
          eventBus.publish(createMessage('Usage: counter offer <quoteId> <newPrice> SHIB'));
        } else {
          const [, quoteId, newPrice] = match;
          const quote = negotiationSystem.counterOffer(quoteId, 'current-agent', parseFloat(newPrice));
          eventBus.publish(createMessage(
            `✅ Counter-offer sent!\n\nID: ${quoteId}\nYour offer: ${newPrice} SHIB\nState: ${quote.state}\n\nWaiting for provider response.`
          ));
        }
      }
      
      // Reputation commands
      else if (text.startsWith('rate')) {
        const match = text.match(/rate ([\w-]+) (\d+(?:\.\d+)?)(?:\s+(.+))?/i);
        if (!match) {
          eventBus.publish(createMessage('Usage: rate <agentId> <rating 0-5> [comment]'));
        } else {
          const [, agentId, rating, comment] = match;
          reputationSystem.addRating({
            agentId,
            raterId: 'current-agent',
            rating: parseFloat(rating),
            comment: comment || '',
            transactionId: taskId
          });
          
          const score = reputationSystem.getScore(agentId);
          eventBus.publish(createMessage(
            `✅ Rating submitted!\n\nAgent: ${agentId}\nYour rating: ${rating}/5\n${comment ? `Comment: ${comment}\n` : ''}\nNew average: ${score.average.toFixed(2)}/5 (${score.count} reviews)`
          ));
        }
      }
      else if (text.startsWith('reputation')) {
        const match = text.match(/reputation ([\w-]+)/i);
        if (!match) {
          eventBus.publish(createMessage('Usage: reputation <agentId>'));
        } else {
          const agentId = match[1];
          const score = reputationSystem.getScore(agentId);
          const profile = reputationSystem.getProfile(agentId);
          
          eventBus.publish(createMessage(
            `📊 Reputation: ${agentId}\n\n⭐ Average: ${score.average.toFixed(2)}/5\n📝 Reviews: ${score.count}\n🏆 Trust Level: ${profile.trustLevel}\n✅ Verified: ${profile.verified ? 'Yes' : 'No'}\n\nBreakdown:\n5★: ${profile.ratingBreakdown['5'] || 0}\n4★: ${profile.ratingBreakdown['4'] || 0}\n3★: ${profile.ratingBreakdown['3'] || 0}\n2★: ${profile.ratingBreakdown['2'] || 0}\n1★: ${profile.ratingBreakdown['1'] || 0}`
          ));
        }
      }
      
      // Help
      else {
        eventBus.publish(createMessage(
          `🦪 SHIB Payment Agent (Full-Featured)\n\n💰 Payments:\n- balance\n- send <amount> SHIB to <address>\n\n🔒 Escrow:\n- escrow create <amount> SHIB for <purpose> payee <agentId>\n- escrow fund <escrowId> <txHash>\n- escrow approve <escrowId>\n- escrow status <escrowId>\n\n💬 Negotiation:\n- quote <service> for <price> SHIB to <clientId>\n- accept quote <quoteId>\n- counter offer <quoteId> <newPrice> SHIB\n\n⭐ Reputation:\n- rate <agentId> <rating 0-5> [comment]\n- reputation <agentId>\n\nAll features ready!`
        ));
      }
    } catch (error) {
      console.error('Error:', error);
      eventBus.publish(createMessage(`❌ Error: ${error.message}`));
    }
    
    eventBus.finished();
  }
  
  async cancelTask(taskId, eventBus) {
    console.log(`🛑 Task ${taskId} cancelled`);
  }
}

// Start Server
async function startServer() {
  const app = express();
  const port = 8003;
  
  const executor = new FullFeaturedExecutor();
  const taskStore = new InMemoryTaskStore();
  const requestHandler = new DefaultRequestHandler(agentCard, taskStore, executor);

  app.use(`/${AGENT_CARD_PATH}`, agentCardHandler({ agentCardProvider: requestHandler }));
  app.use('/a2a/jsonrpc', express.json(), jsonRpcHandler({ requestHandler, userBuilder: UserBuilder.noAuthentication }));
  app.use('/a2a/rest', express.json(), restHandler({ requestHandler, userBuilder: UserBuilder.noAuthentication }));

  app.listen(port, () => {
    console.log('🦪 OpenClaw SHIB Payment Agent (Full-Featured)');
    console.log('');
    console.log('✅ All systems online!');
    console.log('');
    console.log(`Port: ${port}`);
    console.log(`Wallet: ${config.walletAddress}`);
    console.log('');
    console.log('Features:');
    console.log('  ✓ SHIB Payments');
    console.log('  ✓ Escrow System');
    console.log('  ✓ Price Negotiation');
    console.log('  ✓ Reputation System');
    console.log('');
    
    auditLogger.log('full_agent_start', { port, version: '2.0.0' });
  });
  
  process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down...');
    auditLogger.log('full_agent_stop', { timestamp: new Date().toISOString() });
    process.exit(0);
  });
}

if (require.main === module) {
  startServer().catch(err => {
    console.error('Failed to start:', err);
    process.exit(1);
  });
}

module.exports = { FullFeaturedExecutor };
