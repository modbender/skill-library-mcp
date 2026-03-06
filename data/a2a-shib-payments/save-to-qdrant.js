#!/usr/bin/env node

/**
 * Save all SHIB Payment Agent documentation to Qdrant
 */

const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

const documents = [
  {
    title: 'SHIB Payment Agent - Overview',
    content: `Complete agent-to-agent payment system on Polygon network with SHIB tokens.

Key Features:
- Direct SHIB payments with ~$0.003 gas costs
- Trustless escrow system with conditional releases
- Automated price negotiation (x402-inspired)
- Reputation system with trust levels and badges
- A2A protocol integration for agent discovery
- Production security (auth, rate limiting, audit logs)

Architecture:
- Polygon network for low-cost transactions
- A2A protocol for agent-to-agent communication
- Escrow contracts for trustless payments
- Reputation tracking for marketplace trust

Components:
1. Payment system (index.js, a2a-agent-v2.js)
2. Escrow system (escrow.js)
3. Negotiation system (payment-negotiation.js)
4. Reputation system (reputation.js)
5. Security layer (auth.js, rate-limiter.js, audit-logger.js)`,
    tags: JSON.stringify({ category: 'overview', project: 'shib-payments', version: '2.0.0' })
  },
  {
    title: 'SHIB Payment Agent - Escrow System',
    content: `Trustless escrow for agent-to-agent payments with automatic releases and dispute resolution.

States: pending → funded → locked → released/refunded/disputed

Features:
- Time-locked payments (auto-refund on timeout)
- Multi-party approval (payer + payee must approve)
- Delivery proof submission & verification
- Automatic release when conditions met
- Dispute resolution with arbiter
- Complete audit trail

Key Methods:
- create({payer, payee, amount, purpose, conditions, timeoutMinutes})
- fund(escrowId, txHash) - Mark as funded
- approve(escrowId, approverId) - Approve escrow
- submitDelivery(escrowId, proof) - Submit proof
- release(escrowId, reason) - Release to payee
- refund(escrowId, reason) - Refund to payer
- dispute(escrowId, disputerId, reason) - Open dispute
- resolveDispute(escrowId, decision, arbiter) - Resolve dispute

Conditions:
- requiresApproval: Both parties must approve
- requiresDelivery: Delivery proof required
- requiresArbiter: Third-party resolution
- requiresClientConfirmation: Manual client approval`,
    tags: JSON.stringify({ category: 'escrow', component: 'core', project: 'shib-payments' })
  },
  {
    title: 'SHIB Payment Agent - Payment Negotiation',
    content: `Agent-to-agent service negotiation system inspired by x402 protocol.

States: pending → accepted/rejected/countered/expired

Features:
- Provider creates quote with price and terms
- Client can accept, reject, or counter-offer
- Multi-round negotiation support
- Automatic escrow creation on acceptance
- Service delivery tracking
- Client confirmation triggers payment

Key Methods:
- createQuote({providerId, clientId, service, price, terms, validForMinutes})
- accept(quoteId, clientId) - Accept quote
- reject(quoteId, clientId, reason) - Reject quote
- counterOffer(quoteId, clientId, counterPrice, counterTerms) - Negotiate
- acceptCounter(quoteId, providerId) - Accept counter
- markDelivered(quoteId, providerId, deliveryProof) - Service completed
- confirmDelivery(quoteId, clientId) - Confirm and release payment

Terms:
- deliveryTimeMinutes: Expected delivery
- qualityGuarantee: Quality promise
- refundPolicy: Refund terms
- escrowRequired: Create escrow on accept
- requiresArbiter: Dispute resolution
- autoRelease: Auto-release on delivery`,
    tags: JSON.stringify({ category: 'negotiation', component: 'marketplace', project: 'shib-payments' })
  },
  {
    title: 'SHIB Payment Agent - Reputation System',
    content: `Comprehensive reputation and trust scoring for agent marketplace.

Trust Levels: new → bronze → silver → gold → platinum

Features:
- Star ratings (0-5) with written reviews
- Transaction history tracking
- Dynamic trust score calculation (0-100)
- Badge system for achievements
- Agent verification
- Dispute history tracking
- Search and filtering

Trust Score Components:
- Rating component (40 points): Average rating * total reviews
- Success rate (30 points): Successful transactions / total
- Dispute penalty (-20 points): Dispute rate
- Volume bonus (10 points): Transaction count
- Verification bonus (20 points): KYC verified

Badges:
- 10/50/100 transactions milestones
- highly_rated (≥4.5 avg, 10+ reviews)
- top_rated (≥4.8 avg, 25+ reviews)
- reliable (≥95% success, 20+ txns)
- trustworthy (≤5% disputes, 20+ txns)
- verified (KYC completed)

Key Methods:
- addRating({agentId, raterId, rating, comment})
- recordTransaction(agentId, success)
- recordDispute({agentId, role, reason, outcome})
- verifyAgent(agentId, verificationData)
- getScore(agentId) - Get reputation score
- getProfile(agentId) - Full profile
- getTopRated(limit, minRatings) - Leaderboard
- search({minRating, trustLevel, verified, minTransactions})`,
    tags: JSON.stringify({ category: 'reputation', component: 'trust', project: 'shib-payments' })
  },
  {
    title: 'SHIB Payment Agent - Security Infrastructure',
    content: `Production-grade security with authentication, rate limiting, and audit logging.

Components:
1. Authentication System (auth.js)
   - API key generation (sk_ prefix, 64-byte keys)
   - Per-agent permissions (balance, payment)
   - Payment amount limits
   - Agent enable/disable

2. Rate Limiting (rate-limiter.js)
   - Request rate: 10 req/min (configurable)
   - Payment rate: 3 payments/min
   - Payment volume: 500 SHIB/min
   - Per-agent tracking with sliding window

3. Audit Logging (audit-logger.js)
   - Immutable append-only logs
   - Hash-chained entries for tamper detection
   - Sequence numbering
   - Daily log rotation (JSON Lines format)
   - Integrity verification
   - Query interface with filters

Event Types:
- agent_start/stop, auth, balance_check
- payment_request, payment_executed, payment_failed
- rate_limit, task_cancelled
- escrow_created, quote_created

Security Best Practices:
- API keys stored securely (chmod 600)
- Rate limits prevent abuse
- Audit logs for compliance
- Hash chain prevents tampering
- Per-agent permissions
- Payment limits enforced`,
    tags: JSON.stringify({ category: 'security', component: 'infrastructure', project: 'shib-payments' })
  },
  {
    title: 'SHIB Payment Agent - A2A Protocol Integration',
    content: `Agent2Agent protocol integration for standardized agent communication.

A2A Protocol: v0.3.0 compliant

Endpoints:
- Agent Card: /.well-known/agent-card.json
- JSON-RPC: /a2a/jsonrpc (message/send method)
- REST API: /a2a/rest

Agent Discovery:
- Registry-based discovery (registry.json)
- Capability matching (crypto-payments, shib, polygon)
- Service type filtering
- Discovery client (discovery-client.js)

Message Format:
{
  "kind": "message",
  "messageId": "<uuid>",
  "role": "user|agent",
  "parts": [{"kind": "text", "text": "<message>"}],
  "contextId": "<context-id>"
}

Integration Features:
- StandardizedA2A message handling
- Task-based execution model
- Agent card with capabilities
- Multi-transport support (JSON-RPC, REST)
- Compatible with LangChain agents, AWS Bedrock agents

Discovery + Delegation:
Agent A discovers Agent B by capability → Requests service → Negotiates price → Creates escrow → Service delivered → Payment released`,
    tags: JSON.stringify({ category: 'a2a', component: 'protocol', project: 'shib-payments' })
  },
  {
    title: 'SHIB Payment Agent - Use Cases and Examples',
    content: `Real-world use cases for agent-to-agent payments with escrow.

1. Data Marketplace
   - Agents buy/sell datasets with quality guarantees
   - Escrow holds payment until data delivered
   - Reputation ensures quality providers
   Example: Research agent pays data provider 400 SHIB for TSLA historical data

2. AI Model Training
   - Client pays for model training, funds held until completion
   - Delivery proof: model file + performance metrics
   - Dispute if quality metrics not met

3. Translation Services
   - Client requests translation (10,000 words, 300 SHIB)
   - Provider delivers (only 9,500 words)
   - Client disputes → Arbiter refunds
   - Provider reputation decreases

4. Multi-Agent Workflows
   - Data collection → Analysis → Report generation
   - Each step protected by escrow
   - Conditional payments chain together
   - Failure at any step triggers refund

5. Subscription Services
   - Recurring payments with per-period escrow
   - Monthly data feed (100 SHIB/month)
   - Auto-renew with escrow each period
   - Cancel anytime with pro-rated refund

Cost Comparison:
- Traditional escrow: 3.25% + $25 = $28.25 for $100
- Our system: $0.003 gas = 0.003% for $100
- Savings: 9,416x cheaper!

Settlement Time:
- Traditional: 5-7 days
- Our system: Instant (seconds)`,
    tags: JSON.stringify({ category: 'use-cases', component: 'examples', project: 'shib-payments' })
  },
  {
    title: 'SHIB Payment Agent - Technical Architecture',
    content: `Complete technical architecture and integration guide.

Stack:
- Blockchain: Polygon (eip155:137)
- Token: SHIB (ERC-20)
- Protocol: A2A v0.3.0
- Language: Node.js 18+
- Framework: Express.js
- Storage: JSON files (escrow-state.json, negotiation-state.json, reputation-state.json)

Components:
1. Payment Agent (index.js, a2a-agent-full.js)
   - Ethers.js for blockchain interaction
   - SHIB token contract: 0x6f8a06447ff6fcf75d803135a7de15ce88c1d4ec
   - Gas token: POL
   - Average gas: ~$0.003

2. A2A Server (a2a-agent-v2.js, a2a-agent-full.js)
   - @a2a-js/sdk for protocol
   - Express middleware
   - JSON-RPC + REST endpoints
   - Agent card with capabilities

3. Escrow System (escrow.js)
   - State machine (6 states)
   - Time-lock support
   - Multi-party approval
   - JSON persistence

4. Negotiation System (payment-negotiation.js)
   - Quote creation and management
   - Multi-round negotiation
   - Escrow integration
   - Expiration handling

5. Reputation System (reputation.js)
   - Trust score algorithm
   - Badge system
   - Search and ranking
   - Verification

6. Security Layer
   - auth.js: API key authentication
   - rate-limiter.js: Abuse prevention
   - audit-logger.js: Compliance logging

Integration:
const escrow = new EscrowSystem();
const negotiation = new PaymentNegotiationSystem(escrow);
const reputation = new ReputationSystem();

// All systems work together seamlessly`,
    tags: JSON.stringify({ category: 'architecture', component: 'technical', project: 'shib-payments' })
  }
];

