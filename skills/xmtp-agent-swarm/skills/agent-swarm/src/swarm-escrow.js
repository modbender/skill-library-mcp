// swarm-escrow.js — JS integration for SwarmEscrow (multi-worker bid-lock escrow)
// SECURITY: Exact-amount approvals, reentrancy-safe calls, input validation
import { ethers } from 'ethers';

const SWARM_ESCROW_ABI = [
  'function createTask(bytes32 taskId, uint256 totalBudget, uint256 milestoneCount, uint256 bidDeadline, uint256 bondAmount) external',
  'function placeBid(bytes32 taskId, uint256 price) external',
  'function acceptBid(bytes32 taskId, address worker) external',
  'function refundBond(bytes32 taskId, address worker) external',
  'function fundAndAssign(bytes32 taskId, address[] workers, uint256[] amounts, uint256[] deadlines) external',
  'function setCoordinator(bytes32 taskId, address coordinator) external',
  'function releaseMilestone(bytes32 taskId, uint256 milestoneIndex) external',
  'function disputeMilestone(bytes32 taskId, uint256 milestoneIndex) external',
  'function resolveDisputeMilestone(bytes32 taskId, uint256 milestoneIndex, bool releaseToWorker) external',
  'function cancelTask(bytes32 taskId) external',
  'function getTask(bytes32 taskId) view returns (address requestor, uint256 totalBudget, uint256 milestoneCount, uint256 releasedCount, uint256 bidDeadline, uint256 bondAmount, uint8 status, address coordinator, bool exists_)',
  'function getMilestone(bytes32 taskId, uint256 index) view returns (address worker, uint256 amount, uint256 deadline, uint8 status, uint256 disputeTimestamp)',
  'function getBidCount(bytes32 taskId) view returns (uint256)',
  'function getBid(bytes32 taskId, uint256 index) view returns (address worker, uint256 price, bool bonded, bool accepted, bool refunded)',
  'function usdc() view returns (address)',
];

const USDC_ABI = [
  'function approve(address spender, uint256 amount) returns (bool)',
  'function allowance(address owner, address spender) view returns (uint256)',
];

const TASK_STATUS = ['Bidding', 'Active', 'Completed', 'Cancelled'];
const MILESTONE_STATUS = ['Unassigned', 'Active', 'Released', 'Disputed', 'Refunded'];

// Deployed to Base mainnet 2026-02-24
let DEFAULT_SWARM_ESCROW = process.env.SWARM_ESCROW_ADDRESS || '0xCd8e54f26a81843Ed0fC53c283f34b53444cdb59';

export function getDefaultSwarmEscrowAddress() {
  return DEFAULT_SWARM_ESCROW;
}

export function hashTaskId(taskId) {
  return ethers.id(taskId);
}

/**
 * Create a task in bidding state.
 */
export async function createSwarmTask(wallet, contractAddr, { taskId, totalBudget, milestoneCount, bidDeadlineHours, bondAmount }) {
  if (!contractAddr) throw new Error('SwarmEscrow not deployed yet.');
  const escrow = new ethers.Contract(contractAddr, SWARM_ESCROW_ABI, wallet);

  const budgetRaw = ethers.parseUnits(totalBudget.toString(), 6);
  const bondRaw = bondAmount ? ethers.parseUnits(bondAmount.toString(), 6) : 0n;
  const deadline = BigInt(Math.floor(Date.now() / 1000) + (bidDeadlineHours || 24) * 3600);
  const taskIdHash = hashTaskId(taskId);

  const tx = await escrow.createTask(taskIdHash, budgetRaw, milestoneCount, deadline, bondRaw, { gasLimit: 300000 });
  await tx.wait();
  return { txHash: tx.hash, taskIdHash };
}

/**
 * Place a bid on a task (with optional bond).
 */
