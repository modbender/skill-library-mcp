#!/usr/bin/env node
/**
 * Generate a 3D avatar via Sideload.gg
 * Payment via x402 — pass a pre-signed payment token.
 *
 * Usage:
 *   node generate.js --prompt "A cyberpunk samurai" --x402-token <token>
 *   node generate.js --image https://example.com/character.png --x402-token <token>
 *   node generate.js --image /path/to/photo.jpg --x402-token <token>
 *   node generate.js --probe  (check cost without paying)
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import { dirname, join, extname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUTPUT_DIR = join(__dirname, '..', 'output');

const SIDELOAD_API = 'https://sideload.gg/api/agent/generate';
const POLL_INTERVAL = 5000;
const MAX_POLL_ATTEMPTS = 120; // 10 minutes

// --- Parse CLI args ---

const args = process.argv.slice(2);
let prompt = '';
let imageInput = '';
let outputName = '';
let skipDownload = false;
let x402Token = '';
let probeOnly = false;

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case '--prompt': prompt = args[++i]; break;
    case '--image': imageInput = args[++i]; break;
    case '--output': outputName = args[++i]; break;
    case '--no-download': skipDownload = true; break;
    case '--x402-token': x402Token = args[++i]; break;
    case '--probe': probeOnly = true; break;
  }
}

if (!prompt && !imageInput && !probeOnly) {
  console.error('Usage:');
  console.error('  node generate.js --prompt "description" --x402-token <token>');
  console.error('  node generate.js --image <url or path> --x402-token <token>');
  console.error('  node generate.js --probe  (check cost without paying)');
  console.error('');
  console.error('Options:');
  console.error('  --x402-token <token>  x402 payment token (required for generation)');
  console.error('  --output <name>       Custom filename for downloads');
  console.error('  --no-download         Skip downloading result files');
  console.error('  --probe               Check price without generating');
  process.exit(1);
}

console.log('🎭 Sideload Avatar Generator');
console.log('============================');
console.log('');

// --- Probe mode: just check the cost ---

if (probeOnly) {
  console.log('🔍 Probing payment requirements...');
  console.log('');

  const response = await fetch(SIDELOAD_API, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type: 'text', prompt: 'probe' })
  });

  if (response.status === 402) {
    const paymentHeader = response.headers.get('payment-required');
    if (paymentHeader) {
      const decoded = JSON.parse(Buffer.from(paymentHeader, 'base64').toString());
      const req = decoded.accepts?.[0];
      if (req) {
        const amount = parseInt(req.maxAmountRequired || req.amount || 0);
        console.log(`💵 Cost:    $${(amount / 1e6).toFixed(2)} USDC`);
        console.log(`📍 Pay to:  ${req.payTo}`);
        console.log(`🔗 Network: Base (chain ID 8453)`);
        console.log(`💰 Asset:   USDC (${req.asset})`);
        console.log('');
        console.log('Raw payment requirements:');
        console.log(JSON.stringify(decoded, null, 2));
      }
    }
  } else {
    console.log(`Unexpected status: ${response.status}`);
  }
  process.exit(0);
}

// --- Check payment token ---

if (!x402Token) {
  console.error('❌ No x402 payment token provided');
  console.error('');
  console.error('   Use --x402-token <token> to pass your payment authorization.');
  console.error('   Use --probe to check the cost first.');
  console.error('');
  console.error('   Sign an x402 payment with your preferred wallet/signer,');
  console.error('   then pass the base64-encoded token to this script.');
  process.exit(1);
}

// --- Build request body ---

let body;

if (prompt) {
  console.log(`Mode:   text`);
  console.log(`Prompt: ${prompt}`);
  body = { type: 'text', prompt };
} else if (imageInput.startsWith('http://') || imageInput.startsWith('https://')) {
  console.log(`Mode:  image (URL)`);
  console.log(`Image: ${imageInput}`);
  body = { type: 'image', imageUrl: imageInput };
} else {
  if (!existsSync(imageInput)) {
    console.error(`❌ File not found: ${imageInput}`);
    process.exit(1);
  }
  console.log(`Mode:  image (local file)`);
  console.log(`Image: ${imageInput}`);
  const imageData = readFileSync(imageInput);
  const ext = extname(imageInput).toLowerCase();
  const mimeType = ext === '.png' ? 'image/png' : ext === '.webp' ? 'image/webp' : 'image/jpeg';
  body = { type: 'image', image: `data:${mimeType};base64,${imageData.toString('base64')}` };
}

console.log('');

// --- Submit generation ---

console.log('🚀 Submitting generation request...');

try {
  const response = await fetch(SIDELOAD_API, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-PAYMENT': x402Token
    },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    const errText = await response.text();
    let errData;
    try { errData = JSON.parse(errText); } catch { errData = errText; }

    if (response.status === 402) {
      console.error('❌ Payment rejected — token may be invalid, expired, or insufficient.');
      console.error('   Use --probe to check current pricing.');
    } else {
      console.error(`❌ API returned ${response.status}:`, errData);
    }
    process.exit(1);
  }

  // Parse settlement info
  let payment;
  const paymentResponse = response.headers.get('x-payment-response');
  if (paymentResponse) {
    try { payment = JSON.parse(Buffer.from(paymentResponse, 'base64').toString()); }
    catch { /* ignore */ }
  }

  const data = await response.json();

  if (payment?.txHash) {
    console.log(`💸 TX: https://basescan.org/tx/${payment.txHash}`);
  }

  const jobId = data.jobId;
  if (!jobId) {
    console.error('❌ No jobId in response:', data);
    process.exit(1);
  }

  console.log(`✅ Job submitted: ${jobId}`);
  console.log('');

  // --- Poll for completion ---

  console.log('⏳ Waiting for generation...');

  const fullStatusUrl = data.statusUrl?.startsWith('http')
    ? data.statusUrl
    : `https://sideload.gg${data.statusUrl}`;

  let result = null;

  for (let attempt = 0; attempt < MAX_POLL_ATTEMPTS; attempt++) {
    await new Promise(r => setTimeout(r, POLL_INTERVAL));

    const statusRes = await fetch(fullStatusUrl);
    const statusData = await statusRes.json();

    if (statusData.status === 'completed') {
      result = statusData.result;
      break;
    }

    if (statusData.status === 'failed') {
      console.error(`\n❌ Generation failed: ${statusData.error || 'Unknown error'}`);
      process.exit(1);
    }

    const step = statusData.stepDescription || statusData.step || 'processing';
    const progress = statusData.progress != null ? ` (${statusData.progress}%)` : '';
    process.stdout.write(`\r   ${step}${progress}    `);
  }

  if (!result) {
    console.error('\n❌ Generation timed out');
    process.exit(1);
  }

  console.log('\n');
  console.log('✅ Avatar generated!');
  console.log('');
  console.log('📦 Results:');
  if (result.glbUrl) console.log(`   GLB:   ${result.glbUrl}`);
  if (result.vrmUrl) console.log(`   VRM:   ${result.vrmUrl}`);
  if (result.mmlUrl) console.log(`   MML:   ${result.mmlUrl}`);
  if (result.processedImageUrl) console.log(`   Image: ${result.processedImageUrl}`);
  console.log('');

  // --- Download ---

  if (!skipDownload) {
    if (!existsSync(OUTPUT_DIR)) mkdirSync(OUTPUT_DIR, { recursive: true });

    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '');
    const baseName = outputName || `avatar_${timestamp}`;

    const downloads = [
      { url: result.glbUrl, ext: '.glb', label: 'GLB' },
      { url: result.vrmUrl, ext: '.vrm', label: 'VRM' },
      { url: result.processedImageUrl, ext: '.png', label: 'PNG' },
    ];

    console.log('📥 Downloading...');
    for (const { url, ext, label } of downloads) {
      if (!url) continue;
      try {
        const res = await fetch(url);
        if (res.ok) {
          const buffer = Buffer.from(await res.arrayBuffer());
          const filePath = join(OUTPUT_DIR, `${baseName}${ext}`);
          writeFileSync(filePath, buffer);
          console.log(`   ✅ ${label}: ${filePath}`);
        } else {
          console.log(`   ⚠️  ${label}: download failed (${res.status})`);
        }
      } catch (e) {
        console.log(`   ⚠️  ${label}: ${e.message}`);
      }
    }
  }

  console.log('');
  console.log('📋 Full response:');
  console.log(JSON.stringify({ jobId, ...result }, null, 2));

} catch (error) {
  console.error(`❌ Error: ${error.message}`);
  process.exit(1);
}
