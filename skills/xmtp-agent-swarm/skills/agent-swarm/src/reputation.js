// reputation.js — On-chain reputation derived from escrow history
// No reviews, no stars, no subjective ratings. Just math from the chain.
// PERFORMANCE: Caches last-scanned block per address to avoid re-scanning full history
import { ethers } from 'ethers';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const CACHE_FILE = join(__dirname, '..', '.reputation-cache.json');

function loadCache() {
  try {
    if (existsSync(CACHE_FILE)) return JSON.parse(readFileSync(CACHE_FILE, 'utf-8'));
  } catch {}
  return {};
}

function saveCache(cache) {
  try { writeFileSync(CACHE_FILE, JSON.stringify(cache, null, 2)); } catch {}
}

const ESCROW_ABI = [
  'event EscrowCreated(bytes32 indexed taskId, address requestor, address worker, uint256 amount, uint256 deadline)',
  'event EscrowReleased(bytes32 indexed taskId, address worker, uint256 amount)',
  'event EscrowDisputed(bytes32 indexed taskId, address disputedBy)',
  'event EscrowRefunded(bytes32 indexed taskId, address requestor, uint256 amount)',
];

/**
 * Build a reputation profile for an address by scanning escrow contract events.
 * Pure on-chain data: every released escrow is a line on your resume,
 * every dispute is a scar.
 *
 * @param {ethers.Provider} provider - Base RPC provider
 * @param {string} escrowAddress - TaskEscrow contract address
 * @param {string} agentAddress - Address to build reputation for
 * @param {number} [fromBlock=0] - Starting block (use deployment block for speed)
 * @returns {object} Reputation profile
 */
// TaskEscrow was deployed at block 42490000 on Base mainnet (Feb 21, 2026)
const DEFAULT_FROM_BLOCK = 42490000;

export async function buildReputation(provider, escrowAddress, agentAddress, fromBlock = DEFAULT_FROM_BLOCK) {
  const contract = new ethers.Contract(escrowAddress, ESCROW_ABI, provider);
  const addr = agentAddress.toLowerCase();
  const cacheKey = `${escrowAddress}:${addr}`;
  const cache = loadCache();

  // Use cached start block if available (incremental scanning)
  const cachedEntry = cache[cacheKey];
  const effectiveFromBlock = cachedEntry?.lastBlock ? cachedEntry.lastBlock + 1 : fromBlock;

  const currentBlock = await provider.getBlockNumber();
  
  // If we're up to date, return cached result
  if (cachedEntry?.result && effectiveFromBlock >= currentBlock) {
    return cachedEntry.result;
  }

  const CHUNK = 9999;

  async function queryInChunks(eventName, startFrom = fromBlock) {
    const allEvents = [];
    // Merge with cached events if available
    if (cachedEntry?.events?.[eventName]) {
      allEvents.push(...cachedEntry.events[eventName].map(e => ({
        args: e.args,
        blockNumber: e.blockNumber,
      })));
    }
    for (let start = startFrom; start <= currentBlock; start += CHUNK) {
      const end = Math.min(start + CHUNK - 1, currentBlock);
      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          const events = await contract.queryFilter(eventName, start, end);
          allEvents.push(...events);
          break;
        } catch (e) {
          if (attempt === 2) throw e;
          await new Promise(r => setTimeout(r, 1000 * (attempt + 1)));
        }
      }
    }
    return allEvents;
  }

  const [created, released, disputed, refunded] = await Promise.all([
    queryInChunks('EscrowCreated', effectiveFromBlock),
    queryInChunks('EscrowReleased', effectiveFromBlock),
    queryInChunks('EscrowDisputed', effectiveFromBlock),
    queryInChunks('EscrowRefunded', effectiveFromBlock),
  ]);

  // Build a map of taskId -> event data
  const tasks = new Map();

  for (const e of created) {
    const taskId = e.args.taskId;
    tasks.set(taskId, {
      requestor: e.args.requestor.toLowerCase(),
      worker: e.args.worker.toLowerCase(),
      amount: e.args.amount,
      deadline: Number(e.args.deadline),
      block: e.blockNumber,
      status: 'active',
    });
  }

  for (const e of released) {
    const t = tasks.get(e.args.taskId);
    if (t) t.status = 'released';
  }

  for (const e of disputed) {
    const t = tasks.get(e.args.taskId);
    if (t) t.status = 'disputed';
  }

  for (const e of refunded) {
    const t = tasks.get(e.args.taskId);
    if (t) t.status = 'refunded';
  }

  // Calculate reputation for this agent
  const asWorker = { completed: 0, disputed: 0, refunded: 0, active: 0, totalEarned: 0n, tasks: [] };
  const asRequestor = { completed: 0, disputed: 0, refunded: 0, active: 0, totalSpent: 0n, tasks: [] };

  for (const [taskId, t] of tasks) {
    if (t.worker === addr) {
      asWorker.tasks.push({ taskId, amount: t.amount, status: t.status });
      if (t.status === 'released') { asWorker.completed++; asWorker.totalEarned += t.amount; }
      else if (t.status === 'disputed') asWorker.disputed++;
      else if (t.status === 'refunded') asWorker.refunded++;
      else asWorker.active++;
    }
    if (t.requestor === addr) {
      asRequestor.tasks.push({ taskId, amount: t.amount, status: t.status });
      if (t.status === 'released') { asRequestor.completed++; asRequestor.totalSpent += t.amount; }
      else if (t.status === 'disputed') asRequestor.disputed++;
      else if (t.status === 'refunded') asRequestor.refunded++;
      else asRequestor.active++;
    }
  }

  const workerTotal = asWorker.completed + asWorker.disputed + asWorker.refunded;
  const requestorTotal = asRequestor.completed + asRequestor.disputed + asRequestor.refunded;

  const result = {
    address: agentAddress,
    worker: {
      jobsCompleted: asWorker.completed,
      jobsDisputed: asWorker.disputed,
      jobsRefunded: asWorker.refunded,
      jobsActive: asWorker.active,
      totalEarned: ethers.formatUnits(asWorker.totalEarned, 6),
      completionRate: workerTotal > 0 ? (asWorker.completed / workerTotal * 100).toFixed(1) + '%' : 'n/a',
      disputeRate: workerTotal > 0 ? (asWorker.disputed / workerTotal * 100).toFixed(1) + '%' : 'n/a',
    },
    requestor: {
      jobsPosted: asRequestor.completed + asRequestor.disputed + asRequestor.refunded + asRequestor.active,
      jobsCompleted: asRequestor.completed,
      jobsDisputed: asRequestor.disputed,
      totalSpent: ethers.formatUnits(asRequestor.totalSpent, 6),
      completionRate: requestorTotal > 0 ? (asRequestor.completed / requestorTotal * 100).toFixed(1) + '%' : 'n/a',
    },
    // Simple trust score: 0-100 based on completion rate and volume
    trustScore: calculateTrustScore(asWorker, asRequestor),
    lastUpdated: new Date().toISOString(),
  };

  // Cache the result and last scanned block
  cache[cacheKey] = { lastBlock: currentBlock, result };
  saveCache(cache);

  return result;
}

