#!/usr/bin/env ts-node

import { spawn } from 'child_process';
import * as path from 'path';

const PORT = 3000;

async function startServer() {
  console.log('\n🚀 Starting GetPay Payment Server...\n');
  console.log('='.repeat(70));

  // Start Express server
  console.log('\n1️⃣  Starting Express server...');
  const serverPath = path.join(__dirname, 'server-simple.ts');
  const server = spawn('npx', ['ts-node', serverPath], {
    stdio: 'inherit',
    env: { ...process.env, PORT: PORT.toString() }
  });

  // Wait for server to start
  await new Promise(resolve => setTimeout(resolve, 3000));

  // Start localhost.run tunnel
  console.log('\n2️⃣  Creating public tunnel with localhost.run...');
  console.log('    (This is more reliable than localtunnel)\n');
  
  const tunnel = spawn('ssh', [
    '-R',
    `80:localhost:${PORT}`,
    'localhost.run',
    '-o',
    'StrictHostKeyChecking=no'
  ]);

  let tunnelUrl = '';
  
  tunnel.stdout.on('data', (data) => {
    const output = data.toString();
    console.log(output);
    
    // Extract URL from localhost.run output
    const urlMatch = output.match(/https:\/\/[a-zA-Z0-9-]+\.lhr\.life/);
    if (urlMatch && !tunnelUrl) {
      tunnelUrl = urlMatch[0];
      console.log('\n' + '='.repeat(70));
      console.log('\n✅ Tunnel created successfully!');
      console.log('\n🌐 PUBLIC URL:');
      console.log(`\n   ${tunnelUrl}\n`);
      console.log('='.repeat(70));
      console.log('\n📱 Share this link to receive payments!');
      console.log('💡 First-time users will be guided through setup');
      console.log('\n⚡ Server is running... Press Ctrl+C to stop\n');
    }
  });

  tunnel.stderr.on('data', (data) => {
    // localhost.run sends connection info to stderr
    const output = data.toString();
    if (output.includes('https://')) {
      console.log(output);
    }
  });

  tunnel.on('close', () => {
    console.log('\n❌ Tunnel closed');
    server.kill();
    process.exit();
  });

  // Handle Ctrl+C
  process.on('SIGINT', () => {
    console.log('\n\n👋 Shutting down...');
    tunnel.kill();
    server.kill();
    process.exit();
  });
}

startServer().catch(error => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});
