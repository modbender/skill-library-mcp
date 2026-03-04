// escrow.js — JS integration for the TaskEscrow contract
import { ethers } from 'ethers';

const ESCROW_ABI = [
  'function createEscrow(bytes32 taskId, address worker, uint256 amount, uint256 deadline) external',
  'function releaseEscrow(bytes32 taskId) external',
  'function dispute(bytes32 taskId) external',
  'function resolveDispute(bytes32 taskId, bool releaseToWorker) external',
  'function claimDisputeTimeout(bytes32 taskId) external',
  'function releaseAfterDeadline(bytes32 taskId) external',
  'function refund(bytes32 taskId) external',
  'function escrows(bytes32) view returns (address requestor, address worker, uint256 amount, uint256 deadline, uint8 status)',
  'function disputeTimestamps(bytes32) view returns (uint256)',
  'function disputeTimeout() view returns (uint256)',
  'function arbitrator() view returns (address)',
  'function usdc() view returns (address)',
];

const USDC_ABI = [
  'function approve(address spender, uint256 amount) returns (bool)',
  'function allowance(address owner, address spender) view returns (uint256)',
  'function balanceOf(address) view returns (uint256)',
  'function decimals() view returns (uint8)',
];

// Default deployed TaskEscrow on Base mainnet
const DEFAULT_ESCROW_ADDRESS = '0xE2b1D96dfbd4E363888c4c4f314A473E7cA24D2f';

// Compiled bytecode: loaded from build/ if deploying a new instance
const ESCROW_BYTECODE = null; // Set after compiling contracts/Escrow.sol

const STATUS_MAP = ['None', 'Active', 'Released', 'Disputed', 'Refunded'];

/** Get the default deployed escrow address on Base mainnet */
export function getDefaultEscrowAddress() {
  return process.env.ESCROW_ADDRESS || DEFAULT_ESCROW_ADDRESS;
}

/** Hash a task ID string to bytes32 for the contract */
export function hashTaskId(taskId) {
  return ethers.id(taskId);
}

/**
 * Deploy the TaskEscrow contract.
 * @param {ethers.Wallet} wallet - Deployer wallet
 * @param {string} usdcAddress - USDC token address
 * @param {string} bytecode - Compiled contract bytecode (hex string)
 * @returns {{ address: string, txHash: string }}
 */
export async function deployEscrow(wallet, usdcAddress, bytecode) {
  if (!bytecode && !ESCROW_BYTECODE) {
    throw new Error('Contract bytecode required. Compile contracts/Escrow.sol first.');
  }
  const factory = new ethers.ContractFactory(ESCROW_ABI, bytecode || ESCROW_BYTECODE, wallet);
  const contract = await factory.deploy(usdcAddress);
  await contract.waitForDeployment();
  const address = await contract.getAddress();
  return { address, txHash: contract.deploymentTransaction().hash };
}

/**
 * Create an escrow: approve USDC and deposit into the contract.
 * @param {ethers.Wallet} wallet - Requestor wallet
 * @param {string} contractAddr - Deployed TaskEscrow address
 * @param {object} opts - { taskId, worker, amount (human-readable USDC), deadline (unix timestamp) }
 * @returns {{ txHash: string, taskIdHash: string }}
 */
export async function createEscrow(wallet, contractAddr, { taskId, worker, amount, deadline }) {
  const escrow = new ethers.Contract(contractAddr, ESCROW_ABI, wallet);
  const usdcAddr = await escrow.usdc();
  const usdc = new ethers.Contract(usdcAddr, USDC_ABI, wallet);
  const decimals = await usdc.decimals();
  const amountRaw = ethers.parseUnits(amount.toString(), decimals);
  const taskIdHash = hashTaskId(taskId);

  // SECURITY: Approve only the exact amount needed (not MaxUint256)
  // If the contract has a vulnerability, this limits exposure to this single escrow
  const allowance = await usdc.allowance(wallet.address, contractAddr);
  if (allowance < amountRaw) {
    // Reset allowance to 0 first (some tokens require this)
    if (allowance > 0n) {
      const resetTx = await usdc.approve(contractAddr, 0);
      await resetTx.wait();
    }
    const approveTx = await usdc.approve(contractAddr, amountRaw);
    await approveTx.wait();
  }

  // Create the escrow
  const tx = await escrow.createEscrow(taskIdHash, worker, amountRaw, deadline);
  await tx.wait();

  return { txHash: tx.hash, taskIdHash };
}

/**
 * Release escrow funds to the worker.
 * @param {ethers.Wallet} wallet - Requestor wallet
 * @param {string} contractAddr - TaskEscrow address
 * @param {string} taskId - Task ID string
 */
export async function releaseEscrow(wallet, contractAddr, taskId) {
  const escrow = new ethers.Contract(contractAddr, ESCROW_ABI, wallet);
  const tx = await escrow.releaseEscrow(hashTaskId(taskId));
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Flag a dispute on an escrow.
 * @param {ethers.Wallet} wallet - Either party
 * @param {string} contractAddr - TaskEscrow address
 * @param {string} taskId - Task ID string
 */
export async function disputeEscrow(wallet, contractAddr, taskId) {
  const escrow = new ethers.Contract(contractAddr, ESCROW_ABI, wallet);
  const tx = await escrow.dispute(hashTaskId(taskId));
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Trigger auto-release after deadline.
 * @param {ethers.Wallet} wallet - Anyone can call this
 * @param {string} contractAddr - TaskEscrow address
 * @param {string} taskId - Task ID string
 */
export async function releaseAfterDeadline(wallet, contractAddr, taskId) {
  const escrow = new ethers.Contract(contractAddr, ESCROW_ABI, wallet);
  const tx = await escrow.releaseAfterDeadline(hashTaskId(taskId));
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Resolve a dispute (arbitrator only). Sends funds to worker or requestor.
 * @param {ethers.Wallet} wallet - Arbitrator wallet
 * @param {string} contractAddr - TaskEscrow address
 * @param {string} taskId - Task ID string
 * @param {boolean} releaseToWorker - true = pay worker, false = refund requestor
 */
export async function resolveDispute(wallet, contractAddr, taskId, releaseToWorker) {
  const escrow = new ethers.Contract(contractAddr, ESCROW_ABI, wallet);
  const tx = await escrow.resolveDispute(hashTaskId(taskId), releaseToWorker);
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Claim refund after dispute timeout expires (anyone can call, funds go to requestor).
 * @param {ethers.Wallet} wallet - Any wallet
 * @param {string} contractAddr - TaskEscrow address
 * @param {string} taskId - Task ID string
 */
export async function claimDisputeTimeout(wallet, contractAddr, taskId) {
  const escrow = new ethers.Contract(contractAddr, ESCROW_ABI, wallet);
  const tx = await escrow.claimDisputeTimeout(hashTaskId(taskId));
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Get escrow status for a task.
 * @param {ethers.Wallet|ethers.Provider} providerOrWallet
 * @param {string} contractAddr - TaskEscrow address
 * @param {string} taskId - Task ID string
 */
export async function getEscrowStatus(providerOrWallet, contractAddr, taskId) {
  const escrow = new ethers.Contract(contractAddr, ESCROW_ABI, providerOrWallet);
  const [requestor, worker, amount, deadline, status] = await escrow.escrows(hashTaskId(taskId));
  return {
    requestor,
    worker,
    amount: ethers.formatUnits(amount, 6), // USDC has 6 decimals
    deadline: Number(deadline),
    status: STATUS_MAP[status] || 'Unknown',
  };
}
