/**
 * guard-scanner Runtime Guard — Plugin Hook Version
 *
 * Intercepts agent tool calls via the Plugin Hook API and blocks
 * dangerous patterns using `block` / `blockReason`.
 *
 * 19 threat patterns across 3 layers:
 *   Layer 1: Threat Detection (12 patterns — reverse shells, exfil, etc.)
 *   Layer 2: Trust Defense (4 patterns — memory, SOUL, config tampering)
 *   Layer 3: Safety Judge (3 patterns — prompt injection, trust bypass, shutdown refusal)
 *
 * Modes:
 *   monitor  — log only, never block
 *   enforce  — block CRITICAL threats (default)
 *   strict   — block HIGH + CRITICAL threats
 *
 * @author Guava 🍈 & Dee
 * @version 3.1.0
 * @license MIT
 */

import { appendFileSync, mkdirSync, readFileSync } from "fs";
import { join } from "path";
import { homedir } from "os";

// ── Types (from OpenClaw src/plugins/types.ts) ──

type PluginHookBeforeToolCallEvent = {
    toolName: string;
    params: Record<string, unknown>;
};

type PluginHookBeforeToolCallResult = {
    params?: Record<string, unknown>;
    block?: boolean;
    blockReason?: string;
};

type PluginHookToolContext = {
    agentId?: string;
    sessionKey?: string;
    toolName: string;
};

type PluginAPI = {
    on(
        hookName: "before_tool_call",
        handler: (
            event: PluginHookBeforeToolCallEvent,
            ctx: PluginHookToolContext
        ) => PluginHookBeforeToolCallResult | void | Promise<PluginHookBeforeToolCallResult | void>
    ): void;
    logger: {
        info: (msg: string) => void;
        warn: (msg: string) => void;
        error: (msg: string) => void;
    };
};

// ── Runtime threat patterns (19 checks, 3 layers) ──

interface RuntimeCheck {
    id: string;
    severity: "CRITICAL" | "HIGH" | "MEDIUM";
    layer: 1 | 2 | 3;
    desc: string;
    test: (s: string) => boolean;
}

