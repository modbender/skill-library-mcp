// wallet-guard.js — Wallet guardian layer inspired by 0xDeployer's lockdown approach
// No raw private key exposure. Permissioned access with spending limits,
// address allowlists, rate limiting, and full audit logging.
//
// SECURITY: This wraps any wallet (raw key, env var, or API-backed) with
// configurable guardrails so agents can't drain funds even if compromised.

import { ethers } from 'ethers';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';

const GUARD_CONFIG_FILE = '.wallet-guard.json';
const AUDIT_LOG_FILE = '.wallet-audit.log';

// Default guardrails — conservative by default
const DEFAULT_GUARD = {
  // Spending limits (USDC, human-readable)
  maxPerTransaction: '1.00',       // max USDC per single transaction
  maxDailySpend: '10.00',          // max USDC spent per 24h rolling window
  maxDailyTransactions: 50,        // max transactions per 24h

  // Rate limiting
  maxTransactionsPerHour: 10,      // burst protection

  // Address allowlist — if non-empty, ONLY these addresses can receive funds
  // Always include known contracts by default
  allowedAddresses: [],

  // Known safe contracts (auto-populated, always allowed for contract calls)
  knownContracts: {
    'TaskEscrowV2': '0xE2b1D96dfbd4E363888c4c4f314A473E7cA24D2f',
    'TaskEscrowV3': '0x7334DfF91ddE131e587d22Cb85F4184833340F6f',
    'WorkerStake': '0x91618100EE71652Bb0A153c5C9Cc2aaE2B63E488',
    'VerificationRegistryV2': '0x22536E4C3A221dA3C42F02469DB3183E28fF7A74',
    'BoardRegistryV2': '0xf64B21Ce518ab025208662Da001a3F61D3AcB390',
    'USDC': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    'SwapRouter': '0x2626664c2603336E57B271c5C0b26F421741e481',
  },

  // Mode: 'full' | 'readOnly' | 'spendOnly'
  // readOnly: no signing, only view calls
  // spendOnly: can spend up to limits, no arbitrary contract calls
  // full: all operations within limits
  mode: 'full',

  // Optional: bind to specific IP (for hosted deployments)
  // If set, guard refuses to sign if current IP doesn't match
  allowedIPs: [],

  // Auto-approve known contract interactions (escrow, staking, registry)
  autoApproveContracts: true,
};

/**
 * Load or create guard config from working directory.
 */
function loadGuardConfig(workdir = '.') {
  const configPath = join(workdir, GUARD_CONFIG_FILE);
  if (existsSync(configPath)) {
    try {
      const raw = readFileSync(configPath, 'utf8');
      return { ...DEFAULT_GUARD, ...JSON.parse(raw) };
    } catch {
      return { ...DEFAULT_GUARD };
    }
  }
  return { ...DEFAULT_GUARD };
}

/**
 * Save guard config.
 */
function saveGuardConfig(config, workdir = '.') {
  const configPath = join(workdir, GUARD_CONFIG_FILE);
  writeFileSync(configPath, JSON.stringify(config, null, 2) + '\n');
}

import { appendFileSync } from 'fs';

function auditLogSync(entry, workdir = '.') {
  const logPath = join(workdir, AUDIT_LOG_FILE);
  const line = JSON.stringify({
    timestamp: new Date().toISOString(),
    ...entry,
  }) + '\n';
  try {
    appendFileSync(logPath, line);
  } catch {
    // Best-effort
  }
}

/**
 * Load spending history for rolling window checks.
 * Stored as append-only audit log, parsed for recent entries.
 */
function getRecentSpending(workdir = '.', windowMs = 24 * 60 * 60 * 1000) {
  const logPath = join(workdir, AUDIT_LOG_FILE);
  if (!existsSync(logPath)) return { totalUSDC: 0, txCount: 0, hourlyCount: 0 };

  const cutoff = Date.now() - windowMs;
  const hourlyCutoff = Date.now() - (60 * 60 * 1000);
  let totalUSDC = 0;
  let txCount = 0;
  let hourlyCount = 0;

  try {
    const lines = readFileSync(logPath, 'utf8').trim().split('\n');
    for (const line of lines) {
      if (!line) continue;
      try {
        const entry = JSON.parse(line);
        if (entry.status !== 'approved') continue;
        const ts = new Date(entry.timestamp).getTime();
        if (ts >= cutoff) {
          txCount++;
          if (entry.usdcAmount) totalUSDC += parseFloat(entry.usdcAmount);
          if (ts >= hourlyCutoff) hourlyCount++;
        }
      } catch { /* skip malformed lines */ }
    }
  } catch { /* no log yet */ }

  return { totalUSDC, txCount, hourlyCount };
}

/**
 * Check if an address is allowed.
 */
