/**
 * DECIDE phase: Pure, deterministic policy evaluation.
 *
 * evaluate() is a pure function: (ActionIntent, PolicyFile, timestamp) → Verdict.
 * No LLM invocation, no I/O, no side effects. This is what makes authority
 * separation structural rather than behavioral.
 */

import os from "node:os";
import type { ActionIntent } from "./intent.js";
import { computeHash, canonicalize } from "./intent.js";
import type { PolicyFile, PolicyRule, SensitiveDataRule } from "./yaml-parse.js";

// ── Types ────────────────────────────────────────────────────────────

export type VerdictDecision = "approve" | "deny" | "escalate";

export interface Verdict {
  decision: VerdictDecision;
  intent_hash: string;
  rule_matched: string;
  reason: string;
  timestamp: string;
  verdict_hash: string;
}

// ── Hash computation ─────────────────────────────────────────────────

export function computeVerdictHash(
  decision: string,
  intentHash: string,
  rule: string,
  timestamp: string,
): string {
  return computeHash(canonicalize({ decision, intent_hash: intentHash, rule, timestamp }));
}

// ── Glob matching ────────────────────────────────────────────────────

/**
 * Expand ~ to home directory in patterns and paths.
 */
function expandTilde(p: string): string {
  if (p.startsWith("~/") || p === "~") {
    return os.homedir().replace(/\\/g, "/") + p.slice(1);
  }
  return p;
}

/**
 * Normalize to forward slashes for cross-platform matching.
 */
function normalize(p: string): string {
  return p.replace(/\\/g, "/");
}

/**
 * Expand brace patterns: "{a,b,c}" → ["a", "b", "c"].
 * Returns null if no braces found.
 */
function expandBraces(pattern: string): string[] | null {
  const start = pattern.indexOf("{");
  if (start === -1) return null;
  const end = pattern.indexOf("}", start);
  if (end === -1) return null;

  const prefix = pattern.slice(0, start);
  const suffix = pattern.slice(end + 1);
  const alternatives = pattern.slice(start + 1, end).split(",");

  return alternatives.map((alt) => prefix + alt.trim() + suffix);
}

/**
 * Match a path against a glob pattern.
 * Uses path.matchesGlob (Node 22+) with tilde expansion and brace handling.
 */
export function matchGlob(target: string, pattern: string): boolean {
  const normTarget = normalize(expandTilde(target));
  const normPattern = normalize(expandTilde(pattern));

  // Handle negation: "!pattern" means "does NOT match pattern"
  if (normPattern.startsWith("!")) {
    return !matchGlobInner(normTarget, normPattern.slice(1));
  }

  return matchGlobInner(normTarget, normPattern);
}

/**
 * Convert a glob pattern to a RegExp.
 * Handles *, **, ?, and dotfiles (no special dotfile treatment).
 */
function globToRegex(pattern: string): RegExp {
  let re = "^";
  let i = 0;
  while (i < pattern.length) {
    const ch = pattern[i]!;
    if (ch === "*") {
      if (pattern[i + 1] === "*") {
        // ** matches everything including /
        if (pattern[i + 2] === "/") {
          re += "(?:.*/)?";
          i += 3;
        } else {
          re += ".*";
          i += 2;
        }
      } else {
        // * matches everything except /
        re += "[^/]*";
        i++;
      }
    } else if (ch === "?") {
      re += "[^/]";
      i++;
    } else if (".+^${}()|[]\\".includes(ch)) {
      re += "\\" + ch;
      i++;
    } else {
      re += ch;
      i++;
    }
  }
  re += "$";
  return new RegExp(re);
}

function matchGlobInner(target: string, pattern: string): boolean {
  // Try brace expansion
  const expanded = expandBraces(pattern);
  if (expanded !== null) {
    return expanded.some((p) => matchGlobInner(target, p));
  }

  try {
    return globToRegex(pattern).test(target);
  } catch {
    return false;
  }
}

// ── Rule matching ────────────────────────────────────────────────────

