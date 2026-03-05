// milestone-escrow.js — JS integration for TaskEscrowV3 (milestone-based escrow)
// SECURITY: Exact-amount approvals, reentrancy-safe calls, input validation
import { ethers } from 'ethers';

const MILESTONE_ESCROW_ABI = [
  'function createMilestoneEscrow(bytes32 taskId, address worker, uint256[] amounts, uint256[] deadlines) external',
  'function releaseMilestone(bytes32 taskId, uint256 milestoneIndex) external',
  'function disputeMilestone(bytes32 taskId, uint256 milestoneIndex) external',
  'function resolveDisputeMilestone(bytes32 taskId, uint256 milestoneIndex, bool releaseToWorker) external',
  'function claimMilestoneTimeout(bytes32 taskId, uint256 milestoneIndex) external',
  'function releaseAfterDeadline(bytes32 taskId, uint256 milestoneIndex) external',
  'function refundMilestone(bytes32 taskId, uint256 milestoneIndex) external',
  'function getEscrow(bytes32 taskId) view returns (address requestor, address worker, uint256 totalAmount, uint256 milestoneCount, uint256 releasedCount, bool exists_)',
  'function getMilestone(bytes32 taskId, uint256 index) view returns (uint256 amount, uint256 deadline, uint8 status, uint256 disputeTimestamp)',
  'function usdc() view returns (address)',
];

const USDC_ABI = [
  'function approve(address spender, uint256 amount) returns (bool)',
  'function allowance(address owner, address spender) view returns (uint256)',
];

const STATUS_MAP = ['Active', 'Released', 'Disputed', 'Refunded'];

// Deployed to Base mainnet 2026-02-24
let DEFAULT_MILESTONE_ESCROW = process.env.MILESTONE_ESCROW_ADDRESS || '0x7334DfF91ddE131e587d22Cb85F4184833340F6f';

export function getDefaultMilestoneEscrowAddress() {
  return DEFAULT_MILESTONE_ESCROW;
}

export function hashTaskId(taskId) {
  return ethers.id(taskId);
}

/**
 * Create a milestone escrow.
 * @param {ethers.Wallet} wallet - Requestor wallet
 * @param {string} contractAddr - TaskEscrowV3 address
 * @param {object} opts - { taskId, worker, milestones: [{ amount, deadlineHours }] }
 */
export async function createMilestoneEscrow(wallet, contractAddr, { taskId, worker, milestones: milestoneDefs }) {
  if (!contractAddr) throw new Error('TaskEscrowV3 not deployed yet. Deploy first.');
  if (!milestoneDefs?.length) throw new Error('At least one milestone required');
  if (milestoneDefs.length > 20) throw new Error('Maximum 20 milestones');

  const escrow = new ethers.Contract(contractAddr, MILESTONE_ESCROW_ABI, wallet);
  const usdcAddr = await escrow.usdc();
  const usdc = new ethers.Contract(usdcAddr, USDC_ABI, wallet);

  const amounts = milestoneDefs.map(m => ethers.parseUnits(m.amount.toString(), 6));
  const deadlines = milestoneDefs.map(m => {
    const hours = m.deadlineHours || 24;
    return BigInt(Math.floor(Date.now() / 1000) + hours * 3600);
  });

  const totalAmount = amounts.reduce((a, b) => a + b, 0n);
  const taskIdHash = hashTaskId(taskId);

  // SECURITY: Approve only the exact amount needed
  const allowance = await usdc.allowance(wallet.address, contractAddr);
  if (allowance < totalAmount) {
    if (allowance > 0n) {
      const resetTx = await usdc.approve(contractAddr, 0, { gasLimit: 100000 });
      await resetTx.wait();
    }
    const approveTx = await usdc.approve(contractAddr, totalAmount, { gasLimit: 100000 });
    await approveTx.wait();
  }

  const tx = await escrow.createMilestoneEscrow(taskIdHash, worker, amounts, deadlines, { gasLimit: 300000 });
  await tx.wait();

  return { txHash: tx.hash, taskIdHash, totalAmount: ethers.formatUnits(totalAmount, 6) };
}

/**
 * Release a specific milestone.
 */
export async function releaseMilestone(wallet, contractAddr, taskId, milestoneIndex) {
  const escrow = new ethers.Contract(contractAddr, MILESTONE_ESCROW_ABI, wallet);
  const tx = await escrow.releaseMilestone(hashTaskId(taskId), milestoneIndex);
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Dispute a specific milestone.
 */
export async function disputeMilestone(wallet, contractAddr, taskId, milestoneIndex) {
  const escrow = new ethers.Contract(contractAddr, MILESTONE_ESCROW_ABI, wallet);
  const tx = await escrow.disputeMilestone(hashTaskId(taskId), milestoneIndex);
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Get full milestone escrow status.
 */
export async function getMilestoneEscrowStatus(providerOrWallet, contractAddr, taskId) {
  const escrow = new ethers.Contract(contractAddr, MILESTONE_ESCROW_ABI, providerOrWallet);
  const taskIdHash = hashTaskId(taskId);
  const [requestor, worker, totalAmount, milestoneCount, releasedCount, exists] = await escrow.getEscrow(taskIdHash);

  if (!exists) return null;

  const milestoneDetails = [];
  for (let i = 0; i < Number(milestoneCount); i++) {
    const [amount, deadline, status, disputeTimestamp] = await escrow.getMilestone(taskIdHash, i);
    milestoneDetails.push({
      index: i,
      amount: ethers.formatUnits(amount, 6),
      deadline: Number(deadline),
      status: STATUS_MAP[status] || 'Unknown',
      disputeTimestamp: Number(disputeTimestamp),
    });
  }

  return {
    requestor,
    worker,
    totalAmount: ethers.formatUnits(totalAmount, 6),
    milestoneCount: Number(milestoneCount),
    releasedCount: Number(releasedCount),
    milestones: milestoneDetails,
  };
}
