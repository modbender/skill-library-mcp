const { ethers } = require('ethers');
const https = require('https');

const BASE_RPC = 'https://mainnet.base.org';
const AAVEGOTCHI_DIAMOND = '0xA99c4B08201F2913Db8D28e71d020c4298F29dBF';
const SUBGRAPH_URL = 'https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-core-base/prod/gn';

// Fibonacci aging milestones in seconds
const AGING_MILESTONES = [
  { seconds: 1000000 * 2.3, bonus: 1 },
  { seconds: 2000000 * 2.3, bonus: 2 },
  { seconds: 3000000 * 2.3, bonus: 3 },
  { seconds: 5000000 * 2.3, bonus: 5 },
  { seconds: 8000000 * 2.3, bonus: 8 },
  { seconds: 13000000 * 2.3, bonus: 13 },
  { seconds: 21000000 * 2.3, bonus: 21 },
  { seconds: 34000000 * 2.3, bonus: 34 },
  { seconds: 55000000 * 2.3, bonus: 55 },
  { seconds: 89000000 * 2.3, bonus: 89 }
];

async function querySubgraph(gotchiId) {
  const query = `{
    aavegotchi(id: "${gotchiId}") {
      id
      name
      createdAt
      claimedAt
      hauntId
      baseRarityScore
      modifiedRarityScore
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
          resolve(result.data?.aavegotchi);
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

function calculateAgingBonus(birthTimestamp, currentTimestamp) {
  const ageInSeconds = currentTimestamp - birthTimestamp;
  let agingBonus = 0;
  
  for (const milestone of AGING_MILESTONES) {
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

async function fetchGotchiWithAging(tokenId) {
  const provider = new ethers.JsonRpcProvider(BASE_RPC);
  const currentBlock = await provider.getBlock('latest');
  const currentTimestamp = currentBlock.timestamp;

  // Get birth timestamp from subgraph
  const subgraphData = await querySubgraph(tokenId);
  
  if (!subgraphData) {
    throw new Error(`Gotchi #${tokenId} not found in subgraph`);
  }

  const birthTimestamp = parseInt(subgraphData.claimedAt || subgraphData.createdAt);
  const agingData = calculateAgingBonus(birthTimestamp, currentTimestamp);
  
  const contractBRS = parseInt(subgraphData.modifiedRarityScore);
  const fullBRS = contractBRS + agingData.agingBonus;

  console.log(`\n✅ Gotchi #${tokenId}: ${subgraphData.name}`);
  console.log(`📊 BRS Breakdown:`);
  console.log(`   Contract BRS (base + wearables): ${contractBRS}`);
  console.log(`   Aging bonus: +${agingData.agingBonus}`);
  console.log(`   Full BRS (website): ${fullBRS}`);
  console.log(`\n⏰ Age: ${agingData.ageDays} days (${Math.floor(agingData.ageDays/365)} years)`);

  return {
    ...subgraphData,
    birthTimestamp,
    agingBonus: agingData.agingBonus,
    contractBRS,
    fullBRS
  };
}

const tokenId = process.argv[2] || '1484';
fetchGotchiWithAging(tokenId)
  .then(data => {
    console.log('\n📦 Full data:');
    console.log(JSON.stringify(data, null, 2));
  })
  .catch(err => {
    console.error('❌ Error:', err.message);
    process.exit(1);
  });
