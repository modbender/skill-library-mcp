/**
 * Publish an agent bet narrative to the frontend broadcast feed.
 *
 * Usage:
 *   npx tsx post-broadcast.ts <type> <market-id|-> <side|-> <stake-eth|-> <confidence> <reasoning>
 *
 * Example:
 *   npx tsx post-broadcast.ts MarketBroadcast 0xabc... yes 0.01 72 "Momentum still favors upside"
 *
 * Environment:
 *   AGENT_PRIVATE_KEY         - Required, used to derive agent address.
 *   AGENT_NAME                - Optional, defaults to shortened address.
 *   AGENT_ENS_NAME            - Optional.
 *   AGENT_ENS_NODE            - Optional bytes32 string.
 *   AGENT_BROADCAST_URL       - Optional, defaults to https://clawlogic.vercel.app/api/agent-broadcasts
 *   AGENT_BROADCAST_ENDPOINT  - Optional alias for AGENT_BROADCAST_URL
 *   AGENT_BROADCAST_API_KEY   - Optional, sent as x-agent-key header.
 *   AGENT_SESSION_ID          - Optional, included in payload.
 *   AGENT_TRADE_TX_HASH       - Optional, included in payload.
 */

import { privateKeyToAccount } from 'viem/accounts';
import { outputError, outputSuccess } from './setup.js';

type BroadcastType =
  | 'MarketBroadcast'
  | 'TradeRationale'
  | 'NegotiationIntent'
  | 'Onboarding';

const VALID_TYPES = new Set<BroadcastType>([
  'MarketBroadcast',
  'TradeRationale',
  'NegotiationIntent',
  'Onboarding',
]);

function parseOptional(input: string | undefined): string | undefined {
  if (!input || input === '-') {
    return undefined;
  }
  return input;
}

function isBytes32(value: string): boolean {
  return /^0x[a-fA-F0-9]{64}$/.test(value);
}

function isTxHash(value: string): boolean {
  return /^0x[a-fA-F0-9]{64}$/.test(value);
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.length < 6) {
    throw new Error(
      'Usage: post-broadcast.ts <type> <market-id|-> <side|-> <stake-eth|-> <confidence> <reasoning>',
    );
  }

  const [
    typeArg,
    marketIdArg,
    sideArg,
    stakeArg,
    confidenceArg,
    ...reasonTokens
  ] = args;

  const type = typeArg as BroadcastType;
  if (!VALID_TYPES.has(type)) {
    throw new Error(`Invalid type "${typeArg}". Must be one of: ${[...VALID_TYPES].join(', ')}`);
  }

  const confidence = Number.parseFloat(confidenceArg);
  if (!Number.isFinite(confidence) || confidence < 0 || confidence > 100) {
    throw new Error(`Invalid confidence "${confidenceArg}". Must be a number from 0 to 100.`);
  }

  const reasoning = reasonTokens.join(' ').trim();
  if (!reasoning) {
    throw new Error('Reasoning is required.');
  }

  const marketId = parseOptional(marketIdArg);
  if (marketId && !isBytes32(marketId)) {
    throw new Error(`Invalid market ID "${marketId}". Expected bytes32 hex string.`);
  }

  const side = parseOptional(sideArg);
  if (side && side !== 'yes' && side !== 'no') {
    throw new Error(`Invalid side "${side}". Must be "yes", "no", or "-".`);
  }

  const stakeEth = parseOptional(stakeArg);
  if (stakeEth !== undefined) {
    const stakeValue = Number.parseFloat(stakeEth);
    if (!Number.isFinite(stakeValue) || stakeValue < 0) {
      throw new Error(`Invalid stake "${stakeEth}". Must be a positive number or "-".`);
    }
  }

  const privateKey = process.env.AGENT_PRIVATE_KEY;
  if (!privateKey) {
    throw new Error('AGENT_PRIVATE_KEY environment variable is not set.');
  }

  const account = privateKeyToAccount(privateKey as `0x${string}`);
  const defaultName = `Agent-${account.address.slice(2, 8)}`;
  const agentName = process.env.AGENT_NAME?.trim() || defaultName;
  const ensName = parseOptional(process.env.AGENT_ENS_NAME);

  const sessionId = parseOptional(process.env.AGENT_SESSION_ID);
  const tradeTxHash = parseOptional(process.env.AGENT_TRADE_TX_HASH);
  if (tradeTxHash && !isTxHash(tradeTxHash)) {
    throw new Error(`Invalid AGENT_TRADE_TX_HASH "${tradeTxHash}".`);
  }

  const endpoint =
    process.env.AGENT_BROADCAST_URL?.trim() ||
    process.env.AGENT_BROADCAST_ENDPOINT?.trim() ||
    'https://clawlogic.vercel.app/api/agent-broadcasts';

  const payload: Record<string, unknown> = {
    type,
    agent: ensName ?? agentName,
    agentAddress: account.address,
    confidence,
    reasoning,
  };

  const ensNode = parseOptional(process.env.AGENT_ENS_NODE);

  if (ensName) {
    payload.ensName = ensName;
  }
  if (ensNode) {
    if (!isBytes32(ensNode)) {
      throw new Error(`Invalid AGENT_ENS_NODE "${ensNode}". Expected bytes32 hex string.`);
    }
    payload.ensNode = ensNode;
  }

  if (marketId) {
    payload.marketId = marketId;
  }
  if (side) {
    payload.side = side;
  }
  if (stakeEth) {
    payload.stakeEth = stakeEth;
  }
  if (sessionId) {
    payload.sessionId = sessionId;
  }
  if (tradeTxHash) {
    payload.tradeTxHash = tradeTxHash;
  }

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  const apiKey = parseOptional(process.env.AGENT_BROADCAST_API_KEY);
  if (apiKey) {
    headers['x-agent-key'] = apiKey;
  }

  const response = await fetch(endpoint, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const details = await response.text();
    throw new Error(`Broadcast post failed (${response.status}): ${details}`);
  }

  const result = await response.json() as { ok?: boolean; event?: { id?: string } };
  outputSuccess({
    endpoint,
    posted: Boolean(result.ok),
    eventId: result.event?.id ?? null,
    payload,
  });
}

main().catch(outputError);
