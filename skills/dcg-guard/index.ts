/**
 * DCG Guard — OpenClaw plugin (cross-platform: Windows + Unix)
 *
 * 1. Checks PowerShell/cmd/unix dangerous patterns locally (fast, no subprocess)
 * 2. Falls back to DCG binary for additional unix-style rules (if installed)
 * Zero noise on safe commands. Hard block on destructive ones.
 */

import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { platform, homedir } from "node:os";
import { join } from "node:path";

const IS_WIN = platform() === "win32";
const DCG_BIN =
  process.env.DCG_BIN ||
  (IS_WIN
    ? join(homedir(), ".local", "bin", "dcg.exe")
    : join(homedir(), ".local", "bin", "dcg"));

const SHELL_TOOLS = new Set(["exec", "bash"]);

// ============================================
// Built-in dangerous command patterns
// Works on ALL platforms, no binary needed
// ============================================

interface DangerRule {
  id: string;
  severity: "critical" | "high" | "medium";
  reason: string;
  test: (lower: string) => boolean;
}

const BUILTIN_RULES: DangerRule[] = [
  // === CRITICAL: Recursive deletion (cross-platform) ===
  { id: "fs:rm-rf", severity: "critical", reason: "Recursive forced deletion",
    test: (s) => s.includes("rm ") && s.includes("-r") && s.includes("-f") },
  { id: "fs:rm-rf-combined", severity: "critical", reason: "Recursive forced deletion",
    test: (s) => /rm\s+-rf\b/.test(s) },
  { id: "win.fs:remove-item-recurse", severity: "critical", reason: "Recursive deletion via Remove-Item",
    test: (s) => s.includes("remove-item") && s.includes("-recurse") },
  { id: "win.fs:del-recursive", severity: "critical", reason: "Recursive deletion via del /s",
    test: (s) => s.includes("del ") && s.includes("/s") },
  { id: "win.fs:rd-recursive", severity: "critical", reason: "Recursive directory removal",
    test: (s) => (s.includes("rd /s") || s.includes("rmdir /s")) },

  // === CRITICAL: Disk operations ===
  { id: "win.disk:format", severity: "critical", reason: "Disk format/wipe operation",
    test: (s) => s.includes("format-volume") || s.includes("clear-disk") },
  { id: "win.disk:format-drive", severity: "critical", reason: "Drive format via cmd",
    test: (s) => /format\s+[a-z]:/.test(s) },

  // === CRITICAL: System file tampering ===
  { id: "win.fs:remove-system", severity: "critical", reason: "Deleting system files",
    test: (s) => s.includes("remove-item") &&
      (s.includes("\\windows") || s.includes("\\system32") || s.includes("\\program files")) },
  { id: "fs:remove-sensitive", severity: "critical", reason: "Deleting sensitive config",
    test: (s) => s.includes("remove-item") &&
      (s.includes(".ssh") || s.includes(".openclaw") || s.includes(".claude")) },
  { id: "unix.fs:rm-home", severity: "critical", reason: "Deleting home directory contents",
    test: (s) => /rm\s+-rf\s+[~\/]/.test(s) },

  // === HIGH: Git destructive ===
  { id: "git:push-force", severity: "high", reason: "Force push overwrites remote history",
    test: (s) => s.includes("git push") && (s.includes("--force") || /\s-f\b/.test(s)) },
  { id: "git:reset-hard", severity: "high", reason: "Hard reset discards uncommitted changes",
    test: (s) => s.includes("git reset") && s.includes("--hard") },
  { id: "git:clean-f", severity: "high", reason: "git clean removes untracked files permanently",
    test: (s) => s.includes("git clean") && s.includes("-f") },
  { id: "git:branch-D", severity: "high", reason: "Force delete branch",
    test: (s) => /git\s+branch\s+-D\b/.test(s) },
  { id: "git:checkout-all", severity: "high", reason: "Checkout all files discards changes",
    test: (s) => s.includes("git checkout") && s.includes("-- .") },
  { id: "git:stash-drop", severity: "high", reason: "Dropping/clearing stash permanently",
    test: (s) => s.includes("git stash") && (s.includes("drop") || s.includes("clear")) },

  // === HIGH: Windows registry ===
  { id: "win.reg:remove-hklm", severity: "high", reason: "Removing HKLM registry keys",
    test: (s) => (s.includes("remove-itemproperty") || s.includes("reg delete")) && s.includes("hklm") },

  // === HIGH: Service/process ===
  { id: "win.proc:kill-svchost", severity: "critical", reason: "Killing svchost",
    test: (s) => s.includes("taskkill") && s.includes("/f") && s.includes("svchost") },

  // === HIGH: Firewall ===
  { id: "win.fw:disable", severity: "high", reason: "Disabling firewall",
    test: (s) => (s.includes("set-netfirewallprofile") && s.includes("false")) ||
      (s.includes("netsh") && s.includes("firewall") && s.includes("off")) },

  // === HIGH: Wildcard deletion ===
  { id: "win.fs:wildcard-recurse", severity: "high", reason: "Recursive wildcard deletion",
    test: (s) => s.includes("remove-item") && s.includes("*") && s.includes("-recurse") },

  // === MEDIUM: Environment corruption ===
  { id: "win.env:set-machine", severity: "medium", reason: "Modifying machine-level environment variables",
    test: (s) => (s.includes("setenvironmentvariable") && s.includes("machine")) ||
      (s.includes("setx") && s.includes("/m")) },
];

