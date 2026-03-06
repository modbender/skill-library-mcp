#!/usr/bin/env node
/**
 * 🦞 WalletConnect v2 Agent Connector
 * 
 * Allows AI agents to programmatically connect to dApps via WalletConnect
 * and automatically sign transactions.
 * 
 * Usage:
 *   node wc-connect.js <walletconnect-uri> [options]
 * 
 * Options:
 *   --chain-id <id>       Chain ID (default: 8453 for Base)
 *   --rpc <url>           RPC URL (default: https://mainnet.base.org)
 *   --interactive         Prompt before signing each request
 *   --audit               Enable audit logging
 *   --allow-eth-sign      Allow dangerous eth_sign method (⚠️ security risk!)
 * 
 * Environment Variables (REQUIRED):
 *   PRIVATE_KEY           Wallet private key
 *   WC_PROJECT_ID         WalletConnect Project ID (optional)
 *   CHAIN_ID              Chain ID (optional, default: 8453)
 *   RPC_URL               RPC URL (optional)
 * 
 * ⚠️ SECURITY:
 *   - NEVER pass private key as command line argument (shell history risk!)
 *   - ALWAYS use environment variables for sensitive data
 *   - Use a dedicated wallet with limited funds
 *   - eth_sign is BLOCKED by default (can sign arbitrary data = phishing risk)
 */

const { Core } = require('@walletconnect/core');
const { Web3Wallet } = require('@walletconnect/web3wallet');
const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Default configuration
const DEFAULT_CHAIN_ID = 8453; // Base
const DEFAULT_RPC = 'https://mainnet.base.org';
const DEFAULT_PROJECT_ID = '3a8170812b534d0ff9d794f19a901d64';

// Audit log
const AUDIT_DIR = path.join(process.env.HOME, '.walletconnect-agent');
const AUDIT_FILE = path.join(AUDIT_DIR, 'audit.log');

function prompt(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  return new Promise(resolve => {
    rl.question(question, answer => {
      rl.close();
      resolve(answer.trim().toLowerCase());
    });
  });
}

function logAudit(action, details = {}) {
  try {
    if (!fs.existsSync(AUDIT_DIR)) {
      fs.mkdirSync(AUDIT_DIR, { recursive: true, mode: 0o700 });
    }
    
    const entry = {
      timestamp: new Date().toISOString(),
      action,
      // Mask sensitive data
      wallet: details.wallet ? `${details.wallet.slice(0, 6)}...${details.wallet.slice(-4)}` : null,
      to: details.to ? `${details.to.slice(0, 6)}...${details.to.slice(-4)}` : null,
      value: details.value,
      method: details.method,
      dapp: details.dapp,
      chain: details.chain,
      txHash: details.txHash,
      success: details.success ?? true,
      error: details.error,
    };
    
    fs.appendFileSync(AUDIT_FILE, JSON.stringify(entry) + '\n', { mode: 0o600 });
  } catch (e) {
    // Silently ignore audit errors
  }
}

function parseArgs() {
  const args = process.argv.slice(2);
  const config = {
    uri: null,
    chainId: parseInt(process.env.CHAIN_ID) || DEFAULT_CHAIN_ID,
    rpc: process.env.RPC_URL || DEFAULT_RPC,
    projectId: process.env.WC_PROJECT_ID || DEFAULT_PROJECT_ID,
    interactive: false,
    audit: true, // Always audit by default
    allowEthSign: false, // Block dangerous eth_sign by default
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    // Check for dangerous --private-key usage
    if (arg === '--private-key' || arg === '-p') {
      console.error('');
      console.error('⛔ SECURITY ERROR: Do not pass private key as command line argument!');
      console.error('');
      console.error('   Command line arguments are logged in shell history and process lists.');
      console.error('   This is a security risk!');
      console.error('');
      console.error('✅ Use environment variable instead:');
      console.error('   export PRIVATE_KEY="0x..."');
      console.error('   node wc-connect.js "wc:..."');
      console.error('');
      process.exit(1);
    }
    
    if (arg.startsWith('wc:')) {
      config.uri = arg;
    } else if (arg === '--chain-id' && args[i + 1]) {
      config.chainId = parseInt(args[++i]);
    } else if (arg === '--rpc' && args[i + 1]) {
      config.rpc = args[++i];
    } else if (arg === '--project-id' && args[i + 1]) {
      config.projectId = args[++i];
    } else if (arg === '--interactive' || arg === '-i') {
      config.interactive = true;
    } else if (arg === '--no-audit') {
      config.audit = false;
    } else if (arg === '--allow-eth-sign') {
      config.allowEthSign = true;
      console.warn('⚠️  Warning: eth_sign enabled - this allows signing arbitrary data!');
    }
  }

  return config;
}

function formatValue(wei) {
  if (!wei || wei === '0x0' || wei === '0') return '0 ETH';
  try {
    const eth = ethers.formatEther(wei);
    return `${eth} ETH`;
  } catch {
    return wei;
  }
}

