#!/usr/bin/env node
/**
 * Swarm Daemon CLI
 * 
 * Usage:
 *   swarm-daemon start [--port 9999] [--workers 6]
 *   swarm-daemon stop
 *   swarm-daemon status
 */

const { SwarmDaemon } = require('../lib/daemon');
const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

const PID_FILE = path.join(os.tmpdir(), 'swarm-daemon.pid');
const DEFAULT_PORT = 9999;

function getPid() {
  try {
    return parseInt(fs.readFileSync(PID_FILE, 'utf8').trim(), 10);
  } catch {
    return null;
  }
}

function savePid(pid) {
  fs.writeFileSync(PID_FILE, String(pid));
}

function clearPid() {
  try {
    fs.unlinkSync(PID_FILE);
  } catch {}
}

function isRunning(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

async function checkDaemon(port = DEFAULT_PORT) {
  return new Promise((resolve) => {
    const req = http.request({
      hostname: 'localhost',
      port,
      path: '/health',
      method: 'GET',
      timeout: 1000,
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch {
          resolve(null);
        }
      });
    });
    req.on('error', () => resolve(null));
    req.on('timeout', () => { req.destroy(); resolve(null); });
    req.end();
  });
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'status';
  
  // Parse options
  const portIdx = args.indexOf('--port');
  const port = portIdx !== -1 ? parseInt(args[portIdx + 1], 10) : DEFAULT_PORT;
  
  const workersIdx = args.indexOf('--workers');
  const workers = workersIdx !== -1 ? parseInt(args[workersIdx + 1], 10) : 6;

  switch (command) {
    case 'start': {
      // Check if already running
      const health = await checkDaemon(port);
      if (health) {
        console.log(`Swarm Daemon already running on port ${port}`);
        console.log(`   Uptime: ${Math.round(health.uptime / 1000)}s`);
        console.log(`   Workers: ${health.workers}`);
        process.exit(0);
      }

      // Start daemon
      const daemon = new SwarmDaemon({ port, warmWorkers: workers });
      
      // Handle shutdown
      process.on('SIGINT', () => {
        daemon.stop();
        clearPid();
        process.exit(0);
      });
      process.on('SIGTERM', () => {
        daemon.stop();
        clearPid();
        process.exit(0);
      });

      await daemon.start();
      savePid(process.pid);
      break;
    }

    case 'stop': {
      const pid = getPid();
      if (pid && isRunning(pid)) {
        console.log(`Stopping Swarm Daemon (PID ${pid})...`);
        process.kill(pid, 'SIGTERM');
        clearPid();
        console.log('Stopped.');
      } else {
        // Try to check if running on port
        const health = await checkDaemon(port);
        if (health) {
          console.log(`Daemon running on port ${port} but PID unknown.`);
          console.log('Kill it manually or restart.');
        } else {
          console.log('Swarm Daemon is not running.');
        }
      }
      break;
    }

    case 'status': {
      const health = await checkDaemon(port);
      if (health) {
        // Get detailed status
        const status = await new Promise((resolve) => {
          http.get(`http://localhost:${port}/status`, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(JSON.parse(data)));
          }).on('error', () => resolve(health));
        });

        console.log('🐝 Swarm Daemon Status');
        console.log('─'.repeat(40));
        console.log(`   Status:    ✅ Running`);
        console.log(`   Port:      ${port}`);
        console.log(`   Uptime:    ${Math.round(status.uptime / 1000)}s`);
        console.log(`   Workers:   ${status.workers?.totalNodes || health.workers}`);
        console.log(`   Requests:  ${status.requests}`);
        console.log(`   Tasks:     ${status.totalTasks}`);
        if (status.avgResponseMs) {
          console.log(`   Avg time:  ${status.avgResponseMs}ms`);
        }
        console.log(`   Provider:  ${status.config?.provider || 'unknown'}`);
      } else {
        console.log('🐝 Swarm Daemon Status');
        console.log('─'.repeat(40));
        console.log(`   Status:    ❌ Not running`);
        console.log('');
        console.log('Start with: swarm-daemon start');
      }
      break;
    }

    case 'restart': {
      // Stop then start
      const pid = getPid();
      if (pid && isRunning(pid)) {
        process.kill(pid, 'SIGTERM');
        clearPid();
        await new Promise(r => setTimeout(r, 1000));
      }
      
      const daemon = new SwarmDaemon({ port, warmWorkers: workers });
      process.on('SIGINT', () => { daemon.stop(); clearPid(); process.exit(0); });
      process.on('SIGTERM', () => { daemon.stop(); clearPid(); process.exit(0); });
      await daemon.start();
      savePid(process.pid);
      break;
    }

    default:
      console.log('Swarm Daemon');
      console.log('');
      console.log('Usage:');
      console.log('  swarm-daemon start [--port 9999] [--workers 6]');
      console.log('  swarm-daemon stop');
      console.log('  swarm-daemon status');
      console.log('  swarm-daemon restart');
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