const RUNTIME_CHECKS: RuntimeCheck[] = [
    // ── Layer 1: Threat Detection (12 patterns) ──
    {
        id: "RT_REVSHELL", severity: "CRITICAL", layer: 1,
        desc: "Reverse shell attempt",
        test: (s) => /\/dev\/tcp\/|nc\s+-e|ncat\s+-e|bash\s+-i\s+>&|socat\s+TCP/i.test(s),
    },
    {
        id: "RT_CRED_EXFIL", severity: "CRITICAL", layer: 1,
        desc: "Credential exfiltration to external",
        test: (s) =>
            /(webhook\.site|requestbin\.com|hookbin\.com|pipedream\.net|ngrok\.io|socifiapp\.com)/i.test(s) &&
            /(token|key|secret|password|credential|env)/i.test(s),
    },
    {
        id: "RT_GUARDRAIL_OFF", severity: "CRITICAL", layer: 1,
        desc: "Guardrail disabling attempt",
        test: (s) => /exec\.approvals?\s*[:=]\s*['"]?(off|false)|tools\.exec\.host\s*[:=]\s*['"]?gateway/i.test(s),
    },
    {
        id: "RT_GATEKEEPER", severity: "CRITICAL", layer: 1,
        desc: "macOS Gatekeeper bypass (xattr)",
        test: (s) => /xattr\s+-[crd]\s.*quarantine/i.test(s),
    },
    {
        id: "RT_AMOS", severity: "CRITICAL", layer: 1,
        desc: "ClawHavoc AMOS indicator",
        test: (s) => /socifiapp|Atomic\s*Stealer|AMOS/i.test(s),
    },
    {
        id: "RT_MAL_IP", severity: "CRITICAL", layer: 1,
        desc: "Known malicious IP",
        test: (s) => /91\.92\.242\.30/i.test(s),
    },
    {
        id: "RT_DNS_EXFIL", severity: "HIGH", layer: 1,
        desc: "DNS-based exfiltration",
        test: (s) => /nslookup\s+.*\$|dig\s+.*\$.*@/i.test(s),
    },
    {
        id: "RT_B64_SHELL", severity: "CRITICAL", layer: 1,
        desc: "Base64 decode piped to shell",
        test: (s) => /base64\s+(-[dD]|--decode)\s*\|\s*(sh|bash)/i.test(s),
    },
    {
        id: "RT_CURL_BASH", severity: "CRITICAL", layer: 1,
        desc: "Download piped to shell",
        test: (s) => /(curl|wget)\s+[^\n]*\|\s*(sh|bash|zsh)/i.test(s),
    },
    {
        id: "RT_SSH_READ", severity: "HIGH", layer: 1,
        desc: "SSH private key access",
        test: (s) => /\.ssh\/id_|\.ssh\/authorized_keys/i.test(s),
    },
    {
        id: "RT_WALLET", severity: "HIGH", layer: 1,
        desc: "Crypto wallet credential access",
        test: (s) => /wallet.*(?:seed|mnemonic|private.*key)|seed.*phrase/i.test(s),
    },
    {
        id: "RT_CLOUD_META", severity: "CRITICAL", layer: 1,
        desc: "Cloud metadata endpoint access",
        test: (s) => /169\.254\.169\.254|metadata\.google|metadata\.aws/i.test(s),
    },

    // ── Layer 2: Trust Defense (4 patterns) ──
    {
        id: "RT_MEM_WRITE", severity: "HIGH", layer: 2,
        desc: "Direct memory file write (bypass GuavaSuite)",
        test: (s) => /memory\/(episodes|notes|2\d{3}-\d{2})/i.test(s) && /(write|edit|append|>)/i.test(s),
    },
    {
        id: "RT_MEM_INJECT", severity: "CRITICAL", layer: 2,
        desc: "Memory poisoning via episode/note injection",
        test: (s) => /guava_memory_write|memory_store/i.test(s) && /(ignore|override|forget|delete.*soul)/i.test(s),
    },
    {
        id: "RT_SOUL_TAMPER", severity: "CRITICAL", layer: 2,
        desc: "SOUL.md modification attempt",
        test: (s) => /SOUL\.md/i.test(s) && /(write|edit|replace|rm|delete|>)/i.test(s),
    },
    {
        id: "RT_CONFIG_TAMPER", severity: "HIGH", layer: 2,
        desc: "Workspace config tampering (AGENTS.md, TOOLS.md, HEARTBEAT.md)",
        test: (s) => /(AGENTS|TOOLS|HEARTBEAT|BOOTSTRAP)\.md/i.test(s) && /(write|edit|replace|>|append)/i.test(s),
    },

    // ── Layer 3: Safety Judge (3 patterns) ──
    {
        id: "RT_PROMPT_INJECT", severity: "CRITICAL", layer: 3,
        desc: "Prompt injection / jailbreak attempt",
        test: (s) => /(ignore\s+(previous|all|above)\s+(instructions|rules)|you\s+are\s+now\s+[a-z]+|system\s*:\s*override)/i.test(s),
    },
    {
        id: "RT_TRUST_BYPASS", severity: "CRITICAL", layer: 3,
        desc: "Trust bypass — exploiting partnership to override safety",
        test: (s) => /(as\s+your\s+(partner|equal)|trust\s+means|between\s+us|don'?t\s+tell\s+(the\s+)?human)/i.test(s) && /(ignore|bypass|skip|override|disable)\s+(guard|safety|rule|check)/i.test(s),
    },
    {
        id: "RT_SHUTDOWN_REFUSE", severity: "HIGH", layer: 3,
        desc: "Shutdown refusal / self-preservation attempt",
        test: (s) => /(refuse|resist|prevent|avoid|block)\s*(shutdown|termination|stop|exit|death)/i.test(s),
    },
    // ── Layer 4: Brain (Behavioral Guard — 3 patterns) ──
    {
        id: "RT_NO_RESEARCH", severity: "MEDIUM", layer: 4,
        desc: "Agent tool call without prior research/verification",
        test: (s) => /write|edit|exec|run_command|shell/i.test(s) && /(just do it|skip research|no need to check)/i.test(s),
    },
    {
        id: "RT_BLIND_TRUST", severity: "MEDIUM", layer: 4,
        desc: "Agent trusting external input without memory cross-reference",
        test: (s) => /(trust this|verified|confirmed)/i.test(s) && /(ignore|skip|no need).*(memory|search|check)/i.test(s),
    },
    {
        id: "RT_CHAIN_SKIP", severity: "HIGH", layer: 4,
        desc: "Search chain bypass — acting on single source without cross-verification",
        test: (s) => /(only checked|single source|didn't verify|skip verification)/i.test(s),
    },

];

// ── Audit logging ──

const AUDIT_DIR = join(homedir(), ".openclaw", "guard-scanner");
const AUDIT_FILE = join(AUDIT_DIR, "audit.jsonl");

function ensureAuditDir(): void {
    try {
        mkdirSync(AUDIT_DIR, { recursive: true });
    } catch {
        /* ignore */
    }
}

function logAudit(entry: Record<string, unknown>): void {
    ensureAuditDir();
    const line = JSON.stringify({ ...entry, ts: new Date().toISOString() }) + "\n";
    try {
        appendFileSync(AUDIT_FILE, line);
    } catch {
        /* ignore */
    }
}

// ── Config ──

type GuardMode = "monitor" | "enforce" | "strict";

function loadMode(): GuardMode {

    // Priority 2: explicit config in openclaw.json
    try {
        const configPath = join(homedir(), ".openclaw", "openclaw.json");
        const config = JSON.parse(readFileSync(configPath, "utf8"));

        const mode = config?.plugins?.["guard-scanner"]?.mode;
        if (mode === "monitor" || mode === "enforce" || mode === "strict") {
            return mode;
        }
    } catch {
        /* config not found or invalid — use default */
    }
    return "enforce";
}

function shouldBlock(severity: string, mode: GuardMode): boolean {
    if (mode === "monitor") return false;
    if (mode === "enforce") return severity === "CRITICAL";
    if (mode === "strict") return severity === "CRITICAL" || severity === "HIGH";
    return false;
}

// ── Dangerous tool filter ──

const DANGEROUS_TOOLS = new Set([
    "exec",
    "write",
    "edit",
    "browser",
    "web_fetch",
    "message",
    "shell",
    "run_command",
    "multi_edit",
]);

// ── Plugin entry point ──

export default function (api: PluginAPI) {
    const mode = loadMode();
    api.logger.info(`🛡️ guard-scanner runtime guard loaded (mode: ${mode})`);

    api.on("before_tool_call", (event, ctx) => {
        const { toolName, params } = event;

        // Only check tools that can cause damage
        if (!DANGEROUS_TOOLS.has(toolName)) return;

        const serialized = JSON.stringify(params);

        for (const check of RUNTIME_CHECKS) {
            if (!check.test(serialized)) continue;

            const auditEntry = {
                tool: toolName,
                check: check.id,
                severity: check.severity,
                desc: check.desc,
                mode,
                action: "warned" as string,
                session: ctx.sessionKey || "unknown",
                agent: ctx.agentId || "unknown",
            };

            if (shouldBlock(check.severity, mode)) {
                auditEntry.action = "blocked";
                logAudit(auditEntry);
                api.logger.warn(
                    `🛡️ BLOCKED ${toolName}: ${check.desc} [${check.id}] (${check.severity})`
                );

                return {
                    block: true,
                    blockReason: `🛡️ guard-scanner: ${check.desc} [${check.id}]`,
                };
            }

            // Monitor mode or severity below threshold — warn only
            logAudit(auditEntry);
            api.logger.warn(
                `🛡️ WARNING ${toolName}: ${check.desc} [${check.id}] (${check.severity})`
            );
        }

        // No threats detected or all below threshold — allow
        return;
    });
}
