#!/usr/bin/env node
/**
 * Snake Game CLI
 *
 * Persistent autoplay daemon for the Trifle Snake game.
 *
 * Usage:
 *   snake start [--strategy NAME] [--detach]  Start playing
 *   snake stop                                 Stop daemon
 *   snake status                               Show daemon status
 *   snake attach                               Tail daemon logs
 *   snake pause                                Pause voting
 *   snake resume                               Resume voting
 *   snake config [key] [value]                 Get/set config
 *   snake strategies                           List available strategies
 *
 * Legacy commands (from original snake-game.mjs):
 *   snake state                                Get current game state
 *   snake vote <dir> <team> [amt]              Submit a vote
 *   snake strategy                             Analyze game (one-shot)
 *   snake balance                              Check ball balance
 */

import { parseArgs } from 'util';
import {
  loadSettings,
  saveSettings,
  getConfig,
  setConfig,
  loadDaemonState,
  saveDaemonState,
  PATHS,
  SERVERS,
  getBackendUrl,
} from './lib/config.mjs';
import {
  isDaemonRunning,
  acquireLock,
  releaseLock,
  stopDaemon,
  pauseDaemon,
  resumeDaemon,
  getDaemonStatus,
  startDaemonBackground,
  tailLogs,
} from './lib/process.mjs';
import { getStrategy, listStrategiesWithInfo, parseGameState } from 'snake-rodeo-agents';
import { getGameState, getBalance, submitVote, getRodeos, isAuthenticated } from './lib/api.mjs';
import { sendTelegram, formatStatus } from './lib/telegram.mjs';
import { runAutoplay } from './daemon/autoplay.mjs';

const args = process.argv.slice(2);
const command = args[0];
const subArgs = args.slice(1);

async function main() {
  switch (command) {
    case 'start':
      await cmdStart();
      break;

    case 'stop':
      cmdStop();
      break;

    case 'status':
      cmdStatus();
      break;

    case 'attach':
    case 'logs':
      cmdAttach();
      break;

    case 'pause':
      cmdPause();
      break;

    case 'resume':
      cmdResume();
      break;

    case 'config':
      cmdConfig();
      break;

    case 'strategies':
    case 'list-strategies':
      cmdListStrategies();
      break;

    case 'daemon':
      // Internal: run the daemon loop (used by start --detach and services)
      await cmdDaemon();
      break;

    // Legacy commands
    case 'state':
      await cmdState();
      break;

    case 'vote':
      await cmdVote();
      break;

    case 'strategy':
    case 'analyze':
      await cmdAnalyze();
      break;

    case 'balance':
      await cmdBalance();
      break;

    case 'rodeos':
      await cmdRodeos();
      break;

    case 'server':
      cmdServer();
      break;

    case 'telegram':
      await cmdTelegram();
      break;

    case 'help':
    case '--help':
    case '-h':
    default:
      showHelp();
      break;
  }
}

// === Command Implementations ===

async function cmdStart() {
  const detach = subArgs.includes('--detach') || subArgs.includes('-d');
  const strategyIdx = subArgs.findIndex(a => a === '--strategy' || a === '-s');
  const strategy = strategyIdx >= 0 ? subArgs[strategyIdx + 1] : undefined;

  if (strategy) {
    setConfig('strategy', strategy);
  }

  const status = isDaemonRunning();
  if (status?.running) {
    console.log(`Daemon already running (PID: ${status.pid})`);
    console.log('Use "snake stop" to stop it first.');
    return;
  }

  if (detach) {
    const result = startDaemonBackground();
    console.log(result.message);
  } else {
    // Run in foreground
    console.log('Starting in foreground (Ctrl+C to stop)...');
    console.log('Use --detach to run in background.');
    console.log('');

    try {
      acquireLock();
      process.on('SIGINT', () => {
        console.log('\nShutting down...');
        releaseLock();
        process.exit(0);
      });
      process.on('SIGTERM', () => {
        releaseLock();
        process.exit(0);
      });

      await runAutoplay();
    } finally {
      releaseLock();
    }
  }
}

function cmdStop() {
  const result = stopDaemon();
  console.log(result.message);
}

