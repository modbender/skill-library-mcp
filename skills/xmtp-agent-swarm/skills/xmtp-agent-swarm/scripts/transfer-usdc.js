import { ethers } from 'ethers';

const FROM_KEY = process.argv[2];
const TO_ADDR = process.argv[3];
const AMOUNT = process.argv[4] || '5.00';

const provider = new ethers.JsonRpcProvider('https://mainnet.base.org');
const wallet = new ethers.Wallet(FROM_KEY, provider);
const usdc = new ethers.Contract('0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913', [
  'function transfer(address to, uint256 amount) returns (bool)',
  'function balanceOf(address) view returns (uint256)',
], wallet);

const decimals = 6;
const raw = ethers.parseUnits(AMOUNT, decimals);

console.log(`Transferring $${AMOUNT} USDC from ${wallet.address} to ${TO_ADDR}...`);
const bal = await usdc.balanceOf(wallet.address);
console.log(`Balance: $${ethers.formatUnits(bal, decimals)} USDC`);

const tx = await usdc.transfer(TO_ADDR, raw);
console.log(`Tx: ${tx.hash}`);
await tx.wait();
console.log('Done.');
