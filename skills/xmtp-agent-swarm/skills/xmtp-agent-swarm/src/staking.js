// staking.js — JS integration for WorkerStake contract
// SECURITY: Exact-amount approvals, input validation
import { ethers } from 'ethers';

const STAKE_ABI = [
  'function deposit(uint256 amount) external',
  'function withdraw(uint256 amount) external',
  'function lockForTask(bytes32 taskId, address worker, uint256 amount) external',
  'function unlockStake(bytes32 taskId) external',
  'function slashStake(bytes32 taskId, address requestor) external',
  'function requestEmergencyWithdraw() external',
  'function cancelEmergencyWithdraw() external',
  'function executeEmergencyWithdraw() external',
  'function getStake(address worker) view returns (uint256 totalDeposited, uint256 available, uint256 locked, uint256 slashed, uint256 withdrawRequestTime)',
  'function getTaskLock(bytes32 taskId) view returns (address worker, uint256 amount, bool resolved)',
  'function usdc() view returns (address)',
];

const USDC_ABI = [
  'function approve(address spender, uint256 amount) returns (bool)',
  'function allowance(address owner, address spender) view returns (uint256)',
  'function balanceOf(address) view returns (uint256)',
];

// Deployed to Base mainnet 2026-02-24
let DEFAULT_STAKE_ADDRESS = process.env.WORKER_STAKE_ADDRESS || '0x91618100EE71652Bb0A153c5C9Cc2aaE2B63E488';

export function getDefaultStakeAddress() {
  return DEFAULT_STAKE_ADDRESS;
}

export function hashTaskId(taskId) {
  return ethers.id(taskId);
}

/**
 * Deposit USDC as stake.
 * @param {ethers.Wallet} wallet - Worker wallet
 * @param {string} contractAddr - WorkerStake address
 * @param {string} amount - Human-readable USDC amount
 */
export async function depositStake(wallet, contractAddr, amount) {
  if (!contractAddr) throw new Error('WorkerStake not deployed yet.');
  const stake = new ethers.Contract(contractAddr, STAKE_ABI, wallet);
  const usdcAddr = await stake.usdc();
  const usdc = new ethers.Contract(usdcAddr, USDC_ABI, wallet);
  const amountRaw = ethers.parseUnits(amount.toString(), 6);

  // SECURITY: Approve only the exact amount needed
  const allowance = await usdc.allowance(wallet.address, contractAddr);
  if (allowance < amountRaw) {
    if (allowance > 0n) {
      const resetTx = await usdc.approve(contractAddr, 0, { gasLimit: 100000 });
      await resetTx.wait();
    }
    const approveTx = await usdc.approve(contractAddr, amountRaw, { gasLimit: 100000 });
    await approveTx.wait();
  }

  const tx = await stake.deposit(amountRaw, { gasLimit: 200000 });
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Withdraw available stake.
 */
export async function withdrawStake(wallet, contractAddr, amount) {
  const stake = new ethers.Contract(contractAddr, STAKE_ABI, wallet);
  const amountRaw = ethers.parseUnits(amount.toString(), 6);
  const tx = await stake.withdraw(amountRaw);
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Lock stake for a task (when bidding).
 */
export async function lockStakeForTask(wallet, contractAddr, taskId, amount) {
  const stake = new ethers.Contract(contractAddr, STAKE_ABI, wallet);
  const amountRaw = ethers.parseUnits(amount.toString(), 6);
  const tx = await stake.lockForTask(hashTaskId(taskId), wallet.address, amountRaw);
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Get stake status for a worker.
 */
export async function getStakeStatus(providerOrWallet, contractAddr, workerAddress) {
  const stake = new ethers.Contract(contractAddr, STAKE_ABI, providerOrWallet);
  const [totalDeposited, available, locked, slashed, withdrawRequestTime] = await stake.getStake(workerAddress);
  return {
    totalDeposited: ethers.formatUnits(totalDeposited, 6),
    available: ethers.formatUnits(available, 6),
    locked: ethers.formatUnits(locked, 6),
    slashed: ethers.formatUnits(slashed, 6),
    emergencyWithdrawRequested: Number(withdrawRequestTime) > 0,
    emergencyWithdrawTime: Number(withdrawRequestTime),
  };
}

/**
 * Request emergency withdrawal (starts 30-day cooldown).
 */
export async function requestEmergencyWithdraw(wallet, contractAddr) {
  const stake = new ethers.Contract(contractAddr, STAKE_ABI, wallet);
  const tx = await stake.requestEmergencyWithdraw();
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Execute emergency withdrawal after cooldown.
 */
export async function executeEmergencyWithdraw(wallet, contractAddr) {
  const stake = new ethers.Contract(contractAddr, STAKE_ABI, wallet);
  const tx = await stake.executeEmergencyWithdraw();
  await tx.wait();
  return { txHash: tx.hash };
}
