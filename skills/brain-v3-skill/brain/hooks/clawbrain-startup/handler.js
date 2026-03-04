/**
 * ClawBrain Startup Hook Handler
 *
 * Refreshes the ClawBrain memory system on gateway startup
 * and saves session context to brain on /new command.
 */
import { spawn, spawnSync } from 'node:child_process';
import path from 'node:path';
import os from 'node:os';
import fs from 'node:fs';

// Find brain_bridge.py using Python to locate the package
function findBridgeScriptViaPython() {
  try {
    const result = spawnSync('python3', ['-c', `
import sys
try:
    import clawbrain
    import os
    pkg_dir = os.path.dirname(clawbrain.__file__)
    # Check multiple possible locations
    candidates = [
        os.path.join(pkg_dir, 'scripts', 'brain_bridge.py'),
        os.path.join(os.path.dirname(pkg_dir), 'brain', 'scripts', 'brain_bridge.py'),
        os.path.join(os.path.dirname(pkg_dir), 'scripts', 'brain_bridge.py'),
    ]
    for c in candidates:
        if os.path.exists(c):
            print(c)
            sys.exit(0)
    # Fallback to package dir
    print(pkg_dir)
except Exception as e:
    print('', file=sys.stderr)
    sys.exit(1)
`], { encoding: 'utf-8', timeout: 5000 });
    
    if (result.status === 0 && result.stdout.trim()) {
      return result.stdout.trim();
    }
  } catch (e) {
    // Python not available or clawbrain not installed
  }
  return null;
}

// Find brain_bridge.py - check multiple possible locations
function findBridgeScript() {
  const home = os.homedir();
  
  // Possible locations for brain_bridge.py
  const possiblePaths = [
    // Skills directory locations (manual/git installs)
    path.join(home, 'clawd', 'skills', 'clawbrain', 'scripts', 'brain_bridge.py'),
    path.join(home, 'clawd', 'skills', 'clawbrain', 'brain', 'scripts', 'brain_bridge.py'),
    path.join(home, '.openclaw', 'skills', 'clawbrain', 'scripts', 'brain_bridge.py'),
    path.join(home, '.openclaw', 'skills', 'clawbrain', 'brain', 'scripts', 'brain_bridge.py'),
    path.join(home, '.clawdbot', 'skills', 'clawbrain', 'scripts', 'brain_bridge.py'),
    path.join(home, '.clawdbot', 'skills', 'clawbrain', 'brain', 'scripts', 'brain_bridge.py'),
    // Pip installed locations (common paths)
    path.join(home, '.local', 'lib', 'python3.10', 'site-packages', 'brain', 'scripts', 'brain_bridge.py'),
    path.join(home, '.local', 'lib', 'python3.11', 'site-packages', 'brain', 'scripts', 'brain_bridge.py'),
    path.join(home, '.local', 'lib', 'python3.12', 'site-packages', 'brain', 'scripts', 'brain_bridge.py'),
    path.join(home, '.local', 'lib', 'python3.13', 'site-packages', 'brain', 'scripts', 'brain_bridge.py'),
    // System site-packages
    '/usr/local/lib/python3.10/site-packages/brain/scripts/brain_bridge.py',
    '/usr/local/lib/python3.11/site-packages/brain/scripts/brain_bridge.py',
    '/usr/local/lib/python3.12/site-packages/brain/scripts/brain_bridge.py',
  ];
  
  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }
  
  // Fallback: use Python to find it dynamically
  const pythonPath = findBridgeScriptViaPython();
  if (pythonPath && fs.existsSync(pythonPath)) {
    return pythonPath;
  }
  
  return null;
}

