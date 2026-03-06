const { ethers } = require('ethers');

// Configuration
const PRIVATE_KEY = process.env.STAKING_PRIVATE_KEY || 'YOUR_PRIVATE_KEY';
const MY_UP = process.env.MY_UP || 'YOUR_UP_ADDRESS';
const CONTROLLER = process.env.CONTROLLER || 'YOUR_CONTROLLER_ADDRESS';
const STAKINGVERSE_VAULT = '0x9F49a95b0c3c9e2A6c77a16C177928294c0F6F04';

const RPC_URL = 'https://rpc.mainnet.lukso.network';

// ABIs
const VAULT_ABI = [
  'function deposit(address receiver) external payable returns (uint256)',
  'function withdraw(uint256 shares) external',
  'function claim() external',
  'function balanceOf(address account) external view returns (uint256)',
  'function claimable(address account) external view returns (uint256)'
];

const UP_ABI = [
  'function execute(uint256 operation, address to, uint256 value, bytes memory data) external payable returns (bytes memory)',
  'function getData(bytes32 key) external view returns (bytes memory)'
];

const KEY_MANAGER_ABI = [
  'function execute(bytes memory payload) external payable returns (bytes memory)'
];

async function stakeLYX(amountLYX) {
  console.log(`🎯 STAKING ${amountLYX} LYX ON STAKINGVERSE`);
  console.log('=====================================\n');
  
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  
  // Get Key Manager address
  const up = new ethers.Contract(MY_UP, UP_ABI, provider);
  const keyManagerBytes = await up.getData('0xdf30dba06db6ede4cd4a817e2b67b0eb0e9e6e8c2e5a5b6e5d6c7e8f9a0b1c2d'); // LSP6KEY_KEYMANAGER_INTERNAL
  const keyManager = '0x' + keyManagerBytes.slice(26, 66);
  
  console.log('Key Manager:', keyManager);
  
  // Encode deposit call
  const vaultInterface = new ethers.Interface(VAULT_ABI);
  const depositData = vaultInterface.encodeFunctionData('deposit', [MY_UP]);
  
  // Encode UP.execute
  const amountWei = ethers.parseEther(amountLYX.toString());
  const upInterface = new ethers.Interface(UP_ABI);
  const upExecuteData = upInterface.encodeFunctionData('execute', [
    0, // CALL
    STAKINGVERSE_VAULT,
    amountWei,
    depositData
  ]);
  
  console.log('Sending transaction...');
  
  const keyManagerContract = new ethers.Contract(keyManager, KEY_MANAGER_ABI, wallet);
  const tx = await keyManagerContract.execute(upExecuteData, { value: amountWei });
  
  console.log('Transaction sent:', tx.hash);
  const receipt = await tx.wait();
  
  console.log('\n✅ Staked successfully!');
  console.log('Transaction:', receipt.hash);
  console.log('Block:', receipt.blockNumber);
  console.log('Gas used:', receipt.gasUsed.toString());
  
  // Check sLYX balance
  const sLYX = new ethers.Contract(STAKINGVERSE_VAULT, VAULT_ABI, provider);
  const balance = await sLYX.balanceOf(MY_UP);
  console.log('\nsLYX Balance:', ethers.formatEther(balance));
  
  return receipt.hash;
}

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.log('Usage: node stake.js <AMOUNT_LYX>');
    console.log('Example: node stake.js 10');
    process.exit(1);
  }
  
  stakeLYX(args[0]).catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
  });
}

module.exports = { stakeLYX };
