const { ethers } = require('ethers');

const PRIVATE_KEY = process.env.STAKING_PRIVATE_KEY || 'YOUR_PRIVATE_KEY';
const MY_UP = process.env.MY_UP || 'YOUR_UP_ADDRESS';
const CONTROLLER = process.env.CONTROLLER || 'YOUR_CONTROLLER_ADDRESS';
const STAKINGVERSE_VAULT = '0x9F49a95b0c3c9e2A6c77a16C177928294c0F6F04';
const RPC_URL = 'https://rpc.mainnet.lukso.network';

const VAULT_ABI = [
  'function claim() external',
  'function claimable(address account) external view returns (uint256)'
];

const UP_ABI = [
  'function execute(uint256 operation, address to, uint256 value, bytes memory data) external payable returns (bytes memory)'
];

const KEY_MANAGER_ABI = [
  'function execute(bytes memory payload) external payable returns (bytes memory)'
];

async function claimLYX() {
  console.log('💸 CLAIMING UNSTAKED LYX');
  console.log('=======================\n');
  
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  
  // Check claimable amount first
  const vault = new ethers.Contract(STAKINGVERSE_VAULT, VAULT_ABI, provider);
  const claimable = await vault.claimable(MY_UP);
  
  if (claimable == 0) {
    console.log('❌ Nothing to claim yet.');
    console.log('Oracle still processing withdrawal.');
    return null;
  }
  
  console.log('Claimable LYX:', ethers.formatEther(claimable));
  
  // Get Key Manager
  const up = new ethers.Contract(MY_UP, UP_ABI, provider);
  const keyManagerBytes = await up.getData('0xdf30dba06db6ede4cd4a817e2b67b0eb0e9e6e8c2e5a5b6e5d6c7e8f9a0b1c2d');
  const keyManager = '0x' + keyManagerBytes.slice(26, 66);
  
  // Encode claim
  const vaultInterface = new ethers.Interface(VAULT_ABI);
  const claimData = vaultInterface.encodeFunctionData('claim', []);
  
  // Encode UP.execute
  const upInterface = new ethers.Interface(UP_ABI);
  const upExecuteData = upInterface.encodeFunctionData('execute', [
    0, // CALL
    STAKINGVERSE_VAULT,
    0,
    claimData
  ]);
  
  console.log('Sending claim transaction...');
  
  const keyManagerContract = new ethers.Contract(keyManager, KEY_MANAGER_ABI, wallet);
  const tx = await keyManagerContract.execute(upExecuteData);
  
  console.log('Transaction sent:', tx.hash);
  const receipt = await tx.wait();
  
  console.log('\n✅ Claimed successfully!');
  console.log('Transaction:', receipt.hash);
  console.log('LYX received:', ethers.formatEther(claimable));
  
  return receipt.hash;
}

if (require.main === module) {
  claimLYX().catch(console.error);
}

module.exports = { claimLYX };
