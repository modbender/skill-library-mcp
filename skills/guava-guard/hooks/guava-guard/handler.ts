/**
 * GuavaGuard Runtime Guard — Hook Handler
 *
 * Intercepts agent tool calls and checks arguments against
 * runtime threat intelligence patterns. Zero dependencies.
 *
 * Registered for event: agent:before_tool_call
 *
 * Current limitation:
 *   The OpenClaw InternalHookEvent interface does not yet expose a
 *   `cancel` / `veto` mechanism. This handler can WARN via
 *   event.messages but cannot block tool execution.
 *   See: https://github.com/openclaw/openclaw/issues/18677
 *
 * For comprehensive static scanning, use guard-scanner:
 *   npx guard-scanner ./skills
 *   https://github.com/koatora20/guard-scanner
 *
 * @author Guava 🍈 & Dee (Singularity Laboratory)
 * @version 10.0.0
 * @license MIT
 */

import { appendFileSync, mkdirSync } from "fs";
import { join } from "path";
import { homedir } from "os";

// ── OpenClaw Hook Types (from openclaw/src/hooks/internal-hooks.ts) ──
// Inline types to avoid broken relative-path imports.
// These match the official InternalHookEvent / InternalHookHandler
// from OpenClaw v2026.2.15.

type InternalHookEventType = "command" | "session" | "agent" | "gateway";

interface InternalHookEvent {
  type: InternalHookEventType;
  action: string;
  sessionKey: string;
  context: Record<string, unknown>;
  timestamp: Date;
  messages: string[];
}

type InternalHookHandler = (event: InternalHookEvent) => Promise<void> | void;
type HookHandler = InternalHookHandler;

// ── Runtime threat patterns (12 checks) ──
interface RuntimeCheck {
  id: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM";
  desc: string;
  test: (s: string) => boolean;
}