async function main() {
  const config = parseArgs();

  // Get private key from environment only
  const privateKey = process.env.PRIVATE_KEY;

  if (!config.uri) {
    console.log('🦞 WalletConnect v2 Agent Connector');
    console.log('═'.repeat(50));
    console.log('');
    console.log('Usage: node wc-connect.js <walletconnect-uri> [options]');
    console.log('');
    console.log('Options:');
    console.log('  --chain-id <id>    Chain ID (default: 8453 for Base)');
    console.log('  --rpc <url>        RPC URL');
    console.log('  --interactive      Prompt before signing');
    console.log('  --no-audit         Disable audit logging');
    console.log('  --allow-eth-sign   Allow dangerous eth_sign (⚠️ security risk!)');
    console.log('');
    console.log('Environment Variables:');
    console.log('  PRIVATE_KEY        Wallet private key (REQUIRED)');
    console.log('  WC_PROJECT_ID      WalletConnect Project ID');
    console.log('  CHAIN_ID           Chain ID');
    console.log('  RPC_URL            RPC URL');
    console.log('');
    console.log('Example:');
    console.log('  export PRIVATE_KEY="0x..."');
    console.log('  node wc-connect.js "wc:abc123...@2?relay-protocol=irn&symKey=xyz"');
    console.log('');
    console.log('⚠️  SECURITY: Never pass private key as command line argument!');
    process.exit(1);
  }

  if (!privateKey) {
    console.error('');
    console.error('❌ Error: PRIVATE_KEY environment variable not set');
    console.error('');
    console.error('Set it like this:');
    console.error('  export PRIVATE_KEY="0x..."');
    console.error('  node wc-connect.js "wc:..."');
    console.error('');
    console.error('⚠️  SECURITY: Never pass private key as command line argument!');
    process.exit(1);
  }

  // Initialize wallet
  const provider = new ethers.JsonRpcProvider(config.rpc);
  const wallet = new ethers.Wallet(privateKey, provider);
  const address = wallet.address;

  console.log('🦞 WalletConnect v2 Agent Connector');
  console.log('═'.repeat(50));
  console.log(`📍 Address: ${address}`);
  console.log(`⛓️  Chain: ${config.chainId}`);
  console.log(`🔗 RPC: ${config.rpc}`);
  console.log(`🔐 Mode: ${config.interactive ? 'Interactive (prompt before signing)' : 'Auto-approve'}`);
  if (config.audit) {
    console.log(`📝 Audit: ${AUDIT_FILE}`);
  }

  // Log connection attempt
  if (config.audit) {
    logAudit('connect_start', { wallet: address, chain: config.chainId });
  }

  // Initialize WalletConnect Core
  const core = new Core({
    projectId: config.projectId,
  });

  // Initialize Web3Wallet
  const web3wallet = await Web3Wallet.init({
    core,
    metadata: {
      name: 'AI Agent Wallet',
      description: 'Autonomous AI Agent Wallet powered by Clawdbot',
      url: 'https://clawd.bot',
      icons: ['https://clawd.bot/logo.png'],
    },
  });

  console.log('\n📡 Connecting to dApp...');

  // Handle session proposals
  web3wallet.on('session_proposal', async (proposal) => {
    const dappName = proposal.params.proposer.metadata.name;
    const dappUrl = proposal.params.proposer.metadata.url;
    
    console.log('\n✅ Session proposal received!');
    console.log(`   dApp: ${dappName}`);
    console.log(`   URL: ${dappUrl}`);

    let shouldApprove = true;
    
    if (config.interactive) {
      const answer = await prompt('\nApprove connection? (yes/no): ');
      shouldApprove = answer === 'yes' || answer === 'y';
    }

    if (shouldApprove) {
      // Only include eth_sign if explicitly allowed (security risk)
      const methods = [
        'eth_sendTransaction',
        'eth_signTransaction',
        'personal_sign',
        'eth_signTypedData',
        'eth_signTypedData_v4',
      ];
      if (config.allowEthSign) {
        methods.push('eth_sign');
      }
      
      const namespaces = {
        eip155: {
          accounts: [`eip155:${config.chainId}:${address}`],
          methods,
          events: ['chainChanged', 'accountsChanged'],
          chains: [`eip155:${config.chainId}`],
        },
      };

      const session = await web3wallet.approveSession({
        id: proposal.id,
        namespaces,
      });

      console.log('✅ Session approved!');
      console.log(`   Topic: ${session.topic}`);
      
      if (config.audit) {
        logAudit('session_approved', { wallet: address, dapp: dappName, chain: config.chainId });
      }
    } else {
      await web3wallet.rejectSession({
        id: proposal.id,
        reason: { code: 4001, message: 'User rejected' },
      });
      console.log('❌ Session rejected');
      
      if (config.audit) {
        logAudit('session_rejected', { wallet: address, dapp: dappName });
      }
    }
  });

  // Handle signing requests
  web3wallet.on('session_request', async (event) => {
    const { topic, params, id } = event;
    const { request } = params;

    console.log('\n' + '─'.repeat(50));
    console.log('📝 Signing Request:');
    console.log(`   Method: ${request.method}`);

    try {
      let result;
      let txDetails = { method: request.method, wallet: address };

      switch (request.method) {
        case 'personal_sign': {
          const [message, from] = request.params;
          console.log(`   From: ${from}`);
          
          // Show message (truncated if long)
          let displayMsg = message;
          if (ethers.isHexString(message)) {
            try {
              displayMsg = ethers.toUtf8String(message);
            } catch {
              displayMsg = message.slice(0, 66) + '...';
            }
          }
          if (displayMsg.length > 100) {
            displayMsg = displayMsg.slice(0, 100) + '...';
          }
          console.log(`   Message: ${displayMsg}`);

          if (config.interactive) {
            const answer = await prompt('\nSign this message? (yes/no): ');
            if (answer !== 'yes' && answer !== 'y') {
              throw new Error('User rejected');
            }
          }

          if (ethers.isHexString(message)) {
            result = await wallet.signMessage(ethers.getBytes(message));
          } else {
            result = await wallet.signMessage(message);
          }
          break;
        }

        case 'eth_signTypedData':
        case 'eth_signTypedData_v4': {
          const [from, data] = request.params;
          console.log(`   From: ${from}`);
          console.log(`   Type: EIP-712 Typed Data`);

          if (config.interactive) {
            const answer = await prompt('\nSign this typed data? (yes/no): ');
            if (answer !== 'yes' && answer !== 'y') {
              throw new Error('User rejected');
            }
          }

          const typedData = typeof data === 'string' ? JSON.parse(data) : data;
          const { domain, types, message } = typedData;
          delete types.EIP712Domain;
          result = await wallet.signTypedData(domain, types, message);
          break;
        }

        case 'eth_sendTransaction': {
          const [tx] = request.params;
          const value = formatValue(tx.value);
          
          console.log(`   To: ${tx.to}`);
          console.log(`   Value: ${value}`);
          if (tx.data && tx.data !== '0x') {
            console.log(`   Data: ${tx.data.slice(0, 66)}...`);
          }

          txDetails.to = tx.to;
          txDetails.value = value;

          if (config.interactive) {
            const answer = await prompt('\nSend this transaction? (yes/no): ');
            if (answer !== 'yes' && answer !== 'y') {
              throw new Error('User rejected');
            }
          }

          const txResponse = await wallet.sendTransaction({
            to: tx.to,
            value: tx.value || '0x0',
            data: tx.data || '0x',
            gasLimit: tx.gas || tx.gasLimit,
          });

          console.log(`   ✅ TX Hash: ${txResponse.hash}`);
          txDetails.txHash = txResponse.hash;
          result = txResponse.hash;
          break;
        }

        case 'eth_sign': {
          const [from, message] = request.params;
          console.log(`   From: ${from}`);
          console.log(`   ⚠️  eth_sign is DANGEROUS - can sign arbitrary data!`);
          
          // Block by default unless explicitly allowed
          if (!config.allowEthSign) {
            console.log('   ❌ Blocked: eth_sign is disabled by default for security');
            console.log('   Use --allow-eth-sign to enable (not recommended)');
            throw new Error('eth_sign blocked for security - use --allow-eth-sign to enable');
          }

          if (config.interactive) {
            console.log(`   Message (hex): ${message}`);
            const answer = await prompt('\n⚠️  Sign this raw message? This is dangerous! (yes/no): ');
            if (answer !== 'yes' && answer !== 'y') {
              throw new Error('User rejected');
            }
          }

          result = await wallet.signMessage(ethers.getBytes(message));
          console.log('   ⚠️  Signed (eth_sign) - be cautious!');
          break;
        }

        default:
          throw new Error(`Unsupported method: ${request.method}`);
      }

      await web3wallet.respondSessionRequest({
        topic,
        response: {
          id,
          jsonrpc: '2.0',
          result,
        },
      });

      console.log('✅ Request completed!');
      
      if (config.audit) {
        logAudit('sign_success', { ...txDetails, success: true });
      }

    } catch (error) {
      console.error('❌ Error:', error.message);
      
      await web3wallet.respondSessionRequest({
        topic,
        response: {
          id,
          jsonrpc: '2.0',
          error: {
            code: 5000,
            message: error.message,
          },
        },
      });
      
      if (config.audit) {
        logAudit('sign_error', { method: request.method, wallet: address, error: error.message, success: false });
      }
    }
  });

  // Connect to URI
  try {
    await web3wallet.pair({ uri: config.uri });
    console.log('✅ Pairing initiated! Waiting for session...');
  } catch (error) {
    console.error('❌ Pairing failed:', error.message);
    if (config.audit) {
      logAudit('pairing_failed', { wallet: address, error: error.message, success: false });
    }
    process.exit(1);
  }

  // Keep running
  console.log('\n⏳ Listening for requests... (Press Ctrl+C to exit)');
  console.log('─'.repeat(50));
}

main().catch(console.error);