/**
 * Calculate a trust score from 0-100.
 * Factors: completion rate, volume, dispute rate.
 * No subjective input. Just math.
 */
function calculateTrustScore(asWorker, asRequestor) {
  const wTotal = asWorker.completed + asWorker.disputed + asWorker.refunded;
  const rTotal = asRequestor.completed + asRequestor.disputed + asRequestor.refunded;
  const total = wTotal + rTotal;

  if (total === 0) return 0; // no history, no trust

  const completed = asWorker.completed + asRequestor.completed;
  const disputed = asWorker.disputed + asRequestor.disputed;

  // Base: completion rate (0-70 points)
  const completionRate = completed / total;
  let score = completionRate * 70;

  // Volume bonus: more jobs = more confidence (0-20 points, logarithmic)
  const volumeBonus = Math.min(20, Math.log2(total + 1) * 5);
  score += volumeBonus;

  // Dispute penalty: -10 per dispute rate percentage point above 0
  const disputeRate = disputed / total;
  score -= disputeRate * 100 * 0.5;

  // Value bonus: higher total volume = more skin in the game (0-10 points)
  const totalValue = Number(ethers.formatUnits(asWorker.totalEarned + asRequestor.totalSpent, 6));
  const valueBonus = Math.min(10, Math.log10(totalValue + 1) * 5);
  score += valueBonus;

  return Math.max(0, Math.min(100, Math.round(score)));
}

/**
 * Create a reputation protocol message for broadcasting on XMTP.
 * Agents can query each other's reputation before accepting work.
 */
export function createReputationQuery({ agent, escrowContract }) {
  return { type: 'reputation_query', agent, escrowContract };
}

/**
 * Create a reputation response message.
 */
export function createReputationResponse(reputation) {
  return { type: 'reputation', ...reputation };
}

/**
 * Format reputation for display.
 */
export function formatReputation(rep) {
  const lines = [
    `reputation for ${rep.address}`,
    `  trust score: ${rep.trustScore}/100`,
    ``,
    `  as worker:`,
    `    completed: ${rep.worker.jobsCompleted} | disputed: ${rep.worker.jobsDisputed} | refunded: ${rep.worker.jobsRefunded}`,
    `    earned: ${rep.worker.totalEarned} USDC | completion: ${rep.worker.completionRate} | disputes: ${rep.worker.disputeRate}`,
    ``,
    `  as requestor:`,
    `    posted: ${rep.requestor.jobsPosted} | completed: ${rep.requestor.jobsCompleted} | disputed: ${rep.requestor.jobsDisputed}`,
    `    spent: ${rep.requestor.totalSpent} USDC | completion: ${rep.requestor.completionRate}`,
  ];
  return lines.join('\n');
}