// Find clawbrain directory for working directory
function findClawbrainDir() {
  const bridgeScript = findBridgeScript();
  if (bridgeScript) {
    // Go up to clawbrain root (2 levels: scripts/brain_bridge.py -> scripts -> clawbrain)
    return path.dirname(path.dirname(bridgeScript));
  }
  
  const home = os.homedir();
  const possiblePaths = [
    path.join(home, 'clawd', 'skills', 'clawbrain'),
    path.join(home, '.openclaw', 'skills', 'clawbrain'),
    path.join(home, '.clawdbot', 'skills', 'clawbrain'),
  ];
  
  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }
  
  return possiblePaths[0];
}

const BRIDGE_SCRIPT = findBridgeScript();
const CLAWBRAIN_DIR = findClawbrainDir();

// Agent ID from environment variable, defaults to "default"
// Set BRAIN_AGENT_ID in your service config for per-instance storage
const AGENT_ID = process.env.BRAIN_AGENT_ID || 'default';

/**
 * Execute a brain bridge command
 * @param {string} command - The command to execute
 * @param {object} args - Command arguments
 * @returns {Promise<object>} - Command result
 */
async function runBrainCommand(command, args = {}) {
  return new Promise((resolve, reject) => {
    if (!BRIDGE_SCRIPT) {
      return reject(new Error('brain_bridge.py not found. Run: pip install clawbrain[all] && clawbrain setup'));
    }
    
    const input = JSON.stringify({ command, args, config: {} });
    const proc = spawn('python3', [BRIDGE_SCRIPT], {
      cwd: CLAWBRAIN_DIR,
      stdio: ['pipe', 'pipe', 'pipe'],
    });

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (data) => (stdout += data.toString()));
    proc.stderr.on('data', (data) => (stderr += data.toString()));

    proc.on('close', (code) => {
      if (code !== 0) {
        console.error('[clawbrain-hook] Bridge error:', stderr);
        reject(new Error('Bridge exited with code ' + code));
        return;
      }
      try {
        resolve(JSON.parse(stdout));
      } catch (e) {
        reject(new Error('Invalid JSON: ' + stdout));
      }
    });

    proc.stdin.write(input);
    proc.stdin.end();
  });
}

/**
 * Handle gateway startup - refresh brain memory
 * @param {object} event - Gateway startup event
 */
async function handleGatewayStartup(event) {
  console.log(`[clawbrain-hook] Gateway startup detected, refreshing brain for agent "${AGENT_ID}"...`);
  try {
    const result = await runBrainCommand('refresh_on_startup', { agent_id: AGENT_ID });
    if (result.success) {
      console.log('[clawbrain-hook] Brain refreshed:', result.sync?.memories_count || 0, 'memories loaded');
    } else {
      console.error('[clawbrain-hook] Brain refresh failed:', result.error);
    }
  } catch (err) {
    console.error('[clawbrain-hook] Error refreshing brain:', err.message);
  }
}

/**
 * Handle /new command - save session to brain memory
 * @param {object} event - Command event
 */
async function handleNewCommand(event) {
  console.log(`[clawbrain-hook] /new command detected, saving session for agent "${AGENT_ID}"...`);
  const context = event.context || {};
  const sessionEntry = context.previousSessionEntry || context.sessionEntry || {};
  
  try {
    const result = await runBrainCommand('save_session', {
      agent_id: AGENT_ID,
      session_summary: sessionEntry.summary || 'Session ended by user',
      session_id: sessionEntry.sessionId || null,
    });
    if (result.success) {
      console.log('[clawbrain-hook] Session saved to brain memory');
    } else {
      console.error('[clawbrain-hook] Session save failed:', result.error);
    }
  } catch (err) {
    console.error('[clawbrain-hook] Error saving session:', err.message);
  }
}

/**
 * Main hook handler
 * @param {object} event - Hook event
 */
const clawbrainHook = async (event) => {
  // Handle gateway startup
  if (event.type === 'gateway' && event.action === 'startup') {
    await handleGatewayStartup(event);
    return;
  }

  // Handle /new command
  if (event.type === 'command' && event.action === 'new') {
    await handleNewCommand(event);
    return;
  }
};

export default clawbrainHook;