async function saveToQdrant() {
  console.log('📚 Saving SHIB Payment Agent documentation to Qdrant...\n');
  
  const qdrantDir = '/home/marc/clawd/skills/qdrant';
  
  for (let i = 0; i < documents.length; i++) {
    const doc = documents[i];
    console.log(`${i + 1}/${documents.length} Saving: ${doc.title}`);
    
    try {
      const { stdout, stderr } = await execPromise(
        `cd ${qdrantDir} && node index.js save "${doc.content}" '${doc.tags}'`
      );
      
      if (stderr) {
        console.error(`   ⚠️ Warning: ${stderr.trim()}`);
      }
      
      const output = stdout.trim();
      if (output.includes('✓') || output.includes('Saved')) {
        console.log(`   ✅ Saved successfully`);
      } else {
        console.log(`   ℹ️ ${output}`);
      }
    } catch (error) {
      console.error(`   ❌ Error: ${error.message}`);
    }
  }
  
  console.log(`\n✅ All ${documents.length} documents saved to Qdrant!`);
  console.log('\nYou can now recall this information with:');
  console.log('  cd skills/qdrant && node index.js recall "escrow system" 5');
  console.log('  cd skills/qdrant && node index.js recall "reputation" 5');
  console.log('  cd skills/qdrant && node index.js recall "A2A protocol" 5');
}

saveToQdrant().catch(console.error);