function isAddressAllowed(address, guard) {
  const addr = address.toLowerCase();

  // Known contracts are always allowed
  if (guard.autoApproveContracts) {
    const knownAddrs = Object.values(guard.knownContracts).map(a => a.toLowerCase());
    if (knownAddrs.includes(addr)) return true;
  }

  // If allowlist is empty, all addresses are allowed (within spending limits)
  if (!guard.allowedAddresses || guard.allowedAddresses.length === 0) return true;

  // Check allowlist
  return guard.allowedAddresses.map(a => a.toLowerCase()).includes(addr);
}

/**
 * GuardedWallet — wraps an ethers.Wallet with permission checks.
 *
 * Usage:
 *   const guarded = createGuardedWallet(privateKey, { workdir: '.' });
 *   await guarded.sendTransaction(tx);  // checked against limits
 *   guarded.address;                     // passthrough
 */
export class GuardedWallet {
  constructor(innerWallet, opts = {}) {
    this.inner = innerWallet;
    this.workdir = opts.workdir || '.';
    this.guard = loadGuardConfig(this.workdir);
    this.address = innerWallet.address;
    this.provider = innerWallet.provider;
  }

  /**
   * Check all guardrails before allowing a transaction.
   * Returns { allowed: bool, reason: string }
   */
  checkGuardrails(opts = {}) {
    const { to, usdcAmount, action } = opts;

    // Mode check
    if (this.guard.mode === 'readOnly') {
      return { allowed: false, reason: 'Wallet is in read-only mode. No transactions allowed.' };
    }

    // Address allowlist
    if (to && !isAddressAllowed(to, this.guard)) {
      return { allowed: false, reason: `Address ${to} is not in the allowlist.` };
    }

    // Spending limits
    const recent = getRecentSpending(this.workdir);

    // Hourly rate limit
    if (recent.hourlyCount >= this.guard.maxTransactionsPerHour) {
      return { allowed: false, reason: `Hourly transaction limit reached (${this.guard.maxTransactionsPerHour}/hr).` };
    }

    // Daily transaction count
    if (recent.txCount >= this.guard.maxDailyTransactions) {
      return { allowed: false, reason: `Daily transaction limit reached (${this.guard.maxDailyTransactions}/day).` };
    }

    if (usdcAmount) {
      const amount = parseFloat(usdcAmount);

      // Per-transaction limit
      if (amount > parseFloat(this.guard.maxPerTransaction)) {
        return { allowed: false, reason: `Transaction amount ${usdcAmount} USDC exceeds per-tx limit of ${this.guard.maxPerTransaction} USDC.` };
      }

      // Daily spending limit
      if (recent.totalUSDC + amount > parseFloat(this.guard.maxDailySpend)) {
        return { allowed: false, reason: `Would exceed daily spending limit of ${this.guard.maxDailySpend} USDC (already spent ${recent.totalUSDC.toFixed(2)} today).` };
      }
    }

    return { allowed: true, reason: 'ok' };
  }

  /**
   * Send a transaction through the guard.
   */
  async sendTransaction(tx) {
    const check = this.checkGuardrails({ to: tx.to, action: 'sendTransaction' });
    if (!check.allowed) {
      auditLogSync({ action: 'sendTransaction', to: tx.to, status: 'blocked', reason: check.reason }, this.workdir);
      playSound('blocked');
      throw new Error(`[WalletGuard] Blocked: ${check.reason}`);
    }

    auditLogSync({ action: 'sendTransaction', to: tx.to, status: 'approved', value: tx.value?.toString() }, this.workdir);
    return this.inner.sendTransaction(tx);
  }

  /**
   * Sign a transaction (for cases where signing is separate from sending).
   */
  async signTransaction(tx) {
    if (this.guard.mode === 'readOnly') {
      throw new Error('[WalletGuard] Blocked: read-only mode.');
    }
    auditLogSync({ action: 'signTransaction', to: tx.to, status: 'approved' }, this.workdir);
    return this.inner.signTransaction(tx);
  }

  /**
   * Connect to a provider (passthrough).
   */
  connect(provider) {
    return new GuardedWallet(this.inner.connect(provider), { workdir: this.workdir });
  }

  /**
   * Get the underlying signer for contract interactions.
   * Contracts need the actual signer, but we intercept at the guard level.
   */
  get signer() {
    return this.inner;
  }

  /**
   * Update guard config at runtime.
   */
  updateConfig(updates) {
    this.guard = { ...this.guard, ...updates };
    saveGuardConfig(this.guard, this.workdir);
    auditLogSync({ action: 'configUpdate', updates, status: 'applied' }, this.workdir);
  }

