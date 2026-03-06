const { ethers } = require('ethers');
const https = require('https');

const BASE_RPC = 'https://mainnet.base.org';
const AAVEGOTCHI_DIAMOND = '0xA99c4B08201F2913Db8D28e71d020c4298F29dBF';
const SUBGRAPH_URL = 'https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-core-base/prod/gn';

const ABI = [
  'function getAavegotchi(uint256 _tokenId) external view returns (tuple(uint256 tokenId, string name, address owner, uint256 randomNumber, uint256 status, int16[6] numericTraits, int16[6] modifiedNumericTraits, uint16[16] equippedWearables, address collateral, address escrow, uint256 stakedAmount, uint256 minimumStake, uint256 kinship, uint256 lastInteracted, uint256 experience, uint256 toNextLevel, uint256 usedSkillPoints, uint256 level, uint256 hauntId, uint256 baseRarityScore, uint256 modifiedRarityScore, bool locked))',
  'function getAavegotchiSvg(uint256 _tokenId) external view returns (string)'
];

const STATUS_NAMES = {
  0: 'Portal (Unopened)',
  1: 'Portal (Opened)',
  2: 'Gotchi',
  3: 'Gotchi'
};

async function querySubgraph(tokenId) {
  const query = `{
    aavegotchi(id: "${tokenId}") {
      withSetsRarityScore
    }
  }`;

  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ query });
    const url = new URL(SUBGRAPH_URL);
    
    const options = {
      hostname: url.hostname,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(body);
          resolve(result.data?.aavegotchi?.withSetsRarityScore || null);
        } catch (e) {
          resolve(null);
        }
      });
    });

    req.on('error', () => resolve(null));
    req.write(data);
    req.end();
  });
}

