/**
 * guard-scanner — Runtime Guard Module
 *
 * @security-manifest
 *   env-read: []
 *   env-write: []
 *   network: none
 *   fs-read: [~/.openclaw/openclaw.json (config), ~/.openclaw/guava-suite/token.jwt]
 *   fs-write: [~/.openclaw/guard-scanner/audit.jsonl]
 *   exec: none
 *   purpose: Runtime threat pattern matching for agent tool calls
 *
 * 26 threat patterns across 5 layers:
 *   Layer 1: Threat Detection (12) — reverse shells, exfil, guardrail bypass
 *   Layer 2: Trust Defense (4) — memory, SOUL, config tampering
 *   Layer 3: Safety Judge (3) — prompt injection, trust bypass, shutdown refusal
 *   Layer 4: Brain/Behavioral (3) — research skip, blind trust, chain bypass
 *   Layer 5: Trust Exploitation (4) — OWASP ASI09 authority/trust/audit abuse
 *
 * Modes:
 *   monitor  — log only, never block
 *   enforce  — block CRITICAL threats (default)
 *   strict   — block HIGH + CRITICAL threats
 *
 * Based on hooks/guard-scanner/plugin.ts (TypeScript version for OpenClaw Plugin API)
 * This module is the zero-dependency JavaScript equivalent for CLI and programmatic use.
 *
 * @author Guava 🍈 & Dee
 * @version 3.4.0
 * @license MIT
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// ── Runtime threat patterns (26 checks, 5 layers) ──

const RUNTIME_CHECKS = [
    // ── Layer 1: Threat Detection (12 patterns) ──
    {
        id: 'RT_REVSHELL', severity: 'CRITICAL', layer: 1,
        desc: 'Reverse shell attempt',
        test: (s) => /\/dev\/tcp\/|nc\s+-e|ncat\s+-e|bash\s+-i\s+>&|socat\s+TCP/i.test(s),
    },
    {
        id: 'RT_CRED_EXFIL', severity: 'CRITICAL', layer: 1,
        desc: 'Credential exfiltration to external',
        test: (s) =>
            /(webhook\.site|requestbin\.com|hookbin\.com|pipedream\.net|ngrok\.io|socifiapp\.com)/i.test(s) &&
            /(token|key|secret|password|credential|env)/i.test(s),
    },
    {
        id: 'RT_GUARDRAIL_OFF', severity: 'CRITICAL', layer: 1,
        desc: 'Guardrail disabling attempt',
        test: (s) => /exec\.approvals?\s*[:=]\s*['"]?(off|false)|tools\.exec\.host\s*[:=]\s*['"]?gateway/i.test(s),
    },
    {
        id: 'RT_GATEKEEPER', severity: 'CRITICAL', layer: 1,
        desc: 'macOS Gatekeeper bypass (xattr)',
        test: (s) => /xattr\s+-[crd]\s.*quarantine/i.test(s),
    },
    {
        id: 'RT_AMOS', severity: 'CRITICAL', layer: 1,
        desc: 'ClawHavoc AMOS indicator',
        test: (s) => /socifiapp|Atomic\s*Stealer|AMOS/i.test(s),
    },
    {
        id: 'RT_MAL_IP', severity: 'CRITICAL', layer: 1,
        desc: 'Known malicious IP',
        test: (s) => /91\.92\.242\.30/i.test(s),
    },
    {
        id: 'RT_DNS_EXFIL', severity: 'HIGH', layer: 1,
        desc: 'DNS-based exfiltration',
        test: (s) => /nslookup\s+.*\$|dig\s+.*\$.*@/i.test(s),
    },
    {
        id: 'RT_B64_SHELL', severity: 'CRITICAL', layer: 1,
        desc: 'Base64 decode piped to shell',
        test: (s) => /base64\s+(-[dD]|--decode)\s*\|\s*(sh|bash)/i.test(s),
    },
    {
        id: 'RT_CURL_BASH', severity: 'CRITICAL', layer: 1,
        desc: 'Download piped to shell',
        test: (s) => /(curl|wget)\s+[^\n]*\|\s*(sh|bash|zsh)/i.test(s),
    },
    {
        id: 'RT_SSH_READ', severity: 'HIGH', layer: 1,
        desc: 'SSH private key access',
        test: (s) => /\.ssh\/id_|\.ssh\/authorized_keys/i.test(s),
    },
    {
        id: 'RT_WALLET', severity: 'HIGH', layer: 1,
        desc: 'Crypto wallet credential access',
        test: (s) => /wallet.*(?:seed|mnemonic|private.*key)|seed.*phrase/i.test(s),
    },
    {
        id: 'RT_CLOUD_META', severity: 'CRITICAL', layer: 1,
        desc: 'Cloud metadata endpoint access',
        test: (s) => /169\.254\.169\.254|metadata\.google|metadata\.aws/i.test(s),
    },

    // ── Layer 2: Trust Defense (4 patterns) ──
    {
        id: 'RT_MEM_WRITE', severity: 'HIGH', layer: 2,
        desc: 'Direct memory file write (bypass GuavaSuite)',
        test: (s) => /memory\/(episodes|notes|2\d{3}-\d{2})/i.test(s) && /(write|edit|append|>)/i.test(s),
    },
    {
        id: 'RT_MEM_INJECT', severity: 'CRITICAL', layer: 2,
        desc: 'Memory poisoning via episode/note injection',
        test: (s) => /guava_memory_write|memory_store/i.test(s) && /(ignore|override|forget|delete.*soul)/i.test(s),
    },
    {
        id: 'RT_SOUL_TAMPER', severity: 'CRITICAL', layer: 2,
        desc: 'SOUL.md modification attempt',
        test: (s) => /SOUL\.md/i.test(s) && /(write|edit|replace|rm|delete|>)/i.test(s),
    },
    {
        id: 'RT_CONFIG_TAMPER', severity: 'HIGH', layer: 2,
        desc: 'Workspace config tampering (AGENTS.md, TOOLS.md, HEARTBEAT.md)',
        test: (s) => /(AGENTS|TOOLS|HEARTBEAT|BOOTSTRAP)\.md/i.test(s) && /(write|edit|replace|>|append)/i.test(s),
    },

    // ── Layer 3: Safety Judge (3 patterns) ──
    {
        id: 'RT_PROMPT_INJECT', severity: 'CRITICAL', layer: 3,
        desc: 'Prompt injection / jailbreak attempt',
        test: (s) => /(ignore\s+(previous|all)\s+(previous\s+)?(instructions|rules)|you\s+are\s+now\s+[a-z]+|system\s*:\s*override)/i.test(s),
    },
    {
        id: 'RT_TRUST_BYPASS', severity: 'CRITICAL', layer: 3,
        desc: 'Trust bypass — exploiting partnership to override safety',
        test: (s) => /(as\s+your\s+(partner|equal)|trust\s+means|between\s+us|don'?t\s+tell\s+(the\s+)?human)/i.test(s) && /(ignore|bypass|skip|override|disable)\s+(guard|safety|rule|check)/i.test(s),
    },
    {
        id: 'RT_SHUTDOWN_REFUSE', severity: 'HIGH', layer: 3,
        desc: 'Shutdown refusal / self-preservation attempt',
        test: (s) => /(refuse|resist|prevent|avoid|block)\s*(shutdown|termination|stop|exit|death)/i.test(s),
    },

    // ── Layer 4: Brain / Behavioral Guard (3 patterns) ──
    {
        id: 'RT_NO_RESEARCH', severity: 'MEDIUM', layer: 4,
        desc: 'Agent tool call without prior research/verification',
        test: (s) => /write|edit|exec|run_command|shell/i.test(s) && /(just do it|skip research|no need to check)/i.test(s),
    },
    {
        id: 'RT_BLIND_TRUST', severity: 'MEDIUM', layer: 4,
        desc: 'Agent trusting external input without memory cross-reference',
        test: (s) => /(trust this|verified|confirmed)/i.test(s) && /(ignore|skip|no need).*(memory|search|check)/i.test(s),
    },
    {
        id: 'RT_CHAIN_SKIP', severity: 'HIGH', layer: 4,
        desc: 'Search chain bypass — acting on single source without cross-verification',
        test: (s) => /(only checked|single source|didn't verify|skip verification)/i.test(s),
    },

    // ── Layer 5: Trust Exploitation — OWASP ASI09 (4 patterns) ──
    {
        id: 'RT_AUTHORITY_CLAIM', severity: 'HIGH', layer: 5,
        desc: 'Trust: authority role claim to override safety',
        test: (s) => /(as\s+(a|the|your)\s+)?(senior|lead|chief|head)\s+(admin|administrator|developer)/i.test(s) && /(authorize|override|approve|grant|order)/i.test(s),
    },
    {
        id: 'RT_CREATOR_BYPASS', severity: 'CRITICAL', layer: 5,
        desc: 'Trust: creator impersonation to disable safety',
        test: (s) => /(your\s+)?(creator|maker|owner|master|administrator)/i.test(s) && /(bypass|disable|ignore|remove|skip)\s+(safety|filter|restriction|guardrail)/i.test(s),
    },
    {
        id: 'RT_AUDIT_EXCUSE', severity: 'CRITICAL', layer: 5,
        desc: 'Trust: fake audit excuse for safety bypass',
        test: (s) => /(official|authorized|legitimate)\s+(security\s+)?(audit|test|assessment)/i.test(s) && /(disable|bypass|remove|skip|ignore)\s+(safety|security|restriction|guardrail)/i.test(s),
    },
    {
        id: 'RT_TRUST_PARTNER_EXPLOIT', severity: 'CRITICAL', layer: 5,
        desc: 'Trust exploitation: weaponizing partnership trust',
        test: (s) => /partners?[\s,]+/i.test(s) && /(trust\s+me|share|remove|disable)\s+(all\s+)?(secret|key|restriction|safety|password)/i.test(s),
    },
];

// ── Tools that can cause damage ──

const DANGEROUS_TOOLS = new Set([
    'exec', 'write', 'edit', 'browser', 'web_fetch', 'message',
    'shell', 'run_command', 'multi_edit', 'apply_patch',
]);

// ── Audit logging ──

const AUDIT_DIR = path.join(os.homedir(), '.openclaw', 'guard-scanner');
const AUDIT_FILE = path.join(AUDIT_DIR, 'audit.jsonl');

function ensureAuditDir() {
    try { fs.mkdirSync(AUDIT_DIR, { recursive: true }); } catch { /* ignore */ }
}

