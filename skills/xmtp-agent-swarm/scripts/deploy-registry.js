import { ethers } from 'ethers';
import { readFileSync } from 'fs';

const PRIVATE_KEY = process.argv[2] || '0xd8e5b5be6cd771fb9c245314cbb4479df464702432cddac1713296b30318028a';
const RPC = 'https://mainnet.base.org';

const abi = JSON.parse(readFileSync('build/contracts_BoardRegistry_sol_BoardRegistry.abi', 'utf-8'));
const bin = readFileSync('build/contracts_BoardRegistry_sol_BoardRegistry.bin', 'utf-8');

const provider = new ethers.JsonRpcProvider(RPC);
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

console.log(`Deploying BoardRegistry from ${wallet.address}...`);

const factory = new ethers.ContractFactory(abi, '0x' + bin, wallet);
const contract = await factory.deploy();
await contract.waitForDeployment();
const addr = await contract.getAddress();

console.log(`BoardRegistry deployed: ${addr}`);
console.log(`Verify: https://basescan.org/address/${addr}`);
