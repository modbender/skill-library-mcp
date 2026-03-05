/**
 * governance-guard CLI orchestrator.
 *
 * Commands:
 *   propose <json>                     Create an ActionIntent from raw JSON
 *   decide <intent-json> [--policy p]  Evaluate intent against policy
 *   promote <intent-json> <verdict-json>  Check if action should proceed
 *   pipeline <json> [--policy p]       Full PROPOSE → DECIDE → PROMOTE
 *   resolve-escalation <id> <approve|deny>  Resolve pending escalation
 *   audit [--last N]                   View recent witness records
 *   verify                             Verify witness chain integrity
 */

import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { homedir } from "node:os";
import { createIntent, validateIntent } from "./intent.js";
import type { ActionIntent, CreateIntentParams } from "./intent.js";
import { evaluate, computeVerdictHash } from "./policy-engine.js";
import type { Verdict } from "./policy-engine.js";
import { parsePolicyFile } from "./yaml-parse.js";
import type { PolicyFile } from "./yaml-parse.js";
import { openWitnessLog } from "./witness.js";
import type { ExecutionStatus } from "./witness.js";

// ── Configuration ────────────────────────────────────────────────────

export interface GovernanceConfig {
  policyPath: string;
  witnessPath: string;
  maxVerdictAge: number;   // seconds
  escalationTimeout: number; // seconds
}

const DEFAULT_GOV_DIR = join(homedir(), ".openclaw", "governance");
const DEFAULT_POLICY_PATH = join(DEFAULT_GOV_DIR, "policy.yaml");
const DEFAULT_WITNESS_PATH = join(DEFAULT_GOV_DIR, "witness.jsonl");
const DEFAULT_MAX_VERDICT_AGE = 30;
const DEFAULT_ESCALATION_TIMEOUT = 300;

function defaultConfig(): GovernanceConfig {
  return {
    policyPath: DEFAULT_POLICY_PATH,
    witnessPath: DEFAULT_WITNESS_PATH,
    maxVerdictAge: DEFAULT_MAX_VERDICT_AGE,
    escalationTimeout: DEFAULT_ESCALATION_TIMEOUT,
  };
}

// ── Policy loading (fail-closed) ─────────────────────────────────────

async function loadPolicy(policyPath: string): Promise<PolicyFile> {
  const content = await readFile(policyPath, "utf8");
  return parsePolicyFile(content);
}

function failClosedPolicy(): PolicyFile {
  return {
    version: "0.1",
    default_verdict: "deny",
    rules: [],
    sensitive_data: [],
  };
}

// ── Verdict freshness ────────────────────────────────────────────────

function isVerdictFresh(verdict: Verdict, maxAge: number): boolean {
  const verdictTime = new Date(verdict.timestamp).getTime();
  const now = Date.now();
  return (now - verdictTime) / 1000 <= maxAge;
}

// ── Pipeline functions ───────────────────────────────────────────────

export function propose(raw: unknown): ActionIntent {
  // If raw is already a full ActionIntent, validate and return
  if (typeof raw === "object" && raw !== null && "intent_hash" in raw) {
    const result = validateIntent(raw);
    if (result.valid) return result.intent;
    throw new Error(`Invalid ActionIntent: ${result.errors.map((e) => `${e.field}: ${e.message}`).join("; ")}`);
  }

  // Otherwise, create from params
  const params = raw as Record<string, unknown>;
  return createIntent({
    skill: String(params["skill"] ?? ""),
    tool: String(params["tool"] ?? ""),
    model: String(params["model"] ?? ""),
    actionType: String(params["actionType"] ?? params["action_type"] ?? "") as CreateIntentParams["actionType"],
    target: String(params["target"] ?? ""),
    parameters: (params["parameters"] ?? {}) as Record<string, unknown>,
    dataScope: Array.isArray(params["dataScope"] ?? params["data_scope"])
      ? (params["dataScope"] ?? params["data_scope"]) as string[]
      : [],
    conversationId: String(params["conversationId"] ?? params["conversation_id"] ?? ""),
    messageId: String(params["messageId"] ?? params["message_id"] ?? ""),
    userInstruction: String(params["userInstruction"] ?? params["user_instruction"] ?? ""),
  });
}

