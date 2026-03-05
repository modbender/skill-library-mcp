const { ethers } = require('ethers');

const PRIVATE_KEY = process.env.ETH_PRIVATE_KEY || 'YOUR_PRIVATE_KEY';
const MY_ADDRESS = process.env.MY_ADDRESS || 'YOUR_ADDRESS';
const STAKEWISE_VAULT = '0x8A93A876912c9F03F88Bc9114847cf5b63c89f56';
const RPC_URL = 'https://ethereum-rpc.publicnode.com';

const VAULT_ABI = [
  'function isStateUpdateRequired() external view returns (bool)',
  'function totalAssets() external view returns (uint256)',
  'function totalShares() external view returns (uint256)'
];

async function checkVaultState() {
  console.log('🔍 CHECKING STAKEWISE VAULT STATE');
  console.log('=================================\n');
  
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const vault = new ethers.Contract(STAKEWISE_VAULT, VAULT_ABI, provider);
  
  const needsUpdate = await vault.isStateUpdateRequired();
  const totalAssets = await vault.totalAssets();
  const totalShares = await vault.totalShares();
  
  console.log('State Update Required:', needsUpdate);
  console.log('Total Assets:', ethers.formatEther(totalAssets), 'ETH');
  console.log('Total Shares:', ethers.formatEther(totalShares), 'osETH');
  console.log('\nVault:', STAKEWISE_VAULT);
  
  if (needsUpdate) {
    console.log('\n⚠️  State update required before deposits!');
    console.log('Use stake.mjs which handles this automatically.');
  } else {
    console.log('\n✅ Vault ready for deposits');
  }
  
  return {
    needsUpdate,
    totalAssets: ethers.formatEther(totalAssets),
    totalShares: ethers.formatEther(totalShares)
  };
}

if (require.main === module) {
  checkVaultState().catch(console.error);
}

module.exports = { checkVaultState };
