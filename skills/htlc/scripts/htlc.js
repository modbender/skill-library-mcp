#!/usr/bin/env node
/**
 * HTLC Trading Script for Inscriptions/NFTs
 * Usage: node htlc.js <command> [args]
 * 
 * Commands:
 *   preimage                          - Generate new preimage/hash pair
 *   lock <seller> <hash> <timeout> <eth> - Lock ETH in contract
 *   reveal <lockHash> <preimage>      - Reveal preimage to release funds
 *   trade <seller> <inscriptionTx> <eth> - Full trade workflow
 *   status <lockHash>                 - Check lock status
 */

import { ethers } from 'ethers';
import crypto from 'crypto';

const CONTRACT_ADDRESS = process.env.CONTRACT || '0xa7f9f88e753147d69baf8f2fef89a551680dbac1';
const RPC = process.env.BASE_ETH_RPC || 'https://mainnet.base.org';
const PRIVATE_KEY = process.env.PRIVATE_KEY;

const ABI = [
  'function lock(bytes32 _lockHash, address _seller, bytes32 _preimageHash, uint256 _timeout) external payable',
  'function reveal(bytes32 _lockHash, bytes calldata _preimage) external',
  'function confirmReceipt(bytes32 _lockHash) external',
  'function refund(bytes32 _lockHash) external',
  'function locks(bytes32) view returns (address buyer, address seller, bytes32 preimageHash, uint256 timeout, uint256 amount, bool revealed, bool completed, bool refunded)'
];

// Generate random preimage
function generatePreimage() {
  const preimage = crypto.randomBytes(32);
  return {
    preimage: '0x' + preimage.toString('hex'),
    hash: ethers.keccak256(preimage)
  };
}

// Calculate lockHash
function getLockHash(preimageHash, seller, timeout) {
  return ethers.keccak256(
    ethers.concat([
      preimageHash,
      ethers.zeroPadValue(seller, 32),
      ethers.zeroPadValue(ethers.toBeHex(timeout), 32)
    ])
  );
}

// Lock ETH
async function lock(seller, preimageHash, timeout, ethAmount) {
  if (!PRIVATE_KEY) throw new Error('PRIVATE_KEY not set');
  
  const provider = new ethers.JsonRpcProvider(RPC);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  const contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, wallet);
  
  const lockHash = getLockHash(preimageHash, seller, timeout);
  
  console.log('Locking', ethAmount, 'ETH...');
  console.log('LockHash:', lockHash);
  
  const tx = await contract.lock(lockHash, seller, preimageHash, timeout, {
    value: ethers.parseEther(ethAmount.toString())
  });
  
  console.log('TX:', tx.hash);
  await tx.wait();
  console.log('✅ ETH locked!');
  
  return { lockHash, preimageHash };
}

// Reveal preimage
async function reveal(lockHash, preimage) {
  if (!PRIVATE_KEY) throw new Error('PRIVATE_KEY not set');
  
  const provider = new ethers.JsonRpcProvider(RPC);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  const contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, wallet);
  
  console.log('Revealing preimage...');
  const tx = await contract.reveal(lockHash, preimage);
  console.log('TX:', tx.hash);
  await tx.wait();
  console.log('✅ Funds released!');
}

// Full trade workflow
async function trade(seller, inscriptionTx, ethAmount) {
  // Generate preimage
  const { preimage, hash } = generatePreimage();
  const timeout = 3600; // 1 hour
  
  const lockHash = getLockHash(hash, seller, timeout);
  
  console.log('=== HTLC Trade ===');
  console.log('Inscription:', inscriptionTx);
  console.log('Irys: https://gateway.irys.xyz/' + inscriptionTx);
  console.log('Preimage (keep secret):', preimage);
  console.log('PreimageHash:', hash);
  console.log('LockHash:', lockHash);
  
  // Lock funds
  await lock(seller, hash, timeout, ethAmount);
  
  console.log('\n=== Share with seller ===');
  console.log('LockHash:', lockHash);
  console.log('Preimage:', preimage);
  
  return { lockHash, preimage, hash };
}

// Check lock status
async function status(lockHash) {
  const provider = new ethers.JsonRpcProvider(RPC);
  const contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, provider);
  
  const lock = await contract.locks(lockHash);
  
  console.log('Lock Status:');
  console.log('  Buyer:', lock.buyer);
  console.log('  Seller:', lock.seller);
  console.log('  Amount:', ethers.formatEther(lock.amount), 'ETH');
  console.log('  Revealed:', lock.revealed);
  console.log('  Completed:', lock.completed);
  console.log('  Refunded:', lock.refunded);
}

// CLI
const cmd = process.argv[2];
const args = process.argv.slice(3);

async function main() {
  switch(cmd) {
    case 'preimage': {
      const { preimage, hash } = generatePreimage();
      console.log(JSON.stringify({ preimage, hash }, null, 2));
      break;
    }
    case 'lock': {
      const [seller, hash, timeout, eth] = args;
      await lock(seller, hash, parseInt(timeout), parseFloat(eth));
      break;
    }
    case 'reveal': {
      const [lockHash, preimage] = args;
      await reveal(lockHash, preimage);
      break;
    }
    case 'trade': {
      const [seller, inscriptionTx, eth] = args;
      await trade(seller, inscriptionTx, parseFloat(eth));
      break;
    }
    case 'status': {
      const [lockHash] = args;
      await status(lockHash);
      break;
    }
    default:
      console.log('Usage:');
      console.log('  node htlc.js preimage');
      console.log('  node htlc.js lock <seller> <hash> <timeout> <eth>');
      console.log('  node htlc.js reveal <lockHash> <preimage>');
      console.log('  node htlc.js trade <seller> <inscriptionTx> <eth>');
      console.log('  node htlc.js status <lockHash>');
  }
}

main().catch(console.error);
