const { ethers } = require('ethers');

// Aavegotchi Diamond on Base
const DIAMOND_ADDRESS = '0xA99c4B08201F2913Db8D28e71d020c4298F29dBF';
const RPC_URL = process.env.BASE_MAINNET_RPC || 'https://mainnet.base.org';

// SvgFacet ABI - getSvg function
const ABI = [
  'function getSvg(bytes32 _svgType, uint256 _itemId) external view returns (string memory)'
];

async function getPortalSvg(status, hauntId) {
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const contract = new ethers.Contract(DIAMOND_ADDRESS, ABI, provider);
  
  // Convert string to bytes32
  const svgType = status === 0 ? 'portal-closed' : 'portal-open';
  const svgTypeBytes32 = ethers.id(svgType); // keccak256 hash
  
  console.log(`Fetching ${svgType} for Haunt ${hauntId}...`);
  console.log(`SVG Type (bytes32): ${svgTypeBytes32}`);
  
  try {
    const svg = await contract.getSvg(svgTypeBytes32, hauntId);
    console.log(`✅ Got SVG (${svg.length} bytes)`);
    return svg;
  } catch (error) {
    console.error(`❌ Error:`, error.message);
    throw error;
  }
}

// Main
async function main() {
  const status = parseInt(process.argv[2] || '0'); // 0 = closed, 1 = open
  const hauntId = parseInt(process.argv[3] || '1');
  
  const svg = await getPortalSvg(status, hauntId);
  console.log(svg);
}

if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = { getPortalSvg };