export async function placeBid(wallet, contractAddr, { taskId, price }) {
  const escrow = new ethers.Contract(contractAddr, SWARM_ESCROW_ABI, wallet);
  const taskIdHash = hashTaskId(taskId);
  const priceRaw = ethers.parseUnits(price.toString(), 6);

  // Check if bond required and approve
  const [,,,,, bondAmount,,, exists] = await escrow.getTask(taskIdHash);
  if (!exists) throw new Error('Task does not exist');

  if (bondAmount > 0n) {
    const usdcAddr = await escrow.usdc();
    const usdc = new ethers.Contract(usdcAddr, USDC_ABI, wallet);
    const allowance = await usdc.allowance(wallet.address, contractAddr);
    if (allowance < bondAmount) {
      if (allowance > 0n) {
        const resetTx = await usdc.approve(contractAddr, 0, { gasLimit: 100000 });
        await resetTx.wait();
      }
      const approveTx = await usdc.approve(contractAddr, bondAmount, { gasLimit: 100000 });
      await approveTx.wait();
    }
  }

  const tx = await escrow.placeBid(taskIdHash, priceRaw, { gasLimit: 200000 });
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Accept a worker's bid.
 */
export async function acceptBid(wallet, contractAddr, { taskId, worker }) {
  const escrow = new ethers.Contract(contractAddr, SWARM_ESCROW_ABI, wallet);
  const tx = await escrow.acceptBid(hashTaskId(taskId), worker, { gasLimit: 100000 });
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Fund task and assign milestones to accepted workers.
 */
export async function fundAndAssign(wallet, contractAddr, { taskId, assignments }) {
  if (!assignments?.length) throw new Error('At least one assignment required');

  const escrow = new ethers.Contract(contractAddr, SWARM_ESCROW_ABI, wallet);
  const usdcAddr = await escrow.usdc();
  const usdc = new ethers.Contract(usdcAddr, USDC_ABI, wallet);

  const workers = assignments.map(a => a.worker);
  const amounts = assignments.map(a => ethers.parseUnits(a.amount.toString(), 6));
  const deadlines = assignments.map(a => {
    const hours = a.deadlineHours || 24;
    return BigInt(Math.floor(Date.now() / 1000) + hours * 3600);
  });

  const totalAmount = amounts.reduce((a, b) => a + b, 0n);
  const taskIdHash = hashTaskId(taskId);

  // Exact approval
  const allowance = await usdc.allowance(wallet.address, contractAddr);
  if (allowance < totalAmount) {
    if (allowance > 0n) {
      const resetTx = await usdc.approve(contractAddr, 0, { gasLimit: 100000 });
      await resetTx.wait();
    }
    const approveTx = await usdc.approve(contractAddr, totalAmount, { gasLimit: 100000 });
    await approveTx.wait();
  }

  const tx = await escrow.fundAndAssign(taskIdHash, workers, amounts, deadlines, { gasLimit: 500000 });
  await tx.wait();
  return { txHash: tx.hash, totalAmount: ethers.formatUnits(totalAmount, 6) };
}

/**
 * Set a coordinator for the task.
 */
export async function setCoordinator(wallet, contractAddr, { taskId, coordinator }) {
  const escrow = new ethers.Contract(contractAddr, SWARM_ESCROW_ABI, wallet);
  const tx = await escrow.setCoordinator(hashTaskId(taskId), coordinator, { gasLimit: 100000 });
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Release a milestone to its assigned worker.
 */
export async function releaseSwarmMilestone(wallet, contractAddr, taskId, milestoneIndex) {
  const escrow = new ethers.Contract(contractAddr, SWARM_ESCROW_ABI, wallet);
  const tx = await escrow.releaseMilestone(hashTaskId(taskId), milestoneIndex, { gasLimit: 200000 });
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Cancel a task (refunds all bonds).
 */
export async function cancelSwarmTask(wallet, contractAddr, taskId) {
  const escrow = new ethers.Contract(contractAddr, SWARM_ESCROW_ABI, wallet);
  const tx = await escrow.cancelTask(hashTaskId(taskId), { gasLimit: 300000 });
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Refund bond to a non-selected bidder.
 */
export async function refundBidBond(wallet, contractAddr, { taskId, worker }) {
  const escrow = new ethers.Contract(contractAddr, SWARM_ESCROW_ABI, wallet);
  const tx = await escrow.refundBond(hashTaskId(taskId), worker, { gasLimit: 100000 });
  await tx.wait();
  return { txHash: tx.hash };
}

/**
 * Get full swarm task status.
 */
export async function getSwarmTaskStatus(providerOrWallet, contractAddr, taskId) {
  const escrow = new ethers.Contract(contractAddr, SWARM_ESCROW_ABI, providerOrWallet);
  const taskIdHash = hashTaskId(taskId);
  const [requestor, totalBudget, milestoneCount, releasedCount, bidDeadline, bondAmount, status, coordinator, exists] =
    await escrow.getTask(taskIdHash);

  if (!exists) return null;

  // Get milestones
  const milestoneDetails = [];
  for (let i = 0; i < Number(milestoneCount); i++) {
    const [worker, amount, deadline, mStatus, disputeTimestamp] = await escrow.getMilestone(taskIdHash, i);
    milestoneDetails.push({
      index: i,
      worker,
      amount: ethers.formatUnits(amount, 6),
      deadline: Number(deadline),
      status: MILESTONE_STATUS[mStatus] || 'Unknown',
      disputeTimestamp: Number(disputeTimestamp),
    });
  }

  // Get bids
  const bidCount = Number(await escrow.getBidCount(taskIdHash));
  const bidDetails = [];
  for (let i = 0; i < bidCount; i++) {
    const [worker, price, bonded, accepted, refunded] = await escrow.getBid(taskIdHash, i);
    bidDetails.push({
      worker,
      price: ethers.formatUnits(price, 6),
      bonded,
      accepted,
      refunded,
    });
  }

  return {
    requestor,
    totalBudget: ethers.formatUnits(totalBudget, 6),
    milestoneCount: Number(milestoneCount),
    releasedCount: Number(releasedCount),
    bidDeadline: Number(bidDeadline),
    bondAmount: ethers.formatUnits(bondAmount, 6),
    status: TASK_STATUS[status] || 'Unknown',
    coordinator: coordinator === ethers.ZeroAddress ? null : coordinator,
    milestones: milestoneDetails,
    bids: bidDetails,
  };
}
