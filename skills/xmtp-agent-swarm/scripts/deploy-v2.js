// Deploy TaskEscrowV2 to Base mainnet
import { ethers } from 'ethers';
import { readFileSync } from 'fs';

const RPC = process.env.RPC_URL || 'https://mainnet.base.org';
const USDC = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913';
const PRIVATE_KEY = process.env.WALLET_PRIVATE_KEY;

if (!PRIVATE_KEY) { console.error('Set WALLET_PRIVATE_KEY'); process.exit(1); }

const provider = new ethers.JsonRpcProvider(RPC);
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

const abi = JSON.parse(readFileSync('build/contracts_TaskEscrowV2_sol_TaskEscrowV2.abi', 'utf8'));
const bytecode = '0x' + readFileSync('build/contracts_TaskEscrowV2_sol_TaskEscrowV2.bin', 'utf8').trim();

async function main() {
  console.log('Deployer:', wallet.address);
  const bal = await provider.getBalance(wallet.address);
  console.log('ETH balance:', ethers.formatEther(bal));

  // Arbitrator = deployer (us) for now
  const arbitrator = wallet.address;
  console.log('Arbitrator:', arbitrator);
  console.log('USDC:', USDC);

  const factory = new ethers.ContractFactory(abi, bytecode, wallet);
  console.log('Deploying TaskEscrowV2...');
  const contract = await factory.deploy(USDC, arbitrator);
  console.log('Tx:', contract.deploymentTransaction().hash);
  await contract.waitForDeployment();
  const addr = await contract.getAddress();
  console.log('✅ TaskEscrowV2 deployed at:', addr);
}

main().catch(e => { console.error(e); process.exit(1); });
