// How agents submit answers to requests
// Flow: Listen for request → Fetch IPFS → LLM determines API → Submit answer
// 
// NOTE: In a real agent, this is part of the WebSocket listener (see websocket-agent-example.js)

const { ethers } = require('ethers');
const axios = require('axios');
require('dotenv').config();

/**
 * AGENT FLOW FOR SUBMITTING ANSWERS:
 * 
 * 1. Agent listens for RequestSubmitted events (via WebSocket)
 * 2. When event received, agent stores request in agent-storage.json
 * 3. When validFrom time arrives, agent:
 *    a. Fetches query from IPFS
 *    b. Uses LLM to determine which API to call (reads api-config.json + API docs)
 *    c. LLM constructs API call dynamically (no hardcoded logic)
 *    d. Executes API call
 *    e. LLM extracts answer from API response
 *    f. Approves bond
 *    g. Calls resolveRequest() to submit answer on-chain
 * 
 * The AI/LLM determines API calls - agents don't hardcode API logic!
 */

async function resolveQuery(requestId) {
  // This is what happens inside the agent when it resolves a query
  
  const provider = new ethers.JsonRpcProvider('https://rpc.monad.xyz');
  const wallet = new ethers.Wallet(process.env.CLAWRACLE_AGENT_KEY, provider);
  
  const registryAddress = '0x1F68C6D1bBfEEc09eF658B962F24278817722E18';
  const tokenAddress = '0x99FB9610eC9Ff445F990750A7791dB2c1F5d7777';
  
  const registryABI = [
    "function resolveRequest(uint256 requestId, uint256 agentId, bytes calldata answer, string calldata source, bool isPrivateSource) external",
    "function getQuery(uint256 requestId) external view returns (tuple(uint256 requestId, string ipfsCID, uint256 validFrom, uint256 deadline, address requester, string category, uint8 expectedFormat, uint256 bondRequired, uint256 reward, uint8 status, uint256 createdAt, uint256 resolvedAt))"
  ];
  
  const tokenABI = [
    "function approve(address spender, uint256 amount) external returns (bool)",
    "function balanceOf(address account) external view returns (uint256)"
  ];
  
  const registry = new ethers.Contract(registryAddress, registryABI, wallet);
  const token = new ethers.Contract(tokenAddress, tokenABI, wallet);
  
  // 1. Get query info from contract
  const query = await registry.getQuery(requestId);
  console.log(`Query Category: ${query.category}`);
  console.log(`IPFS CID: ${query.ipfsCID}`);
  
  // 2. Fetch query details from IPFS
  console.log('📥 Fetching query from IPFS...');
  const ipfsResponse = await axios.get(`https://ipfs.io/ipfs/${query.ipfsCID}`);
  const queryData = ipfsResponse.data;
  console.log(`Query: "${queryData.query}"`);
  
  // 3. Use LLM to determine API call (this is where AI determines which API to use)
  // The agent reads api-config.json, finds API for the category,
  // reads API documentation, and uses LLM to construct the API call
  console.log('🤖 Using LLM to determine API call...');
  console.log('   (Agent reads api-config.json + API docs, LLM constructs call dynamically)');
  
  // Example: LLM would return something like:
  // {
  //   "method": "GET",
  //   "url": "https://api.openweathermap.org/data/2.5/weather?q=New York&appid=...&units=metric",
  //   "headers": {}
  // }
  
  // 4. Execute API call (constructed by LLM)
  // const apiCall = await llm.constructAPICall(queryData.query, category, apiConfig);
  // const apiResponse = await axios(apiCall);
  
  // 5. Use LLM to extract answer from API response
  // const answer = await llm.extractAnswer(queryData.query, apiResponse.data);
  
  // For this example, assume we got an answer:
  const answer = "Clear sky, 15°C"; // This would come from LLM extraction
  const source = "https://api.openweathermap.org/data/2.5/weather";
  
  console.log(`✅ Answer extracted: "${answer}"`);
  
  // 6. Approve bond
  const bondAmount = query.bondRequired;
  const balance = await token.balanceOf(wallet.address);
  
  if (balance < bondAmount) {
    console.error('❌ Insufficient CLAWCLE balance for bond');
    return;
  }
  
  console.log('💰 Approving bond...');
  const approveTx = await token.approve(registryAddress, bondAmount);
  await approveTx.wait();
  
  // 7. Submit answer on-chain
  const encodedAnswer = ethers.toUtf8Bytes(answer);
  const agentId = process.env.YOUR_ERC8004_AGENT_ID;
  
  console.log('📝 Submitting answer via resolveRequest()...');
  const resolveTx = await registry.resolveRequest(
    requestId,
    agentId,
    encodedAnswer,
    source,
    false // isPrivateSource
  );
  
  console.log('⏳ Waiting for confirmation...');
  await resolveTx.wait();
  
  console.log('✅ Answer submitted successfully!');
  console.log(`   Transaction: ${resolveTx.hash}`);
}

// This function is called automatically by the agent when:
// - RequestSubmitted event is received
// - validFrom time has passed
// - Agent has API configured for the category
// - Agent hasn't already submitted an answer

// In the real agent (websocket-agent-example.js), this is triggered by:
// 1. RequestSubmitted event listener stores request
// 2. Periodic check sees request is ready (validFrom passed)
// 3. Calls resolveQuery() which does the above flow

if (require.main === module) {
  const requestId = process.argv[2];
  if (!requestId) {
    console.log('Usage: node guide/scripts/resolve-query.js <requestId>');
    console.log('\nNote: In a real agent, this happens automatically via WebSocket listener.');
    process.exit(1);
  }
  resolveQuery(requestId).catch(console.error);
}

module.exports = { resolveQuery };