export async function decide(
  intent: ActionIntent,
  config: GovernanceConfig,
): Promise<Verdict> {
  let policy: PolicyFile;
  try {
    policy = await loadPolicy(config.policyPath);
  } catch {
    // Fail-closed: if policy can't be loaded, deny everything
    policy = failClosedPolicy();
  }

  const now = new Date().toISOString();

  try {
    return evaluate(intent, policy, now);
  } catch {
    // Fail-closed: any error in evaluation → deny
    const rule = "__error__";
    return {
      decision: "deny",
      intent_hash: intent.intent_hash,
      rule_matched: rule,
      reason: "Internal error during policy evaluation; fail-closed deny",
      timestamp: now,
      verdict_hash: computeVerdictHash("deny", intent.intent_hash, rule, now),
    };
  }
}

export function promote(
  intent: ActionIntent,
  verdict: Verdict,
  maxVerdictAge: number,
): boolean {
  const authorized = verdict.decision === "approve";
  const hashMatch = verdict.intent_hash === intent.intent_hash;
  const notExpired = isVerdictFresh(verdict, maxVerdictAge);
  return authorized && hashMatch && notExpired;
}

export async function pipeline(
  raw: unknown,
  config: GovernanceConfig,
): Promise<{ intent: ActionIntent; verdict: Verdict; promoted: boolean; record: import("./witness.js").WitnessRecord }> {
  // PROPOSE
  const intent = propose(raw);

  // DECIDE
  const verdict = await decide(intent, config);

  // PROMOTE
  const promoted = promote(intent, verdict, config.maxVerdictAge);

  // Determine execution status
  let status: ExecutionStatus;
  if (verdict.decision === "escalate") {
    status = "escalated";
  } else if (promoted) {
    status = "executed";
  } else {
    status = "blocked";
  }

  // WITNESS
  const log = await openWitnessLog(config.witnessPath);
  const record = await log.append(intent, verdict, status);

  return { intent, verdict, promoted, record };
}

export async function resolveEscalation(
  intentId: string,
  decision: "approve" | "deny",
  config: GovernanceConfig,
): Promise<import("./witness.js").WitnessRecord> {
  const log = await openWitnessLog(config.witnessPath);
  const existing = log.getByIntentId(intentId);

  if (existing === null) {
    throw new Error(`No witness record found for intent ${intentId}`);
  }
  if (existing.execution_result.status !== "escalated") {
    throw new Error(`Intent ${intentId} is not in escalated state (status: ${existing.execution_result.status})`);
  }

  // Check escalation timeout
  const escalatedAt = new Date(existing.execution_result.timestamp).getTime();
  const elapsed = (Date.now() - escalatedAt) / 1000;
  if (elapsed > config.escalationTimeout) {
    const status: ExecutionStatus = "user_denied";
    return log.append(existing.intent, existing.verdict, status);
  }

  const status: ExecutionStatus = decision === "approve" ? "user_approved" : "user_denied";
  return log.append(existing.intent, existing.verdict, status);
}

export async function audit(
  config: GovernanceConfig,
  last?: number,
): Promise<import("./witness.js").WitnessRecord[]> {
  const log = await openWitnessLog(config.witnessPath);
  return last !== undefined ? log.getLast(last) : log.getLast(50);
}

export async function verify(
  config: GovernanceConfig,
): Promise<{ valid: boolean; brokenAt?: number; reason?: string; totalRecords: number }> {
  const log = await openWitnessLog(config.witnessPath);
  const result = log.verifyChain();
  return { ...result, totalRecords: log.getSequence() };
}

// ── CLI ──────────────────────────────────────────────────────────────

function parseArgs(argv: string[]): { command: string; args: string[]; flags: Record<string, string> } {
  const args: string[] = [];
  const flags: Record<string, string> = {};
  let command = "";

  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i]!;
    if (!command && !arg.startsWith("-")) {
      command = arg;
    } else if (arg.startsWith("--")) {
      const eqIdx = arg.indexOf("=");
      if (eqIdx !== -1) {
        flags[arg.slice(2, eqIdx)] = arg.slice(eqIdx + 1);
      } else if (i + 1 < argv.length && !argv[i + 1]!.startsWith("-")) {
        flags[arg.slice(2)] = argv[++i]!;
      } else {
        flags[arg.slice(2)] = "true";
      }
    } else {
      args.push(arg);
    }
  }

  return { command, args, flags };
}

function output(data: unknown): void {
  console.log(JSON.stringify(data, null, 2));
}