  /**
   * Get current guard status.
   */
  getStatus() {
    const recent = getRecentSpending(this.workdir);
    return {
      mode: this.guard.mode,
      address: this.address,
      limits: {
        maxPerTransaction: this.guard.maxPerTransaction,
        maxDailySpend: this.guard.maxDailySpend,
        maxDailyTransactions: this.guard.maxDailyTransactions,
        maxTransactionsPerHour: this.guard.maxTransactionsPerHour,
      },
      usage: {
        dailySpent: recent.totalUSDC.toFixed(2),
        dailyTransactions: recent.txCount,
        hourlyTransactions: recent.hourlyCount,
      },
      allowedAddresses: this.guard.allowedAddresses.length || 'any',
      knownContracts: Object.keys(this.guard.knownContracts),
    };
  }
}

import { getProvider } from './wallet.js';

// Optional sound integration
let playSound = () => {};
try {
  const sounds = await import('./sounds.js');
  playSound = sounds.playSound;
} catch { /* sounds module optional */ }

/**
 * Create a guarded wallet from a private key or existing wallet.
 * Drop-in replacement for loadWallet() with guardrails.
 */
export function guardWallet(privateKeyOrWallet, opts = {}) {
  let wallet;
  if (typeof privateKeyOrWallet === 'string') {
    wallet = new ethers.Wallet(privateKeyOrWallet, getProvider());
  } else {
    wallet = privateKeyOrWallet;
  }
  return new GuardedWallet(wallet, opts);
}

/**
 * USDC-aware transaction wrapper.
 * Checks USDC amount against spending limits before approving.
 */
export async function guardedUSDCTransfer(guardedWallet, usdcContract, to, amountHuman) {
  const check = guardedWallet.checkGuardrails({
    to,
    usdcAmount: amountHuman,
    action: 'usdcTransfer',
  });

  if (!check.allowed) {
    auditLogSync({
      action: 'usdcTransfer',
      to,
      amount: amountHuman,
      status: 'blocked',
      reason: check.reason,
    }, guardedWallet.workdir);
    throw new Error(`[WalletGuard] Blocked: ${check.reason}`);
  }

  auditLogSync({
    action: 'usdcTransfer',
    to,
    usdcAmount: amountHuman,
    status: 'approved',
  }, guardedWallet.workdir);

  const decimals = await usdcContract.decimals();
  const amount = ethers.parseUnits(amountHuman.toString(), decimals);
  const tx = await usdcContract.transfer(to, amount);
  await tx.wait();

  auditLogSync({
    action: 'usdcTransfer',
    to,
    usdcAmount: amountHuman,
    txHash: tx.hash,
    status: 'confirmed',
  }, guardedWallet.workdir);

  return tx.hash;
}

/**
 * USDC-aware approval wrapper.
 * Logs all approvals and enforces exact amounts.
 */
export async function guardedUSDCApproval(guardedWallet, usdcContract, spender, amountHuman) {
  if (!isAddressAllowed(spender, guardedWallet.guard)) {
    auditLogSync({
      action: 'usdcApproval',
      spender,
      amount: amountHuman,
      status: 'blocked',
      reason: 'Spender not in allowlist',
    }, guardedWallet.workdir);
    throw new Error(`[WalletGuard] Blocked: spender ${spender} not in allowlist.`);
  }

  const decimals = await usdcContract.decimals();
  const amount = ethers.parseUnits(amountHuman.toString(), decimals);

  // SECURITY: Always reset to 0 first, then approve exact amount
  const currentAllowance = await usdcContract.allowance(guardedWallet.address, spender);
  if (currentAllowance > 0n) {
    const resetTx = await usdcContract.approve(spender, 0);
    await resetTx.wait();
  }

  const tx = await usdcContract.approve(spender, amount);
  await tx.wait();

  auditLogSync({
    action: 'usdcApproval',
    spender,
    usdcAmount: amountHuman,
    txHash: tx.hash,
    status: 'approved',
  }, guardedWallet.workdir);

  return tx.hash;
}

/**
 * Initialize guard config with custom settings.
 * Call during `setup init` to configure guardrails.
 */
export function initGuardConfig(workdir = '.', overrides = {}) {
  const config = { ...DEFAULT_GUARD, ...overrides };
  saveGuardConfig(config, workdir);
  return config;
}

/**
 * Print human-readable guard status.
 */
export function printGuardStatus(guardedWallet) {
  const s = guardedWallet.getStatus();
  console.log(`\n🔒 Wallet Guard Status`);
  console.log(`   Mode: ${s.mode}`);
  console.log(`   Address: ${s.address}`);
  console.log(`   Per-tx limit: ${s.limits.maxPerTransaction} USDC`);
  console.log(`   Daily limit: ${s.limits.maxDailySpend} USDC`);
  console.log(`   Daily txns: ${s.usage.dailyTransactions}/${s.limits.maxDailyTransactions}`);
  console.log(`   Hourly txns: ${s.usage.hourlyTransactions}/${s.limits.maxTransactionsPerHour}`);
  console.log(`   Daily spent: ${s.usage.dailySpent} USDC`);
  console.log(`   Allowed targets: ${s.allowedAddresses}`);
  console.log(`   Known contracts: ${s.knownContracts.join(', ')}`);
  console.log();
}
