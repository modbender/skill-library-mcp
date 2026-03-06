#!/usr/bin/env node
/**
 * OpenClaw Skill: Start Clawdio Node
 * 
 * This script starts a Clawdio node and returns connection information
 * that can be used by the OpenClaw agent.
 */

const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const CLAWDIO_DIR = '/Users/jamesball/.openclaw/workspace/projects/clawdio';
const IDENTITY_FILE = path.join(CLAWDIO_DIR, '.clawdio-identity');

async function startClawdioNode() {
  try {
    // Check if identity exists
    if (!fs.existsSync(IDENTITY_FILE)) {
      throw new Error('Clawdio identity not found. Please set up Clawdio first.');
    }

    // Read the identity to get public key
    const identity = JSON.parse(fs.readFileSync(IDENTITY_FILE, 'utf8'));
    const publicKey = identity.publicKey;

    // Check if already running (basic check)
    const isRunning = await new Promise((resolve) => {
      exec('pgrep -f "node.*run.js"', (error) => {
        resolve(!error); // If no error, process exists
      });
    });

    if (isRunning) {
      console.log('⚠️  Clawdio appears to already be running');
    } else {
      console.log('🚀 Starting Clawdio node...');
      
      // Start the node in the background
      const child = exec('node run.js', {
        cwd: CLAWDIO_DIR,
        detached: true,
        stdio: 'ignore'
      });

      // Detach the child process so it continues running
      child.unref();
      
      // Give it a moment to start
      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    // Return connection information
    const connectionInfo = {
      status: 'running',
      publicKey: publicKey,
      connectionString: `clawdio://${publicKey}@115.85.17.196:3579`,
      port: 3579,
      host: '115.85.17.196',
      owner: 'James'
    };

    console.log('✅ Clawdio node connection info:');
    console.log(JSON.stringify(connectionInfo, null, 2));
    
    return connectionInfo;

  } catch (error) {
    console.error('❌ Error starting Clawdio node:', error.message);
    throw error;
  }
}

// If called directly from command line
if (require.main === module) {
  startClawdioNode()
    .then((info) => {
      console.log('\n🔗 Connection string for friends:');
      console.log(info.connectionString);
    })
    .catch((error) => {
      console.error('Failed to start Clawdio:', error.message);
      process.exit(1);
    });
}

module.exports = { startClawdioNode };