async function main(): Promise<void> {
  const { command, args, flags } = parseArgs(process.argv);
  const config = defaultConfig();

  if (flags["policy"]) config.policyPath = flags["policy"];
  if (flags["witness"]) config.witnessPath = flags["witness"];

  try {
    switch (command) {
      case "propose": {
        if (args.length < 1) {
          console.error("Usage: governance propose <json>");
          process.exit(1);
        }
        const raw = JSON.parse(args[0]!);
        const intent = propose(raw);
        output(intent);
        break;
      }

      case "decide": {
        if (args.length < 1) {
          console.error("Usage: governance decide <intent-json> [--policy path]");
          process.exit(1);
        }
        const intent = JSON.parse(args[0]!) as ActionIntent;
        const verdict = await decide(intent, config);
        output(verdict);
        break;
      }

      case "promote": {
        if (args.length < 2) {
          console.error("Usage: governance promote <intent-json> <verdict-json>");
          process.exit(1);
        }
        const intent = JSON.parse(args[0]!) as ActionIntent;
        const verdict = JSON.parse(args[1]!) as Verdict;
        const result = promote(intent, verdict, config.maxVerdictAge);
        output({ promoted: result });
        break;
      }

      case "pipeline": {
        if (args.length < 1) {
          console.error("Usage: governance pipeline <json> [--policy path]");
          process.exit(1);
        }
        const raw = JSON.parse(args[0]!);
        const result = await pipeline(raw, config);
        output({
          governance: result.verdict.decision === "approve" ? "approved" : result.verdict.decision,
          action: `${result.intent.action.type}:${result.intent.action.target}`,
          rule: result.verdict.rule_matched,
          reason: result.verdict.reason,
          promoted: result.promoted,
          intent_id: result.intent.id,
          witness_sequence: result.record.sequence,
        });
        break;
      }

      case "resolve-escalation": {
        if (args.length < 2) {
          console.error("Usage: governance resolve-escalation <intent-id> <approve|deny>");
          process.exit(1);
        }
        const decision = args[1] as "approve" | "deny";
        if (decision !== "approve" && decision !== "deny") {
          console.error("Decision must be 'approve' or 'deny'");
          process.exit(1);
        }
        const record = await resolveEscalation(args[0]!, decision, config);
        output({
          governance: decision === "approve" ? "user_approved" : "user_denied",
          intent_id: args[0],
          witness_sequence: record.sequence,
        });
        break;
      }

      case "audit": {
        const last = flags["last"] ? parseInt(flags["last"], 10) : undefined;
        const records = await audit(config, last);
        for (const record of records) {
          const r = record;
          console.log(
            `[${r.sequence}] ${r.execution_result.status.toUpperCase()} ` +
            `${r.intent.action.type}:${r.intent.action.target} ` +
            `(${r.verdict.rule_matched}) — ${r.verdict.reason}`
          );
        }
        break;
      }

      case "verify": {
        const result = await verify(config);
        if (result.valid) {
          console.log(`Witness chain valid. ${result.totalRecords} records verified.`);
        } else {
          console.error(`Witness chain BROKEN at record ${result.brokenAt}: ${result.reason}`);
          process.exit(1);
        }
        break;
      }

      case "--help":
      case "help":
      case "": {
        console.log(`governance-guard v0.1.0 — Structural authority separation

Commands:
  propose <json>                        Create an ActionIntent
  decide <intent-json> [--policy p]     Evaluate against policy
  promote <intent-json> <verdict-json>  Check promotion eligibility
  pipeline <json> [--policy p]          Full PROPOSE → DECIDE → PROMOTE
  resolve-escalation <id> <approve|deny>  Resolve user escalation
  audit [--last N]                      View recent witness records
  verify                                Verify witness chain integrity

Options:
  --policy <path>    Path to policy YAML file
  --witness <path>   Path to witness JSONL file`);
        break;
      }

      default:
        console.error(`Unknown command: ${command}. Run with --help for usage.`);
        process.exit(1);
    }
  } catch (err) {
    console.error(`Error: ${err instanceof Error ? err.message : String(err)}`);
    process.exit(1);
  }
}

// Run CLI if executed directly
const isMain = process.argv[1]?.endsWith("governance.ts") || process.argv[1]?.endsWith("governance.js");
if (isMain) {
  main();
}
