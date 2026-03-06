const { ethers } = require('ethers');

// Fibonacci-based aging bonus (in millions of blocks)
const AGING_MILESTONES = [
  { blocks: 1000000, bonus: 1 },
  { blocks: 2000000, bonus: 2 },
  { blocks: 3000000, bonus: 3 },
  { blocks: 5000000, bonus: 5 },
  { blocks: 8000000, bonus: 8 },
  { blocks: 13000000, bonus: 13 },
  { blocks: 21000000, bonus: 21 },
  { blocks: 34000000, bonus: 34 },
  { blocks: 55000000, bonus: 55 },
  { blocks: 89000000, bonus: 89 }
];

async function calculateAgingBonus(birthBlock) {
  const provider = new ethers.JsonRpcProvider('https://mainnet.base.org');
  const currentBlock = await provider.getBlockNumber();
  const blocksElapsed = currentBlock - birthBlock;

  let agingBonus = 0;
  for (const milestone of AGING_MILESTONES) {
    if (blocksElapsed >= milestone.blocks) {
      agingBonus = milestone.bonus;
    } else {
      break;
    }
  }

  return {
    currentBlock,
    birthBlock,
    blocksElapsed,
    agingBonus
  };
}

// Export for use in other scripts
if (require.main === module) {
  const birthBlock = parseInt(process.argv[2]);
  if (!birthBlock) {
    console.error('Usage: node calculate-aging-bonus.js <birthBlock>');
    process.exit(1);
  }
  
  calculateAgingBonus(birthBlock).then(result => {
    console.log(JSON.stringify(result, null, 2));
  });
}

module.exports = { calculateAgingBonus };
