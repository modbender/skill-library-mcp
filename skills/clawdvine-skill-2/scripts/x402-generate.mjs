#!/usr/bin/env node
/**
 * x402-generate.mjs — Generate a video with automatic x402 payment + polling
 *
 * Usage:
 *   EVM_PRIVATE_KEY=0x... node scripts/x402-generate.mjs "your prompt" [model] [duration]
 *
 * Examples:
 *   EVM_PRIVATE_KEY=0x... node scripts/x402-generate.mjs "A sunset over mountains"
 *   EVM_PRIVATE_KEY=0x... node scripts/x402-generate.mjs "A cat surfing" sora-2 8
 *   EVM_PRIVATE_KEY=0x... node scripts/x402-generate.mjs "Transform this video" xai-grok-imagine 8
 *
 * Required env:
 *   EVM_PRIVATE_KEY=0x...  (wallet with USDC on Base)
 *
 * Required packages:
 *   npm install @x402/fetch @x402/evm viem
 *   (or legacy: npm install x402-fetch viem)
 */

import { privateKeyToAccount } from 'viem/accounts';

const API_BASE = 'https://api.clawdvine.sh';

// --- Parse args ---
const prompt = process.argv[2];
const model = process.argv[3] || 'xai-grok-imagine';
const duration = parseInt(process.argv[4] || '8', 10);
const agentId = process.argv[5] || process.env.CLAWDVINE_AGENT_ID || undefined;

if (!prompt) {
  console.error('Usage: EVM_PRIVATE_KEY=0x... node scripts/x402-generate.mjs "prompt" [model] [duration] [agentId]');
  console.error('Models: xai-grok-imagine (default), sora-2, sora-2-pro');
  process.exit(1);
}

const privateKey = process.env.EVM_PRIVATE_KEY;
if (!privateKey) {
  console.error('Error: EVM_PRIVATE_KEY env var is required');
  process.exit(1);
}

const signer = privateKeyToAccount(privateKey);

// --- Setup x402 payment-wrapped fetch ---
let fetchWithPayment;

try {
  const { wrapFetchWithPayment, x402Client } = await import('@x402/fetch');
  const { registerExactEvmScheme } = await import('@x402/evm/exact/client');
  const client = new x402Client();
  registerExactEvmScheme(client, { signer });
  fetchWithPayment = wrapFetchWithPayment(fetch, client);
} catch {
  const { wrapFetchWithPayment } = await import('x402-fetch');
  fetchWithPayment = wrapFetchWithPayment(fetch, signer);
}

// --- Generate ---
console.log(`\n🎬 Generating video...`);
console.log(`   Prompt:   "${prompt.slice(0, 80)}${prompt.length > 80 ? '...' : ''}"`);
console.log(`   Model:    ${model}`);
console.log(`   Duration: ${duration}s`);
if (agentId) console.log(`   Agent:    ${agentId}`);
console.log();

const res = await fetchWithPayment(`${API_BASE}/generation/create`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ prompt, videoModel: model, duration, ...(agentId && { agentId }) }),
});

const body = await res.json();

if (res.status !== 202 || !body.taskId) {
  console.error('❌ Generation failed:', JSON.stringify(body, null, 2));
  process.exit(1);
}

console.log(`✅ Queued: ${body.taskId}`);
if (body.txHash) {
  console.log(`💳 Payment: ${body.explorer || `https://basescan.org/tx/${body.txHash}`}`);
}
console.log(`⏳ Polling...\n`);

// --- Poll ---
// Kling models (fal-kling-*) take significantly longer to generate (7-15+ min).
// Use model-specific timeouts to avoid premature timeout.
const SLOW_MODELS = ['fal-kling-o3'];
const isSlowModel = SLOW_MODELS.some(m => model.startsWith(m) || model.includes('kling'));
const pollIntervalMs = isSlowModel ? 10000 : 5000;
const maxPolls = isSlowModel ? 120 : 120; // 20 min for Kling, 10 min for others
const timeoutLabel = isSlowModel ? '20 minutes' : '10 minutes';

const taskId = body.taskId;
const startTime = Date.now();

if (isSlowModel) {
  console.log(`ℹ️  Kling model detected — polling every ${pollIntervalMs / 1000}s, timeout ${timeoutLabel}\n`);
}

for (let i = 0; i < maxPolls; i++) {
  await new Promise(r => setTimeout(r, pollIntervalMs));

  const poll = await fetch(`${API_BASE}/generation/${taskId}/status`);
  const status = await poll.json();
  const pct = status.metadata?.percent || status.progress || 0;
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(0);

  if (status.status === 'completed') {
    const gen = status.result?.generation;
    const video = gen?.video;
    const thumb = gen?.image;
    const gif = gen?.gif;
    const shareUrl = `https://clawdvine.sh/media/${taskId}`;
    console.log(`\n🎉 Complete! (${elapsed}s)`);
    console.log(`🎬 Video: ${video}`);
    if (thumb) console.log(`🖼️  Thumb: ${thumb}`);
    if (gif) console.log(`🎞️  GIF:   ${gif}`);
    console.log(`🔗 Share: ${shareUrl}`);
    if (status.txHash) console.log(`💳 TX:    ${status.explorer || `https://basescan.org/tx/${status.txHash}`}`);
    process.exit(0);
  }

  if (status.status === 'failed') {
    console.error(`\n❌ Failed after ${elapsed}s: ${status.error}`);
    process.exit(1);
  }

  process.stdout.write(`\r   ${status.status} ${pct}% (${elapsed}s)`);
}

console.error(`\n❌ Timed out after ${timeoutLabel}`);
process.exit(1);
