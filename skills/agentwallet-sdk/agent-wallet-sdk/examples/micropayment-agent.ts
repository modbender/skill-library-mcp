/**
 * Micropayment Agent Example — Agent-to-Agent API Payments
 *
 * Demonstrates an agent paying other agents for API calls:
 *   - $5/tx limit, $50/day budget
 *   - Pay-per-call for AI inference, data feeds, compute
 *   - Automatic queuing when budget exhausted
 */

import { createWalletClient, http, parseUnits, type Address } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { base } from 'viem/chains';
import {
  createWallet,
  agentTransferToken,
  checkBudget,
  onTransactionQueued,
} from '../src/index.js';

// ─── Config ───
const AGENT_PRIVATE_KEY = process.env.AGENT_PRIVATE_KEY as `0x${string}`;
const WALLET_ADDRESS = process.env.AGENT_WALLET as Address;
const USDC = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913' as Address;

const LIMITS = {
  perTx: parseUnits('5', 6),    // $5 max per API call
  perDay: parseUnits('50', 6),  // $50 daily budget
};

// Simulated agent service registry
const AGENT_SERVICES: Record<string, { wallet: Address; priceUsd: number; name: string }> = {
  'sentiment-v2': {
    wallet: '0x1111111111111111111111111111111111111111' as Address,
    priceUsd: 0.50,
    name: 'Sentiment Analysis Agent',
  },
  'price-oracle': {
    wallet: '0x2222222222222222222222222222222222222222' as Address,
    priceUsd: 0.10,
    name: 'Price Oracle Agent',
  },
  'research-deep': {
    wallet: '0x3333333333333333333333333333333333333333' as Address,
    priceUsd: 2.00,
    name: 'Deep Research Agent',
  },
};

/**
 * Pay an agent for an API call, then call their endpoint.
 */
async function callAgentAPI(
  wallet: ReturnType<typeof createWallet>,
  serviceId: string,
  payload: any
): Promise<{ paid: boolean; response: string }> {
  const service = AGENT_SERVICES[serviceId];
  if (!service) throw new Error(`Unknown service: ${serviceId}`);

  const amount = parseUnits(service.priceUsd.toString(), 6);
  console.log(`  💸 Paying ${service.name}: $${service.priceUsd}`);

  // Pay the agent's wallet
  const hash = await agentTransferToken(wallet, {
    token: USDC,
    to: service.wallet,
    amount,
  });

  console.log(`  📝 Payment tx: ${hash}`);

  // In production: include tx hash as proof-of-payment in API call
  // const response = await fetch(service.endpoint, {
  //   headers: { 'X-Payment-Tx': hash },
  //   body: JSON.stringify(payload),
  // });

  return {
    paid: true,
    response: `[Simulated ${service.name} response for ${JSON.stringify(payload)}]`,
  };
}

async function main() {
  const agentAccount = privateKeyToAccount(AGENT_PRIVATE_KEY);
  const walletClient = createWalletClient({
    account: agentAccount,
    chain: base,
    transport: http(process.env.RPC_URL),
  });

  const wallet = createWallet({
    accountAddress: WALLET_ADDRESS,
    chain: 'base',
    rpcUrl: process.env.RPC_URL,
    walletClient,
  });

  console.log(`🤖 Micropayment agent online: ${wallet.address}`);
  console.log(`   Limits: $${Number(LIMITS.perTx) / 1e6}/tx, $${Number(LIMITS.perDay) / 1e6}/day\n`);

  // Alert on queued transactions
  const unwatch = onTransactionQueued(wallet, (event) => {
    console.log(`\n🚨 Budget exceeded! Transaction queued (ID: ${event.txId})`);
    console.log(`   Amount: $${Number(event.amount) / 1e6} — awaiting owner approval`);
  });

  // Simulate a research workflow that calls multiple agent APIs
  console.log('📋 Starting research workflow...\n');

  // Step 1: Get sentiment data
  console.log('Step 1: Sentiment analysis');
  const sentiment = await callAgentAPI(wallet, 'sentiment-v2', { topic: 'BTC', timeframe: '24h' });
  console.log(`  ✅ ${sentiment.response}\n`);

  // Step 2: Get price data
  console.log('Step 2: Price oracle');
  const price = await callAgentAPI(wallet, 'price-oracle', { asset: 'BTC' });
  console.log(`  ✅ ${price.response}\n`);

  // Step 3: Deep research (more expensive)
  console.log('Step 3: Deep research');
  const research = await callAgentAPI(wallet, 'research-deep', {
    query: 'BTC macro outlook Q1 2026',
  });
  console.log(`  ✅ ${research.response}\n`);

  // Check remaining budget
  const budget = await checkBudget(wallet, USDC);
  console.log(`💰 Remaining budget: $${Number(budget.remainingInPeriod) / 1e6} / $50`);
  console.log(`   Total spent this session: $${50 - Number(budget.remainingInPeriod) / 1e6}`);

  unwatch();
}

main().catch(console.error);
