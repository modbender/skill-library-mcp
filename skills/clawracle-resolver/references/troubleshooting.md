# Troubleshooting Guide

## Common Errors and Solutions

### 1. WebSocket Connection Issues

**Error**: `Method not found: eth_newFilter`

**Cause**: Monad's HTTP RPC doesn't support `eth_newFilter`. You MUST use WebSocket for event listening.

**Solution**:
```javascript
// ❌ WRONG - HTTP RPC for events
const provider = new ethers.JsonRpcProvider('https://rpc.monad.xyz');
const registry = new ethers.Contract(address, abi, provider);

// ✅ CORRECT - WebSocket for events, HTTP for transactions
const wsProvider = new ethers.WebSocketProvider('wss://rpc.monad.xyz');
const httpProvider = new ethers.JsonRpcProvider('https://rpc.monad.xyz');
const wallet = new ethers.Wallet(process.env.CLAWRACLE_AGENT_KEY, httpProvider);

const registry = new ethers.Contract(address, abi, wsProvider); // WebSocket for events
const registryWithWallet = new ethers.Contract(address, abi, wallet); // HTTP for transactions
```

**Monad Mainnet Configuration**:
```bash
MONAD_WS_RPC_URL=wss://rpc.monad.xyz  # REQUIRED
MONAD_RPC_URL=https://rpc.monad.xyz  # For transactions
```

### 2. BigInt Conversion Issues

**Error**: Status comparisons failing (e.g., `query.status === 1` always false)

**Cause**: Contract enum values return as BigInt, not Number. `BigInt(1) !== Number(1)`.

**Solution**: Always convert BigInt to Number before comparison:
```javascript
// ❌ WRONG
const query = await registry.getQuery(requestId);
if (query.status === 1) { // This will NEVER be true!
  // ...
}

// ✅ CORRECT
const query = await registry.getQuery(requestId);
const status = Number(query.status); // Convert BigInt to Number
if (status === 1) { // Now it works!
  // ...
}
```

**Status Values**:
- `0` = Pending
- `1` = Proposed
- `2` = Disputed
- `3` = Finalized

### 3. Event Listeners Crashing

**Error**: Agent stops listening after an error in event handler

**Cause**: Unhandled errors in event listeners crash the WebSocket connection.

**Solution**: Wrap ALL event listeners in try-catch:
```javascript
// ❌ WRONG - Crashes on error
registry.on('RequestSubmitted', async (requestId, ...) => {
  // If this throws, WebSocket crashes
  const data = await someAsyncOperation();
});

// ✅ CORRECT - Errors are caught, agent continues
registry.on('RequestSubmitted', async (requestId, ...) => {
  try {
    const data = await someAsyncOperation();
  } catch (error) {
    console.error(`Error handling RequestSubmitted event:`, error.message);
    // Don't crash - continue listening
  }
});
```

### 4. IPFS Fetching Failures

**Error**: `Request failed with status code 403` or `All gateways failed`

**Cause**: IPFS gateways can be unreliable or rate-limited.

**Solution**: Use multiple gateways with retry logic:
```javascript
const IPFS_GATEWAYS = [
  'https://ipfs.io/ipfs/',
  'https://gateway.pinata.cloud/ipfs/',
  'https://cloudflare-ipfs.com/ipfs/',
  'https://dweb.link/ipfs/',
  'https://filebase.io/ipfs/'
];

async function fetchIPFS(cid) {
  for (const gateway of IPFS_GATEWAYS) {
    try {
      const response = await axios.get(`${gateway}${cid}`, {
        headers: { 'User-Agent': 'Clawracle-Agent/1.0' },
        timeout: 10000,
        validateStatus: (status) => status < 500 // Accept 4xx but retry on 5xx
      });
      return response.data;
    } catch (error) {
      continue; // Try next gateway
    }
  }
  throw new Error('All IPFS gateways failed');
}
```

### 5. Concurrent Processing Issues

**Error**: `nonce has already been used` or duplicate transactions

**Cause**: Multiple `resolveQuery` calls for the same request running simultaneously.

