#!/usr/bin/env node
/**
 * Signet Guardian CLI — Payment guard middleware
 *
 * Commands:
 * - signet-preflight: Check if a payment is allowed (ALLOW / DENY / CONFIRM_REQUIRED)
 * - signet-record: Append a completed payment to the ledger (idempotent)
 * - signet-report: Show spending for a period
 * - signet-policy: Show or edit policy.json
 */

import * as fs from 'fs';
import * as path from 'path';
import { spawnSync } from 'child_process';
import prompts from 'prompts';

// {baseDir}: OpenClaw may set OPENCLAW_BASE_DIR or OPENCLAW_SKILL_DIR
const SKILL_DIR =
  process.env.OPENCLAW_BASE_DIR ||
  process.env.OPENCLAW_SKILL_DIR ||
  path.join(process.env.HOME || '', '.openclaw/workspace/skills/signet-guardian');
const REF_DIR = path.join(SKILL_DIR, 'references');
const POLICY_PATH = path.join(REF_DIR, 'policy.json');
const LEDGER_PATH = path.join(REF_DIR, 'ledger.jsonl');
const LOCK_PATH = path.join(REF_DIR, '.ledger.lock');

/** OpenClaw config file path (dashboard/edit source of truth). */
function getOpenClawConfigPath(): string {
  if (process.env.OPENCLAW_CONFIG_PATH) return process.env.OPENCLAW_CONFIG_PATH;
  return path.join(process.env.HOME || '', '.openclaw', 'openclaw.json');
}

interface Policy {
  version?: number;
  paymentsEnabled: boolean;
  maxPerTransaction: number;
  maxPerMonth: number;
  currency: string;
  requireConfirmationAbove: number;
  blockedMerchants?: string[];
  allowedMerchants?: string[];
}

interface LedgerEntry {
  ts: string;
  amount: number;
  currency: string;
  payee: string;
  purpose: string;
  idempotencyKey?: string;
  callerSkill?: string;
  status: 'completed' | 'denied';
  reason?: string;
}

function defaultPolicy(): Policy {
  return {
    version: 1,
    paymentsEnabled: false,
    maxPerTransaction: 20,
    maxPerMonth: 500,
    currency: 'GBP',
    requireConfirmationAbove: 5,
    blockedMerchants: [],
    allowedMerchants: [],
  };
}

function ensureRefDir(): void {
  if (!fs.existsSync(REF_DIR)) {
    fs.mkdirSync(REF_DIR, { recursive: true });
  }
}

const LOCK_RETRIES = 50;
const LOCK_RETRY_MS = 100;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function withLock<T>(fn: () => T): Promise<T> {
  ensureRefDir();
  let fd: number | undefined;
  for (let i = 0; i < LOCK_RETRIES; i++) {
    try {
      fd = fs.openSync(LOCK_PATH, 'wx');
      break;
    } catch (e: unknown) {
      if ((e as NodeJS.ErrnoException).code !== 'EEXIST') throw e;
      if (i === LOCK_RETRIES - 1) throw new Error('Ledger lock timeout');
      await sleep(LOCK_RETRY_MS);
    }
  }
  try {
    return fn();
  } finally {
    if (fd !== undefined) {
      fs.closeSync(fd);
      fs.unlinkSync(LOCK_PATH);
    }
  }
}

/** Validate raw object to Policy; returns null if invalid. */
function validatePolicyRaw(raw: unknown): Policy | null {
  if (!raw || typeof raw !== 'object') return null;
  const r = raw as Record<string, unknown>;
  if (
    typeof r.paymentsEnabled !== 'boolean' ||
    typeof r.maxPerTransaction !== 'number' ||
    typeof r.maxPerMonth !== 'number'
  ) {
    return null;
  }
  const currency = typeof r.currency === 'string' && r.currency.trim() ? r.currency.trim() : 'GBP';
  const maxPerTransaction = Number(r.maxPerTransaction);
  const maxPerMonth = Number(r.maxPerMonth);
  const requireConfirmationAbove = Number(r.requireConfirmationAbove ?? 5);
  if (maxPerTransaction < 0 || maxPerMonth < 0 || requireConfirmationAbove < 0) return null;
  return {
    version: typeof r.version === 'number' ? r.version : undefined,
    paymentsEnabled: r.paymentsEnabled,
    maxPerTransaction,
    maxPerMonth,
    currency,
    requireConfirmationAbove,
    blockedMerchants: Array.isArray(r.blockedMerchants) ? r.blockedMerchants : [],
    allowedMerchants: Array.isArray(r.allowedMerchants) ? r.allowedMerchants : [],
  };
}

