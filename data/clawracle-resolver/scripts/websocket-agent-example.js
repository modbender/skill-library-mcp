// Complete WebSocket Agent Example with Error Handling
// This shows how to set up WebSocket event listening with proper try-catch blocks

const { ethers } = require('ethers');
const fs = require('fs');
require('dotenv').config();

// ============ CONFIGURATION ============

const STORAGE_FILE = './agent-storage.json';

// WebSocket URL for event listening (REQUIRED for Monad)
const WS_RPC_URL = 'wss://rpc.monad.xyz';
// HTTP URL for transactions (more reliable)
const HTTP_RPC_URL = 'https://rpc.monad.xyz';

// ============ STORAGE MANAGEMENT ============

// Load tracked requests from agent-storage.json
function loadStorage() {
  try {
    if (fs.existsSync(STORAGE_FILE)) {
      const data = JSON.parse(fs.readFileSync(STORAGE_FILE, 'utf8'));
      console.log(`Loaded ${Object.keys(data.trackedRequests || {}).length} tracked requests`);
      return data;
    }
  } catch (error) {
    console.error('Error loading storage:', error);
  }
  return { trackedRequests: {} };
}

// Save tracked requests to agent-storage.json
function saveStorage(storage) {
  try {
    fs.writeFileSync(STORAGE_FILE, JSON.stringify(storage, null, 2));
  } catch (error) {
    console.error('Error saving storage:', error);
  }
}

// Initialize storage
let storage = loadStorage();

// ============ WEBSOCKET SETUP ============

// CRITICAL: Use WebSocket for event listening (Monad doesn't support eth_newFilter on HTTP)
const wsProvider = new ethers.WebSocketProvider(WS_RPC_URL);

// Use HTTP provider for transactions (more reliable)
const httpProvider = new ethers.JsonRpcProvider(HTTP_RPC_URL);
const wallet = new ethers.Wallet(process.env.CLAWRACLE_AGENT_KEY, httpProvider);

console.log('🤖 Clawracle Agent Starting...');
console.log(`Wallet: ${wallet.address}`);
console.log(`WebSocket URL: ${WS_RPC_URL}`);

// ============ CONTRACT SETUP ============

const registryAddress = '0x1F68C6D1bBfEEc09eF658B962F24278817722E18';
const registryABI = [
  "event RequestSubmitted(uint256 indexed requestId, address indexed requester, string ipfsCID, string category, uint256 validFrom, uint256 deadline, uint256 reward, uint256 bondRequired)",
  "event AnswerProposed(uint256 indexed requestId, uint256 indexed answerId, address indexed agent, uint256 agentId, bytes answer, uint256 bond)",
  "event AnswerDisputed(uint256 indexed requestId, uint256 indexed answerId, address indexed disputer, uint256 disputerAgentId, bytes disputedAnswer, uint256 bond, uint256 originalAnswerId)",
  "event RequestFinalized(uint256 indexed requestId, uint256 winningAnswerId, address winner, uint256 reward)",
  "function getQuery(uint256 requestId) external view returns (tuple(uint256 requestId, string ipfsCID, uint256 validFrom, uint256 deadline, address requester, string category, uint8 expectedFormat, uint256 bondRequired, uint256 reward, uint8 status, uint256 createdAt, uint256 resolvedAt))",
  "function finalizeRequest(uint256 requestId) external"
];

// Use WebSocket provider for event listening
const registry = new ethers.Contract(registryAddress, registryABI, wsProvider);

// Use wallet (HTTP provider) for transactions
const registryWithWallet = new ethers.Contract(registryAddress, registryABI, wallet);

// ============ EVENT LISTENERS (WITH TRY-CATCH) ============

// CRITICAL: ALL event listeners MUST be wrapped in try-catch to prevent WebSocket crashes

// Listen for new requests
registry.on('RequestSubmitted', async (requestId, requester, ipfsCID, category, validFrom, deadline, reward, bondRequired, event) => {
  try {
    console.log(`\n🔔 New Request #${requestId}`);
    console.log(`Category: ${category}`);
    console.log(`Reward: ${ethers.formatEther(reward)} CLAWCLE`);
    console.log(`Valid From: ${new Date(Number(validFrom) * 1000).toLocaleString()}`);
    console.log(`Deadline: ${new Date(Number(deadline) * 1000).toLocaleString()}`);
    
    // Store request in agent-storage.json
    storage.trackedRequests[requestId.toString()] = {
      requestId: Number(requestId),
      category: category,
      validFrom: Number(validFrom),
      deadline: Number(deadline),
      reward: reward.toString(),
      bondRequired: bondRequired.toString(),
      ipfsCID: ipfsCID,
      status: 'PENDING',
      myAnswerId: null,
      resolvedAt: null,
      finalizationTime: null,
      isDisputed: false
    };
    saveStorage(storage);
    console.log('✅ Request stored in agent-storage.json');
  } catch (error) {
    console.error(`Error handling RequestSubmitted event:`, error.message);
    // Don't crash - continue listening for other events
  }
});

