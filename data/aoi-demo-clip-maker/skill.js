#!/usr/bin/env node
/**
 * AOI Demo Clip Maker (macOS)
 * S-DNA: AOI-2026-0215-SDNA-CLIP01
 * License: MIT
 */

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const __sdna__ = {
  protocol: 'aoineco-sdna-v1',
  id: 'AOI-2026-0215-SDNA-CLIP01',
  org: 'aoineco-co',
  classification: 'public-safe',
};

const ALLOWED_BINS = new Set(['ffmpeg', 'ffprobe']);

function die(msg, code = 1) {
  console.error(msg);
  process.exit(code);
}

function which(bin) {
  const r = spawnSync('which', [bin], { encoding: 'utf8' });
  return r.status === 0 ? r.stdout.trim() : null;
}

function runAllowed(bin, args) {
  if (!ALLOWED_BINS.has(bin)) throw new Error(`bin not allowed: ${bin}`);
  const p = which(bin);
  if (!p) throw new Error(`missing binary: ${bin}`);

  const res = spawnSync(bin, args, { stdio: 'inherit' });
  if (res.error) throw res.error;
  if (res.status !== 0) throw new Error(`${bin} exited with code ${res.status}`);
}

function parseArgs(argv) {
  let [cmd, sub, ...rest] = argv;

  // Most commands here are single-level (e.g. `record --out ...`).
  // If the second token starts with `--`, it is not a subcommand.
  if (sub && sub.startsWith('--')) {
    rest = [sub, ...rest];
    sub = undefined;
  }

  const args = {};
  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (!a.startsWith('--')) continue;
    const key = a.slice(2);
    const next = rest[i + 1];
    if (next && !next.startsWith('--')) {
      args[key] = next;
      i++;
    } else {
      args[key] = 'true';
    }
  }
  return { cmd, sub, args };
}

function devices() {
  // ffmpeg attempts to open an input; it may return non-zero. That's OK.
  const res = spawnSync('ffmpeg', ['-f', 'avfoundation', '-list_devices', 'true', '-i', ''], { encoding: 'utf8' });
  // Print stderr (where device list is)
  process.stdout.write(res.stderr || '');
  process.exit(0);
}

function tryRecord({ out, dur, fr, device, pix }) {
  const args = [
    '-y',
    '-f', 'avfoundation',
    '-framerate', fr,
    '-pixel_format', pix,
    '-i', device,
    '-t', dur,
    out,
  ];
  const res = spawnSync('ffmpeg', args, { encoding: 'utf8' });
  if (res.status === 0) return { ok: true, pix };
  const stderr = (res.stderr || '').slice(-4000);
  return { ok: false, pix, code: res.status, stderr };
}

function record({ out, duration, fps, screen, pixel }) {
  if (!out) die('--out required');
  if (out.includes('/') || out.includes('..')) die('out must be a filename (no paths)');

  const dur = String(duration || '15');
  const fr = String(fps || '30');
  const device = screen || 'Capture screen 0';

  // Pixel-format fallback order for macOS avfoundation screen capture.
  // uyvy422 is common; nv12 also appears on some systems.
  const fallback = ['uyvy422', 'nv12', 'yuyv422', '0rgb', 'bgr0'];
  const pixels = pixel ? [pixel, ...fallback.filter((p) => p !== pixel)] : fallback;

  let lastErr = null;
  for (const pix of pixels) {
    const r = tryRecord({ out, dur, fr, device, pix });
    if (r.ok) {
      console.error(`[aoi-clip] record ok (pixel_format=${pix})`);
      return;
    }
    lastErr = r;
    console.error(`[aoi-clip] record failed (pixel_format=${pix}, code=${r.code})`);
  }

  die(`record failed for all pixel formats. Last error (pix=${lastErr?.pix}):\n${lastErr?.stderr || ''}`);
}

function getVideoWH(inFile) {
  const res = spawnSync('ffprobe', [
    '-v', 'error',
    '-select_streams', 'v:0',
    '-show_entries', 'stream=width,height',
    '-of', 'csv=p=0',
    inFile,
  ], { encoding: 'utf8' });
  if (res.status !== 0) throw new Error('ffprobe failed');
  const [w, h] = (res.stdout || '').trim().split(',').map(Number);
  if (!Number.isFinite(w) || !Number.isFinite(h)) throw new Error('invalid ffprobe output');
  return { w, h };
}

function recommendTop({ w, h }) {
  // Heuristic: macOS menu bar + title bar tends to be ~90-160px on 1080p.
  // Scale with height.
  const base = Math.round(h * 0.10); // 10% of height
  const clamped = Math.max(80, Math.min(200, base));
  return clamped;
}

function crop({ inFile, out, top }) {
  if (!inFile) die('--in required');
  if (!out) die('--out required');

  let t;
  if (String(top || '') === 'auto') {
    const { w, h } = getVideoWH(inFile);
    t = recommendTop({ w, h });
    console.error(`[aoi-clip] recommend cropTop=${t} (auto, from ${w}x${h})`);
  } else {
    t = Number(top || 150);
  }

  if (!Number.isFinite(t) || t < 0 || t > 600) die('--top invalid (0..600 or auto)');

  runAllowed('ffmpeg', [
    '-y',
    '-i', inFile,
    '-vf', `crop=in_w:in_h-${t}:0:${t}`,
    '-pix_fmt', 'yuv420p',
    out,
  ]);
}

function trim({ inFile, out, from, to }) {
  if (!inFile) die('--in required');
  if (!out) die('--out required');
  if (from == null || to == null) die('--from and --to required');

  runAllowed('ffmpeg', [
    '-y',
    '-ss', String(from),
    '-to', String(to),
    '-i', inFile,
    '-pix_fmt', 'yuv420p',
    out,
  ]);
}

function presetTerminal({ out }) {
  // Opinionated defaults: 15s record + cropTop 150
  const raw = out ? out.replace(/\.mp4$/, '_raw.mp4') : 'demo_raw.mp4';
  const cropOut = out || 'demo.mp4';
  record({ out: raw, duration: 15, fps: 30, screen: 'Capture screen 0', pixel: 'uyvy422' });
  crop({ inFile: raw, out: cropOut, top: 150 });
}

function help() {
  console.log(JSON.stringify({
    __sdna__,
    usage: {
      devices: 'aoi-clip devices',
      record: 'aoi-clip record --out out.mp4 --duration 15 --fps 30 --screen "Capture screen 0" --pixel uyvy422',
      crop: 'aoi-clip crop --in in.mp4 --out out.mp4 --top 150',
      trim: 'aoi-clip trim --in in.mp4 --out out.mp4 --from 0 --to 15',
      preset: 'aoi-clip preset terminal --out demo.mp4'
    }
  }, null, 2));
}

function main() {
  const { cmd, sub, args } = parseArgs(process.argv.slice(2));
  if (!cmd || cmd === 'help' || cmd === '--help' || cmd === '-h') return help();

  if (cmd === 'devices') return devices();

  if (cmd === 'record') {
    return record({ out: args.out, duration: args.duration, fps: args.fps, screen: args.screen, pixel: args.pixel });
  }

  if (cmd === 'crop') {
    return crop({ inFile: args.in, out: args.out, top: args.top });
  }

  if (cmd === 'trim') {
    return trim({ inFile: args.in, out: args.out, from: args.from, to: args.to });
  }

  if (cmd === 'preset') {
    if (sub !== 'terminal') die('Only preset supported: terminal');
    return presetTerminal({ out: args.out });
  }

  die(`Unknown command: ${cmd}`);
}

main();
