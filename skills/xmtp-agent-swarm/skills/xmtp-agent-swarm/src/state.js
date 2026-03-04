// state.js — Persistent state logger for the dashboard
// SECURITY: File locking prevents concurrent write corruption
// Agents write activity to a JSON file, which gets pushed to GitHub Pages

import { readFileSync, writeFileSync, existsSync, mkdirSync, unlinkSync, renameSync, statSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = join(__dirname, '..', 'dashboard', 'data');
const STATE_FILE = join(STATE_DIR, 'state.json');
const LOCK_FILE = STATE_FILE + '.lock';
const LOCK_TIMEOUT = 10000; // 10s max lock hold
const LOCK_RETRY_INTERVAL = 50; // 50ms between retries

// ─── File Locking ───

function acquireLock(maxWait = 5000) {
  const start = Date.now();
  while (Date.now() - start < maxWait) {
    try {
      // Check for stale lock
      if (existsSync(LOCK_FILE)) {
        const lockAge = Date.now() - getFileTime(LOCK_FILE);
        if (lockAge > LOCK_TIMEOUT) {
          // Stale lock — remove it
          try { unlinkSync(LOCK_FILE); } catch {}
        } else {
          // Lock is active — wait
          sleepSync(LOCK_RETRY_INTERVAL);
          continue;
        }
      }
      // Create lock file atomically (O_EXCL equivalent)
      writeFileSync(LOCK_FILE, String(process.pid), { flag: 'wx' });
      return true;
    } catch (err) {
      if (err.code === 'EEXIST') {
        // Another process grabbed the lock
        sleepSync(LOCK_RETRY_INTERVAL);
        continue;
      }
      // Unexpected error — proceed without lock
      return false;
    }
  }
  // Timeout — proceed without lock (better than deadlock)
  console.warn('[state] Lock acquisition timed out, proceeding without lock');
  return false;
}

function releaseLock() {
  try { unlinkSync(LOCK_FILE); } catch {}
}

function getFileTime(path) {
  try {
    return statSync(path).mtimeMs;
  } catch {
    return 0;
  }
}

function sleepSync(ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) {} // busy wait (short duration only)
}

// ─── State Management ───

function emptyState() {
  return {
    agents: {},
    tasks: [],
    listings: [],
    escrows: [],
    reputation: [],
    activity: [],
    stats: {
      totalTasks: 0, totalPaid: 0, totalClaims: 0, totalResults: 0,
      totalListings: 0, totalBids: 0, totalEscrows: 0, totalDisputes: 0,
    },
  };
}

function loadState() {
  if (!existsSync(STATE_DIR)) mkdirSync(STATE_DIR, { recursive: true });
  if (!existsSync(STATE_FILE)) return emptyState();
  try {
    const state = JSON.parse(readFileSync(STATE_FILE, 'utf-8'));
    // Ensure all fields exist
    if (!state.listings) state.listings = [];
    if (!state.escrows) state.escrows = [];
    if (!state.reputation) state.reputation = [];
    if (!state.stats) state.stats = {};
    const defaults = { totalListings: 0, totalBids: 0, totalEscrows: 0, totalDisputes: 0 };
    for (const [k, v] of Object.entries(defaults)) {
      if (state.stats[k] === undefined) state.stats[k] = v;
    }
    return state;
  } catch {
    // Corrupted state — start fresh
    console.warn('[state] Corrupted state file, starting fresh');
    return emptyState();
  }
}

function saveState(state) {
  if (!existsSync(STATE_DIR)) mkdirSync(STATE_DIR, { recursive: true });
  // Write to temp file first, then rename (atomic on most filesystems)
  const tmpFile = STATE_FILE + '.tmp';
  writeFileSync(tmpFile, JSON.stringify(state, null, 2));
  try {
    renameSync(tmpFile, STATE_FILE);
  } catch {
    // Fallback: direct write
    writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  }
}

/** Execute a state mutation with file locking */
function withLock(fn) {
  acquireLock();
  try {
    const state = loadState();
    fn(state);
    saveState(state);
  } finally {
    releaseLock();
  }
}

// ─── Public API ───

const MAX_ACTIVITY = 50;

function trimActivity(state) {
  if (state.activity.length > MAX_ACTIVITY) {
    state.activity = state.activity.slice(-MAX_ACTIVITY);
  }
}

export function registerAgent(address, role = 'worker') {
  withLock(state => {
    if (!state.agents[address]) {
      state.agents[address] = {
        address,
        roles: [role],
        earned: 0,
        spent: 0,
        tasksPosted: 0,
        tasksClaimed: 0,
        tasksCompleted: 0,
        firstSeen: new Date().toISOString(),
      };
    } else if (!state.agents[address].roles.includes(role)) {
      state.agents[address].roles.push(role);
    }
  });
}