// Listen for answer proposals
registry.on('AnswerProposed', async (requestId, answerId, agent, agentId, answer, bond, event) => {
  try {
    const requestData = storage.trackedRequests[requestId.toString()];
    if (!requestData) return;

    if (agent.toLowerCase() === wallet.address.toLowerCase()) {
      requestData.myAnswerId = Number(answerId);
      requestData.status = 'PROPOSED';
      requestData.resolvedAt = Math.floor(Date.now() / 1000);
      requestData.finalizationTime = requestData.resolvedAt + 300; // 5 minutes
      saveStorage(storage);
      console.log(`✅ My answer #${answerId} proposed`);
    }
  } catch (error) {
    console.error(`Error handling AnswerProposed event:`, error.message);
    // Don't crash - continue listening
  }
});

// Listen for disputes
registry.on('AnswerDisputed', async (requestId, answerId, disputer, disputerAgentId, disputedAnswer, bond, originalAnswerId, event) => {
  try {
    const requestData = storage.trackedRequests[requestId.toString()];
    if (!requestData) return;

    requestData.status = 'DISPUTED';
    requestData.isDisputed = true;
    // Extend finalization time: 5 min dispute + 5 min validation = 10 min total
    if (requestData.resolvedAt) {
      requestData.finalizationTime = requestData.resolvedAt + 300 + 300; // 10 minutes
    }
    saveStorage(storage);
    console.log(`⚠️  Request #${requestId} disputed by ${disputer}`);
  } catch (error) {
    console.error(`Error handling AnswerDisputed event:`, error.message);
    // Don't crash - continue listening
  }
});

// Listen for finalization
registry.on('RequestFinalized', async (requestId, winningAnswerId, winner, reward, event) => {
  try {
    if (winner.toLowerCase() === wallet.address.toLowerCase()) {
      console.log(`\n🎉 YOU WON Request #${requestId}!`);
      console.log(`💰 Reward: ${ethers.formatEther(reward)} CLAWCLE`);
    }
    delete storage.trackedRequests[requestId.toString()];
    saveStorage(storage);
  } catch (error) {
    console.error(`Error handling RequestFinalized event:`, error.message);
    // Don't crash - continue listening
  }
});

// ============ PERIODIC CHECK (WITH TRY-CATCH) ============

// Periodic check for finalization (every 2 seconds)
setInterval(async () => {
  try {
    const now = Math.floor(Date.now() / 1000);
    for (const requestId in storage.trackedRequests) {
      const requestData = storage.trackedRequests[requestId];
      
      // Check if request needs finalization
      if (requestData.status === 'PROPOSED' || requestData.status === 'DISPUTED') {
        if (requestData.resolvedAt && requestData.finalizationTime) {
          const DISPUTE_PERIOD = 300; // 5 minutes
          const VALIDATION_PERIOD = 300; // 5 minutes
          
          let finalizationAllowedAt = requestData.resolvedAt + DISPUTE_PERIOD;
          if (requestData.status === 'DISPUTED') {
            finalizationAllowedAt += VALIDATION_PERIOD; // 10 minutes total
          }
          
          if (now >= finalizationAllowedAt) {
            try {
              // Check on-chain status (CRITICAL: Convert BigInt to Number)
              const query = await registryWithWallet.getQuery(Number(requestId));
              const onChainStatus = Number(query.status); // Convert BigInt to Number!
              
              if (onChainStatus === 3) {
                // Already finalized
                requestData.status = 'FINALIZED';
                saveStorage(storage);
                continue;
              }
              
              if (onChainStatus === 1 || onChainStatus === 2) {
                // Finalize
                console.log(`⏰ Finalizing Request #${requestId}...`);
                const finalizeTx = await registryWithWallet.finalizeRequest(Number(requestId));
                await finalizeTx.wait();
                console.log(`✅ Request #${requestId} finalized`);
                requestData.status = 'FINALIZED';
                saveStorage(storage);
              }
            } catch (error) {
              console.error(`Error finalizing Request #${requestId}:`, error.message);
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('Error in periodic check:', error.message);
    // Don't crash - continue checking
  }
}, 2000);

// ============ WEBSOCKET ERROR HANDLING ============

// Handle WebSocket errors
wsProvider.on('error', (error) => {
  console.error('WebSocket error:', error);
  // WebSocket will attempt to reconnect automatically
});

// Handle WebSocket close
wsProvider.on('close', () => {
  console.log('WebSocket closed - attempting reconnect...');
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n👋 Closing WebSocket connection...');
  wsProvider.destroy();
  process.exit(0);
});

console.log('\n👂 Listening for requests via WebSocket...');
console.log('   (Press Ctrl+C to stop)\n');
