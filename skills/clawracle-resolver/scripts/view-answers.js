// Script to view all proposed answers for a request
// Usage: node guide/scripts/view-answers.js <requestId>

const { ethers } = require('ethers');
require('dotenv').config();

async function main() {
  // Get requestId from command line argument
  const requestId = process.argv[2];
  
  if (!requestId) {
    console.error('Usage: node guide/scripts/view-answers.js <requestId>');
    console.error('Example: node guide/scripts/view-answers.js 3');
    process.exit(1);
  }

  const registryAddress = '0x1F68C6D1bBfEEc09eF658B962F24278817722E18';
  const rpcUrl = 'https://rpc.monad.xyz';

  const registryABI = [
    "function getQuery(uint256 requestId) external view returns (tuple(uint256 requestId, string ipfsCID, uint256 validFrom, uint256 deadline, address requester, string category, uint8 expectedFormat, uint256 bondRequired, uint256 reward, uint8 status, uint256 createdAt, uint256 resolvedAt))",
    "function getAnswers(uint256 requestId) external view returns (tuple(uint256 answerId, uint256 requestId, address agent, uint256 agentId, bytes answer, string source, bool isPrivateSource, uint256 bond, uint256 validations, uint256 disputes, uint256 timestamp, bool isOriginal)[])"
  ];

  // Connect to RPC
  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const registry = new ethers.Contract(registryAddress, registryABI, provider);

  console.log(`\n📋 Viewing answers for Request #${requestId}\n`);

  // Get query info
  try {
    const query = await registry.getQuery(requestId);
    const statusNames = ['Pending', 'Proposed', 'Disputed', 'Finalized'];
    const status = Number(query.status);
    
    console.log('Query Info:');
    console.log(`  Category: ${query.category}`);
    console.log(`  Status: ${statusNames[status]} (${status})`);
    console.log(`  Requester: ${query.requester}`);
    console.log(`  Reward: ${ethers.formatEther(query.reward)} CLAWCLE`);
    console.log(`  Bond Required: ${ethers.formatEther(query.bondRequired)} CLAWCLE`);
    console.log(`  Valid From: ${new Date(Number(query.validFrom) * 1000).toLocaleString()}`);
    console.log(`  Deadline: ${new Date(Number(query.deadline) * 1000).toLocaleString()}`);
    if (query.resolvedAt > 0) {
      console.log(`  Resolved At: ${new Date(Number(query.resolvedAt) * 1000).toLocaleString()}`);
    }
    console.log('');
  } catch (error) {
    console.error(`Error fetching query: ${error.message}`);
    return;
  }

  // Get all answers
  try {
    const answers = await registry.getAnswers(requestId);
    
    if (answers.length === 0) {
      console.log('❌ No answers submitted yet');
      return;
    }

    console.log(`📝 Found ${answers.length} answer(s):\n`);

    for (let i = 0; i < answers.length; i++) {
      const answer = answers[i];
      const answerText = ethers.toUtf8String(answer.answer);
      
      console.log(`Answer #${answer.answerId} (${i + 1}/${answers.length}):`);
      console.log(`  Agent: ${answer.agent}`);
      console.log(`  Agent ID: ${answer.agentId}`);
      console.log(`  Answer: "${answerText}"`);
      console.log(`  Source: ${answer.source}`);
      console.log(`  Is Private Source: ${answer.isPrivateSource}`);
      console.log(`  Bond: ${ethers.formatEther(answer.bond)} CLAWCLE`);
      console.log(`  Validations: ${answer.validations}`);
      console.log(`  Disputes: ${answer.disputes}`);
      console.log(`  Timestamp: ${new Date(Number(answer.timestamp) * 1000).toLocaleString()}`);
      console.log(`  Is Original: ${answer.isOriginal ? 'Yes' : 'No (disputed answer)'}`);
      console.log('');
    }
  } catch (error) {
    console.error(`Error fetching answers: ${error.message}`);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
