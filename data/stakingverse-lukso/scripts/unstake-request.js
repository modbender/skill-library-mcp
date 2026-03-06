const { ethers } = require('ethers');

const PRIVATE_KEY = process.env.STAKING_PRIVATE_KEY || 'YOUR_PRIVATE_KEY';
const MY_UP = process.env.MY_UP || 'YOUR_UP_ADDRESS';
const CONTROLLER = process.env.CONTROLLER || 'YOUR_CONTROLLER_ADDRESS';
const STAKINGVERSE_VAULT = '0x9F49a95b0c3c9e2A6c77a16C177928294c0F6F04';
const RPC_URL = 'https://rpc.mainnet.lukso.network';

const VAULT_ABI = [
  'function withdraw(uint256 shares) external'
];

const UP_ABI = [
  'function execute(uint256 operation, address to, uint256 value, bytes memory data) external payable returns (bytes memory)'
];

const KEY_MANAGER_ABI = [
  'function execute(bytes memory payload) external payable returns (bytes memory)'
];

async function requestUnstake(amountSLYX) {
  console.log(`🚪 REQUESTING UNSTAKE: ${amountSLYX} sLYX`);
  console.log('==================================\n');
  
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  
  // Get Key Manager
  const up = new ethers.Contract(MY_UP, UP_ABI, provider);
  const keyManagerBytes = await up.getData('0xdf30dba06db6ede4cd4a817e2b67b0eb0e9e6e8c2e5a5b6e5d6c7e8f9a0b1c2d');
  const keyManager = '0x' + keyManagerBytes.slice(26, 66);
  
  // Encode withdraw
  const vaultInterface = new ethers.Interface(VAULT_ABI);
  const withdrawData = vaultInterface.encodeFunctionData('withdraw', [
    ethers.parseEther(amountSLYX.toString())
  ]);
  
  // Encode UP.execute
  const upInterface = new ethers.Interface(UP_ABI);
  const upExecuteData = upInterface.encodeFunctionData('execute', [
    0, // CALL
    STAKINGVERSE_VAULT,
    0,
    withdrawData
  ]);
  
  console.log('Sending withdrawal request...');
  
  const keyManagerContract = new ethers.Contract(keyManager, KEY_MANAGER_ABI, wallet);
  const tx = await keyManagerContract.execute(upExecuteData);
  
  console.log('Transaction sent:', tx.hash);
  const receipt = await tx.wait();
  
  console.log('\n✅ Unstake requested!');
  console.log('Transaction:', receipt.hash);
  console.log('\n⚠️  Note: Oracle needs to process this.');
  console.log('Check claimable balance with: node scripts/balance.js');
  console.log('Claim with: node scripts/claim.js');
  
  return receipt.hash;
}

if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.log('Usage: node unstake-request.js <sLYX_AMOUNT>');
    console.log('Example: node unstake-request.js 5');
    process.exit(1);
  }
  
  requestUnstake(args[0]).catch(console.error);
}

module.exports = { requestUnstake };
