/**
 * Trading Agent Example — Polymarket
 *
 * Demonstrates an autonomous trading agent with:
 *   - $100/tx limit, $2000/day budget
 *   - USDC spend policy on Base
 *   - Auto-queues over-limit trades for owner approval
 */

import { createWalletClient, http, parseUnits, type Address } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { base } from 'viem/chains';
import {
  createWallet,
  setSpendPolicy,
  agentTransferToken,
  checkBudget,
  deployWallet,
  onTransactionQueued,
  NATIVE_TOKEN,
} from '../src/index.js';

// ─── Config ───
const AGENT_PRIVATE_KEY = process.env.AGENT_PRIVATE_KEY as `0x${string}`;
const WALLET_ADDRESS = process.env.AGENT_WALLET as Address;
const USDC = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913' as Address; // USDC on Base
const POLYMARKET_CTF_EXCHANGE = '0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E' as Address; // example

const LIMITS = {
  perTx: parseUnits('100', 6),       // $100 max per trade
  perDay: parseUnits('2000', 6),     // $2,000 daily budget
};

async function main() {
  // 1. Create agent signer
  const agentAccount = privateKeyToAccount(AGENT_PRIVATE_KEY);
  const walletClient = createWalletClient({
    account: agentAccount,
    chain: base,
    transport: http(process.env.RPC_URL),
  });

  // 2. Connect to the AgentAccountV2
  const wallet = createWallet({
    accountAddress: WALLET_ADDRESS,
    chain: 'base',
    rpcUrl: process.env.RPC_URL,
    walletClient,
  });

  console.log(`🤖 Trading agent connected to wallet: ${wallet.address}`);

  // 3. Check current budget
  const budget = await checkBudget(wallet, USDC);
  console.log(`💰 Budget remaining: $${Number(budget.remainingInPeriod) / 1e6} / $2000`);
  console.log(`   Per-tx limit: $${Number(budget.perTxLimit) / 1e6}`);

  // 4. Listen for queued transactions (over-limit trades)
  const unwatch = onTransactionQueued(wallet, (event) => {
    console.log(`⚠️  Trade queued for owner approval!`);
    console.log(`   TxId: ${event.txId}, Amount: $${Number(event.amount) / 1e6}`);
    console.log(`   → Notify owner via push notification / Telegram / etc.`);
  });

  // 5. Simulate trading loop
  const markets = [
    { name: 'BTC > $150k by March', outcome: 'YES', size: parseUnits('50', 6) },
    { name: 'Fed cuts rates in Q1', outcome: 'YES', size: parseUnits('75', 6) },
    { name: 'ETH flips BTC', outcome: 'NO', size: parseUnits('25', 6) },
    { name: 'Big whale trade attempt', outcome: 'YES', size: parseUnits('500', 6) }, // over limit!
  ];

  for (const market of markets) {
    console.log(`\n📊 Trading: ${market.name} — ${market.outcome} — $${Number(market.size) / 1e6}`);

    try {
      // In production, this would encode the actual Polymarket CTF exchange calldata.
      // Here we show the spend-limit flow with a simple USDC transfer.
      const hash = await agentTransferToken(wallet, {
        token: USDC,
        to: POLYMARKET_CTF_EXCHANGE,
        amount: market.size,
      });
      console.log(`   ✅ Executed: ${hash}`);
    } catch (err: any) {
      console.log(`   ❌ Error: ${err.message}`);
    }

    // Brief pause between trades
    await new Promise((r) => setTimeout(r, 1000));
  }

  // 6. Final budget check
  const finalBudget = await checkBudget(wallet, USDC);
  console.log(`\n📈 Final budget remaining: $${Number(finalBudget.remainingInPeriod) / 1e6}`);

  unwatch();
}

main().catch(console.error);