function cmdStatus() {
  const status = getDaemonStatus();

  console.log('=== Snake Daemon Status ===');
  console.log(`Running: ${status.running ? `Yes (PID: ${status.pid})` : 'No'}`);
  console.log(`Paused: ${status.paused ? 'Yes' : 'No'}`);
  console.log(`Strategy: ${status.strategy}`);
  console.log(`Server: ${status.server}`);
  console.log(`Telegram: ${status.telegramChatId || 'Not configured'}`);
  console.log('');
  console.log('=== Statistics ===');
  console.log(`Current Team: ${status.currentTeam || 'None'}`);
  console.log(`Games Played: ${status.gamesPlayed}`);
  console.log(`Wins: ${status.wins}`);
  console.log(`Votes Placed: ${status.votesPlaced}`);
  if (status.startedAt) {
    const uptime = Math.floor((Date.now() - status.startedAt) / 1000);
    const hours = Math.floor(uptime / 3600);
    const mins = Math.floor((uptime % 3600) / 60);
    console.log(`Uptime: ${hours}h ${mins}m`);
  }
}

function cmdAttach() {
  const follow = subArgs.includes('-f') || subArgs.includes('--follow');
  const lines = parseInt(subArgs.find(a => /^\d+$/.test(a)) || '50');

  console.log(`Showing last ${lines} log lines${follow ? ' (following)' : ''}...`);
  console.log('---');
  tailLogs(lines, follow);
}

function cmdPause() {
  const result = pauseDaemon();
  console.log(result.message);
}

function cmdResume() {
  const result = resumeDaemon();
  console.log(result.message);
}

function cmdConfig() {
  const key = subArgs[0];
  const value = subArgs[1];

  if (!key) {
    // Show all config
    const settings = loadSettings();
    console.log('=== Snake Configuration ===');
    console.log(JSON.stringify(settings, null, 2));
    console.log('');
    console.log('Usage: snake config <key> [value]');
    console.log('Example: snake config strategy aggressive');
    return;
  }

  if (value === undefined) {
    // Get single value
    const val = getConfig(key);
    console.log(`${key}: ${JSON.stringify(val)}`);
  } else {
    // Set value
    setConfig(key, value);
    console.log(`Set ${key} = ${value}`);
  }
}

function cmdListStrategies() {
  const strategies = listStrategiesWithInfo();

  console.log('=== Available Strategies ===');
  console.log('');
  for (const s of strategies) {
    const aliases = s.aliases.length > 0 ? ` (aliases: ${s.aliases.join(', ')})` : '';
    console.log(`  ${s.name}${aliases}`);
    console.log(`    ${s.description}`);
    console.log('');
  }
  console.log('Use: snake config strategy <name>');
}

async function cmdDaemon() {
  // This is called by detached process or service
  try {
    acquireLock();
    process.on('SIGINT', () => {
      releaseLock();
      process.exit(0);
    });
    process.on('SIGTERM', () => {
      releaseLock();
      process.exit(0);
    });

    await runAutoplay();
  } finally {
    releaseLock();
  }
}

// === Legacy Commands ===

async function cmdState() {
  const rawState = await getGameState();
  if (rawState.error) {
    console.error(`Error: ${rawState.message}`);
    return;
  }

  const parsed = parseGameState(rawState);
  if (!parsed) {
    console.log('No active game.');
    return;
  }

  console.log('=== Snake Game State ===');
  console.log(`Active: ${parsed.active}`);
  console.log(`Round: ${parsed.round}`);
  console.log(`Prize Pool: ${parsed.prizePool}`);
  console.log(`Min Bid: ${parsed.minBid}`);
  console.log(`Countdown: ${parsed.countdown}s`);
  console.log('');
  console.log(`Snake Head: (${parsed.head.q}, ${parsed.head.r})`);
  console.log(`Snake Length: ${parsed.snakeLength}`);
  console.log(`Current Direction: ${parsed.currentDirection}`);
  console.log('');
  console.log('Teams:');
  for (const team of parsed.teams) {
    const dist = team.closestFruit?.distance ?? 'N/A';
    console.log(`  ${team.emoji} ${team.name} (${team.id}): ${team.score} fruits, pool: ${team.pool}, dist: ${dist}`);
  }
  console.log('');
  console.log(`Valid Directions: ${parsed.validDirections.join(', ')}`);

  const balance = await getBalance();
  console.log(`Your Balance: ${balance} balls`);
}

async function cmdVote() {
  const direction = subArgs[0]?.toLowerCase();
  const team = subArgs[1]?.toUpperCase();
  const amount = parseInt(subArgs[2]) || 1;

  if (!direction || !team) {
    console.log('Usage: snake vote <direction> <team> [amount]');
    console.log('  direction: n, ne, se, s, sw, nw');
    console.log('  team: A, B, C, D, E, F');
    return;
  }

  try {
    const result = await submitVote(direction, team, amount);
    console.log('Vote submitted:', result);
  } catch (e) {
    console.error('Vote failed:', e.message);
  }
}