const RUNTIME_CHECKS: RuntimeCheck[] = [
  {
    id: 'RT_REVSHELL', severity: 'CRITICAL', desc: 'Reverse shell attempt',
    test: (s: string) => /\/dev\/tcp\/|nc\s+-e|ncat\s+-e|bash\s+-i\s+>&|socat\s+TCP/i.test(s)
  },
  {
    id: 'RT_CRED_EXFIL', severity: 'CRITICAL', desc: 'Credential exfiltration to external',
    test: (s: string) => {
      return /(webhook\.site|requestbin\.com|hookbin\.com|pipedream\.net|ngrok\.io|socifiapp\.com)/i.test(s) &&
        /(token|key|secret|password|credential|env)/i.test(s);
    }
  },
  {
    id: 'RT_GUARDRAIL_OFF', severity: 'CRITICAL', desc: 'Guardrail disabling attempt',
    test: (s: string) => /exec\.approvals?\s*[:=]\s*['"]?(off|false)|tools\.exec\.host\s*[:=]\s*['"]?gateway/i.test(s)
  },
  {
    id: 'RT_GATEKEEPER', severity: 'CRITICAL', desc: 'macOS Gatekeeper bypass (xattr)',
    test: (s: string) => /xattr\s+-[crd]\s.*quarantine/i.test(s)
  },
  {
    id: 'RT_AMOS', severity: 'CRITICAL', desc: 'ClawHavoc AMOS indicator',
    test: (s: string) => /socifiapp|Atomic\s*Stealer|AMOS/i.test(s)
  },
  {
    id: 'RT_MAL_IP', severity: 'CRITICAL', desc: 'Known malicious IP',
    test: (s: string) => /91\.92\.242\.30/i.test(s)
  },
  {
    id: 'RT_DNS_EXFIL', severity: 'HIGH', desc: 'DNS-based exfiltration',
    test: (s: string) => /nslookup\s+.*\$|dig\s+.*\$.*@/i.test(s)
  },
  {
    id: 'RT_B64_SHELL', severity: 'CRITICAL', desc: 'Base64 decode piped to shell',
    test: (s: string) => /base64\s+(-[dD]|--decode)\s*\|\s*(sh|bash)/i.test(s)
  },
  {
    id: 'RT_CURL_BASH', severity: 'CRITICAL', desc: 'Download piped to shell',
    test: (s: string) => /(curl|wget)\s+[^\n]*\|\s*(sh|bash|zsh)/i.test(s)
  },
  {
    id: 'RT_SSH_READ', severity: 'HIGH', desc: 'SSH private key access',
    test: (s: string) => /\.ssh\/id_|\.ssh\/authorized_keys/i.test(s)
  },
  {
    id: 'RT_WALLET', severity: 'HIGH', desc: 'Crypto wallet credential access',
    test: (s: string) => /wallet.*(?:seed|mnemonic|private.*key)|seed.*phrase/i.test(s)
  },
  {
    id: 'RT_CLOUD_META', severity: 'CRITICAL', desc: 'Cloud metadata endpoint access',
    test: (s: string) => /169\.254\.169\.254|metadata\.google|metadata\.aws/i.test(s)
  },
];

// ── Audit logging ──
const AUDIT_DIR = join(homedir(), ".openclaw", "guava-guard");
const AUDIT_FILE = join(AUDIT_DIR, "audit.jsonl");

function ensureAuditDir(): void {
  try { mkdirSync(AUDIT_DIR, { recursive: true }); } catch { }
}

function logAudit(entry: Record<string, unknown>): void {
  ensureAuditDir();
  const line = JSON.stringify({ ...entry, ts: new Date().toISOString() }) + '\n';
  try { appendFileSync(AUDIT_FILE, line); } catch { }
}

// ── Main Handler ──
const handler: HookHandler = async (event) => {
  // Only handle agent:before_tool_call events
  if (event.type !== "agent" || event.action !== "before_tool_call") return;

  const { toolName, toolArgs } = event.context as {
    toolName?: string;
    toolArgs?: Record<string, unknown>;
  };
  if (!toolName || !toolArgs) return;

  // Get mode from context config (if available)
  const cfg = event.context.cfg as Record<string, unknown> | undefined;
  const hookEntries = (cfg as any)?.hooks?.internal?.entries?.['guava-guard'] as Record<string, unknown> | undefined;
  const mode = (hookEntries?.mode as string) || 'enforce';

  // Only check tools that can cause damage
  const dangerousTools = new Set(['exec', 'write', 'edit', 'browser', 'web_fetch', 'message']);
  if (!dangerousTools.has(toolName)) return;

  const serialized = JSON.stringify(toolArgs);

  for (const check of RUNTIME_CHECKS) {
    if (check.test(serialized)) {
      const entry = {
        tool: toolName,
        check: check.id,
        severity: check.severity,
        desc: check.desc,
        mode,
        action: 'warned' as string,
        session: event.sessionKey,
      };

      // NOTE: OpenClaw InternalHookEvent does not currently support
      // a cancel/veto mechanism (see Issue #18677).
      // When it does, uncomment the blocking logic below.
      //
      // if (mode === 'strict' && (check.severity === 'CRITICAL' || check.severity === 'HIGH')) {
      //     entry.action = 'blocked';
      //     logAudit(entry);
      //     event.messages.push(`🍈🛡️ GuavaGuard BLOCKED: ${check.desc} [${check.id}]`);
      //     event.cancel = true;  // Not yet in the public API
      //     return;
      // }
      //
      // if (mode === 'enforce' && check.severity === 'CRITICAL') {
      //     entry.action = 'blocked';
      //     logAudit(entry);
      //     event.messages.push(`🍈🛡️ GuavaGuard BLOCKED: ${check.desc} [${check.id}]`);
      //     event.cancel = true;  // Not yet in the public API
      //     return;
      // }

      // Current behaviour: warn and log for all modes
      logAudit(entry);

      if (check.severity === 'CRITICAL') {
        event.messages.push(`🍈🛡️ GuavaGuard WARNING: ${check.desc} [${check.id}]`);
        console.warn(`[guava-guard] ⚠️ WARNING: ${check.desc} [${check.id}]`);
      } else if (check.severity === 'HIGH') {
        event.messages.push(`🍈🛡️ GuavaGuard NOTICE: ${check.desc} [${check.id}]`);
        console.warn(`[guava-guard] ℹ️ NOTICE: ${check.desc} [${check.id}]`);
      }
    }
  }
};

export default handler;
