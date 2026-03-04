#!/usr/bin/env node
/**
 * YouTube Music Controller
 * Controls YouTube Music via OpenClaw browser automation
 */

const { execSync } = require('child_process');
const path = require('path');

const YOUTUBE_MUSIC_URL = 'https://music.youtube.com';

/**
 * Send command to OpenClaw browser
 */
function browserAction(action, params = {}) {
  try {
    const cmd = `openclaw browser ${action} ${Object.entries(params)
      .map(([k, v]) => `--${k}="${v}"`)
      .join(' ')}`;
    return execSync(cmd, { encoding: 'utf8' });
  } catch (error) {
    console.error('Browser action failed:', error.message);
    throw error;
  }
}

/**
 * Ensure browser is running
 */
function ensureBrowser() {
  try {
    const status = browserAction('status');
    if (!status.includes('"running": true')) {
      console.log('Starting browser...');
      browserAction('start');
    }
  } catch (error) {
    console.log('Browser not available, starting...');
    browserAction('start');
  }
}

/**
 * Search YouTube Music
 */
async function search(query) {
  const url = `${YOUTUBE_MUSIC_URL}/search?q=${encodeURIComponent(query)}`;
  browserAction('open', { targetUrl: url });
  console.log(`Searching for: ${query}`);
}

/**
 * Play a specific track
 */
async function play(query) {
  ensureBrowser();
  
  if (query.includes('youtube.com') || query.includes('youtu.be')) {
    // Direct URL
    browserAction('open', { targetUrl: query });
  } else {
    // Search and play first result
    const url = `${YOUTUBE_MUSIC_URL}/search?q=${encodeURIComponent(query + ' song')}`;
    browserAction('open', { targetUrl: url });
  }
  
  console.log(`Playing: ${query}`);
}

/**
 * Playback controls
 */
function control(action) {
  const controls = {
    play: 'ref=e855',    // Play button
    pause: 'ref=e855',   // Pause button (same ref, different state)
    next: 'ref=e1744',   // Next track
    previous: 'ref=e1734', // Previous track
  };
  
  console.log(`Control: ${action}`);
  // Would need snapshot to get current refs
}

/**
 * Set volume
 */
function setVolume(level) {
  console.log(`Setting volume to ${level}%`);
  // Would need to interact with volume slider
}

/**
 * Get current track info
 */
async function nowPlaying() {
  console.log('Getting current track...');
  // Would need snapshot to read current track info
}

// Main command handler
const args = process.argv.slice(2);
const command = args[0];

if (!command) {
  console.log(`
YouTube Music Controller 🎵

Usage:
  node control-youtube-music.js play <query>
  node control-youtube-music.js search <query>
  node control-youtube-music.js pause
  node control-youtube-music.js skip
  node control-youtube-music.js volume <level>
  node control-youtube-music.js now-playing

Examples:
  node control-youtube-music.js play "Ye Tune Kya Kiya"
  node control-youtube-music.js search "Arijit Singh"
  node control-youtube-music.js pause
  node control-youtube-music.js skip
  node control-youtube-music.js volume 75
  node control-youtube-music.js now-playing
`);
  process.exit(0);
}

// Command routing
switch (command) {
  case 'play':
    play(args.slice(1).join(' '));
    break;
  case 'search':
    search(args.slice(1).join(' '));
    break;
  case 'pause':
  case 'stop':
    control('pause');
    break;
  case 'skip':
  case 'next':
    control('next');
    break;
  case 'previous':
  case 'back':
    control('previous');
    break;
  case 'volume':
    setVolume(args[1]);
    break;
  case 'now-playing':
    nowPlaying();
    break;
  default:
    console.error(`Unknown command: ${command}`);
    process.exit(1);
}