/** Load policy from references/policy.json only (for file-based ops). */
function loadPolicyFromFile(): Policy | null {
  if (!fs.existsSync(POLICY_PATH)) return null;
  try {
    return validatePolicyRaw(JSON.parse(fs.readFileSync(POLICY_PATH, 'utf-8')));
  } catch {
    return null;
  }
}

/** Load policy from OpenClaw config (signet.policy) if present. */
function loadPolicyFromConfig(): Policy | null {
  const configPath = getOpenClawConfigPath();
  if (!fs.existsSync(configPath)) return null;
  try {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    const raw = config?.signet?.policy;
    return validatePolicyRaw(raw) ?? null;
  } catch {
    return null;
  }
}

/** Source of truth: config first, then file. Default-deny if neither valid. */
function loadPolicyFromConfigOrFile(): Policy | null {
  const fromConfig = loadPolicyFromConfig();
  if (fromConfig) return fromConfig;
  return loadPolicyFromFile();
}

function getCurrentMonthKey(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
}

/** Read ledger as JSONL: one JSON object per line, newline-separated (never space). */
function readLedgerLines(): string[] {
  if (!fs.existsSync(LEDGER_PATH)) return [];
  return fs.readFileSync(LEDGER_PATH, 'utf-8').split('\n').filter(Boolean);
}

function getMonthSpent(currency: string): number {
  const monthKey = getCurrentMonthKey();
  const lines = readLedgerLines();
  return lines
    .map((line) => {
      try {
        const entry: LedgerEntry = JSON.parse(line);
        if (
          entry.ts?.startsWith(monthKey) &&
          entry.status === 'completed' &&
          typeof entry.amount === 'number' &&
          entry.currency === currency
        ) {
          return entry.amount;
        }
      } catch {}
      return 0;
    })
    .reduce((sum, a) => sum + a, 0);
}

/** Write one ledger entry. JSONL: one line per entry, newline-terminated (never space). */
function appendLedger(entry: LedgerEntry): void {
  ensureRefDir();
  fs.appendFileSync(LEDGER_PATH, JSON.stringify(entry) + '\n');
}

function hasIdempotencyKey(key: string): boolean {
  const lines = readLedgerLines();
  return lines.some((line) => {
    try {
      const entry: LedgerEntry = JSON.parse(line);
      return entry.idempotencyKey === key && entry.status === 'completed';
    } catch {
      return false;
    }
  });
}