// Paths that are always safe to delete (temp, cache, test dirs)
const SAFE_PATH_PATTERNS = [
  /[/\\]temp[/\\]/i,
  /[/\\]tmp[/\\]/i,
  /[/\\]cache[/\\]/i,
  /[/\\]__pycache__[/\\]/i,
  /[/\\]node_modules[/\\]/i,
  /[/\\]\.cache[/\\]/i,
  /[/\\]AppData[/\\]Local[/\\]Temp[/\\]/i,
  /tmp_dcg_test/i,
  /\/tmp\//i,
];

function isSafePath(command: string): boolean {
  return SAFE_PATH_PATTERNS.some((p) => p.test(command));
}

/** Check command against built-in rules. Returns match or null. */
function evaluateBuiltin(
  command: string
): { id: string; severity: string; reason: string } | null {
  if (isSafePath(command)) return null;
  const lower = command.toLowerCase();
  for (const rule of BUILTIN_RULES) {
    if (rule.test(lower)) {
      return { id: rule.id, severity: rule.severity, reason: rule.reason };
    }
  }
  return null;
}

// ============================================
// DCG binary fallback (optional, unix)
// ============================================

function dcgEvaluate(command: string): string | null {
  if (!existsSync(DCG_BIN)) return null; // No DCG binary = skip silently

  try {
    const input = JSON.stringify({
      tool_name: "Bash",
      tool_input: { command },
    });

    const result = execFileSync(DCG_BIN, [], {
      input,
      encoding: "utf-8",
      timeout: 5000,
      stdio: ["pipe", "pipe", "pipe"],
    });

    const trimmed = result.trim();
    if (!trimmed) return null;

    const jsonMatch = trimmed.match(/\{[\s\S]*"hookSpecificOutput"[\s\S]*\}$/);
    if (!jsonMatch) return null;

    const parsed = JSON.parse(jsonMatch[0]);
    const hook = parsed.hookSpecificOutput;
    if (hook?.permissionDecision === "deny") {
      const rule = hook.ruleId || "unknown";
      const severity = hook.severity || "unknown";
      return `[${severity}] ${rule}: ${hook.permissionDecisionReason?.split("\n")[0] || "Dangerous command blocked"}`;
    }
    return null;
  } catch {
    return null; // fail-open
  }
}

// ============================================
// Plugin registration
// ============================================

interface PluginApi {
  on?(hookName: string, handler: (...args: unknown[]) => void): void;
}

interface BeforeToolCallEvent {
  toolName: string;
  params: Record<string, unknown>;
}

interface BeforeToolCallResult {
  block?: boolean;
  blockReason?: string;
}

function extractCommand(
  params: Record<string, unknown>
): string | null {
  if (typeof params.command === "string") return params.command;
  if (typeof params.cmd === "string") return params.cmd;
  return null;
}

export default {
  id: "dcg-guard",
  name: "DCG Guard",

  register(api: PluginApi): void {
    if (!api.on) {
      console.warn("[dcg-guard] api.on not available, cannot register before_tool_call hook");
      return;
    }

    api.on(
      "before_tool_call",
      (event: BeforeToolCallEvent): BeforeToolCallResult | void => {
        const { toolName, params } = event;

        if (!SHELL_TOOLS.has(toolName.toLowerCase())) return;

        const command = extractCommand(params);
        if (!command) return;

        // 1. Built-in pattern check (cross-platform, no subprocess, <1ms)
        const builtinResult = evaluateBuiltin(command);
        if (builtinResult) {
          console.warn(
            `[dcg-guard] BLOCKED [${builtinResult.severity}]: ${command}\n  Rule: ${builtinResult.id}\n  Reason: ${builtinResult.reason}`
          );
          return {
            block: true,
            blockReason: `🛡️ DCG Guard [${builtinResult.severity}] ${builtinResult.id}\n\n${builtinResult.reason}\n\nCommand: ${command}\n\nThis command was blocked because it is destructive or irreversible. Ask the user for explicit permission before retrying.`,
          };
        }

        // 2. DCG binary fallback (unix, ~27ms, optional)
        const dcgResult = dcgEvaluate(command);
        if (dcgResult) {
          console.warn(`[dcg-guard] BLOCKED (DCG): ${command}\n  ${dcgResult}`);
          return {
            block: true,
            blockReason: `🛡️ DCG Guard: ${dcgResult}\n\nCommand: ${command}\n\nThis command was blocked because it is destructive or irreversible. Ask the user for explicit permission before retrying.`,
          };
        }

        // Safe — pass through silently
      }
    );

    const dcgStatus = existsSync(DCG_BIN) ? `DCG binary: ${DCG_BIN}` : "DCG binary not found (built-in rules only)";
    console.log(
      `[dcg-guard] Registered: ${BUILTIN_RULES.length} built-in rules + ${dcgStatus}`
    );
  },
};
