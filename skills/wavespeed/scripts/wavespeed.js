#!/usr/bin/env node
/**
 * WaveSpeed AI CLI — Generate images and videos via 700+ models
 * Usage:
 *   wavespeed.js generate --model <model-id> --prompt "..." [--output file.png]
 *   wavespeed.js edit     --model <model-id> --prompt "..." --image <url> [--images <url2>] [--output file.png]
 *   wavespeed.js video    --model <model-id> --prompt "..." [--image <url>] [--output file.mp4]
 *   wavespeed.js models   [--search <query>]
 *   wavespeed.js status   --id <task-id>
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const API_BASE = 'api.wavespeed.ai';
const API_KEY = process.env.WAVESPEED_API_KEY;

// ── Quick model aliases ─────────────────────────────────────────────────────
const ALIASES = {
  'nbp':        'google/nano-banana-pro/edit',
  'nbp-edit':   'google/nano-banana-pro/edit',
  'nb-edit':    'google/nano-banana/edit',
  'flux':       'wavespeed-ai/flux-dev',
  'flux-schnell': 'wavespeed-ai/flux-schnell',
  'flux-pro':   'wavespeed-ai/flux-pro-v1.1-ultra',
  'sdxl':       'wavespeed-ai/stable-diffusion-xl',
  'seedream':   'bytedance/seedream-v3.1',
  'qwen':       'wavespeed-ai/qwen-image/text-to-image',
  'kling':      'kling-ai/kling-o1/image-to-video-pro',
  'veo':        'google/veo-3.1/text-to-video',
  'sora':       'openai/sora-2/text-to-video',
  'wan-i2v':    'wavespeed-ai/wan-2.2/i2v-720p',
  'wan-t2v':    'alibaba/wan-2.6/image-to-video-pro',
  'hailuo':     'minimax/hailuo-02/i2v-standard',
  'upscale':    'wavespeed-ai/ultimate-video-upscaler',
};

function resolveModel(id) {
  return ALIASES[id] || id;
}

// ── HTTP helpers ─────────────────────────────────────────────────────────────
function req(method, apiPath, body) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const opts = {
      hostname: API_BASE,
      path: apiPath,
      method,
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
        ...(data ? { 'Content-Length': Buffer.byteLength(data) } : {}),
      },
    };
    const r = https.request(opts, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        try { resolve(JSON.parse(d)); }
        catch { resolve({ raw: d }); }
      });
    });
    r.on('error', reject);
    if (data) r.write(data);
    r.end();
  });
}

async function submit(modelId, params) {
  const resp = await req('POST', `/api/v3/${modelId}`, params);
  if (resp.code !== 200) throw new Error(`Submit failed: ${resp.message} (code ${resp.code})`);
  return resp.data;
}

async function poll(taskId, maxMs = 300000) {
  const start = Date.now();
  while (Date.now() - start < maxMs) {
    await new Promise(r => setTimeout(r, 2000));
    const resp = await req('GET', `/api/v3/predictions/${taskId}/result`);
    if (resp.code !== 200) throw new Error(`Poll failed: ${resp.message}`);
    const d = resp.data;
    process.stderr.write(`\r⏳ ${d.status} (${Math.round((Date.now() - start) / 1000)}s)...`);
    if (d.status === 'completed') {
      process.stderr.write('\n');
      return d.outputs;
    }
    if (d.status === 'failed') throw new Error(`Generation failed: ${d.error}`);
  }
  throw new Error('Timeout waiting for result');
}

async function download(url, dest) {
  return new Promise((resolve, reject) => {
    const proto = url.startsWith('https') ? https : require('http');
    const f = fs.createWriteStream(dest);
    proto.get(url, res => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        f.close();
        return download(res.headers.location, dest).then(resolve).catch(reject);
      }
      res.pipe(f);
      f.on('finish', () => f.close(resolve));
    }).on('error', reject);
  });
}

// ── Commands ─────────────────────────────────────────────────────────────────
async function cmdGenerate(args) {
  const modelId = resolveModel(args.model || 'flux');
  const params = {
    prompt: args.prompt,
    ...(args.size ? { size: args.size } : {}),
    ...(args.width ? { width: parseInt(args.width) } : {}),
    ...(args.height ? { height: parseInt(args.height) } : {}),
    ...(args.seed ? { seed: parseInt(args.seed) } : {}),
  };
  console.error(`🎨 Generating with ${modelId}...`);
  const task = await submit(modelId, params);
  console.error(`📋 Task ID: ${task.id}`);
  const outputs = await poll(task.id);
  return handleOutputs(outputs, args.output, 'generated');
}

async function cmdEdit(args) {
  const modelId = resolveModel(args.model || 'nbp');
  const images = [
    ...(args.image ? [args.image] : []),
    ...(args.images ? args.images.split(',').map(s => s.trim()) : []),
  ];
  if (!images.length) throw new Error('--image <url> required for edit');
  const params = {
    prompt: args.prompt,
    images,
    ...(args.seed ? { seed: parseInt(args.seed) } : {}),
  };
  console.error(`✏️  Editing with ${modelId}...`);
  const task = await submit(modelId, params);
  console.error(`📋 Task ID: ${task.id}`);
  const outputs = await poll(task.id);
  return handleOutputs(outputs, args.output, 'edited');
}

async function cmdVideo(args) {
  const modelId = resolveModel(args.model || 'wan-i2v');
  const params = {
    prompt: args.prompt,
    ...(args.image ? { image: args.image } : {}),
    ...(args.duration ? { duration: parseInt(args.duration) } : {}),
  };
  console.error(`🎬 Generating video with ${modelId}...`);
  const task = await submit(modelId, params);
  console.error(`📋 Task ID: ${task.id}`);
  const outputs = await poll(task.id, 600000); // videos take longer
  return handleOutputs(outputs, args.output, 'video');
}

async function cmdStatus(args) {
  if (!args.id) throw new Error('--id <task-id> required');
  const resp = await req('GET', `/api/v3/predictions/${args.id}/result`);
  if (resp.code !== 200) throw new Error(resp.message);
  const d = resp.data;
  console.log(`Status: ${d.status}`);
  if (d.outputs?.length) console.log(`Outputs:\n${d.outputs.join('\n')}`);
  if (d.error) console.log(`Error: ${d.error}`);
  return d;
}

async function cmdModels(args) {
  console.log('=== WaveSpeed AI Model Aliases ===\n');
  for (const [alias, id] of Object.entries(ALIASES)) {
    console.log(`  ${alias.padEnd(16)} → ${id}`);
  }
  console.log('\nUse full model IDs like: google/nano-banana-pro/edit');
  console.log('Browse all 700+ models at: https://wavespeed.ai/models');
}

async function handleOutputs(outputs, outputFlag, defaultPrefix) {
  if (!outputs?.length) throw new Error('No outputs returned');
  
  const results = [];
  for (let i = 0; i < outputs.length; i++) {
    const url = outputs[i];
    let dest;
    if (outputFlag) {
      dest = outputs.length === 1 ? outputFlag : outputFlag.replace(/(\.\w+)$/, `-${i+1}$1`);
    } else {
      const ext = url.match(/\.(png|jpg|jpeg|webp|mp4|gif)/i)?.[1] || 'png';
      dest = `${defaultPrefix}-${Date.now()}${i > 0 ? `-${i+1}` : ''}.${ext}`;
    }
    console.error(`⬇️  Downloading → ${dest}`);
    await download(url, dest);
    console.log(dest);
    results.push(dest);
  }
  return results;
}

// ── Arg parser ───────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const cmd = argv[0];
  const args = {};
  for (let i = 1; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      args[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    }
  }
  return { cmd, args };
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  if (!API_KEY) {
    console.error('❌ WAVESPEED_API_KEY env var not set');
    process.exit(1);
  }
  const { cmd, args } = parseArgs(process.argv.slice(2));
  
  switch (cmd) {
    case 'generate': await cmdGenerate(args); break;
    case 'edit':     await cmdEdit(args);     break;
    case 'video':    await cmdVideo(args);    break;
    case 'status':   await cmdStatus(args);   break;
    case 'models':   await cmdModels(args);   break;
    default:
      console.error('Commands: generate | edit | video | status | models');
      console.error('');
      console.error('Examples:');
      console.error('  wavespeed.js generate --model flux --prompt "sunset over mountains" --output out.png');
      console.error('  wavespeed.js edit --model nbp --prompt "change to black hoodie" --image https://... --output avatar.png');
      console.error('  wavespeed.js video --model wan-i2v --prompt "camera slowly zooms in" --image https://... --output video.mp4');
      console.error('  wavespeed.js models');
      process.exit(1);
  }
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
