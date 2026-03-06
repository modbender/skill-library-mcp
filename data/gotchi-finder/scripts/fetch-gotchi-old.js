const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

const AAVEGOTCHI_DIAMOND = '0xA99c4B08201F2913Db8D28e71d020c4298F29dBF';
const BASE_RPC = process.env.BASE_MAINNET_RPC || 'https://mainnet.base.org';

const ABI = [
  'function getAavegotchiSvg(uint256 _tokenId) external view returns (string memory)',
  'function getAavegotchi(uint256 _tokenId) external view returns (tuple(uint256 tokenId, string name, address owner, uint256 randomNumber, uint256 status, int16[6] numericTraits, int16[6] modifiedNumericTraits, uint16[16] equippedWearables, address collateral, address escrow, uint256 stakedAmount, uint256 minimumStake, uint256 kinship, uint256 lastInteracted, uint256 experience, uint256 toNextLevel, uint256 usedSkillPoints, uint256 level, uint256 hauntId, uint256 baseRarityScore, uint256 modifiedRarityScore, bool locked))'
];

const STATUS_NAMES = {
  0: 'Portal (Unopened)',
  1: 'Portal (Opened)',
  2: 'Gotchi',
  3: 'Gotchi'
};

async function fetchGotchi(tokenId, outputDir = '.') {
  const provider = new ethers.JsonRpcProvider(BASE_RPC);
  const contract = new ethers.Contract(AAVEGOTCHI_DIAMOND, ABI, provider);

  try {
    console.log(`\n🔍 Fetching Gotchi #${tokenId} from Base mainnet...`);
    
    // Fetch gotchi data
    const gotchiData = await contract.getAavegotchi(tokenId);
    const status = Number(gotchiData.status);
    const statusName = STATUS_NAMES[status] || `Unknown (${status})`;
    
    const result = {
      tokenId: tokenId.toString(),
      name: gotchiData.name || 'Unnamed',
      owner: gotchiData.owner,
      status: status,
      statusName: statusName,
      hauntId: gotchiData.hauntId.toString(),
      baseRarityScore: gotchiData.baseRarityScore.toString(),
      modifiedRarityScore: gotchiData.modifiedRarityScore.toString(),
      brs: gotchiData.modifiedRarityScore.toString(), // TOTAL BRS (base + wearables)
      baseBrs: gotchiData.baseRarityScore.toString(), // Base only (no wearables)
      kinship: gotchiData.kinship.toString(),
      level: gotchiData.level.toString(),
      experience: gotchiData.experience.toString(),
      collateral: gotchiData.collateral,
      stakedAmount: ethers.formatEther(gotchiData.stakedAmount),
      locked: gotchiData.locked,
      
      // Numeric traits (Energy, Aggression, Spookiness, Brain Size, Eye Shape, Eye Color)
      traits: {
        energy: gotchiData.numericTraits[0].toString(),
        aggression: gotchiData.numericTraits[1].toString(),
        spookiness: gotchiData.numericTraits[2].toString(),
        brainSize: gotchiData.numericTraits[3].toString(),
        eyeShape: gotchiData.numericTraits[4].toString(),
        eyeColor: gotchiData.numericTraits[5].toString()
      },
      
      // Modified traits (with wearables)
      modifiedTraits: {
        energy: gotchiData.modifiedNumericTraits[0].toString(),
        aggression: gotchiData.modifiedNumericTraits[1].toString(),
        spookiness: gotchiData.modifiedNumericTraits[2].toString(),
        brainSize: gotchiData.modifiedNumericTraits[3].toString(),
        eyeShape: gotchiData.modifiedNumericTraits[4].toString(),
        eyeColor: gotchiData.modifiedNumericTraits[5].toString()
      }
    };
    
    if (status === 2 || status === 3) {
      console.log(`📛 Name: ${result.name}`);
      console.log(`⭐ Total BRS: ${result.brs} (Base: ${result.baseBrs} + Wearables: ${result.brs - result.baseBrs})`);
      console.log(`💜 Kinship: ${result.kinship}`);
      console.log(`🎯 Level: ${result.level}`);
      console.log(`✨ XP: ${result.experience}`);
      console.log(`🔒 Locked: ${result.locked ? 'Yes' : 'No'}`);
      console.log(`\n🎭 Base Traits (without wearables):`);
      console.log(`   Energy: ${result.traits.energy}`);
      console.log(`   Aggression: ${result.traits.aggression}`);
      console.log(`   Spookiness: ${result.traits.spookiness}`);
      console.log(`   Brain Size: ${result.traits.brainSize}`);
      console.log(`\n👔 Modified Traits (with wearables):`);
      console.log(`   Energy: ${result.modifiedTraits.energy} (${result.modifiedTraits.energy - result.traits.energy >= 0 ? '+' : ''}${result.modifiedTraits.energy - result.traits.energy})`);
      console.log(`   Aggression: ${result.modifiedTraits.aggression} (${result.modifiedTraits.aggression - result.traits.aggression >= 0 ? '+' : ''}${result.modifiedTraits.aggression - result.traits.aggression})`);
      console.log(`   Spookiness: ${result.modifiedTraits.spookiness} (${result.modifiedTraits.spookiness - result.traits.spookiness >= 0 ? '+' : ''}${result.modifiedTraits.spookiness - result.traits.spookiness})`);
      console.log(`   Brain Size: ${result.modifiedTraits.brainSize} (${result.modifiedTraits.brainSize - result.traits.brainSize >= 0 ? '+' : ''}${result.modifiedTraits.brainSize - result.traits.brainSize})`);
    }
    
    // Fetch SVG
    console.log(`\n📥 Fetching SVG...`);
    const svg = await contract.getAavegotchiSvg(tokenId);
    
    // Determine image type
    let imageType = 'Unknown';
    if (svg.includes('gotchi-body') || svg.includes('gotchi-wearable')) {
      imageType = 'Aavegotchi';
    } else if (svg.includes('Haunt')) {
      imageType = 'Portal';
    }
    
    result.imageType = imageType;
    
    // Save JSON
    const jsonPath = path.join(outputDir, `gotchi-${tokenId}.json`);
    fs.writeFileSync(jsonPath, JSON.stringify(result, null, 2));
    console.log(`\n✅ Saved JSON: ${jsonPath}`);
    
    // Save SVG
    const svgPath = path.join(outputDir, `gotchi-${tokenId}.svg`);
    fs.writeFileSync(svgPath, svg);
    console.log(`✅ Saved SVG: ${svgPath} (${imageType})`);
    
    return result;
  } catch (error) {
    if (error.message.includes('SVG type or id does not exist')) {
      console.error(`\n❌ Gotchi #${tokenId} does not exist on Base chain`);
      console.error('Fatal error:', error.message);
      process.exit(1);
    }
    throw error;
  }
}

// CLI usage
if (require.main === module) {
  const tokenId = process.argv[2];
  const outputDir = process.argv[3] || '.';
  
  if (!tokenId) {
    console.error('Usage: node fetch-gotchi.js <tokenId> [outputDir]');
    process.exit(1);
  }
  
  fetchGotchi(parseInt(tokenId), outputDir)
    .then(() => process.exit(0))
    .catch(error => {
      console.error('Error:', error);
      process.exit(1);
    });
}

module.exports = { fetchGotchi };
