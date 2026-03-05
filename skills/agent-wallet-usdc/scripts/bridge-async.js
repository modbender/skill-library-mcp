/**
 * Async Bridge - Production-grade CCTP bridging
 * 
 * Features:
 * - State machine with persistent state
 * - Resumable from any step
 * - Polls attestation API (no blocking)
 * - Clear status reporting
 * - Idempotent operations
 */

import { ethers } from 'ethers';
import * as bip39 from 'bip39';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.join(__dirname, '..', '.env') });

// State file for persistence
const STATE_DIR = path.join(__dirname, '..', 'data');
const STATE_FILE = path.join(STATE_DIR, 'bridge-states.json');

// Ensure data directory exists
if (!fs.existsSync(STATE_DIR)) {
  fs.mkdirSync(STATE_DIR, { recursive: true });
}

// Chain configurations (CCTP V2 - Fast Transfer enabled!)
const CHAINS = {
  base_sepolia: {
    name: 'Base Sepolia',
    chainId: 84532,
    rpc: 'https://sepolia.base.org',
    usdc: '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
    tokenMessenger: '0x8fe6b999dc680ccfdd5bf7eb0974218be2542daa',  // V2
    messageTransmitter: '0xe737e5cebeeba77efe34d4aa090756590b1ce275',  // V2
    domain: 6,
    explorer: 'https://sepolia.basescan.org/tx/'
  },
  ethereum_sepolia: {
    name: 'Ethereum Sepolia', 
    chainId: 11155111,
    rpc: 'https://sepolia.drpc.org',
    usdc: '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
    tokenMessenger: '0x8fe6b999dc680ccfdd5bf7eb0974218be2542daa',  // V2
    messageTransmitter: '0xe737e5cebeeba77efe34d4aa090756590b1ce275',  // V2
    domain: 0,
    explorer: 'https://sepolia.etherscan.io/tx/'
  }
};

// Circle Attestation API (testnet)
const ATTESTATION_API = 'https://iris-api-sandbox.circle.com/attestations';

// ABIs (minimal)
const ERC20_ABI = [
  'function approve(address spender, uint256 amount) returns (bool)',
  'function allowance(address owner, address spender) view returns (uint256)',
  'function balanceOf(address account) view returns (uint256)'
];

// CCTP V2 TokenMessengerV2 ABI (Fast Transfer!)
const TOKEN_MESSENGER_ABI = [
  'function depositForBurn(uint256 amount, uint32 destinationDomain, bytes32 mintRecipient, address burnToken, bytes32 destinationCaller, uint256 maxFee, uint32 minFinalityThreshold) external',
  'event DepositForBurn(address indexed burnToken, uint256 amount, address indexed depositor, bytes32 mintRecipient, uint32 destinationDomain, bytes32 destinationTokenMessenger, bytes32 destinationCaller, uint256 maxFee, uint32 indexed minFinalityThreshold, bytes hookData)'
];

const MESSAGE_TRANSMITTER_ABI = [
  'function receiveMessage(bytes message, bytes attestation) returns (bool)',
  'event MessageSent(bytes message)'
];

// Bridge states
const STATES = {
  PENDING: 'pending',
  APPROVING: 'approving',
  APPROVED: 'approved',
  BURNING: 'burning',
  BURNED: 'burned',
  ATTESTING: 'attesting',
  ATTESTED: 'attested',
  MINTING: 'minting',
  COMPLETE: 'complete',
  FAILED: 'failed'
};

// Load/save state
function loadStates() {
  try {
    if (fs.existsSync(STATE_FILE)) {
      return JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
    }
  } catch (e) {
    console.error('Error loading states:', e.message);
  }
  return {};
}

function saveStates(states) {
  fs.writeFileSync(STATE_FILE, JSON.stringify(states, null, 2));
}

function getState(bridgeId) {
  const states = loadStates();
  return states[bridgeId];
}

function setState(bridgeId, state) {
  const states = loadStates();
  states[bridgeId] = { ...states[bridgeId], ...state, updatedAt: Date.now() };
  saveStates(states);
  return states[bridgeId];
}

