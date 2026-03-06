const { ethers } = require('ethers');

const BASE_RPC = 'https://mainnet.base.org';
const AAVEGOTCHI_DIAMOND = '0xA99c4B08201F2913Db8D28e71d020c4298F29dBF';

// The gotchi is "born" when it's claimed from a portal
// We need to find the ClaimAavegotchi event or the first Transfer event to a non-zero address
const ABI = [
  'event Transfer(address indexed from, address indexed to, uint256 indexed tokenId)',
  'event ClaimAavegotchi(uint256 indexed tokenId)'
];

async function getGotchiBirthBlock(tokenId) {
  const provider = new ethers.JsonRpcProvider(BASE_RPC);
  const contract = new ethers.Contract(AAVEGOTCHI_DIAMOND, ABI, provider);
  
  const currentBlock = await provider.getBlockNumber();
  
  // Base started at block ~0, but Aavegotchi migrated later
  // Let's start from a known deployment block (you might need to adjust this)
  const START_BLOCK = 0; // Start from genesis
  const CHUNK_SIZE = 10000; // Query in chunks to avoid rate limits
  
  console.log(`Searching for birth of gotchi #${tokenId}...`);
  console.log(`Current block: ${currentBlock}`);
  
  // Look for the first Transfer event where 'from' is zero address (mint)
  // or ClaimAavegotchi event
  
  try {
    // Try to find ClaimAavegotchi event first (more specific)
    const claimFilter = contract.filters.ClaimAavegotchi(tokenId);
    const claimEvents = await contract.queryFilter(claimFilter, START_BLOCK, currentBlock);
    
    if (claimEvents.length > 0) {
      const birthBlock = claimEvents[0].blockNumber;
      console.log(`✅ Found ClaimAavegotchi event at block ${birthBlock}`);
      return birthBlock;
    }
  } catch (e) {
    console.log(`ClaimAavegotchi event not found or not indexed: ${e.message}`);
  }
  
  // Fallback: Look for first Transfer to a non-zero address
  try {
    const transferFilter = contract.filters.Transfer(null, null, tokenId);
    const transferEvents = await contract.queryFilter(transferFilter, START_BLOCK, currentBlock);
    
    if (transferEvents.length > 0) {
      // Find the first transfer from zero address (mint)
      const mintEvent = transferEvents.find(e => e.args.from === ethers.ZeroAddress);
      if (mintEvent) {
        const birthBlock = mintEvent.blockNumber;
        console.log(`✅ Found mint Transfer event at block ${birthBlock}`);
        return birthBlock;
      }
      
      // If no mint found, use first transfer (gotchi was already minted)
      const birthBlock = transferEvents[0].blockNumber;
      console.log(`⚠️  Using first Transfer event at block ${birthBlock}`);
      return birthBlock;
    }
  } catch (e) {
    console.error(`Error querying Transfer events: ${e.message}`);
  }
  
  throw new Error(`Could not find birth block for gotchi #${tokenId}`);
}

// Run if called directly
if (require.main === module) {
  const tokenId = process.argv[2];
  if (!tokenId) {
    console.error('Usage: node get-gotchi-birth-block.js <tokenId>');
    process.exit(1);
  }
  
  getGotchiBirthBlock(tokenId)
    .then(birthBlock => {
      console.log(`\nBirth block: ${birthBlock}`);
    })
    .catch(err => {
      console.error('Error:', err.message);
      process.exit(1);
    });
}

module.exports = { getGotchiBirthBlock };