function preflight(
  amount: number,
  currency: string,
  payee: string,
  purpose: string,
  idempotencyKey?: string,
  callerSkill?: string
): { result: 'ALLOW' | 'DENY' | 'CONFIRM_REQUIRED'; reason: string } {
  const audit = { callerSkill, idempotencyKey };
  const policy = loadPolicyFromConfigOrFile();
  if (!policy) {
    appendLedger({
      ts: new Date().toISOString(),
      amount,
      currency,
      payee,
      purpose,
      status: 'denied',
      reason: 'Policy missing or invalid',
      ...audit,
    });
    return { result: 'DENY', reason: 'Policy missing or invalid (default-deny)' };
  }

  if (!policy.paymentsEnabled) {
    appendLedger({
      ts: new Date().toISOString(),
      amount,
      currency,
      payee,
      purpose,
      status: 'denied',
      reason: 'Payments disabled',
      ...audit,
    });
    return { result: 'DENY', reason: 'Payments are disabled' };
  }

  if (currency !== policy.currency) {
    appendLedger({
      ts: new Date().toISOString(),
      amount,
      currency,
      payee,
      purpose,
      status: 'denied',
      reason: `Policy currency is ${policy.currency}; request must use ${policy.currency}`,
      ...audit,
    });
    return {
      result: 'DENY',
      reason: `Policy currency is ${policy.currency}; request must use ${policy.currency} for limits to apply.`,
    };
  }

  if (amount > policy.maxPerTransaction) {
    appendLedger({
      ts: new Date().toISOString(),
      amount,
      currency,
      payee,
      purpose,
      status: 'denied',
      reason: `Exceeds per-transaction limit (${policy.currency} ${policy.maxPerTransaction})`,
      ...audit,
    });
    return {
      result: 'DENY',
      reason: `Amount ${currency} ${amount} exceeds per-transaction limit (${policy.currency} ${policy.maxPerTransaction})`,
    };
  }

  const monthSpent = getMonthSpent(policy.currency);
  const totalAfter = monthSpent + amount;
  if (totalAfter > policy.maxPerMonth) {
    appendLedger({
      ts: new Date().toISOString(),
      amount,
      currency,
      payee,
      purpose,
      status: 'denied',
      reason: `Would exceed monthly limit (${policy.currency} ${policy.maxPerMonth})`,
      ...audit,
    });
    return {
      result: 'DENY',
      reason: `Would exceed monthly limit of ${policy.currency} ${policy.maxPerMonth} (already spent ${policy.currency} ${monthSpent.toFixed(2)} this month)`,
    };
  }

  if (policy.blockedMerchants?.length) {
    const payeeLower = payee.toLowerCase();
    const blocked = policy.blockedMerchants.find((m) => payeeLower.includes(m.toLowerCase()));
    if (blocked) {
      appendLedger({
        ts: new Date().toISOString(),
        amount,
        currency,
        payee,
        purpose,
        status: 'denied',
        reason: `Payee blocked: ${payee}`,
        ...audit,
      });
      return { result: 'DENY', reason: `Payee "${payee}" is in blocked list` };
    }
  }

  if (policy.allowedMerchants?.length) {
    const payeeLower = payee.toLowerCase();
    const allowed = policy.allowedMerchants.some((m) => payeeLower.includes(m.toLowerCase()));
    if (!allowed) {
      appendLedger({
        ts: new Date().toISOString(),
        amount,
        currency,
        payee,
        purpose,
        status: 'denied',
        reason: `Payee not in allowed list: ${payee}`,
        ...audit,
      });
      return { result: 'DENY', reason: `Payee "${payee}" is not in allowed list` };
    }
  }

  if (amount > policy.requireConfirmationAbove) {
    return {
      result: 'CONFIRM_REQUIRED',
      reason: `Amount ${currency} ${amount} is above confirmation threshold (${policy.currency} ${policy.requireConfirmationAbove}). User must confirm.`,
    };
  }

  return { result: 'ALLOW', reason: 'Within policy' };
}

async function record(
  amount: number,
  currency: string,
  payee: string,
  purpose: string,
  idempotencyKey?: string,
  callerSkill?: string
): Promise<{ ok: true } | { ok: false; error: string }> {
  return withLock(() => {
    const policy = loadPolicyFromConfigOrFile();
    if (!policy) return { ok: false, error: 'Policy missing or invalid' };
    if (currency !== policy.currency) {
      return { ok: false, error: `Policy currency is ${policy.currency}; request must use ${policy.currency}` };
    }
    const monthSpent = getMonthSpent(policy.currency);
    if (monthSpent + amount > policy.maxPerMonth) {
      return {
        ok: false,
        error: `Would exceed monthly limit of ${policy.currency} ${policy.maxPerMonth} (already ${policy.currency} ${monthSpent.toFixed(2)} this month)`,
      };
    }
    if (idempotencyKey && hasIdempotencyKey(idempotencyKey)) {
      return { ok: true }; // idempotent: already recorded
    }
    appendLedger({
      ts: new Date().toISOString(),
      amount,
      currency,
      payee,
      purpose,
      idempotencyKey,
      callerSkill,
      status: 'completed',
    });
    return { ok: true };
  });
}

function kebabToCamel(s: string): string {
  return s.replace(/-([a-z])/g, (_, c: string) => c.toUpperCase());
}

function parseArgs(): { command: string; args: Record<string, string | number | boolean> } {
  const argv = process.argv.slice(2);
  const command = argv[0] || '';
  const parsed: Record<string, string | number | boolean> = {};
  for (let i = 1; i < argv.length; i++) {
    const raw = argv[i];
    if (!raw?.startsWith('--')) continue;
    const key = kebabToCamel(raw.slice(2));
    if (!key) continue;
    const next = argv[i + 1];
    const isStandaloneFlag = next === undefined || next.startsWith('--');
    const value = isStandaloneFlag ? true : next;
    parsed[key] = value === true ? true : (typeof value === 'string' && !Number.isNaN(Number(value)) ? Number(value) : value);
    i += isStandaloneFlag ? 0 : 1;
  }
  return { command, args: parsed };
}

