/**
 * Process Management
 *
 * Handles PID files, locking, and daemon control.
 */

import { readFileSync, writeFileSync, unlinkSync, existsSync, appendFileSync } from 'fs';
import { execSync, spawn } from 'child_process';
import { PATHS, loadSettings, loadDaemonState, saveDaemonState } from './config.mjs';

/**
 * Check if daemon is running
 */
export function isDaemonRunning() {
  if (!existsSync(PATHS.pidFile)) {
    return false;
  }

  try {
    const pid = parseInt(readFileSync(PATHS.pidFile, 'utf8').trim());
    // Check if process is running
    process.kill(pid, 0);
    return { running: true, pid };
  } catch (e) {
    // Process not running, clean up stale PID file
    try {
      unlinkSync(PATHS.pidFile);
    } catch {}
    return false;
  }
}

/**
 * Write PID file
 */
export function writePidFile() {
  PATHS._dirs.ensureDir(PATHS._dirs.state);
  writeFileSync(PATHS.pidFile, process.pid.toString());
}

/**
 * Remove PID file
 */
export function removePidFile() {
  try {
    unlinkSync(PATHS.pidFile);
  } catch {}
}

/**
 * Acquire exclusive lock (prevent multiple instances)
 */
export function acquireLock() {
  const status = isDaemonRunning();
  if (status?.running) {
    throw new Error(`Daemon already running (PID: ${status.pid})`);
  }
  writePidFile();
}

/**
 * Release lock
 */
export function releaseLock() {
  removePidFile();
}

/**
 * Log to daemon log file
 */
export function logToFile(message) {
  const settings = loadSettings();
  if (!settings.logToFile) return;

  PATHS._dirs.ensureDir(PATHS._dirs.data);
  const timestamp = new Date().toISOString();
  const line = `[${timestamp}] ${message}\n`;
  appendFileSync(PATHS.logFile, line);
}

/**
 * Stop the running daemon
 */
export function stopDaemon() {
  const status = isDaemonRunning();
  if (!status?.running) {
    return { success: false, message: 'Daemon is not running' };
  }

  try {
    process.kill(status.pid, 'SIGTERM');
    // Wait a bit then check
    let retries = 10;
    while (retries > 0 && isDaemonRunning()) {
      execSync('sleep 0.5');
      retries--;
    }
    return { success: true, message: `Stopped daemon (PID: ${status.pid})` };
  } catch (e) {
    return { success: false, message: `Failed to stop: ${e.message}` };
  }
}

/**
 * Pause voting (daemon keeps running but doesn't vote)
 */
export function pauseDaemon() {
  const state = loadDaemonState();
  state.paused = true;
  saveDaemonState(state);
  return { success: true, message: 'Daemon paused' };
}

/**
 * Resume voting
 */
export function resumeDaemon() {
  const state = loadDaemonState();
  state.paused = false;
  saveDaemonState(state);
  return { success: true, message: 'Daemon resumed' };
}

/**
 * Get daemon status
 */
export function getDaemonStatus() {
  const running = isDaemonRunning();
  const state = loadDaemonState();
  const settings = loadSettings();

  return {
    running: running?.running || false,
    pid: running?.pid || null,
    paused: state.paused,
    currentTeam: state.currentTeam,
    gamesPlayed: state.gamesPlayed,
    votesPlaced: state.votesPlaced,
    wins: state.wins,
    startedAt: state.startedAt,
    strategy: settings.strategy,
    server: settings.server,
    telegramChatId: settings.telegramChatId,
  };
}

/**
 * Start daemon in background
 */
export function startDaemonBackground() {
  const status = isDaemonRunning();
  if (status?.running) {
    return { success: false, message: `Already running (PID: ${status.pid})` };
  }

  // Path to the snake CLI
  const snakePath = new URL('../snake.mjs', import.meta.url).pathname;

  const child = spawn('node', [snakePath, 'daemon'], {
    detached: true,
    stdio: ['ignore', 'ignore', 'ignore'],
  });

  child.unref();

  return { success: true, message: `Started daemon (PID: ${child.pid})`, pid: child.pid };
}

/**
 * Tail the log file
 */
export function tailLogs(lines = 50, follow = false) {
  if (!existsSync(PATHS.logFile)) {
    console.log('No log file yet.');
    return;
  }

  if (follow) {
    const tail = spawn('tail', ['-f', '-n', lines.toString(), PATHS.logFile], {
      stdio: 'inherit',
    });
    tail.on('error', () => {
      // Fallback for systems without tail
      console.log(readFileSync(PATHS.logFile, 'utf8'));
    });
    return tail;
  } else {
    try {
      const output = execSync(`tail -n ${lines} "${PATHS.logFile}"`, { encoding: 'utf8' });
      console.log(output);
    } catch {
      // Fallback
      const content = readFileSync(PATHS.logFile, 'utf8');
      const lineArray = content.split('\n');
      console.log(lineArray.slice(-lines).join('\n'));
    }
  }
}
