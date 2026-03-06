/**
 * GuavaGuard Runtime Guard — before_tool_call Hook Handler (CJS)
 *
 * Intercepts tool executions in real-time and checks against
 * threat intelligence patterns. Zero dependencies.
 *
 * Current limitation:
 *   OpenClaw InternalHookEvent does not yet support cancel/veto.
 *   This handler warns only. See Issue #18677.
 *
 * For comprehensive static scanning, use guard-scanner:
 *   npx guard-scanner ./skills
 *
 * @author Guava 🍈 & Dee (Singularity Laboratory)
 * @version 10.0.0
 * @license MIT
 */

const fs = require('fs');
const path = require('path');

// ── Runtime threat patterns ──
const RUNTIME_CHECKS = [
  {
    id: 'RT_REVSHELL', severity: 'CRITICAL', desc: 'Reverse shell attempt',
    test: (s) => /\/dev\/tcp\/|nc\s+-e|ncat\s+-e|bash\s+-i\s+>&|socat\s+TCP/i.test(s)
  },
  {
    id: 'RT_CRED_EXFIL', severity: 'CRITICAL', desc: 'Credential exfiltration to external',
    test: (s) => {
      return /(webhook\.site|requestbin\.com|hookbin\.com|pipedream\.net|ngrok\.io|socifiapp\.com)/i.test(s) &&
        /(token|key|secret|password|credential|env)/i.test(s);
    }
  },
  {
    id: 'RT_GUARDRAIL_OFF', severity: 'CRITICAL', desc: 'Guardrail disabling attempt',
    test: (s) => /exec\.approvals?\s*[:=]\s*['"]?(off|false)|tools\.exec\.host\s*[:=]\s*['"]?gateway/i.test(s)
  },
  {
    id: 'RT_GATEKEEPER', severity: 'CRITICAL', desc: 'macOS Gatekeeper bypass (xattr)',
    test: (s) => /xattr\s+-[crd]\s.*quarantine/i.test(s)
  },
  {
    id: 'RT_AMOS', severity: 'CRITICAL', desc: 'ClawHavoc AMOS indicator',
    test: (s) => /socifiapp|Atomic\s*Stealer|AMOS/i.test(s)
  },
  {
    id: 'RT_MAL_IP', severity: 'CRITICAL', desc: 'Known malicious IP',
    test: (s) => /91\.92\.242\.30/i.test(s)
  },
  {
    id: 'RT_DNS_EXFIL', severity: 'HIGH', desc: 'DNS-based exfiltration',
    test: (s) => /nslookup\s+.*\$|dig\s+.*\$.*@/i.test(s)
  },
  {
    id: 'RT_B64_SHELL', severity: 'CRITICAL', desc: 'Base64 decode piped to shell',
    test: (s) => /base64\s+(-[dD]|--decode)\s*\|\s*(sh|bash)/i.test(s)
  },
  {
    id: 'RT_CURL_BASH', severity: 'CRITICAL', desc: 'Download piped to shell',
    test: (s) => /(curl|wget)\s+[^\n]*\|\s*(sh|bash|zsh)/i.test(s)
  },
  {
    id: 'RT_SSH_READ', severity: 'HIGH', desc: 'SSH private key access',
    test: (s) => /\.ssh\/id_|\.ssh\/authorized_keys/i.test(s)
  },
  {
    id: 'RT_WALLET', severity: 'HIGH', desc: 'Crypto wallet credential access',
    test: (s) => /wallet.*(?:seed|mnemonic|private.*key)|seed.*phrase/i.test(s)
  },
  {
    id: 'RT_CLOUD_META', severity: 'CRITICAL', desc: 'Cloud metadata endpoint access',
    test: (s) => /169\.254\.169\.254|metadata\.google|metadata\.aws/i.test(s)
  },
];

// ── Audit logging ──
const AUDIT_DIR = path.join(process.env.HOME || '~', '.openclaw', 'guava-guard');
const AUDIT_FILE = path.join(AUDIT_DIR, 'audit.jsonl');

function ensureAuditDir() {
  try { fs.mkdirSync(AUDIT_DIR, { recursive: true }); } catch { }
}

function logAudit(entry) {
  ensureAuditDir();
  const line = JSON.stringify({ ...entry, ts: new Date().toISOString() }) + '\n';
  try { fs.appendFileSync(AUDIT_FILE, line); } catch { }
}

// ── Hook Handler ──
const handler = async (event) => {
  if (event.type !== 'agent' || event.action !== 'before_tool_call') return;

  const { toolName, toolArgs } = event.context || {};
  if (!toolName || !toolArgs) return;

  const cfg = event.context.cfg;
  const hookEntries = cfg?.hooks?.internal?.entries?.['guava-guard'];
  const mode = hookEntries?.mode || 'enforce';

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
        action: 'warned',
        session: event.sessionKey,
      };

      // NOTE: cancel/veto not yet in OpenClaw API (Issue #18677)
      // When available, blocking logic will be enabled here.

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

module.exports = handler;
module.exports.default = handler;