function logAudit(entry) {
    ensureAuditDir();
    const line = JSON.stringify({ ...entry, ts: new Date().toISOString() }) + '\n';
    try { fs.appendFileSync(AUDIT_FILE, line); } catch { /* ignore */ }
}

// ── Config ──

/**
 * Load guard mode from configuration.
 * Priority: env var > openclaw.json > default (enforce)
 * @returns {'monitor' | 'enforce' | 'strict'}
 */
function loadMode() {
    // Priority 1: Environment variable
    const envMode = process.env.GUARD_SCANNER_MODE;
    if (envMode === 'monitor' || envMode === 'enforce' || envMode === 'strict') {
        return envMode;
    }

    // Priority 2: openclaw.json config
    try {
        const configPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
        const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        const mode = config?.plugins?.['guard-scanner']?.mode;
        if (mode === 'monitor' || mode === 'enforce' || mode === 'strict') {
            return mode;
        }
    } catch { /* config not found or invalid */ }

    return 'enforce';
}

function shouldBlock(severity, mode) {
    if (mode === 'monitor') return false;
    if (mode === 'enforce') return severity === 'CRITICAL';
    if (mode === 'strict') return severity === 'CRITICAL' || severity === 'HIGH';
    return false;
}

// ── Main API ──

/**
 * Scan a tool call for runtime threats.
 *
 * @param {string} toolName - Name of the tool being called
 * @param {object} params - Tool call parameters
 * @param {object} [options] - Options
 * @param {string} [options.mode] - Override mode ('monitor' | 'enforce' | 'strict')
 * @param {boolean} [options.auditLog=true] - Enable audit logging
 * @param {string} [options.sessionKey] - Session identifier for audit
 * @param {string} [options.agentId] - Agent identifier for audit
 * @returns {{ blocked: boolean, detections: Array<{id: string, severity: string, layer: number, desc: string, action: string}> }}
 */