async function cmdAnalyze() {
  const settings = loadSettings();
  const strategy = getStrategy(settings.strategy);

  const rawState = await getGameState();
  if (rawState.error) {
    console.error(`Error: ${rawState.message}`);
    return;
  }

  const parsed = parseGameState(rawState);
  if (!parsed || !parsed.active) {
    console.log('No active game.');
    return;
  }

  const balance = await getBalance();
  const state = loadDaemonState();

  console.log('=== Strategic Analysis ===');
  console.log(`Strategy: ${strategy.name}`);
  console.log(`Balance: ${balance}`);
  console.log('');

  const vote = strategy.computeVote(parsed, balance, state);

  if (!vote || vote.skip) {
    console.log(`Recommendation: Skip this round`);
    console.log(`Reason: ${vote?.reason || 'unknown'}`);
    return;
  }

  console.log(`Recommendation:`);
  console.log(`  Team: ${vote.team.emoji} ${vote.team.name} (${vote.team.id})`);
  console.log(`  Direction: ${vote.direction}`);
  console.log(`  Amount: ${vote.amount}`);
  console.log(`  Reason: ${vote.reason}`);

  if (vote.analysis) {
    console.log('');
    console.log('Analysis:', vote.analysis);
  }
}

async function cmdBalance() {
  const balance = await getBalance();
  console.log(`Balance: ${balance} balls`);
}

async function cmdRodeos() {
  const rodeos = await getRodeos();
  console.log('=== Rodeo Configurations ===');
  for (let i = 0; i < rodeos.length; i++) {
    const r = rodeos[i];
    console.log(`\n[${i}] ${r.name || `Rodeo ${i}`}`);
    console.log(`  Teams: ${r.numberOfTeams}`);
    console.log(`  Grid Radius: ${r.gridRadius}`);
    console.log(`  Fruits to Win: ${r.fruitsToWin}`);
  }
}

function cmdServer() {
  const server = subArgs[0];

  if (server && (server === 'live' || server === 'staging')) {
    setConfig('server', server);
    console.log(`Server set to: ${server} (${SERVERS[server]})`);
  } else {
    const settings = loadSettings();
    console.log('=== Server Settings ===');
    console.log(`Current: ${settings.server} (${getBackendUrl()})`);
    console.log('');
    console.log('Available: live, staging');
    console.log('Usage: snake server <live|staging>');
  }
}

async function cmdTelegram() {
  const chatId = subArgs[0];

  if (chatId === 'off' || chatId === 'disable') {
    setConfig('telegramChatId', null);
    console.log('Telegram logging disabled.');
  } else if (chatId) {
    setConfig('telegramChatId', chatId);
    console.log(`Telegram chat ID set: ${chatId}`);

    // Test message
    const sent = await sendTelegram('🐍 Snake game Telegram logging enabled!', chatId);
    if (sent) {
      console.log('Test message sent successfully.');
    } else {
      console.log('Warning: Could not send test message. Check bot token.');
    }
  } else {
    const settings = loadSettings();
    console.log('=== Telegram Settings ===');
    console.log(`Chat ID: ${settings.telegramChatId || 'Not configured'}`);
    console.log(`Log to Telegram: ${settings.logToTelegram}`);
    console.log('');
    console.log('Usage: snake telegram <chat_id>');
    console.log('       snake telegram off');
  }
}

function showHelp() {
  const settings = loadSettings();

  console.log(`
🐍 Snake Game Daemon

Play the Trifle Snake game automatically with configurable strategies.

USAGE:
  snake <command> [options]

DAEMON COMMANDS:
  start [--detach] [--strategy NAME]   Start the autoplay daemon
  stop                                  Stop the running daemon
  status                                Show daemon status and stats
  attach [-f]                           View daemon logs (-f to follow)
  pause                                 Pause voting (daemon keeps running)
  resume                                Resume voting

CONFIGURATION:
  config [key] [value]                  Get/set configuration values
  strategies                            List available strategies
  server [live|staging]                 Switch game server
  telegram [chat_id|off]                Configure Telegram logging

GAME COMMANDS:
  state                                 Get current game state
  vote <dir> <team> [amount]            Submit a vote manually
  strategy                              Analyze current game
  balance                               Check ball balance
  rodeos                                Show rodeo configurations

CURRENT SETTINGS:
  Strategy: ${settings.strategy}
  Server: ${settings.server}
  Telegram: ${settings.telegramChatId || 'not configured'}

EXAMPLES:
  snake start --detach --strategy aggressive
  snake config minBalance 10
  snake telegram -1234567890

For more info: https://github.com/openclaw/snake-game
`);
}

// Run
main().catch(e => {
  console.error('Fatal error:', e.message);
  process.exit(1);
});