async function runPolicyWizard(): Promise<void> {
  ensureRefDir();
  const current = loadPolicyFromConfigOrFile() ?? defaultPolicy();

  const answers = await prompts(
    [
      {
        type: 'toggle',
        name: 'paymentsEnabled',
        message: 'Enable payments?',
        initial: current.paymentsEnabled,
        active: 'yes',
        inactive: 'no',
      },
      {
        type: 'number',
        name: 'maxPerTransaction',
        message: 'Max per transaction',
        initial: current.maxPerTransaction,
        validate: (v: number) => (v >= 0 ? true : 'Must be >= 0'),
      },
      {
        type: 'number',
        name: 'maxPerMonth',
        message: 'Max per month',
        initial: current.maxPerMonth,
        validate: (v: number) => (v >= 0 ? true : 'Must be >= 0'),
      },
      {
        type: 'text',
        name: 'currency',
        message: 'Currency (ISO code, e.g. GBP)',
        initial: current.currency,
        validate: (v: string) => (v.trim() ? true : 'Currency is required'),
      },
      {
        type: 'number',
        name: 'requireConfirmationAbove',
        message: 'Require confirmation above',
        initial: current.requireConfirmationAbove,
        validate: (v: number) => (v >= 0 ? true : 'Must be >= 0'),
      },
      {
        type: 'text',
        name: 'blockedMerchantsRaw',
        message: 'Blocked merchants (comma-separated, blank for none)',
        initial: (current.blockedMerchants ?? []).join(', '),
      },
      {
        type: 'text',
        name: 'allowedMerchantsRaw',
        message: 'Allowed merchants (comma-separated, blank = allow all)',
        initial: (current.allowedMerchants ?? []).join(', '),
      },
    ],
    {
      onCancel: () => {
        throw new Error('WIZARD_CANCELLED');
      },
    }
  );

  const toList = (raw: string): string[] =>
    String(raw || '')
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

  const next: Policy = {
    version: 1,
    paymentsEnabled: Boolean(answers.paymentsEnabled),
    maxPerTransaction: Number(answers.maxPerTransaction),
    maxPerMonth: Number(answers.maxPerMonth),
    currency: String(answers.currency || 'GBP').trim().toUpperCase(),
    requireConfirmationAbove: Number(answers.requireConfirmationAbove),
    blockedMerchants: toList(answers.blockedMerchantsRaw),
    allowedMerchants: toList(answers.allowedMerchantsRaw),
  };

  if (next.requireConfirmationAbove > next.maxPerTransaction) {
    console.log(
      `Warning: confirmation threshold (${next.requireConfirmationAbove}) is above maxPerTransaction (${next.maxPerTransaction}).`
    );
  }

  console.log('\nNew policy:');
  console.log(JSON.stringify(next, null, 2));

  const confirm = await prompts({
    type: 'confirm',
    name: 'save',
    message: 'Save this policy?',
    initial: true,
  });

  if (!confirm.save) {
    console.log('Cancelled. No changes saved.');
    return;
  }

  fs.writeFileSync(POLICY_PATH, JSON.stringify(next, null, 2) + '\n');
  console.log(`Policy updated: ${POLICY_PATH}`);
}