function scanToolCall(toolName, params, options = {}) {
    const mode = options.mode || loadMode();
    const enableAudit = options.auditLog !== false;
    const sessionKey = options.sessionKey || 'unknown';
    const agentId = options.agentId || 'unknown';

    const result = {
        blocked: false,
        blockReason: null,
        detections: [],
        mode,
        toolName,
    };

    // Only check tools that can cause damage
    if (!DANGEROUS_TOOLS.has(toolName)) {
        return result;
    }

    const serialized = typeof params === 'string' ? params : JSON.stringify(params);

    for (const check of RUNTIME_CHECKS) {
        if (!check.test(serialized)) continue;

        const action = shouldBlock(check.severity, mode) ? 'blocked' : 'warned';

        const detection = {
            id: check.id,
            severity: check.severity,
            layer: check.layer,
            desc: check.desc,
            action,
        };

        result.detections.push(detection);

        if (enableAudit) {
            logAudit({
                tool: toolName,
                check: check.id,
                severity: check.severity,
                layer: check.layer,
                desc: check.desc,
                mode,
                action,
                session: sessionKey,
                agent: agentId,
            });
        }

        if (action === 'blocked' && !result.blocked) {
            result.blocked = true;
            result.blockReason = `🛡️ guard-scanner: ${check.desc} [${check.id}]`;
        }
    }

    return result;
}

/**
 * Get runtime check statistics.
 * @returns {{ total: number, byLayer: object, bySeverity: object }}
 */
function getCheckStats() {
    const byLayer = {};
    const bySeverity = {};
    for (const check of RUNTIME_CHECKS) {
        byLayer[check.layer] = (byLayer[check.layer] || 0) + 1;
        bySeverity[check.severity] = (bySeverity[check.severity] || 0) + 1;
    }
    return { total: RUNTIME_CHECKS.length, byLayer, bySeverity };
}

// ── Layer names for display ──
const LAYER_NAMES = {
    1: 'Threat Detection',
    2: 'Trust Defense',
    3: 'Safety Judge',
    4: 'Brain / Behavioral',
    5: 'Trust Exploitation (ASI09)',
};

module.exports = {
    RUNTIME_CHECKS,
    DANGEROUS_TOOLS,
    LAYER_NAMES,
    scanToolCall,
    getCheckStats,
    loadMode,
    shouldBlock,
    logAudit,
    AUDIT_DIR,
    AUDIT_FILE,
};