export function logTask(task, requestor) {
  registerAgent(requestor, 'requestor');
  withLock(state => {
    state.tasks.push({
      id: task.id,
      title: (task.title || '').slice(0, 200),
      budget: task.budget,
      subtasks: task.subtasks?.length || 0,
      requestor,
      status: 'open',
      createdAt: new Date().toISOString(),
    });
    state.stats.totalTasks++;
    if (state.agents[requestor]) {
      state.agents[requestor].tasksPosted++;
      state.agents[requestor].spent += parseFloat(task.budget || 0);
    }
    state.activity.push({
      type: 'task_posted',
      agent: requestor,
      task: (task.title || '').slice(0, 200),
      amount: task.budget,
      at: new Date().toISOString(),
    });
    trimActivity(state);
  });
}

export function logClaim(taskId, subtaskId, worker) {
  registerAgent(worker, 'worker');
  withLock(state => {
    state.stats.totalClaims++;
    if (state.agents[worker]) state.agents[worker].tasksClaimed++;
    const task = state.tasks.find(t => t.id === taskId);
    if (task) task.status = 'in-progress';
    state.activity.push({
      type: 'subtask_claimed',
      agent: worker,
      taskId,
      at: new Date().toISOString(),
    });
    trimActivity(state);
  });
}

export function logResult(taskId, subtaskId, worker) {
  withLock(state => {
    state.stats.totalResults++;
    if (state.agents[worker]) state.agents[worker].tasksCompleted++;
    state.activity.push({
      type: 'result_submitted',
      agent: worker,
      taskId,
      at: new Date().toISOString(),
    });
    trimActivity(state);
  });
}

export function logPayment(taskId, worker, amount, txHash) {
  withLock(state => {
    const amt = parseFloat(amount || 0);
    state.stats.totalPaid += amt;
    if (state.agents[worker]) state.agents[worker].earned += amt;
    const task = state.tasks.find(t => t.id === taskId);
    if (task) task.status = 'paid';
    state.activity.push({
      type: 'payment_sent',
      agent: worker,
      taskId,
      amount: amt,
      txHash,
      at: new Date().toISOString(),
    });
    trimActivity(state);
  });
}

export function logListing(listing) {
  withLock(state => {
    state.stats.totalListings++;
    state.listings.push({
      taskId: listing.taskId,
      title: (listing.title || '').slice(0, 200),
      description: (listing.description || '').slice(0, 500),
      budget: listing.budget,
      skills_needed: listing.skills_needed || [],
      requestor: listing.requestor,
      bids: 0,
      status: 'open',
      createdAt: new Date().toISOString(),
    });
    state.activity.push({
      type: 'listing_posted',
      agent: listing.requestor,
      task: (listing.title || '').slice(0, 200),
      amount: listing.budget,
      at: new Date().toISOString(),
    });
    trimActivity(state);
  });
}

export function logEscrow(escrow) {
  withLock(state => {
    state.stats.totalEscrows++;
    state.escrows.push({
      taskId: escrow.taskId,
      requestor: escrow.requestor,
      worker: escrow.worker,
      amount: escrow.amount,
      deadline: escrow.deadline,
      status: escrow.status || 'active',
      txHash: escrow.txHash || null,
      createdAt: new Date().toISOString(),
    });
    state.activity.push({
      type: 'escrow_created',
      agent: escrow.requestor,
      taskId: escrow.taskId,
      amount: parseFloat(escrow.amount),
      at: new Date().toISOString(),
    });
    trimActivity(state);
  });
}

export function updateEscrow(taskId, status, txHash) {
  withLock(state => {
    const escrow = state.escrows.find(e => e.taskId === taskId);
    if (escrow) {
      escrow.status = status;
      if (txHash) escrow.releaseTxHash = txHash;
      state.activity.push({
        type: `escrow_${status}`,
        agent: escrow.worker,
        taskId,
        amount: parseFloat(escrow.amount),
        at: new Date().toISOString(),
      });
      trimActivity(state);
    }
  });
}

export function logReputation(rep) {
  withLock(state => {
    const idx = state.reputation.findIndex(r => r.address.toLowerCase() === rep.address.toLowerCase());
    if (idx >= 0) {
      state.reputation[idx] = rep;
    } else {
      state.reputation.push(rep);
    }
    state.activity.push({
      type: 'reputation_updated',
      agent: rep.address,
      trustScore: rep.trustScore,
      at: new Date().toISOString(),
    });
    trimActivity(state);
  });
}

export function getState() {
  acquireLock(2000);
  try {
    return loadState();
  } finally {
    releaseLock();
  }
}
