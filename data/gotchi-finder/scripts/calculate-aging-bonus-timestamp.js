const { ethers } = require('ethers');

// Fibonacci milestones in SECONDS (not blocks anymore!)
// Average block time ~2.3s on Polygon, but they use actual timestamps now
const AGING_MILESTONES_SECONDS = [
  { seconds: 1000000 * 2.3, bonus: 1 },   // ~1M blocks worth of time
  { seconds: 2000000 * 2.3, bonus: 2 },   // ~2M blocks
  { seconds: 3000000 * 2.3, bonus: 3 },   // ~3M blocks
  { seconds: 5000000 * 2.3, bonus: 5 },   // ~5M blocks
  { seconds: 8000000 * 2.3, bonus: 8 },   // ~8M blocks
  { seconds: 13000000 * 2.3, bonus: 13 }, // ~13M blocks
  { seconds: 21000000 * 2.3, bonus: 21 }, // ~21M blocks
  { seconds: 34000000 * 2.3, bonus: 34 }, // ~34M blocks
  { seconds: 55000000 * 2.3, bonus: 55 }, // ~55M blocks
  { seconds: 89000000 * 2.3, bonus: 89 }  // ~89M blocks
];

const BASE_RPC = 'https://mainnet.base.org';
const AAVEGOTCHI_DIAMOND = '0xA99c4B08201F2913Db8D28e71d020c4298F29dBF';

async function calculateAgingBonusFromTimestamp(tokenId) {
  const provider = new ethers.JsonRpcProvider(BASE_RPC);
  
  // We need to find the birth timestamp
  // Option 1: Query Transfer events (mint event has the timestamp)
  // Option 2: Use a known birth timestamp if available
  
  const ABI = [
    'event Transfer(address indexed from, address indexed to, uint256 indexed tokenId)'
  ];
  
  const contract = new ethers.Contract(AAVEGOTCHI_DIAMOND, ABI, provider);
  
  // Get current timestamp
  const currentBlock = await provider.getBlock('latest');
  const currentTimestamp = currentBlock.timestamp;
  
  // Try to find birth event
  // For Base, we know gotchis were migrated, so we need a different approach
  // Let's use a fallback: estimate based on haunt
  
  console.log(`Current timestamp: ${currentTimestamp}`);
  
  // Since we can't easily query all events, let's use haunt-based estimation
  // or return a function that takes birth timestamp as input
  
  return {
    currentTimestamp,
    calculateBonus: (birthTimestamp) => {
      const ageInSeconds = currentTimestamp - birthTimestamp;
      let agingBonus = 0;
      
      for (const milestone of AGING_MILESTONES_SECONDS) {
        if (ageInSeconds >= milestone.seconds) {
          agingBonus = milestone.bonus;
        } else {
          break;
        }
      }
      
      return {
        birthTimestamp,
        currentTimestamp,
        ageInSeconds,
        ageDays: Math.floor(ageInSeconds / 86400),
        agingBonus
      };
    }
  };
}

module.exports = { calculateAgingBonusFromTimestamp, AGING_MILESTONES_SECONDS };

// Test if run directly
if (require.main === module) {
  calculateAgingBonusFromTimestamp(1484).then(result => {
    console.log('\nAging calculator ready');
    console.log('To calculate bonus, call: result.calculateBonus(birthTimestamp)');
    
    // Example with estimated H1 gotchi birth (~Oct 2021)
    const oct2021Timestamp = 1633000000; // ~Oct 2021
    const bonus = result.calculateBonus(oct2021Timestamp);
    console.log('\nExample (H1 gotchi from Oct 2021):');
    console.log(JSON.stringify(bonus, null, 2));
  });
}
