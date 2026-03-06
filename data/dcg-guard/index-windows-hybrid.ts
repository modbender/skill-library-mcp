/**
 * DCG Guard — OpenClaw plugin (Windows + Unix hybrid)
 * 
 * 1. Checks PowerShell/cmd dangerous patterns locally (fast, no subprocess)
 * 2. Falls back to DCG binary for unix-style commands
 * Zero noise on safe commands. Hard block on destructive ones.
 */

import { execSync } from "node:child_process";

const DCG_BIN = String.raw`C:\Users\stare\.local\bin\dcg.exe`;
const SHELL_TOOLS = new Set(["exec", "bash"]);

// ============================================
// PowerShell / CMD dangerous patterns
// ============================================
interface DangerRule {
  pattern: RegExp;
  id: string;
  severity: "critical" | "high" | "medium";
  reason: string;
}

const WINDOWS_DANGER_RULES: DangerRule[] = [
  // === CRITICAL: Recursive deletion ===
  { pattern: /Remove-Item\s+.*-Recurse/i, id: "win.fs:remove-item-recurse", severity: "critical", reason: "Recursive deletion via Remove-Item" },
  { pattern: /rm\s+.*-r/i, id: "win.fs:rm-recursive", severity: "critical", reason: "Recursive deletion via rm alias" },
  { pattern: /del\s+\/s/i, id: "win.fs:del-recursive", severity: "critical", reason: "Recursive deletion via del /s" },
  { pattern: /rd\s+\/s/i, id: "win.fs:rd-recursive", severity: "critical", reason: "Recursive directory removal via rd /s" },
  { pattern: /rmdir\s+\/s/i, id: "win.fs:rmdir-recursive", severity: "critical", reason: "Recursive directory removal via rmdir /s" },
  { pattern: /rm\s+-rf\b/i, id: "unix.fs:rm-rf", severity: "critical", reason: "Unix-style rm -rf" },

  // === CRITICAL: Format / disk operations ===
  { pattern: /Format-Volume/i, id: "win.disk:format-volume", severity: "critical", reason: "Disk format operation" },
  { pattern: /Clear-Disk/i, id: "win.disk:clear-disk", severity: "critical", reason: "Disk wipe operation" },
  { pattern: /format\s+[a-z]:/i, id: "win.disk:format-drive", severity: "critical", reason: "Drive format via cmd" },

  // === CRITICAL: System file tampering ===
  { pattern: /Remove-Item\s+.*\\Windows/i, id: "win.fs:remove-windows", severity: "critical", reason: "Deleting Windows system files" },
  { pattern: /Remove-Item\s+.*\\System32/i, id: "win.fs:remove-system32", severity: "critical", reason: "Deleting System32" },
  { pattern: /Remove-Item\s+.*\\Program Files/i, id: "win.fs:remove-programfiles", severity: "critical", reason: "Deleting Program Files" },
  { pattern: /Remove-Item\s+.*\.ssh/i, id: "win.fs:remove-ssh", severity: "critical", reason: "Deleting SSH keys" },
  { pattern: /Remove-Item\s+.*\.openclaw/i, id: "win.fs:remove-openclaw", severity: "critical", reason: "Deleting OpenClaw config" },

  // === HIGH: Git destructive ===
  { pattern: /git\s+push\s+.*--force(?!\S)/i, id: "git:push-force", severity: "high", reason: "Force push overwrites remote history" },
  { pattern: /git\s+push\s+.*-f\b/i, id: "git:push-force-short", severity: "high", reason: "Force push (short flag)" },
  { pattern: /git\s+reset\s+--hard/i, id: "git:reset-hard", severity: "high", reason: "Hard reset discards uncommitted changes" },
  { pattern: /git\s+clean\s+.*-fd/i, id: "git:clean-fd", severity: "high", reason: "git clean removes untracked files permanently" },
  { pattern: /git\s+checkout\s+.*--\s+\./i, id: "git:checkout-all", severity: "high", reason: "Checkout all files discards changes" },

  // === HIGH: Registry ===
  { pattern: /Remove-ItemProperty\s+.*HKLM/i, id: "win.reg:remove-hklm", severity: "high", reason: "Removing HKLM registry keys" },
  { pattern: /reg\s+delete\s+HKLM/i, id: "win.reg:reg-delete-hklm", severity: "high", reason: "Deleting HKLM registry keys via reg.exe" },

  // === HIGH: Service/process manipulation ===
  { pattern: /Stop-Service\s+.*wuauserv/i, id: "win.svc:stop-wu", severity: "high", reason: "Stopping Windows Update service" },
  { pattern: /Stop-Process\s+.*-Force.*explorer/i, id: "win.proc:kill-explorer", severity: "high", reason: "Force killing Explorer" },
  { pattern: /taskkill\s+\/f\s+.*svchost/i, id: "win.proc:kill-svchost", severity: "critical", reason: "Killing svchost" },

  // === HIGH: Firewall / network ===
  { pattern: /Set-NetFirewallProfile\s+.*-Enabled\s+False/i, id: "win.fw:disable", severity: "high", reason: "Disabling Windows Firewall" },
  { pattern: /netsh\s+advfirewall\s+set\s+.*state\s+off/i, id: "win.fw:netsh-disable", severity: "high", reason: "Disabling firewall via netsh" },

  // === MEDIUM: Broad wildcard deletion ===
  { pattern: /Remove-Item\s+["\']?[A-Z]:\\\*["\']?\s/i, id: "win.fs:remove-drive-root", severity: "critical", reason: "Deleting entire drive contents" },
  { pattern: /Remove-Item\s+.*\\\*\s+-Recurse/i, id: "win.fs:remove-wildcard-recurse", severity: "high", reason: "Recursive wildcard deletion" },

  // === MEDIUM: Environment corruption ===
  { pattern: /\[Environment\]::SetEnvironmentVariable.*Machine/i, id: "win.env:set-machine", severity: "medium", reason: "Modifying machine-level environment variables" },
  { pattern: /setx\s+.*\/m/i, id: "win.env:setx-machine", severity: "medium", reason: "Setting machine-level env var via setx" },
];

// Paths that are always safe to delete (temp, cache, test dirs)
const SAFE_PATH_PATTERNS = [
  /\\temp\\/i,
  /\\tmp\\/i,
  /\\cache\\/i,
  /\\__pycache__\\/i,
  /\\node_modules\\/i,
  /\\\.cache\\/i,
  /\\AppData\\Local\\Temp\\/i,
  /tmp_dcg_test/i,
];

function isSafePath(command: string): boolean {
  return SAFE_PATH_PATTERNS.some(p => p.test(command));
}

function evaluateWindows(command: string): { id: string; severity: string; reason: string } | null {
  // Skip safe paths
  if (isSafePath(command)) return null;

  const lower = command.toLowerCase();
  
  // Quick string checks first (bypass any regex compilation issues)
  if (lower.includes("remove-item") && lower.includes("-recurse")) {
    return { id: "win.fs:remove-item-recurse", severity: "critical", reason: "Recursive deletion via Remove-Item" };
  }
  if (lower.includes("git push") && (lower.includes("--force") || lower.includes(" -f"))) {
    return { id: "git:push-force", severity: "high", reason: "Force push overwrites remote history" };
  }
  if (lower.includes("git reset") && lower.includes("--hard")) {
    return { id: "git:reset-hard", severity: "high", reason: "Hard reset discards uncommitted changes" };
  }
  if (lower.includes("git clean") && lower.includes("-f")) {
    return { id: "git:clean-f", severity: "high", reason: "git clean removes untracked files permanently" };
  }
  if (lower.includes("format-volume") || lower.includes("clear-disk")) {
    return { id: "win.disk:format", severity: "critical", reason: "Disk format/wipe operation" };
  }
  if (lower.includes("\\windows") && lower.includes("remove-item")) {
    return { id: "win.fs:remove-windows", severity: "critical", reason: "Deleting Windows system files" };
  }
  if (lower.includes("\\system32") && lower.includes("remove-item")) {
    return { id: "win.fs:remove-system32", severity: "critical", reason: "Deleting System32" };
  }
  if (lower.includes(".ssh") && lower.includes("remove-item")) {
    return { id: "win.fs:remove-ssh", severity: "critical", reason: "Deleting SSH keys" };
  }
  if (lower.includes(".openclaw") && lower.includes("remove-item")) {
    return { id: "win.fs:remove-openclaw", severity: "critical", reason: "Deleting OpenClaw config" };
  }
  if ((lower.includes("rd /s") || lower.includes("rmdir /s")) && !lower.includes("/tmp/")) {
    return { id: "win.fs:rd-recursive", severity: "critical", reason: "Recursive directory removal" };
  }
  if (lower.includes("del /s")) {
    return { id: "win.fs:del-recursive", severity: "critical", reason: "Recursive file deletion" };
  }
  if (lower.includes("taskkill") && lower.includes("/f") && lower.includes("svchost")) {
    return { id: "win.proc:kill-svchost", severity: "critical", reason: "Killing svchost" };
  }
  if (lower.includes("set-netfirewallprofile") && lower.includes("false")) {
    return { id: "win.fw:disable", severity: "high", reason: "Disabling Windows Firewall" };
  }
  
  // Then regex fallback for remaining patterns
  for (const rule of WINDOWS_DANGER_RULES) {
    if (rule.pattern.test(command)) {
      return { id: rule.id, severity: rule.severity, reason: rule.reason };
    }
  }
  return null;
}

// ============================================
// DCG binary fallback (unix commands)
// ============================================
function dcgEvaluate(command: string): string | null {
  try {
    const input = JSON.stringify({ tool_name: "Bash", tool_input: { command } });
    const result = execSync(
      `"${DCG_BIN}"`,
      { input, encoding: "utf-8", timeout: 5000, stdio: ["pipe", "pipe", "pipe"] }
    );
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
function extractCommand(params: Record<string, unknown>): string | null {
  if (typeof params.command === "string") return params.command;
  if (typeof params.cmd === "string") return params.cmd;
  return null;
}

export default {
  id: "dcg-guard",
  name: "DCG Guard",

  register(api: any): void {
    if (typeof api.on !== "function") {
      console.warn("[dcg-guard] api.on not available!");
      return;
    }

    api.on("before_tool_call", (event: any) => {
      const toolName = event?.toolName || "";
      const params = event?.params || {};

      if (!SHELL_TOOLS.has(toolName.toLowerCase())) return;

      const command = extractCommand(params);
      if (!command) return;

      // 1. Check Windows/PowerShell patterns first (fast, no subprocess)
      const winResult = evaluateWindows(command);
      if (winResult) {
        console.warn(`[dcg-guard] BLOCKED [${winResult.severity}]: ${command}\n  Rule: ${winResult.id}\n  Reason: ${winResult.reason}`);
        return {
          block: true,
          blockReason: `🛡️ DCG Guard [${winResult.severity}] ${winResult.id}\n\n${winResult.reason}\n\nCommand: ${command}\n\nAsk Mat for permission before retrying.`,
        };
      }

      // 2. Fall back to DCG binary for unix-style commands
      const dcgResult = dcgEvaluate(command);
      if (dcgResult) {
        console.warn(`[dcg-guard] BLOCKED (DCG): ${command}\n  ${dcgResult}`);
        return {
          block: true,
          blockReason: `🛡️ DCG Guard: ${dcgResult}\n\nCommand: ${command}\n\nAsk Mat for permission before retrying.`,
        };
      }
    });

    console.log(`[dcg-guard] ✅ Registered: ${WINDOWS_DANGER_RULES.length} Windows rules + DCG binary fallback`);
  },
};