// Derive wallet from seed
function getWallet(chain) {
  const seedPhrase = process.env.WALLET_SEED_PHRASE;
  if (!seedPhrase) throw new Error('WALLET_SEED_PHRASE not set');
  
  const hdNode = ethers.HDNodeWallet.fromPhrase(seedPhrase.trim());
  const provider = new ethers.JsonRpcProvider(chain.rpc);
  return hdNode.connect(provider);
}

// Generate unique bridge ID
function generateBridgeId() {
  return `bridge_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// Convert address to bytes32 (for CCTP)
function addressToBytes32(address) {
  return ethers.zeroPadValue(address, 32);
}

// Get message hash from burn TX receipt
function getMessageHashFromReceipt(receipt, messageTransmitterAddress) {
  for (const log of receipt.logs) {
    if (log.address.toLowerCase() === messageTransmitterAddress.toLowerCase()) {
      // MessageSent event
      if (log.topics[0] === ethers.id('MessageSent(bytes)')) {
        const iface = new ethers.Interface(MESSAGE_TRANSMITTER_ABI);
        const decoded = iface.parseLog({ topics: log.topics, data: log.data });
        const message = decoded.args[0];
        return { message, messageHash: ethers.keccak256(message) };
      }
    }
  }
  return null;
}

// Poll attestation API (V2 format with domain + txHash)
async function getAttestation(messageHash, burnTxHash, sourceDomain) {
  try {
    // V2 API format: /v2/messages/{domainId}?transactionHash={txHash}
    const baseUrl = ATTESTATION_API.replace('/attestations', '');
    const v2Url = `${baseUrl}/v2/messages/${sourceDomain}?transactionHash=${burnTxHash}`;
    
    const response = await fetch(v2Url);
    if (response.ok) {
      const data = await response.json();
      if (data.messages && data.messages.length > 0) {
        const msg = data.messages[0];
        if (msg.status === 'complete') {
          return { attestation: msg.attestation, message: msg.message };
        }
        process.stdout.write(` [${msg.status}]`);
      }
    }
    
    // Fallback to V1 endpoint (for V1 contracts)
    const v1Response = await fetch(`${ATTESTATION_API}/${messageHash}`);
    if (v1Response.ok) {
      const data = await v1Response.json();
      if (data.status === 'complete') {
        return { attestation: data.attestation, message: null };
      }
      process.stdout.write(` [${data.status}]`);
    }
    
    return null;
  } catch (e) {
    return null;
  }
}

// ===================
// BRIDGE OPERATIONS
// ===================

async function initiateBridge(fromChainKey, toChainKey, amount) {
  const fromChain = CHAINS[fromChainKey];
  const toChain = CHAINS[toChainKey];
  
  if (!fromChain || !toChain) {
    throw new Error(`Unknown chain. Supported: ${Object.keys(CHAINS).join(', ')}`);
  }
  
  const bridgeId = generateBridgeId();
  const wallet = getWallet(fromChain);
  const amountWei = ethers.parseUnits(amount.toString(), 6); // USDC has 6 decimals
  
  const state = setState(bridgeId, {
    id: bridgeId,
    status: STATES.PENDING,
    fromChain: fromChainKey,
    toChain: toChainKey,
    amount: amount,
    amountWei: amountWei.toString(),
    walletAddress: wallet.address,
    createdAt: Date.now(),
    approveTx: null,
    burnTx: null,
    message: null,
    messageHash: null,
    attestation: null,
    mintTx: null,
    error: null
  });
  
  console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌉 BRIDGE INITIATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID:     ${bridgeId}
From:   ${fromChain.name}
To:     ${toChain.name}
Amount: ${amount} USDC
Wallet: ${wallet.address}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
  
  return bridgeId;
}

async function stepApprove(bridgeId) {
  const state = getState(bridgeId);
  if (!state) throw new Error(`Bridge ${bridgeId} not found`);
  if (state.approveTx) {
    console.log(`✅ Already approved: ${state.approveTx}`);
    return state;
  }
  
  const fromChain = CHAINS[state.fromChain];
  const wallet = getWallet(fromChain);
  const usdc = new ethers.Contract(fromChain.usdc, ERC20_ABI, wallet);
  
  setState(bridgeId, { status: STATES.APPROVING });
  console.log('🔐 Approving USDC spend...');
  
  // For V2, we need to approve amount + maxFee (10%)
  // Use a generous allowance to avoid issues
  const approveAmount = BigInt(state.amountWei) * 2n; // 2x amount to cover any fees
  
  // Check current allowance
  const allowance = await usdc.allowance(wallet.address, fromChain.tokenMessenger);
  if (allowance >= approveAmount) {
    console.log('✅ Already has sufficient allowance');
    return setState(bridgeId, { status: STATES.APPROVED });
  }
  
  // Approve generous amount
  const tx = await usdc.approve(fromChain.tokenMessenger, approveAmount);
  console.log(`📝 Approve TX: ${fromChain.explorer}${tx.hash}`);
  
  const receipt = await tx.wait();
  if (receipt.status !== 1) {
    throw new Error('Approve transaction failed');
  }
  
  console.log('✅ Approved!');
  return setState(bridgeId, { 
    status: STATES.APPROVED, 
    approveTx: tx.hash 
  });
}

async function stepBurn(bridgeId) {
  const state = getState(bridgeId);
  if (!state) throw new Error(`Bridge ${bridgeId} not found`);
  if (state.burnTx) {
    console.log(`✅ Already burned: ${state.burnTx}`);
    return state;
  }
  if (state.status !== STATES.APPROVED && !state.approveTx) {
    throw new Error('Must approve first');
  }
  
  const fromChain = CHAINS[state.fromChain];
  const toChain = CHAINS[state.toChain];
  const wallet = getWallet(fromChain);
  
  const tokenMessenger = new ethers.Contract(
    fromChain.tokenMessenger, 
    TOKEN_MESSENGER_ABI, 
    wallet
  );
  
  setState(bridgeId, { status: STATES.BURNING });
  console.log('🔥 Burning USDC on source chain (FAST TRANSFER)...');
  
  const mintRecipient = addressToBytes32(wallet.address);
  const destinationCaller = ethers.zeroPadValue('0x', 32); // bytes32(0) = anyone can call
  const maxFee = BigInt(state.amountWei) / 10n; // 10% max fee (generous for fast transfer)
  const minFinalityThreshold = 1000; // FAST TRANSFER! (1000 = ~8 seconds vs 2000 = 30+ min)
  
  console.log('   Using Fast Transfer (minFinalityThreshold: 1000)');
  
  const tx = await tokenMessenger.depositForBurn(
    state.amountWei,
    toChain.domain,
    mintRecipient,
    fromChain.usdc,
    destinationCaller,
    maxFee,
    minFinalityThreshold
  );
  
  console.log(`📝 Burn TX: ${fromChain.explorer}${tx.hash}`);
  
  const receipt = await tx.wait();
  if (receipt.status !== 1) {
    throw new Error('Burn transaction failed');
  }
  
  // Extract message and hash
  const msgData = getMessageHashFromReceipt(receipt, fromChain.messageTransmitter);
  if (!msgData) {
    throw new Error('Could not extract message from burn TX');
  }
  
  console.log(`✅ Burned! Message hash: ${msgData.messageHash}`);
  
  return setState(bridgeId, {
    status: STATES.BURNED,
    burnTx: tx.hash,
    message: msgData.message,
    messageHash: msgData.messageHash
  });
}

async function stepAttest(bridgeId, maxAttempts = 60, intervalMs = 3000) {
  const state = getState(bridgeId);
  if (!state) throw new Error(`Bridge ${bridgeId} not found`);
  if (state.attestation) {
    console.log('✅ Already have attestation');
    return state;
  }
  if (!state.burnTx) {
    throw new Error('No burn TX - must burn first');
  }
  
  const fromChain = CHAINS[state.fromChain];
  
  setState(bridgeId, { status: STATES.ATTESTING });
  console.log('⏳ Waiting for Circle attestation (FAST TRANSFER ~8-30s)...');
  console.log(`   Burn TX: ${state.burnTx}`);
  console.log(`   Source Domain: ${fromChain.domain}`);
  console.log(`   Polling every ${intervalMs/1000}s (max ${maxAttempts} attempts)`);
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const result = await getAttestation(state.messageHash, state.burnTx, fromChain.domain);
    
    if (result) {
      console.log(`\n✅ Attestation received after ${attempt} attempts (~${attempt * intervalMs / 1000}s)!`);
      
      // V2 API returns the message too - update if available
      const updateData = {
        status: STATES.ATTESTED,
        attestation: result.attestation
      };
      if (result.message) {
        updateData.message = result.message;
      }
      
      return setState(bridgeId, updateData);
    }
    
    if (attempt < maxAttempts) {
      process.stdout.write(`   Attempt ${attempt}/${maxAttempts}...`);
      await new Promise(r => setTimeout(r, intervalMs));
      process.stdout.write('\r                                        \r');
    }
  }
  
  console.log(`\n⚠️ Attestation not ready after ${maxAttempts} attempts`);
  console.log('   Run again later to continue polling');
  return state;
}

async function stepMint(bridgeId) {
  const state = getState(bridgeId);
  if (!state) throw new Error(`Bridge ${bridgeId} not found`);
  if (state.mintTx) {
    console.log(`✅ Already minted: ${state.mintTx}`);
    return state;
  }
  if (!state.attestation) {
    throw new Error('No attestation - must wait for attestation first');
  }
  
  const toChain = CHAINS[state.toChain];
  const wallet = getWallet(toChain);
  
  const messageTransmitter = new ethers.Contract(
    toChain.messageTransmitter,
    MESSAGE_TRANSMITTER_ABI,
    wallet
  );
  
  setState(bridgeId, { status: STATES.MINTING });
  console.log('💰 Minting USDC on destination chain...');
  
  const tx = await messageTransmitter.receiveMessage(
    state.message,
    state.attestation
  );
  
  console.log(`📝 Mint TX: ${toChain.explorer}${tx.hash}`);
  
  const receipt = await tx.wait();
  if (receipt.status !== 1) {
    throw new Error('Mint transaction failed');
  }
  
  console.log('✅ Minted! Bridge complete!');
  
  return setState(bridgeId, {
    status: STATES.COMPLETE,
    mintTx: tx.hash
  });
}

// Run full bridge (all steps)
async function runBridge(bridgeId) {
  try {
    await stepApprove(bridgeId);
    await stepBurn(bridgeId);
    await stepAttest(bridgeId);
    await stepMint(bridgeId);
    
    const state = getState(bridgeId);
    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ BRIDGE COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID:        ${bridgeId}
Amount:    ${state.amount} USDC
From:      ${CHAINS[state.fromChain].name}
To:        ${CHAINS[state.toChain].name}
Approve:   ${state.approveTx}
Burn:      ${state.burnTx}
Mint:      ${state.mintTx}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
    return state;
  } catch (e) {
    setState(bridgeId, { status: STATES.FAILED, error: e.message });
    throw e;
  }
}

// Resume a bridge from current state
async function resumeBridge(bridgeId) {
  const state = getState(bridgeId);
  if (!state) throw new Error(`Bridge ${bridgeId} not found`);
  
  console.log(`Resuming bridge ${bridgeId} from status: ${state.status}`);
  
  switch (state.status) {
    case STATES.PENDING:
    case STATES.APPROVING:
      await stepApprove(bridgeId);
      // fall through
    case STATES.APPROVED:
    case STATES.BURNING:
      await stepBurn(bridgeId);
      // fall through
    case STATES.BURNED:
    case STATES.ATTESTING:
      await stepAttest(bridgeId);
      // fall through
    case STATES.ATTESTED:
    case STATES.MINTING:
      await stepMint(bridgeId);
      break;
    case STATES.COMPLETE:
      console.log('Bridge already complete!');
      break;
    case STATES.FAILED:
      console.log('Bridge failed. Check error and retry individual steps.');
      break;
  }
  
  return getState(bridgeId);
}

// List all bridges
function listBridges() {
  const states = loadStates();
  const bridges = Object.values(states);
  
  if (bridges.length === 0) {
    console.log('No bridges found');
    return;
  }
  
  console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 BRIDGE LIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  
  for (const b of bridges) {
    const status = b.status === STATES.COMPLETE ? '✅' : 
                   b.status === STATES.FAILED ? '❌' : '⏳';
    console.log(`${status} ${b.id}`);
    console.log(`   ${b.amount} USDC: ${CHAINS[b.fromChain]?.name || b.fromChain} → ${CHAINS[b.toChain]?.name || b.toChain}`);
    console.log(`   Status: ${b.status}`);
    if (b.error) console.log(`   Error: ${b.error}`);
    console.log('');
  }
}

// Get bridge status
function bridgeStatus(bridgeId) {
  const state = getState(bridgeId);
  if (!state) {
    console.log(`Bridge ${bridgeId} not found`);
    return null;
  }
  
  const fromChain = CHAINS[state.fromChain];
  const toChain = CHAINS[state.toChain];
  
  console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌉 BRIDGE STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID:      ${state.id}
Status:  ${state.status}
Amount:  ${state.amount} USDC
From:    ${fromChain?.name || state.fromChain}
To:      ${toChain?.name || state.toChain}
Wallet:  ${state.walletAddress}

Steps:
  ${state.approveTx ? '✅' : '⬜'} Approve ${state.approveTx ? `(${state.approveTx.slice(0,10)}...)` : ''}
  ${state.burnTx ? '✅' : '⬜'} Burn    ${state.burnTx ? `(${state.burnTx.slice(0,10)}...)` : ''}
  ${state.attestation ? '✅' : '⬜'} Attest  ${state.messageHash ? `(${state.messageHash.slice(0,10)}...)` : ''}
  ${state.mintTx ? '✅' : '⬜'} Mint    ${state.mintTx ? `(${state.mintTx.slice(0,10)}...)` : ''}
${state.error ? `\nError: ${state.error}` : ''}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
  
  return state;
}

// CLI
const command = process.argv[2];
const args = process.argv.slice(3);

switch (command) {
  case 'start':
    // start <from> <to> <amount>
    if (args.length < 3) {
      console.log('Usage: bridge-async.js start <from_chain> <to_chain> <amount>');
      console.log('Chains: base_sepolia, ethereum_sepolia');
      process.exit(1);
    }
    initiateBridge(args[0], args[1], args[2])
      .then(id => runBridge(id))
      .catch(e => console.error('Error:', e.message));
    break;
    
  case 'resume':
    // resume <bridge_id>
    if (!args[0]) {
      console.log('Usage: bridge-async.js resume <bridge_id>');
      process.exit(1);
    }
    resumeBridge(args[0])
      .catch(e => console.error('Error:', e.message));
    break;
    
  case 'status':
    // status <bridge_id>
    if (!args[0]) {
      console.log('Usage: bridge-async.js status <bridge_id>');
      process.exit(1);
    }
    bridgeStatus(args[0]);
    break;
    
  case 'list':
    listBridges();
    break;
    
  case 'attest':
    // Just poll attestation for a bridge
    if (!args[0]) {
      console.log('Usage: bridge-async.js attest <bridge_id>');
      process.exit(1);
    }
    stepAttest(args[0])
      .catch(e => console.error('Error:', e.message));
    break;
    
  case 'mint':
    // Just mint for a bridge (if attestation ready)
    if (!args[0]) {
      console.log('Usage: bridge-async.js mint <bridge_id>');
      process.exit(1);
    }
    stepMint(args[0])
      .catch(e => console.error('Error:', e.message));
    break;
    
  default:
    console.log(`
Async Bridge - Production CCTP Bridging

Commands:
  start <from> <to> <amount>  Start a new bridge
  resume <bridge_id>          Resume a bridge from current state
  status <bridge_id>          Check bridge status
  list                        List all bridges
  attest <bridge_id>          Poll for attestation only
  mint <bridge_id>            Mint on destination (needs attestation)

Chains: base_sepolia, ethereum_sepolia

Examples:
  node bridge-async.js start base_sepolia ethereum_sepolia 1
  node bridge-async.js status bridge_1234567890_abc123
  node bridge-async.js resume bridge_1234567890_abc123
`);
}
