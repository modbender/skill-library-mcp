const { ethers } = require('ethers');

const PRIVATE_KEY = process.env.STAKING_PRIVATE_KEY || 'YOUR_PRIVATE_KEY';
const MY_UP = process.env.MY_UP || 'YOUR_UP_ADDRESS';
const STAKINGVERSE_VAULT = '0x9F49a95b0c3c9e2A6c77a16C177928294c0F6F04';
const RPC_URL = 'https://rpc.mainnet.lukso.network';

const VAULT_ABI = [
  'function balanceOf(address account) external view returns (uint256)',
  'function claimable(address account) external view returns (uint256)',
  'function convertToAssets(uint256 shares) external view returns (uint256)'
];

async function checkBalance() {
  console.log('💰 CHECKING STAKINGVERSE POSITION');
  console.log('=================================\n');
  
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const vault = new ethers.Contract(STAKINGVERSE_VAULT, VAULT_ABI, provider);
  
  const sLYXBalance = await vault.balanceOf(MY_UP);
  const claimableLYX = await vault.claimable(MY_UP);
  const underlyingAssets = await vault.convertToAssets(sLYXBalance);
  
  console.log('sLYX Balance:', ethers.formatEther(sLYXBalance));
  console.log('Underlying LYX:', ethers.formatEther(underlyingAssets));
  console.log('Claimable LYX:', ethers.formatEther(claimableLYX));
  console.log('\nVault:', STAKINGVERSE_VAULT);
  console.log('Your UP:', MY_UP);
  
  return {
    sLYX: ethers.formatEther(sLYXBalance),
    underlyingLYX: ethers.formatEther(underlyingAssets),
    claimableLYX: ethers.formatEther(claimableLYX)
  };
}

if (require.main === module) {
  checkBalance().catch(console.error);
}

module.exports = { checkBalance };
