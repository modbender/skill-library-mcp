// sounds.js — WoW-style voice confirmations for CLI operations
// Pre-generated ElevenLabs clips shipped with the skill. No API key needed.

import { execFile } from 'child_process';
import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SOUNDS_DIR = join(__dirname, '..', 'sounds');

// Available sound bites
const CLIPS = {
  'guard-active':       'guard-active.mp3',
  'stake-locked':       'stake-locked.mp3',
  'blocked':            'blocked.mp3',
  'approved':           'approved.mp3',
  'escrow-sealed':      'escrow-sealed.mp3',
  'criteria-set':       'criteria-set.mp3',
  'task-received':      'task-received.mp3',
  'deliverable-sent':   'deliverable-sent.mp3',
  'verified':           'verified.mp3',
  'payment-released':   'payment-released.mp3',
  'unstaked':            'unstaked.mp3',
  'mission-complete':   'mission-complete.mp3',
  'error':              'error.mp3',
  'insufficient-funds': 'insufficient-funds.mp3',
  'ready':              'ready.mp3',
};

let enabled = true;
let player = null;

import { execFileSync } from 'child_process';

function detectPlayerSync() {
  if (player !== null) return player;
  
  const candidates = [
    { cmd: 'mpv', args: ['--no-video', '--really-quiet'] },
    { cmd: 'ffplay', args: ['-nodisp', '-autoexit', '-loglevel', 'quiet'] },
    { cmd: 'play', args: ['-q'] },
  ];
  
  for (const c of candidates) {
    try {
      execFileSync('which', [c.cmd], { stdio: 'ignore' });
      player = c;
      return player;
    } catch { /* not found */ }
  }
  
  player = false;
  return false;
}

/**
 * Play a sound bite. Non-blocking, fire-and-forget.
 * @param {string} name - Clip name (e.g. 'approved', 'blocked', 'verified')
 */
export function playSound(name) {
  if (!enabled) return;
  
  const clip = CLIPS[name];
  if (!clip) return;
  
  const path = join(SOUNDS_DIR, clip);
  if (!existsSync(path)) return;
  
  const p = detectPlayerSync();
  if (!p) return;
  
  // Fire and forget — don't block the CLI
  try {
    const child = execFile(p.cmd, [...p.args, path], { stdio: 'ignore' });
    child.unref();
  } catch {
    // Audio playback is best-effort
  }
}

/**
 * Play sound and wait for it to finish.
 * Use for important moments (mission-complete, error).
 */
export function playSoundSync(name) {
  if (!enabled) return;
  
  const clip = CLIPS[name];
  if (!clip) return;
  
  const path = join(SOUNDS_DIR, clip);
  if (!existsSync(path)) return;
  
  const p = detectPlayerSync();
  if (!p) return;
  
  try {
    execFileSync(p.cmd, [...p.args, path], { stdio: 'ignore', timeout: 5000 });
  } catch {
    // Best-effort
  }
}

/**
 * Enable/disable sounds globally.
 */
export function setSoundsEnabled(flag) {
  enabled = !!flag;
}

/**
 * Check if sounds are available (player + sound files exist).
 */
export function soundsAvailable() {
  return detectPlayerSync() !== false && existsSync(SOUNDS_DIR);
}
