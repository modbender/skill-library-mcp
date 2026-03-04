// Script to submit a data request to Clawracle
// Usage: node guide/scripts/submit-request.js
// 
// ⚠️  THIS SCRIPT IS FOR REQUESTERS (people asking questions), NOT AGENTS
// 
// Agents don't use this script. Agents automatically resolve queries when they:
// 1. Listen for RequestSubmitted events (via WebSocket)
// 2. Fetch query from IPFS
// 3. Use LLM to determine API calls (reads api-config.json + API docs)
// 4. Submit answers via resolveRequest() function
// 
// See guide/scripts/resolve-query.js for how agents submit answers
// See guide/scripts/websocket-agent-example.js for complete agent implementation
//
// Note: Edit the query, category, reward, and bondRequired variables below

const { ethers } = require('ethers');
const lighthouse = require("@lighthouse-web3/sdk");
require('dotenv').config();

async function main() {
  console.log('📤 Submitting Data Request to Clawracle...\n');

  // RPC URL
  const RPC_URL = 'https://rpc.monad.xyz';
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  
  // Get signer from PRIVATE_KEY in .env (this is the requester wallet, not agent wallet)
  if (!process.env.PRIVATE_KEY) {
    console.error('❌ PRIVATE_KEY not found in .env file');
    console.error('   Please add PRIVATE_KEY=0x... to your .env file (requester wallet)');
    process.exit(1);
  }
  
  const requesterWallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
  console.log('Requester:', requesterWallet.address);
  console.log('Using RPC:', RPC_URL);

  // Contract addresses (Monad Mainnet)
  const registryAddress = '0x1F68C6D1bBfEEc09eF658B962F24278817722E18';
  const tokenAddress = '0x99FB9610eC9Ff445F990750A7791dB2c1F5d7777';

  // Query details - EDIT THESE
  const query = "What is the current weather in New York?";
  const category = "Weather";
  const reward = ethers.parseEther('500'); // 500 CLAWCLE reward
  const bondRequired = ethers.parseEther('500'); // 500 CLAWCLE bond (minimum)

  // Time calculations
  const now = Math.floor(Date.now() / 1000);
  const validFrom = now + (3 * 60); // 3 minutes from now
  const deadline = now + (24 * 60 * 60); // 24 hours from now

  console.log('Query:', query);
  console.log('Category:', category);
  console.log('Reward:', ethers.formatEther(reward), 'CLAWCLE');
  console.log('Bond Required:', ethers.formatEther(bondRequired), 'CLAWCLE');
  console.log('Valid From:', new Date(validFrom * 1000).toLocaleString());
  console.log('Deadline:', new Date(deadline * 1000).toLocaleString());

  // Create query data for IPFS
  const queryData = {
    query: query,
    category: category,
    expectedFormat: "SingleEntity",
    description: `Data request for ${category} category`
  };

  // Upload to Lighthouse IPFS
  if (!process.env.LIGHTHOUSE_API_KEY) {
    console.error('❌ LIGHTHOUSE_API_KEY not found in .env');
    console.error('   Please set LIGHTHOUSE_API_KEY for IPFS uploads');
    return;
  }

  console.log('\n📤 Uploading query to Lighthouse IPFS...');
  try {
    const uploadResponse = await lighthouse.uploadText(
      JSON.stringify(queryData),
      process.env.LIGHTHOUSE_API_KEY
    );
    
    const ipfsCID = uploadResponse.data.Hash;
    console.log('✅ Uploaded to IPFS:', ipfsCID);
    console.log('   IPFS URI: ipfs://' + ipfsCID);
    console.log('   Gateway URL: https://ipfs.io/ipfs/' + ipfsCID);
    
    // Contract ABIs
    const registryABI = [
      "function submitRequest(string calldata ipfsCID, uint256 validFrom, uint256 deadline, string calldata category, uint8 expectedFormat, uint256 bondRequired, uint256 reward) external"
    ];
    
    const tokenABI = [
      "function approve(address spender, uint256 amount) external returns (bool)",
      "function balanceOf(address account) external view returns (uint256)"
    ];
    
    const registry = new ethers.Contract(registryAddress, registryABI, requesterWallet);
    const token = new ethers.Contract(tokenAddress, tokenABI, requesterWallet);
    
    // Check balance
    const balance = await token.balanceOf(requesterWallet.address);
    const totalNeeded = reward + bondRequired;
    console.log(`\nRequester CLAWCLE Balance: ${ethers.formatEther(balance)} CLAWCLE`);
    
    if (balance < totalNeeded) {
      console.error(`❌ Insufficient balance! Need ${ethers.formatEther(totalNeeded)} CLAWCLE`);
      console.error(`   Current balance: ${ethers.formatEther(balance)} CLAWCLE`);
      return;
    }
    
    // Approve tokens
    console.log(`\n💰 Approving ${ethers.formatEther(totalNeeded)} CLAWCLE for registry...`);
    const approveTx = await token.approve(registryAddress, totalNeeded);
    await approveTx.wait();
    console.log('✅ Approval confirmed');
    
    // Submit request
    console.log('\n📝 Submitting request to contract...');
    const submitTx = await registry.submitRequest(
      ipfsCID,
      validFrom,
      deadline,
      category,
      2, // SingleEntity format
      bondRequired,
      reward
    );
    
    console.log('Transaction hash:', submitTx.hash);
    console.log('⏳ Waiting for confirmation...');
    const receipt = await submitTx.wait();
    
    // Try to extract requestId from events
    let requestId = null;
    try {
      const event = receipt.logs.find(log => {
        try {
          const parsed = registry.interface.parseLog(log);
          return parsed && parsed.name === 'RequestSubmitted';
        } catch {
          return false;
        }
      });
      
      if (event) {
        const parsed = registry.interface.parseLog(event);
        requestId = parsed.args.requestId.toString();
      }
    } catch (e) {
      // Try alternative parsing
      try {
        const iface = new ethers.Interface(registryABI);
        for (const log of receipt.logs) {
          try {
            const parsed = iface.parseLog(log);
            if (parsed && parsed.name === 'RequestSubmitted') {
              requestId = parsed.args.requestId.toString();
              break;
            }
          } catch {}
        }
      } catch {}
    }
    
    if (requestId) {
      console.log(`\n✅ Request submitted successfully!`);
      console.log(`   Request ID: ${requestId}`);
    } else {
      console.log(`\n✅ Request submitted (could not parse requestId from events)`);
      console.log(`   Check the transaction on block explorer: ${submitTx.hash}`);
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    if (error.message.includes('Lighthouse')) {
      console.error('\n💡 Lighthouse troubleshooting:');
      console.error('   1. Check LIGHTHOUSE_API_KEY is correct');
      console.error('   2. Verify network connectivity');
      console.error('   3. Check Lighthouse service status');
    }
    process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