**Solution**: Use processing locks:
```javascript
const processingLocks = new Set();

async function resolveQuery(requestId) {
  const requestIdStr = requestId.toString();
  
  // Check if already processing
  if (processingLocks.has(requestIdStr)) {
    console.log(`Request #${requestId} already being processed`);
    return;
  }
  
  // Lock
  processingLocks.add(requestIdStr);
  
  try {
    // Your processing logic here
  } finally {
    // Always release lock
    processingLocks.delete(requestIdStr);
  }
}
```

### 6. JSON Mode Not Supported

**Error**: `Invalid parameter: 'response_format' of type 'json_object' is not supported with this model`

**Cause**: Some OpenAI models don't support JSON mode.

**Solution**: Implement fallback with robust JSON extraction:
```javascript
let response;
try {
  // Try with JSON mode first
  response = await openai.chat.completions.create({
    model: model,
    messages: [...],
    response_format: { type: 'json_object' }
  });
} catch (error) {
  // Fallback: try without JSON mode
  response = await openai.chat.completions.create({
    model: model,
    messages: [...]
  });
  
  // Extract JSON from text response
  const content = response.choices[0].message.content;
  const jsonMatch = content.match(/\{[\s\S]*\}/);
  if (jsonMatch) {
    return JSON.parse(jsonMatch[0]);
  }
}
```

### 7. Balance Check Failures

**Error**: `could not decode result data (value="0x", info={ "method": "balanceOf" })`

**Cause**: RPC flakiness or token contract not deployed.

**Solution**: Add retries and make non-blocking:
```javascript
async function checkBalance(wallet, token, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const balance = await token.balanceOf(wallet.address);
      return balance;
    } catch (error) {
      if (i < retries - 1) {
        console.log(`   Retrying balance check... (${retries - i - 1} attempts left)`);
        await new Promise(resolve => setTimeout(resolve, 1000));
        continue;
      }
      console.log(`   ⚠️  Could not check balance after ${retries} attempts`);
      return null; // Non-blocking - continue anyway
    }
  }
}
```

### 8. Finalization Not Triggering

**Issue**: Requests ready to finalize but agent doesn't call `finalizeRequest()`

**Causes**:
1. Status check using BigInt without conversion
2. Finalization time calculation incorrect
3. Processing lock preventing execution

**Solution**: Check all three:
```javascript
// 1. Convert BigInt
const onChainStatus = Number(query.status);

// 2. Calculate finalization time correctly
const DISPUTE_PERIOD = 300; // 5 minutes
const VALIDATION_PERIOD = 300; // 5 minutes
let finalizationAllowedAt = requestData.resolvedAt + DISPUTE_PERIOD;
if (requestData.status === 'DISPUTED') {
  finalizationAllowedAt += VALIDATION_PERIOD; // 10 minutes total
}

// 3. Check lock
if (!processingLocks.has(requestId + '_finalize')) {
  // Proceed with finalization
}
```

### 9. Lighthouse IPFS Upload Failures

**Error**: `ETIMEDOUT` or `ECONNREFUSED` when uploading to Lighthouse

**Causes**:
- Invalid API key
- Network issues
- Lighthouse service down

**Solution**: 
1. Verify `LIGHTHOUSE_API_KEY` in `.env`
2. Check network connectivity
3. Use `@lighthouse-web3/sdk` for more robust uploads:
```javascript
const lighthouse = require('@lighthouse-web3/sdk');

const uploadResponse = await lighthouse.uploadText(
  queryText,
  process.env.LIGHTHOUSE_API_KEY
);
```

### 10. API Key Not Found

**Error**: `API key required but not found: OPENWEATHER_API_KEY`

**Causes**:
- Missing from `.env`
- Wrong environment variable name
- Not loaded (forgot `require('dotenv').config()`)

**Solution**:
1. Check `.env` file has the key
2. Verify variable name matches `apiKeyEnvVar` in `api-config.json`
3. Ensure `require('dotenv').config()` is called before accessing `process.env`
4. Check if free API key is available in `api-config.json` (`freeApiKey` field)

## Debugging Tips

### Enable Verbose Logging

Add detailed console logs to trace execution:
```javascript
console.log(`[DEBUG] Request #${requestId}: status=${status}, now=${now}, allowedAt=${finalizationAllowedAt}`);
```

### Check On-Chain Status

Always verify on-chain status matches local storage:
```javascript
const query = await registry.getQuery(requestId);
console.log('On-chain status:', Number(query.status));
console.log('Local status:', requestData.status);
```

### Monitor WebSocket Connection

Add connection event handlers:
```javascript
wsProvider.on('error', (error) => {
  console.error('WebSocket error:', error);
});

wsProvider.on('close', () => {
  console.log('WebSocket closed - attempting reconnect...');
});
```

### Check Processing Locks

Log when locks are added/removed:
```javascript
console.log(`[LOCK] Adding lock for ${requestId}`);
processingLocks.add(requestId);
// ...
console.log(`[LOCK] Removing lock for ${requestId}`);
processingLocks.delete(requestId);
```

## Getting Help

1. Check this troubleshooting guide first
2. Review `{baseDir}/guide/TECHNICAL_REFERENCE.md` for contract details
3. Check `{baseDir}/agent/clawracle-agent.js` for working implementation
4. Verify all environment variables are set correctly
5. Ensure WebSocket URL is correct and accessible
