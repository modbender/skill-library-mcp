const { ethers } = require('ethers');

const BASE_RPC = 'https://mainnet.base.org';
const AAVEGOTCHI_DIAMOND = '0xA99c4B08201F2913Db8D28e71d020c4298F29dBF';

async function testBRSMethods(tokenId) {
  const provider = new ethers.JsonRpcProvider(BASE_RPC);
  
  // Try different possible function signatures
  const possibleFunctions = [
    'function calculateRarityScore(uint256 _tokenId) external view returns (uint256)',
    'function getFullRarityScore(uint256 _tokenId) external view returns (uint256)',
    'function rarityScoreWithAge(uint256 _tokenId) external view returns (uint256)',
    'function getTotalRarityScore(uint256 _tokenId) external view returns (uint256)'
  ];
  
  for (const funcSig of possibleFunctions) {
    try {
      const contract = new ethers.Contract(AAVEGOTCHI_DIAMOND, [funcSig], provider);
      const funcName = funcSig.match(/function (\w+)/)[1];
      console.log(`Testing ${funcName}...`);
      const result = await contract[funcName](tokenId);
      console.log(`✅ ${funcName}: ${result}`);
      return;
    } catch (e) {
      console.log(`❌ ${funcSig.match(/function (\w+)/)[1]} not found`);
    }
  }
  
  console.log('\n⚠️ No alternative BRS methods found');
  console.log('We need to calculate aging bonus manually');
}

const tokenId = process.argv[2] || '1484';
testBRSMethods(tokenId);