async function fetchGotchi(tokenId, outputDir = '.') {
  const provider = new ethers.JsonRpcProvider(BASE_RPC);
  const contract = new ethers.Contract(AAVEGOTCHI_DIAMOND, ABI, provider);

  try {
    console.log(`\n🔍 Fetching Gotchi #${tokenId} from Base mainnet...`);
    
    // Fetch gotchi data from contract
    const gotchiData = await contract.getAavegotchi(tokenId);
    const status = Number(gotchiData.status);
    const statusName = STATUS_NAMES[status] || `Unknown (${status})`;
    
    // Fetch withSetsRarityScore from subgraph
    const withSetsBRS = await querySubgraph(tokenId);
    
    const modifiedBRS = gotchiData.modifiedRarityScore.toString();
    const displayBRS = withSetsBRS || modifiedBRS; // Use withSets if available, fallback to modified

    const setBonus = withSetsBRS ? parseInt(withSetsBRS) - parseInt(modifiedBRS) : 0;

    console.log(`📛 Name: ${gotchiData.name}`);
    console.log(`⭐ Total BRS: ${displayBRS}${setBonus > 0 ? ` (Base: ${gotchiData.baseRarityScore} + Wearables: ${parseInt(modifiedBRS) - parseInt(gotchiData.baseRarityScore)} + Sets: +${setBonus})` : ` (Base: ${gotchiData.baseRarityScore} + Wearables: ${parseInt(modifiedBRS) - parseInt(gotchiData.baseRarityScore)})`}`);
    console.log(`💜 Kinship: ${gotchiData.kinship}`);
    console.log(`🎯 Level: ${gotchiData.level}`);
    console.log(`✨ XP: ${gotchiData.experience}`);
    console.log(`🔒 Locked: ${gotchiData.locked ? 'Yes' : 'No'}`);
    
    console.log(`\n🎭 Base Traits (without wearables):`);
    console.log(`   Energy: ${gotchiData.numericTraits[0]}`);
    console.log(`   Aggression: ${gotchiData.numericTraits[1]}`);
    console.log(`   Spookiness: ${gotchiData.numericTraits[2]}`);
    console.log(`   Brain Size: ${gotchiData.numericTraits[3]}`);
    
    console.log(`\n👔 Modified Traits (with wearables):`);
    console.log(`   Energy: ${gotchiData.modifiedNumericTraits[0]} (${gotchiData.modifiedNumericTraits[0] - gotchiData.numericTraits[0] >= 0 ? '+' : ''}${gotchiData.modifiedNumericTraits[0] - gotchiData.numericTraits[0]})`);
    console.log(`   Aggression: ${gotchiData.modifiedNumericTraits[1]} (${gotchiData.modifiedNumericTraits[1] - gotchiData.numericTraits[1] >= 0 ? '+' : ''}${gotchiData.modifiedNumericTraits[1] - gotchiData.numericTraits[1]})`);
    console.log(`   Spookiness: ${gotchiData.modifiedNumericTraits[2]} (${gotchiData.modifiedNumericTraits[2] - gotchiData.numericTraits[2] >= 0 ? '+' : ''}${gotchiData.modifiedNumericTraits[2] - gotchiData.numericTraits[2]})`);
    console.log(`   Brain Size: ${gotchiData.modifiedNumericTraits[3]} (${gotchiData.modifiedNumericTraits[3] - gotchiData.numericTraits[3] >= 0 ? '+' : ''}${gotchiData.modifiedNumericTraits[3] - gotchiData.numericTraits[3]})`);
    
    // Build result object
    const result = {
      tokenId: tokenId.toString(),
      name: gotchiData.name,
      owner: gotchiData.owner,
      status: status,
      statusName: statusName,
      hauntId: gotchiData.hauntId.toString(),
      
      baseRarityScore: gotchiData.baseRarityScore.toString(),
      modifiedRarityScore: modifiedBRS,
      withSetsRarityScore: withSetsBRS,
      brs: displayBRS, // DISPLAY BRS (what website shows)
      baseBrs: gotchiData.baseRarityScore.toString(),
      setBonus: setBonus,
      
      kinship: gotchiData.kinship.toString(),
      level: gotchiData.level.toString(),
      experience: gotchiData.experience.toString(),
      collateral: gotchiData.collateral,
      stakedAmount: ethers.formatEther(gotchiData.stakedAmount),
      locked: gotchiData.locked,
      
      traits: {
        energy: gotchiData.numericTraits[0].toString(),
        aggression: gotchiData.numericTraits[1].toString(),
        spookiness: gotchiData.numericTraits[2].toString(),
        brainSize: gotchiData.numericTraits[3].toString(),
        eyeShape: gotchiData.numericTraits[4].toString(),
        eyeColor: gotchiData.numericTraits[5].toString()
      },
      
      modifiedTraits: {
        energy: gotchiData.modifiedNumericTraits[0].toString(),
        aggression: gotchiData.modifiedNumericTraits[1].toString(),
        spookiness: gotchiData.modifiedNumericTraits[2].toString(),
        brainSize: gotchiData.modifiedNumericTraits[3].toString(),
        eyeShape: gotchiData.modifiedNumericTraits[4].toString(),
        eyeColor: gotchiData.modifiedNumericTraits[5].toString()
      }
    };
    
    // Fetch SVG
    console.log(`\n📥 Fetching SVG...`);
    const svg = await contract.getAavegotchiSvg(tokenId);
    
    // Determine image type
    let imageType = 'Unknown';
    if (svg.includes('class="gotchi-body"')) imageType = 'Aavegotchi';
    else if (svg.includes('portal')) imageType = 'Portal';
    
    result.imageType = imageType;
    
    // Save JSON
    const fs = require('fs');
    const jsonPath = `${outputDir}/gotchi-${tokenId}.json`;
    fs.writeFileSync(jsonPath, JSON.stringify(result, null, 2));
    console.log(`✅ Saved JSON: ${jsonPath}`);
    
    // Save SVG
    const svgPath = `${outputDir}/gotchi-${tokenId}.svg`;
    fs.writeFileSync(svgPath, svg);
    console.log(`✅ Saved SVG: ${svgPath} (${imageType})`);
    
    return result;
    
  } catch (error) {
    console.error(`\n❌ Error fetching gotchi #${tokenId}:`, error.message);
    throw error;
  }
}

const tokenId = process.argv[2];
if (!tokenId) {
  console.error('Usage: node fetch-gotchi-updated.js <tokenId>');
  process.exit(1);
}

fetchGotchi(tokenId);
