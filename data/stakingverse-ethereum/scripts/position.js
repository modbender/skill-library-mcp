const { ethers } = require('ethers');

const PRIVATE_KEY = process.env.ETH_PRIVATE_KEY || 'YOUR_PRIVATE_KEY';
const MY_ADDRESS = process.env.MY_ADDRESS || 'YOUR_ADDRESS';
const STAKEWISE_VAULT = '0x8A93A876912c9F03F88Bc9114847cf5b63c89f56';
const RPC_URL = 'https://ethereum-rpc.publicnode.com';

const VAULT_ABI = [
  'function balanceOf(address account) external view returns (uint256)',
  'function convertToAssets(uint256 shares) external view returns (uint256)',
  'function convertToShares(uint256 assets) external view returns (uint256)',
  'function totalAssets() external view returns (uint256)'
];

async function checkPosition() {
  console.log('💰 CHECKING STAKEWISE POSITION');
  console.log('==============================\n');
  
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const vault = new ethers.Contract(STAKEWISE_VAULT, VAULT_ABI, provider);
  
  const shares = await vault.balanceOf(MY_ADDRESS);
  const underlyingETH = await vault.convertToAssets(shares);
  const totalVaultAssets = await vault.totalAssets();
  
  console.log('osETH Shares:', ethers.formatEther(shares));
  console.log('Underlying ETH:', ethers.formatEther(underlyingETH));
  console.log('Vault Total Assets:', ethers.formatEther(totalVaultAssets));
  console.log('\nVault:', STAKEWISE_VAULT);
  console.log('Your Address:', MY_ADDRESS);
  
  return {
    shares: ethers.formatEther(shares),
    underlyingETH: ethers.formatEther(underlyingETH),
    totalVaultAssets: ethers.formatEther(totalVaultAssets)
  };
}

if (require.main === module) {
  checkPosition().catch(console.error);
}

module.exports = { checkPosition };
