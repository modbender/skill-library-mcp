#!/usr/bin/env node
/**
 * TikTok Video Pipeline v2 — Main Orchestrator
 * =============================================
 * End-to-end: script_text → Veo base video → caption overlay → audio mix → final MP4
 *
 * Usage:
 *   node generate.js \
 *     --product-id rain_cloud \
 *     --script-text "Hook|Feature 1|Feature 2|Buy now" \
 *     [--lang EN|AR] \
 *     [--logo /path/to/logo.png] \
 *     [--audio /path/to/bgm.mp3] \
 *     [--veo-model veo-3.1-generate-preview] \
 *     [--prompt "Cinematic mist floating..."] \
 *     [--segments 1] \
 *     [--dry-run]
 *
 * Env vars:
 *   GEMINI_API_KEY — required for Veo generation
 */

const { execSync, spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// ── Config ──────────────────────────────────────────────────────────────────
const WORKSPACE = path.resolve(__dirname, '../../..');
const SKILL_DIR = path.resolve(__dirname, '..');
const VEO_SCRIPT = path.resolve(WORKSPACE, 'skills/veo3-video-gen/scripts/generate_video.py');
const OVERLAY_SCRIPT = path.resolve(__dirname, 'tiktok_overlay_engine_v3.py');
const OUTPUT_DIR = path.resolve(WORKSPACE, 'output/tiktok');
const DEFAULT_AUDIO = path.resolve(SKILL_DIR, 'assets/bgm_default.mp3');
const DEFAULT_VEO_MODEL = 'veo-3.1-generate-preview';

// ── Args ─────────────────────────────────────────────────────────────────────
function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    productId: null,
    scriptText: null,
    lang: 'EN',
    logo: null,
    audio: null,
    veoModel: DEFAULT_VEO_MODEL,
    prompt: null,
    segments: 1,
    dryRun: false,
  };
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--product-id':   opts.productId  = args[++i]; break;
      case '--script-text':  opts.scriptText = args[++i]; break;
      case '--lang':         opts.lang       = args[++i].toUpperCase(); break;
      case '--logo':         opts.logo       = args[++i]; break;
      case '--audio':        opts.audio      = args[++i]; break;
      case '--veo-model':    opts.veoModel   = args[++i]; break;
      case '--prompt':       opts.prompt     = args[++i]; break;
      case '--segments':     opts.segments   = parseInt(args[++i], 10); break;
      case '--dry-run':      opts.dryRun     = true; break;
    }
  }
  if (!opts.productId) { console.error('ERROR: --product-id required'); process.exit(1); }
  if (!opts.scriptText) { console.error('ERROR: --script-text required'); process.exit(1); }
  return opts;
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function run(cmd, opts = {}) {
  console.log(`\n▶ ${cmd}\n`);
  return spawnSync('bash', ['-lc', cmd], {
    stdio: 'inherit',
    env: { ...process.env },
    ...opts,
  });
}

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

// ── Steps ────────────────────────────────────────────────────────────────────

function step1_generateBaseVideo(opts, baseVideoPath) {
  console.log('\n━━ Step 1: Generate base video via Veo ━━');

  const prompt = opts.prompt ||
    `Cinematic product showcase, 9:16 vertical, smooth motion, professional lighting, no text`;

  if (!fs.existsSync(VEO_SCRIPT)) {
    throw new Error(`Veo script not found at: ${VEO_SCRIPT}`);
  }

  const cmd = [
    'uv run', JSON.stringify(VEO_SCRIPT),
    '--prompt', JSON.stringify(prompt),
    '--filename', JSON.stringify(baseVideoPath),
    '--model', opts.veoModel,
    '--aspect-ratio', '9:16',
    '--segments', opts.segments,
    '--poll-seconds', '10',
  ].join(' ');

  if (opts.dryRun) {
    console.log('[dry-run] Would run:', cmd);
    // Create dummy mp4 for dry-run testing
    execSync(`ffmpeg -y -f lavfi -i color=c=black:s=1080x1920:d=8 -c:v libx264 ${JSON.stringify(baseVideoPath)} 2>/dev/null`);
    return;
  }

  const r = run(cmd);
  if (r.status !== 0) throw new Error('Veo generation failed');
}

function step2_overlayCaption(opts, baseVideoPath, overlayedPath) {
  console.log('\n━━ Step 2: Caption + logo overlay ━━');

  const logoFlag = opts.logo && fs.existsSync(opts.logo)
    ? `--logo ${JSON.stringify(opts.logo)}`
    : '';

  const cmd = [
    'uv run', JSON.stringify(OVERLAY_SCRIPT),
    '--input', JSON.stringify(baseVideoPath),
    '--output', JSON.stringify(overlayedPath),
    '--captions', JSON.stringify(opts.scriptText),
    '--lang', opts.lang,
    logoFlag,
  ].filter(Boolean).join(' ');

  const r = run(cmd);
  if (r.status !== 0) throw new Error('Overlay engine failed');
}

function step3_mixAudio(opts, overlayedPath, finalPath) {
  console.log('\n━━ Step 3: Mix background audio at 20% ━━');

  // Use provided audio, default asset, or skip
  const audioSrc = opts.audio || (fs.existsSync(DEFAULT_AUDIO) ? DEFAULT_AUDIO : null);

  if (!audioSrc) {
    console.log('No background audio found — copying overlayed video as final (no bgm).');
    fs.copyFileSync(overlayedPath, finalPath);
    return;
  }

  // amix: original audio at 100% + background at 20%
  const cmd = [
    'ffmpeg -y',
    `-i ${JSON.stringify(overlayedPath)}`,
    `-i ${JSON.stringify(audioSrc)}`,
    '-filter_complex',
    '"[0:a]volume=1.0[va];[1:a]volume=0.20[bgm];[va][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"',
    '-map 0:v',
    '-map "[aout]"',
    '-c:v copy',
    '-c:a aac -b:a 192k',
    '-shortest',
    JSON.stringify(finalPath),
  ].join(' ');

  const r = run(cmd);
  if (r.status !== 0) {
    console.warn('Audio mix failed — falling back to overlayed video without bgm');
    fs.copyFileSync(overlayedPath, finalPath);
  }
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const opts = parseArgs();

  ensureDir(OUTPUT_DIR);
  const tmpDir = path.join(OUTPUT_DIR, `.tmp_${opts.productId}_${Date.now()}`);
  ensureDir(tmpDir);

  const baseVideoPath  = path.join(tmpDir, 'base.mp4');
  const overlayedPath  = path.join(tmpDir, 'overlayed.mp4');
  const finalPath      = path.join(OUTPUT_DIR, `${opts.productId}_${opts.lang}_final.mp4`);

  console.log(`\n🎬 TikTok Pipeline v2`);
  console.log(`   Product : ${opts.productId}`);
  console.log(`   Lang    : ${opts.lang}`);
  console.log(`   Output  : ${finalPath}`);
  console.log(`   Dry-run : ${opts.dryRun}`);

  try {
    step1_generateBaseVideo(opts, baseVideoPath);
    step2_overlayCaption(opts, baseVideoPath, overlayedPath);
    step3_mixAudio(opts, overlayedPath, finalPath);

    // Cleanup tmp
    fs.rmSync(tmpDir, { recursive: true, force: true });

    console.log(`\n✅ Pipeline complete!`);
    console.log(`MEDIA:${finalPath}`);
  } catch (err) {
    console.error(`\n❌ Pipeline failed: ${err.message}`);
    process.exit(1);
  }
}

main();