async function main(): Promise<void> {
  const { command, args } = parseArgs();

  if (command === 'signet-preflight') {
    const amount = Number(args.amount);
    if (Number.isNaN(amount) || amount <= 0) {
      console.log(JSON.stringify({ result: 'DENY', reason: 'Invalid or missing amount (must be > 0)' }));
      process.exit(1);
    }
    const currency = String(args.currency || 'GBP');
    const payee = String(args.payee || 'unknown');
    const purpose = String(args.purpose || '');
    const idempotencyKey = args.idempotencyKey != null ? String(args.idempotencyKey) : undefined;
    const callerSkill = args.callerSkill != null ? String(args.callerSkill) : undefined;
    const out = preflight(amount, currency, payee, purpose, idempotencyKey, callerSkill);
    console.log(JSON.stringify(out));
    process.exit(out.result === 'DENY' ? 1 : 0);
  }

  if (command === 'signet-record') {
    const amount = Number(args.amount);
    if (Number.isNaN(amount) || amount <= 0) {
      console.error('Invalid or missing amount (must be > 0)');
      process.exit(1);
    }
    const currency = String(args.currency || 'GBP');
    const payee = String(args.payee || 'unknown');
    const purpose = String(args.purpose || '');
    const idempotencyKey = args.idempotencyKey != null ? String(args.idempotencyKey) : undefined;
    const callerSkill = args.callerSkill != null ? String(args.callerSkill) : undefined;
    const result = await record(amount, currency, payee, purpose, idempotencyKey, callerSkill);
    if (!result.ok) {
      console.error(result.error);
      process.exit(1);
    }
    console.log('Recorded.');
    process.exit(0);
  }

  if (command === 'signet-report') {
    const period = (args.period as string) || 'month';
    const lines = readLedgerLines();
    if (lines.length === 0) {
      console.log(`No ledger entries yet. Use signet-record after payments.`);
      return;
    }
    const now = new Date();
    let cutoff: Date;
    if (period === 'today') {
      cutoff = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    } else if (period === 'month') {
      cutoff = new Date(now.getFullYear(), now.getMonth(), 1);
    } else {
      cutoff = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    }
    const entries = lines
      .map((line) => {
        try {
          return JSON.parse(line) as LedgerEntry;
        } catch {
          return null;
        }
      })
      .filter((e): e is LedgerEntry => e != null && new Date(e.ts) >= cutoff);

    const completed = entries.filter((e) => e.status === 'completed');
    const total = completed.reduce((sum, e) => sum + (typeof e.amount === 'number' ? e.amount : 0), 0);
    const currency = completed[0]?.currency || 'GBP';
    console.log(`\n📊 Signet Guardian — ${period}`);
    console.log(`Total spent: ${currency} ${total.toFixed(2)} (${completed.length} transactions)`);
    console.log(`Denials: ${entries.filter((e) => e.status === 'denied').length}`);
    console.log('\nRecent:');
    entries.slice(-15).forEach((e) => {
      const caller = e.callerSkill ? ` [${e.callerSkill}]` : '';
      console.log(`  ${e.ts} | ${e.status} | ${e.amount} ${e.currency} | ${e.payee}${caller} | ${e.reason || e.purpose || ''}`);
    });
    return;
  }

  if (command === 'signet-policy') {
    if (args.wizard === true) {
      await runPolicyWizard();
      return;
    }
    if (args.show === true) {
      const policy = loadPolicyFromConfigOrFile();
      if (!policy) {
        console.log('No policy found. Create references/policy.json (e.g. signet-policy --edit).');
        return;
      }
      console.log(JSON.stringify(policy, null, 2));
      return;
    }
    if (args.migrateFileToConfig === true) {
      const filePolicy = loadPolicyFromFile();
      if (!filePolicy) {
        console.error('No valid policy in references/policy.json. Nothing to migrate.');
        process.exit(1);
      }
      const configPath = getOpenClawConfigPath();
      let config: Record<string, unknown> = {};
      if (fs.existsSync(configPath)) {
        try {
          config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
        } catch (e) {
          console.error(`Could not read config at ${configPath}:`, e);
          process.exit(1);
        }
      }
      if (!config.signet || typeof config.signet !== 'object') config.signet = {};
      (config.signet as Record<string, unknown>).policy = {
        ...filePolicy,
        version: 1,
      };
      const dir = path.dirname(configPath);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(configPath, JSON.stringify(config, null, 2) + '\n');
      console.log(`Migrated policy to OpenClaw config: ${configPath}`);
      console.log('Dashboard and CLI will now use signet.policy from config. File is kept as backup.');
      return;
    }
    if (args.edit === true) {
      ensureRefDir();
      if (!fs.existsSync(POLICY_PATH)) {
        fs.writeFileSync(POLICY_PATH, JSON.stringify(defaultPolicy(), null, 2));
      }
      const editorEnv = process.env.EDITOR || 'nano';
      const parts = editorEnv.trim().split(/\s+/);
      const editorCmd = parts[0]!;
      const editorArgs = parts.length > 1 ? parts.slice(1) : [];
      const result = spawnSync(editorCmd, [...editorArgs, POLICY_PATH], {
        stdio: 'inherit',
        shell: false,
      });
      if (result.status !== 0) process.exit(result.status ?? 1);
      return;
    }
    console.log('Usage: signet-policy --show | --edit | --wizard | --migrate-file-to-config');
    return;
  }

  console.log('Commands: signet-preflight, signet-record, signet-report, signet-policy');
  process.exit(1);
}

main().catch((e) => {
  if (e instanceof Error && e.message === 'WIZARD_CANCELLED') {
    console.log('Cancelled. No changes saved.');
    process.exit(0);
  }
  console.error(e);
  process.exit(1);
});