/**
 * Check if an ActionIntent matches a single policy rule.
 */
export function matchRule(intent: ActionIntent, rule: PolicyRule): boolean {
  const match = rule.match;

  // action_type: exact match (string) or any-of match (string[])
  if (match.action_type !== undefined) {
    if (Array.isArray(match.action_type)) {
      if (!match.action_type.includes(intent.action.type)) return false;
    } else {
      if (match.action_type !== intent.action.type) return false;
    }
  }

  // target_pattern: glob against action target
  if (match.target_pattern !== undefined) {
    if (!matchGlob(intent.action.target, match.target_pattern)) return false;
  }

  // tool_pattern: glob against "skill:tool" or just "tool"
  if (match.tool_pattern !== undefined) {
    const toolId = `${intent.source.skill}.${intent.source.tool}`;
    // Match against both the combined id and just the tool name
    if (!matchGlob(toolId, match.tool_pattern) && !matchGlob(intent.source.tool, match.tool_pattern)) {
      return false;
    }
  }

  // skill_pattern: glob against skill identifier
  if (match.skill_pattern !== undefined) {
    if (!matchGlob(intent.source.skill, match.skill_pattern)) return false;
  }

  // data_scope: array intersection (at least one common element)
  if (match.data_scope !== undefined && match.data_scope.length > 0) {
    const intentScopes = new Set(intent.action.data_scope);
    const hasIntersection = match.data_scope.some((s) => intentScopes.has(s));
    if (!hasIntersection) return false;
  }

  return true;
}

/**
 * Check if intent target matches any sensitive data pattern.
 */
export function checkSensitiveData(
  intent: ActionIntent,
  rules: SensitiveDataRule[],
): SensitiveDataRule | null {
  for (const rule of rules) {
    for (const pattern of rule.patterns) {
      if (matchGlob(intent.action.target, pattern)) {
        return rule;
      }
    }
    // Also check data_scope overlap
    const intentScopes = new Set(intent.action.data_scope);
    if (intentScopes.has(rule.category)) {
      return rule;
    }
  }
  return null;
}

// ── Core DECIDE function ─────────────────────────────────────────────

/**
 * Pure, deterministic policy evaluation.
 *
 * @param intent - The ActionIntent to evaluate
 * @param policy - The active PolicyFile
 * @param now    - ISO 8601 timestamp (injected for testable determinism)
 * @returns Verdict with decision, matched rule, and hash binding
 */
export function evaluate(
  intent: ActionIntent,
  policy: PolicyFile,
  now: string,
): Verdict {
  // Check sensitive data rules first (these override regular rules)
  const sensitiveMatch = checkSensitiveData(intent, policy.sensitive_data);
  if (sensitiveMatch !== null) {
    const decision = sensitiveMatch.action;
    const rule = `__sensitive_data__:${sensitiveMatch.category}`;
    return {
      decision,
      intent_hash: intent.intent_hash,
      rule_matched: rule,
      reason: `Sensitive data category '${sensitiveMatch.category}' detected`,
      timestamp: now,
      verdict_hash: computeVerdictHash(decision, intent.intent_hash, rule, now),
    };
  }

  // Evaluate rules in order; first match wins
  for (const rule of policy.rules) {
    if (matchRule(intent, rule)) {
      return {
        decision: rule.verdict,
        intent_hash: intent.intent_hash,
        rule_matched: rule.name,
        reason: rule.reason ?? `Matched rule: ${rule.name}`,
        timestamp: now,
        verdict_hash: computeVerdictHash(rule.verdict, intent.intent_hash, rule.name, now),
      };
    }
  }

  // No rule matched: apply default verdict (fail-closed = deny)
  const rule = "__default__";
  return {
    decision: policy.default_verdict,
    intent_hash: intent.intent_hash,
    rule_matched: rule,
    reason: "No matching rule; default policy applied",
    timestamp: now,
    verdict_hash: computeVerdictHash(policy.default_verdict, intent.intent_hash, rule, now),
  };
}
