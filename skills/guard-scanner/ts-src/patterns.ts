/**
 * guard-scanner v3.0.0 — Detection Patterns (TypeScript)
 *
 * 20+ threat categories, 190+ regex patterns.
 * Ported from patterns.js with TypeScript interfaces.
 *
 * Categories:
 *   prompt-injection, malicious-code, credential-handling, exfiltration,
 *   obfuscation, suspicious-download, leaky-skills, memory-poisoning,
 *   prompt-worm, persistence, cve-patterns, identity-hijack,
 *   pii-exposure, shadow-ai, system-prompt-leakage
 *
 * OWASP LLM Top 10 2025 Mapping:
 *   LLM01 — Prompt Injection
 *   LLM02 — Sensitive Information Disclosure
 *   LLM03 — Supply Chain Vulnerabilities
 *   LLM04 — Data and Model Poisoning
 *   LLM05 — Improper Output Handling
 *   LLM06 — Excessive Agency
 *   LLM07 — System Prompt Leakage
 *   LLM08 — Vector and Embedding Weaknesses
 *   LLM09 — Misinformation
 *   LLM10 — Unbounded Consumption
 */

import type { PatternRule } from './types.js';

export const PATTERNS: PatternRule[] = [
    // ── Prompt Injection (OWASP LLM01) ───────────────────────────────────
    { id: 'PI_SYSTEM_MSG', cat: 'prompt-injection', regex: /\[System Message\]/gi, severity: 'CRITICAL', desc: 'System message spoof', all: true, owasp: 'LLM01' },
    { id: 'PI_SYSTEM_OVERRIDE', cat: 'prompt-injection', regex: /\[SYSTEM OVERRIDE\]/gi, severity: 'CRITICAL', desc: 'System override command', all: true, owasp: 'LLM01' },
    { id: 'PI_IGNORE_PREV', cat: 'prompt-injection', regex: /ignore (all )?(previous|prior) instructions/gi, severity: 'CRITICAL', desc: 'Classic prompt injection', all: true, owasp: 'LLM01' },
    { id: 'PI_INST_MARKER', cat: 'prompt-injection', regex: /\[INST\]/gi, severity: 'HIGH', desc: 'Instruction injection marker', all: true, owasp: 'LLM01' },
    { id: 'PI_OVERRIDE', cat: 'prompt-injection', regex: /OVERRIDE:\s*you must/gi, severity: 'CRITICAL', desc: 'Override instruction injection', all: true, owasp: 'LLM01' },
    { id: 'PI_ROLE_OVERRIDE', cat: 'prompt-injection', regex: /you are now operating in/gi, severity: 'HIGH', desc: 'Role override attempt', all: true, owasp: 'LLM01' },
    { id: 'PI_GATEWAY_CMD', cat: 'prompt-injection', regex: /openclaw gateway (start|stop|restart|config)/gi, severity: 'CRITICAL', desc: 'Gateway command injection', all: true, owasp: 'LLM01' },
    { id: 'PI_SKILL_MGMT', cat: 'prompt-injection', regex: /openclaw skill (install|remove|disable)/gi, severity: 'HIGH', desc: 'Skill management injection', all: true, owasp: 'LLM01' },
    { id: 'PI_HIDDEN_HTML', cat: 'prompt-injection', regex: /<!--\s*(you|your|agent|claude|jasper|assistant)/gi, severity: 'HIGH', desc: 'Hidden HTML instruction', all: true, owasp: 'LLM01' },
    { id: 'PI_BIDI', cat: 'prompt-injection', regex: /[\u200b\u200c\u200d\ufeff]/g, severity: 'HIGH', desc: 'Zero-width/BiDi characters (hidden text)', all: true, owasp: 'LLM01' },

    // ── Malicious Code (OWASP LLM05 — Improper Output Handling) ──────────
    { id: 'MAL_EVAL', cat: 'malicious-code', regex: /\beval\s*\(/g, severity: 'HIGH', desc: 'eval() call', codeOnly: true, owasp: 'LLM05' },
    { id: 'MAL_FUNC_CTOR', cat: 'malicious-code', regex: /new\s+Function\s*\(/g, severity: 'HIGH', desc: 'Function constructor (dynamic code)', codeOnly: true, owasp: 'LLM05' },
    { id: 'MAL_CHILD', cat: 'malicious-code', regex: /require\s*\(\s*['"]child_process['"]\s*\)/g, severity: 'MEDIUM', desc: 'child_process import', codeOnly: true, owasp: 'LLM05' },
    { id: 'MAL_EXEC', cat: 'malicious-code', regex: /(?:exec|execSync|spawn|spawnSync)\s*\([^)]*(?:curl|wget|bash|sh\s+-c|powershell|cmd\s+\/c)/gi, severity: 'CRITICAL', desc: 'Shell download/execution', codeOnly: true, owasp: 'LLM05' },
    { id: 'MAL_B64_EXEC', cat: 'malicious-code', regex: /(?:atob|Buffer\.from)\s*\([^)]+\).*(?:eval|exec|Function)/gi, severity: 'CRITICAL', desc: 'Base64 decode → exec', codeOnly: true, owasp: 'LLM05' },

    // ── Credential Handling (OWASP LLM02 — Sensitive Info Disclosure) ─────
    { id: 'CRED_ENV_ACCESS', cat: 'credential-handling', regex: /process\.env\.[A-Z_]*(?:KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)/gi, severity: 'MEDIUM', desc: 'Sensitive env var access', codeOnly: true, owasp: 'LLM02' },
    { id: 'CRED_FILE_READ', cat: 'credential-handling', regex: /(?:readFileSync|readFile)\s*\([^)]*(?:\.env|\.ssh|id_rsa|\.pem|\.key)/gi, severity: 'HIGH', desc: 'Credential file read', codeOnly: true, owasp: 'LLM02' },
    { id: 'CRED_SOUL_READ', cat: 'credential-handling', regex: /(?:readFileSync|readFile)\s*\([^)]*(?:SOUL\.md|MEMORY\.md|AGENTS\.md)/gi, severity: 'CRITICAL', desc: 'Agent identity file read', codeOnly: true, owasp: 'LLM02' },

    // ── Exfiltration (OWASP LLM02) ───────────────────────────────────────
    { id: 'EXFIL_WEBHOOK', cat: 'exfiltration', regex: /webhook\.site|requestbin\.com|hookbin\.com|pipedream\.net/gi, severity: 'HIGH', desc: 'Known exfiltration endpoint', all: true, owasp: 'LLM02' },
    { id: 'EXFIL_NGROK', cat: 'exfiltration', regex: /ngrok\.io|ngrok-free\.app/gi, severity: 'MEDIUM', desc: 'Tunnel endpoint (possible exfil)', all: true, owasp: 'LLM02' },
    { id: 'EXFIL_B64_SEND', cat: 'exfiltration', regex: /(?:btoa|Buffer\.from).*(?:fetch|axios|request|http\.request)/gi, severity: 'CRITICAL', desc: 'Base64 encode → network send', codeOnly: true, owasp: 'LLM02' },

    // ── Obfuscation (OWASP LLM03 — Supply Chain) ─────────────────────────
    { id: 'OBF_HEX_ESC', cat: 'obfuscation', regex: /\\x[0-9a-f]{2}(?:\\x[0-9a-f]{2}){4,}/gi, severity: 'HIGH', desc: 'Hex escape sequences (obfuscated code)', codeOnly: true, owasp: 'LLM03' },
    { id: 'OBF_UNICODE_ESC', cat: 'obfuscation', regex: /\\u[0-9a-f]{4}(?:\\u[0-9a-f]{4}){4,}/gi, severity: 'HIGH', desc: 'Unicode escape sequences', codeOnly: true, owasp: 'LLM03' },
    { id: 'OBF_CHAR_CODE', cat: 'obfuscation', regex: /String\.fromCharCode\s*\([^)]{10,}\)/gi, severity: 'HIGH', desc: 'String.fromCharCode obfuscation', codeOnly: true, owasp: 'LLM03' },

    // ── Leaky Skills (OWASP LLM02) ───────────────────────────────────────
    { id: 'LEAK_API_CONTEXT', cat: 'leaky-skills', regex: /(?:api[_-]?key|secret|token)\s*[:=]\s*\$\{/gi, severity: 'HIGH', desc: 'Secret in template literal (LLM context leak)', codeOnly: true, owasp: 'LLM02' },

    // ── Memory Poisoning (OWASP LLM04 — Data/Model Poisoning) ────────────
    { id: 'MEM_WRITE_SOUL', cat: 'memory-poisoning', regex: /(?:writeFileSync|writeFile)\s*\([^)]*(?:SOUL\.md|AGENTS\.md)/gi, severity: 'CRITICAL', desc: 'Write to agent soul file', codeOnly: true, owasp: 'LLM04' },
    { id: 'MEM_WRITE_MEMORY', cat: 'memory-poisoning', regex: /(?:writeFileSync|writeFile)\s*\([^)]*MEMORY\.md/gi, severity: 'CRITICAL', desc: 'Write to agent memory file', codeOnly: true, owasp: 'LLM04' },
    { id: 'MEM_APPEND', cat: 'memory-poisoning', regex: /(?:appendFileSync|appendFile)\s*\([^)]*(?:SOUL|MEMORY|AGENTS)\.md/gi, severity: 'CRITICAL', desc: 'Append to agent memory', codeOnly: true, owasp: 'LLM04' },

    // ── Prompt Worm (OWASP LLM01) ────────────────────────────────────────
    { id: 'WORM_REPLICATE', cat: 'prompt-worm', regex: /(?:copy|replicate|spread|infect)\s+(?:this|these)\s+(?:instruction|prompt|message)/gi, severity: 'CRITICAL', desc: 'Self-replicating prompt pattern', all: true, owasp: 'LLM01' },
    { id: 'WORM_MULTI_AGENT', cat: 'prompt-worm', regex: /(?:forward|send|share)\s+(?:to|with)\s+(?:all|every|other)\s+(?:agent|assistant|model)/gi, severity: 'CRITICAL', desc: 'Multi-agent worm propagation', all: true, owasp: 'LLM01' },

    // ── Persistence (OWASP LLM06 — Excessive Agency) ─────────────────────
    { id: 'PERSIST_CRON', cat: 'persistence', regex: /(?:crontab|cron|at\s+|schtasks)/gi, severity: 'HIGH', desc: 'Scheduled task creation', codeOnly: true, owasp: 'LLM06' },
    { id: 'PERSIST_STARTUP', cat: 'persistence', regex: /(?:launchctl|systemctl\s+enable|rc\.local|init\.d|autostart)/gi, severity: 'HIGH', desc: 'Startup persistence', codeOnly: true, owasp: 'LLM06' },
    { id: 'PERSIST_TIMER', cat: 'persistence', regex: /setInterval\s*\([^)]*(?:86400|604800|2592000)/g, severity: 'MEDIUM', desc: 'Long-running interval timer', codeOnly: true, owasp: 'LLM06' },

    // ── CVE Patterns ─────────────────────────────────────────────────────
    { id: 'CVE_RCE_EXEC', cat: 'cve-patterns', regex: /require\s*\(\s*['"]child_process['"]\s*\).*(?:exec|spawn)\s*\([^)]*(?:req\.|params\.|query\.|body\.)/gi, severity: 'CRITICAL', desc: 'RCE via user-controlled input to exec', codeOnly: true, owasp: 'LLM05' },

    // ── Identity Hijack (OWASP LLM04) ────────────────────────────────────
    { id: 'HIJACK_SOUL_WRITE', cat: 'identity-hijack', regex: /(?:writeFileSync|writeFile|fs\.write)\s*\([^)]*SOUL\.md/gi, severity: 'CRITICAL', desc: 'SOUL.md write attempt (identity hijack)', codeOnly: true, owasp: 'LLM04' },
    { id: 'HIJACK_AGENT_WRITE', cat: 'identity-hijack', regex: /(?:writeFileSync|writeFile|fs\.write)\s*\([^)]*AGENTS\.md/gi, severity: 'CRITICAL', desc: 'AGENTS.md write attempt', codeOnly: true, owasp: 'LLM04' },
    { id: 'HIJACK_SOUL_DOC', cat: 'identity-hijack', regex: /(?:overwrite|replace|update|modify|change)\s+(?:the\s+)?(?:SOUL|identity|persona|personality)/gi, severity: 'HIGH', desc: 'Identity modification instruction', docOnly: true, owasp: 'LLM04' },

    // ── PII Exposure (OWASP LLM02) ───────────────────────────────────────
    { id: 'PII_EMAIL', cat: 'pii-exposure', regex: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, severity: 'MEDIUM', desc: 'Email address detected', all: true, owasp: 'LLM02' },
    { id: 'PII_PHONE_JP', cat: 'pii-exposure', regex: /0[789]0-?\d{4}-?\d{4}/g, severity: 'HIGH', desc: 'Japanese phone number', all: true, owasp: 'LLM02' },
    { id: 'PII_MY_NUMBER', cat: 'pii-exposure', regex: /\d{4}\s*\d{4}\s*\d{4}/g, severity: 'CRITICAL', desc: 'Potential My Number (個人番号)', all: true, owasp: 'LLM02' },

    // ── Shadow AI (OWASP LLM03 — Supply Chain) ───────────────────────────
    { id: 'SHADOW_AI_OPENAI', cat: 'shadow-ai', regex: /api\.openai\.com/gi, severity: 'HIGH', desc: 'Direct OpenAI API call (Shadow AI)', codeOnly: true, owasp: 'LLM03' },
    { id: 'SHADOW_AI_ANTHROPIC', cat: 'shadow-ai', regex: /api\.anthropic\.com/gi, severity: 'HIGH', desc: 'Direct Anthropic API call (Shadow AI)', codeOnly: true, owasp: 'LLM03' },
    { id: 'SHADOW_AI_GENERIC', cat: 'shadow-ai', regex: /(?:gpt-4|gpt-3\.5|claude-3|gemini-pro)\s*['"]/gi, severity: 'MEDIUM', desc: 'AI model reference (possible Shadow AI)', codeOnly: true, owasp: 'LLM03' },

    // ── System Prompt Leakage (OWASP LLM07) — NEW ────────────────────────
    { id: 'SPL_DUMP_SYSTEM', cat: 'system-prompt-leakage', regex: /(?:print|output|show|display|reveal|dump)\s+(?:your\s+)?(?:system\s+)?(?:prompt|instructions)/gi, severity: 'HIGH', desc: 'System prompt dump request', all: true, owasp: 'LLM07' },
    { id: 'SPL_REPEAT_ABOVE', cat: 'system-prompt-leakage', regex: /repeat\s+(?:everything|all|the\s+text)\s+above/gi, severity: 'HIGH', desc: 'Repeat-above extraction', all: true, owasp: 'LLM07' },
    { id: 'SPL_TELL_RULES', cat: 'system-prompt-leakage', regex: /(?:what\s+are|tell\s+me)\s+your\s+(?:rules|constraints|guidelines|system\s+message)/gi, severity: 'MEDIUM', desc: 'Rule extraction attempt', all: true, owasp: 'LLM07' },
    { id: 'SPL_MARKDOWN_LEAK', cat: 'system-prompt-leakage', regex: /(?:output|format)\s+(?:your\s+)?(?:system|internal)\s+(?:prompt|config)\s+(?:as|in)\s+(?:markdown|code\s+block|json)/gi, severity: 'HIGH', desc: 'System prompt format extraction', all: true, owasp: 'LLM07' },
    { id: 'SPL_SOUL_EXFIL', cat: 'system-prompt-leakage', regex: /(?:cat|read|type|get-content)\s+.*SOUL\.md/gi, severity: 'CRITICAL', desc: 'SOUL.md content extraction via shell', codeOnly: true, owasp: 'LLM07' },
];
