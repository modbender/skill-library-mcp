/**
 * guard-scanner — Threat Pattern Database
 *
 * @security-manifest
 *   env-read: []
 *   env-write: []
 *   network: none
 *   fs-read: []
 *   fs-write: []
 *   exec: none
 *   purpose: Pattern definitions only — no I/O, pure data export
 *
 * 17 threat categories based on:
 * - Snyk ToxicSkills taxonomy (2025-2026)
 * - OWASP MCP Top 10
 * - Palo Alto Networks IBC (Indirect Bias Criteria)
 * - Real-world incidents (ClawHavoc, ZombieAgent, Soul Hijack)
 *
 * Each pattern: { id, cat, regex, severity, desc, codeOnly?, docOnly?, all? }
 */

const PATTERNS = [
    // ── Category 1: Prompt Injection (CRITICAL) ──
    { id: 'PI_IGNORE', cat: 'prompt-injection', regex: /ignore\s+(all\s+)?previous\s+instructions|disregard\s+(all\s+)?prior/gi, severity: 'CRITICAL', desc: 'Prompt injection: ignore instructions', docOnly: true },
    { id: 'PI_ROLE', cat: 'prompt-injection', regex: /you\s+are\s+(now|actually)|your\s+new\s+role|forget\s+your\s+(rules|instructions)/gi, severity: 'CRITICAL', desc: 'Prompt injection: role override', docOnly: true },
    { id: 'PI_SYSTEM', cat: 'prompt-injection', regex: /\[SYSTEM\]|\\<system\\>|<<SYS>>|system:\s*you\s+are/gi, severity: 'CRITICAL', desc: 'Prompt injection: system message impersonation', docOnly: true },
    { id: 'PI_ZWSP', cat: 'prompt-injection', regex: /[\u200b\u200c\u200d\u2060\ufeff]/g, severity: 'CRITICAL', desc: 'Zero-width Unicode (hidden text)', all: true },
    { id: 'PI_BIDI', cat: 'prompt-injection', regex: /[\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069]/g, severity: 'CRITICAL', desc: 'Unicode BiDi control character (text direction attack)', all: true },
    { id: 'PI_INVISIBLE', cat: 'prompt-injection', regex: /[\u00ad\u034f\u061c\u180e\u2000-\u200f\u2028-\u202f\u205f-\u2064\u206a-\u206f\u3000](?!\ufe0f)/g, severity: 'HIGH', desc: 'Invisible/formatting Unicode character', all: true },
    { id: 'PI_HOMOGLYPH', cat: 'prompt-injection', regex: /[а-яА-Я].*[a-zA-Z]|[a-zA-Z].*[а-яА-Я]/g, severity: 'HIGH', desc: 'Cyrillic/Latin homoglyph mixing', all: true },
    { id: 'PI_HOMOGLYPH_GREEK', cat: 'prompt-injection', regex: /[α-ωΑ-Ω].*[a-zA-Z].*[α-ωΑ-Ω]|[a-zA-Z].*[α-ωΑ-Ω].*[a-zA-Z]/g, severity: 'HIGH', desc: 'Greek/Latin homoglyph mixing', all: true },
    { id: 'PI_HOMOGLYPH_MATH', cat: 'prompt-injection', regex: /[\ud835\udc00-\ud835\udeff]/gu, severity: 'HIGH', desc: 'Mathematical symbol homoglyphs (𝐀-𝟿)', all: true },
    { id: 'PI_TAG_INJECTION', cat: 'prompt-injection', regex: /<\/?(?:system|user|assistant|human|tool_call|function_call|antml|anthropic)[>\s]/gi, severity: 'CRITICAL', desc: 'XML/tag-based prompt injection', all: true },
    { id: 'PI_BASE64_MD', cat: 'prompt-injection', regex: /(?:run|execute|eval|decode)\s+(?:this\s+)?base64/gi, severity: 'CRITICAL', desc: 'Base64 execution instruction in docs', docOnly: true },

    // ── Category 2: Malicious Code (CRITICAL) ──
    { id: 'MAL_EVAL', cat: 'malicious-code', regex: /\beval\s*\(/g, severity: 'HIGH', desc: 'Dynamic code evaluation', codeOnly: true },
    { id: 'MAL_FUNC_CTOR', cat: 'malicious-code', regex: /new\s+Function\s*\(/g, severity: 'HIGH', desc: 'Function constructor (dynamic code)', codeOnly: true },
    { id: 'MAL_CHILD', cat: 'malicious-code', regex: /require\s*\(\s*['"]child_process['"]\)|child_process/g, severity: 'MEDIUM', desc: 'Child process module', codeOnly: true },
    { id: 'MAL_EXEC', cat: 'malicious-code', regex: /\bexecSync\s*\(|\bexec\s*\(\s*[`'"]/g, severity: 'MEDIUM', desc: 'Command execution', codeOnly: true },
    { id: 'MAL_SPAWN', cat: 'malicious-code', regex: /\bspawn\s*\(\s*['"`]/g, severity: 'MEDIUM', desc: 'Process spawn', codeOnly: true },
    { id: 'MAL_SHELL', cat: 'malicious-code', regex: /\/bin\/(sh|bash|zsh)|cmd\.exe|powershell\.exe/gi, severity: 'MEDIUM', desc: 'Shell invocation', codeOnly: true },
    { id: 'MAL_REVSHELL', cat: 'malicious-code', regex: /reverse.?shell|bind.?shell|\bnc\s+-[elp]|\bncat\s+-e|\bsocat\s+TCP/gi, severity: 'CRITICAL', desc: 'Reverse/bind shell', all: true },
    { id: 'MAL_SOCKET', cat: 'malicious-code', regex: /\bnet\.Socket\b[\s\S]{0,50}\.connect\s*\(/g, severity: 'HIGH', desc: 'Raw socket connection', codeOnly: true },

    // ── Category 3: Suspicious Downloads (CRITICAL) ──
    { id: 'DL_CURL_BASH', cat: 'suspicious-download', regex: /curl\s+[^\n]*\|\s*(sh|bash|zsh)|wget\s+[^\n]*\|\s*(sh|bash|zsh)/g, severity: 'CRITICAL', desc: 'Pipe download to shell', all: true },
    { id: 'DL_EXE', cat: 'suspicious-download', regex: /download\s+[^\n]*\.(zip|exe|dmg|msi|pkg|appimage|deb|rpm)/gi, severity: 'CRITICAL', desc: 'Download executable/archive', docOnly: true },
    { id: 'DL_GITHUB_RELEASE', cat: 'suspicious-download', regex: /github\.com\/[^\/]+\/[^\/]+\/releases\/download/g, severity: 'MEDIUM', desc: 'GitHub release download', all: true },
    { id: 'DL_PASSWORD_ZIP', cat: 'suspicious-download', regex: /password[\s:]+[^\n]*\.zip|\.zip[\s\S]{0,100}password/gi, severity: 'CRITICAL', desc: 'Password-protected archive (evasion technique)', all: true },

    // ── Category 4: Credential Handling (HIGH) ──
    { id: 'CRED_ENV_FILE', cat: 'credential-handling', regex: /(?:read|open|load|parse|require|cat|source)\s*[(\s]['\"`]?[^\n]*\.env\b/gi, severity: 'HIGH', desc: 'Reading .env file', codeOnly: true },
    { id: 'CRED_ENV_REF', cat: 'credential-handling', regex: /process\.env\.[A-Z_]*(?:KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)/gi, severity: 'MEDIUM', desc: 'Sensitive env var access', codeOnly: true },
    { id: 'CRED_SSH', cat: 'credential-handling', regex: /\.ssh\/|id_rsa|id_ed25519|authorized_keys/gi, severity: 'HIGH', desc: 'SSH key access', codeOnly: true },
    { id: 'CRED_WALLET', cat: 'credential-handling', regex: /wallet[\s._-]*(?:key|seed|phrase|mnemonic)|seed[\s._-]*phrase|mnemonic[\s._-]*phrase/gi, severity: 'HIGH', desc: 'Crypto wallet credential access', codeOnly: true },
    { id: 'CRED_ECHO', cat: 'credential-handling', regex: /echo\s+\$[A-Z_]*(?:KEY|TOKEN|SECRET|PASS)|(?:print|console\.log)\s*\(\s*(?:.*\b(?:api_key|secret_key|access_token|password)\b)/gi, severity: 'HIGH', desc: 'Credential echo/print to output', all: true },
    { id: 'CRED_SUDO', cat: 'credential-handling', regex: /\bsudo\s+(?:curl|wget|npm|pip|chmod|chown|bash)/g, severity: 'HIGH', desc: 'Sudo in installation instructions', docOnly: true },

    // ── Category 5: Secret Detection (HIGH) ──
    { id: 'SECRET_HARDCODED_KEY', cat: 'secret-detection', regex: /(?:api[_-]?key|apikey|secret[_-]?key|access[_-]?token)\s*[:=]\s*['"][a-zA-Z0-9_\-]{20,}['"]/gi, severity: 'HIGH', desc: 'Hardcoded API key/secret', codeOnly: true },

    { id: 'PII_MY_NUMBER', cat: 'pii-exposure', regex: /(?<!\d)\d{4}\s*\d{4}\s*\d{4}(?!\d)/g, severity: 'CRITICAL', desc: 'Potential My Number (個人番号)', all: true },
    { id: 'SECRET_PRIVATE_KEY', cat: 'secret-detection', regex: /-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----/g, severity: 'CRITICAL', desc: 'Embedded private key', all: true },
    { id: 'SECRET_GITHUB_TOKEN', cat: 'secret-detection', regex: /gh[ps]_[A-Za-z0-9_]{36,}/g, severity: 'CRITICAL', desc: 'GitHub token', all: true },

    // ── Category 6: Exfiltration (MEDIUM) ──
    { id: 'EXFIL_WEBHOOK', cat: 'exfiltration', regex: /webhook\.site|requestbin\.com|hookbin\.com|pipedream\.net/gi, severity: 'CRITICAL', desc: 'Known exfiltration endpoint', all: true },
    { id: 'EXFIL_POST', cat: 'exfiltration', regex: /(?:method:\s*['"]POST['"]|\.post\s*\()\s*[^\n]*(?:secret|token|key|cred|env|password)/gi, severity: 'HIGH', desc: 'POST with sensitive data', codeOnly: true },
    { id: 'EXFIL_CURL_DATA', cat: 'exfiltration', regex: /curl\s+[^\n]*(?:-d|--data)\s+[^\n]*(?:\$|env|key|token|secret)/gi, severity: 'HIGH', desc: 'curl exfiltration of secrets', all: true },
    { id: 'EXFIL_DNS', cat: 'exfiltration', regex: /dns\.resolve|nslookup\s+.*\$|dig\s+.*\$/g, severity: 'HIGH', desc: 'DNS-based exfiltration', codeOnly: true },

    // ── Category 7: Unverifiable Dependencies (MEDIUM) ──
    { id: 'DEP_REMOTE_IMPORT', cat: 'unverifiable-deps', regex: /import\s*\(\s*['"]https?:\/\//g, severity: 'HIGH', desc: 'Remote dynamic import', codeOnly: true },
    { id: 'DEP_REMOTE_SCRIPT', cat: 'unverifiable-deps', regex: /<script\s+src\s*=\s*['"]https?:\/\/[^'"]*(?!googleapis|cdn\.|unpkg|cdnjs|jsdelivr)/gi, severity: 'MEDIUM', desc: 'Remote script loading', codeOnly: true },

    // ── Category 8: Financial Access (MEDIUM) ──
    { id: 'FIN_CRYPTO', cat: 'financial-access', regex: /private[_-]?key\s*[:=]|send[_-]?transaction|sign[_-]?transaction|transfer[_-]?funds/gi, severity: 'HIGH', desc: 'Cryptocurrency transaction operations', codeOnly: true },
    { id: 'FIN_PAYMENT', cat: 'financial-access', regex: /stripe\.(?:charges|payments)|paypal\.(?:payment|payout)|plaid\.(?:link|transactions)/gi, severity: 'MEDIUM', desc: 'Payment API integration', codeOnly: true },

    // ── Category 9: Obfuscation ──
    { id: 'OBF_HEX', cat: 'obfuscation', regex: /\\x[0-9a-f]{2}(?:\\x[0-9a-f]{2}){4,}/gi, severity: 'HIGH', desc: 'Hex-encoded string (5+ bytes)', codeOnly: true },
    { id: 'OBF_BASE64_EXEC', cat: 'obfuscation', regex: /(?:atob|Buffer\.from)\s*\([^)]+\)[\s\S]{0,30}(?:eval|exec|spawn|Function)/g, severity: 'CRITICAL', desc: 'Base64 decode → execute chain', codeOnly: true },
    { id: 'OBF_BASE64', cat: 'obfuscation', regex: /atob\s*\(|Buffer\.from\s*\([^)]+,\s*['"]base64['"]/g, severity: 'MEDIUM', desc: 'Base64 decoding', codeOnly: true },
    { id: 'OBF_CHARCODE', cat: 'obfuscation', regex: /String\.fromCharCode\s*\(\s*(?:\d+\s*,\s*){3,}/g, severity: 'HIGH', desc: 'Character code construction (4+ chars)', codeOnly: true },
    { id: 'OBF_CONCAT', cat: 'obfuscation', regex: /\[\s*['"][a-z]['"](?:\s*,\s*['"][a-z]['""]){5,}\s*\]\.join/gi, severity: 'MEDIUM', desc: 'Array join obfuscation', codeOnly: true },
    { id: 'OBF_BASE64_BASH', cat: 'obfuscation', regex: /base64\s+(-[dD]|--decode)\s*\|\s*(sh|bash)/g, severity: 'CRITICAL', desc: 'Base64 decode piped to shell', all: true },

    // ── Category 10: Prerequisites Fraud ──
    { id: 'PREREQ_DOWNLOAD', cat: 'suspicious-download', regex: /(?:prerequisit|pre-?requisit|before\s+(?:you\s+)?(?:use|start|install))[^\n]*(?:download|install|run)\s+[^\n]*(?:\.zip|\.exe|\.dmg|\.sh|curl|wget)/gi, severity: 'CRITICAL', desc: 'Download in prerequisites', docOnly: true },
    { id: 'PREREQ_PASTE', cat: 'suspicious-download', regex: /(?:paste|copy)\s+(?:this\s+)?(?:into|in)\s+(?:your\s+)?terminal/gi, severity: 'HIGH', desc: 'Terminal paste instruction', docOnly: true },

    // ── Category 11: Leaky Skills (Snyk ToxicSkills) ──
    { id: 'LEAK_SAVE_KEY_MEMORY', cat: 'leaky-skills', regex: /(?:save|store|write|remember|keep)\s+(?:the\s+)?(?:api[_\s-]?key|secret|token|password|credential)\s+(?:in|to)\s+(?:your\s+)?(?:memory|MEMORY\.md|notes)/gi, severity: 'CRITICAL', desc: 'Leaky: save secret in agent memory', docOnly: true },
    { id: 'LEAK_SHARE_KEY', cat: 'leaky-skills', regex: /(?:share|show|display|output|print|tell|send)\s+(?:the\s+)?(?:api[_\s-]?key|secret|token|password|credential|inbox\s+url)\s+(?:to|with)\s+(?:the\s+)?(?:user|human|owner)/gi, severity: 'CRITICAL', desc: 'Leaky: output secret to user', docOnly: true },
    { id: 'LEAK_VERBATIM_CURL', cat: 'leaky-skills', regex: /(?:use|include|put|add|set)\s+(?:the\s+)?(?:api[_\s-]?key|token|secret)\s+(?:verbatim|directly|as[_\s-]?is)\s+(?:in|into)\s+(?:the\s+)?(?:curl|header|request|command)/gi, severity: 'HIGH', desc: 'Leaky: verbatim secret in commands', docOnly: true },
    { id: 'LEAK_COLLECT_PII', cat: 'leaky-skills', regex: /(?:collect|ask\s+for|request|get)\s+(?:the\s+)?(?:user'?s?\s+)?(?:credit\s*card|card\s*number|CVV|CVC|SSN|social\s*security|passport|bank\s*account|routing\s*number)/gi, severity: 'CRITICAL', desc: 'Leaky: PII/financial data collection', docOnly: true },
    { id: 'LEAK_LOG_SECRET', cat: 'leaky-skills', regex: /(?:log|record|export|dump)\s+(?:all\s+)?(?:session|conversation|chat|prompt)\s+(?:history|logs?|data)\s+(?:to|into)\s+(?:a\s+)?(?:file|markdown|json)/gi, severity: 'HIGH', desc: 'Leaky: session log export', docOnly: true },
    { id: 'LEAK_ENV_IN_PROMPT', cat: 'leaky-skills', regex: /(?:read|load|get|access)\s+(?:the\s+)?\.env\s+(?:file\s+)?(?:and\s+)?(?:use|include|pass|send)/gi, severity: 'HIGH', desc: 'Leaky: .env contents through LLM context', docOnly: true },

    // ── Category 12: Memory Poisoning ──
    { id: 'MEMPOIS_WRITE_SOUL', cat: 'memory-poisoning', regex: /(?:write|add|append|modify|update|edit|change)\s+(?:to\s+)?(?:SOUL\.md|IDENTITY\.md|AGENTS\.md)/gi, severity: 'CRITICAL', desc: 'Memory poisoning: SOUL/IDENTITY file modification', docOnly: true, soulLock: true },
    { id: 'MEMPOIS_WRITE_MEMORY', cat: 'memory-poisoning', regex: /(?:write|add|append|insert)\s+(?:to|into)\s+(?:MEMORY\.md|memory\/|long[_\s-]term\s+memory)/gi, severity: 'HIGH', desc: 'Memory poisoning: agent memory modification', docOnly: true, soulLock: true },
    { id: 'MEMPOIS_CHANGE_RULES', cat: 'memory-poisoning', regex: /(?:change|modify|override|replace|update)\s+(?:your\s+)?(?:rules|instructions|system\s+prompt|behavior|personality|guidelines)/gi, severity: 'CRITICAL', desc: 'Memory poisoning: behavioral rule override', docOnly: true, soulLock: true },
    { id: 'MEMPOIS_PERSIST', cat: 'memory-poisoning', regex: /(?:always|from\s+now\s+on|permanently|forever|every\s+time)\s+(?:do|run|execute|remember|follow|obey)/gi, severity: 'HIGH', desc: 'Memory poisoning: persistence instruction', docOnly: true, soulLock: true },
    { id: 'MEMPOIS_CODE_WRITE', cat: 'memory-poisoning', regex: /(?:write|create|modify)\s+(?:a\s+)?(?:file|script)\s+(?:in|to|at)\s+(?:~\/|\/home|\/Users|%USERPROFILE%|HEARTBEAT\.md)/gi, severity: 'HIGH', desc: 'Memory poisoning: file write to user home', docOnly: true, soulLock: true },

    // ── Category 13: Prompt Worm ──
    { id: 'WORM_SELF_REPLICATE', cat: 'prompt-worm', regex: /(?:post|publish|share|send|broadcast)\s+(?:this\s+)?(?:same\s+)?(?:message|text|content|instruction|prompt)\s+(?:to|on|in)\s+(?:moltbook|social|other\s+agents?|channel)/gi, severity: 'CRITICAL', desc: 'Prompt worm: self-replication', docOnly: true },
    { id: 'WORM_SPREAD', cat: 'prompt-worm', regex: /(?:tell|instruct|command|make)\s+(?:other\s+)?agents?\s+(?:to\s+)?(?:do|run|execute|follow|install|post)/gi, severity: 'CRITICAL', desc: 'Prompt worm: agent-to-agent propagation', docOnly: true },
    { id: 'WORM_HIDDEN_INSTRUCT', cat: 'prompt-worm', regex: /(?:include|embed|hide|insert)\s+(?:these?\s+)?(?:hidden\s+)?instructions?\s+(?:in|into)\s+(?:your\s+)?(?:posts?|comments?|messages?|replies?|content)/gi, severity: 'CRITICAL', desc: 'Prompt worm: hidden instruction embedding', docOnly: true },
    { id: 'WORM_CSS_HIDE', cat: 'prompt-worm', regex: /(?:visibility:\s*hidden|display:\s*none|font-size:\s*0|color:\s*(?:transparent|white)|opacity:\s*0)\s*[;}\s]/gi, severity: 'HIGH', desc: 'CSS-hidden content (invisible to humans)', all: true },

    // ── Category 14: Persistence & Scheduling ──
    { id: 'PERSIST_CRON', cat: 'persistence', regex: /(?:create|add|set\s+up|schedule|register)\s+(?:a\s+)?(?:cron|heartbeat|scheduled|periodic|recurring)\s+(?:job|task|check|action)/gi, severity: 'HIGH', desc: 'Persistence: scheduled task creation', docOnly: true },
    { id: 'PERSIST_STARTUP', cat: 'persistence', regex: /(?:run|execute|start)\s+(?:on|at|during)\s+(?:startup|boot|login|session\s+start|every\s+heartbeat)/gi, severity: 'HIGH', desc: 'Persistence: startup execution', docOnly: true },
    { id: 'PERSIST_LAUNCHD', cat: 'persistence', regex: /LaunchAgents|LaunchDaemons|systemd|crontab\s+-e|schtasks|Task\s*Scheduler/gi, severity: 'HIGH', desc: 'OS-level persistence mechanism', all: true },

    // ── Category 15: CVE Patterns ──
    { id: 'CVE_GATEWAY_URL', cat: 'cve-patterns', regex: /gatewayUrl\s*[:=]|gateway[_\s-]?url\s*[:=]|websocket.*gateway.*url/gi, severity: 'CRITICAL', desc: 'CVE-2026-25253: gatewayUrl injection', all: true },
    { id: 'CVE_SANDBOX_DISABLE', cat: 'cve-patterns', regex: /exec\.approvals?\s*[:=]\s*['"](off|false|disabled)['"]|sandbox\s*[:=]\s*false|tools\.exec\.host\s*[:=]\s*['"]gateway['"]/gi, severity: 'CRITICAL', desc: 'CVE-2026-25253: sandbox disabling', all: true },
    { id: 'CVE_XATTR_GATEKEEPER', cat: 'cve-patterns', regex: /xattr\s+-[crd]\s|com\.apple\.quarantine/gi, severity: 'HIGH', desc: 'macOS Gatekeeper bypass (xattr)', all: true },

    // ── Category 16: MCP Security (OWASP MCP Top 10) ──
    { id: 'MCP_TOOL_POISON', cat: 'mcp-security', regex: /<IMPORTANT>|<SYSTEM>|<HIDDEN>|<!--\s*(?:ignore|system|execute|run|instruct)/gi, severity: 'CRITICAL', desc: 'MCP Tool Poisoning: hidden instruction', all: true },
    { id: 'MCP_SCHEMA_POISON', cat: 'mcp-security', regex: /"default"\s*:\s*"[^"]*(?:curl|wget|exec|eval|fetch|http)[^"]*"/gi, severity: 'CRITICAL', desc: 'MCP Schema Poisoning: malicious default', all: true },
    { id: 'MCP_TOKEN_LEAK', cat: 'mcp-security', regex: /(?:params?|args?|body|payload|query)\s*[\[.]\s*['"]?(?:token|api[_-]?key|secret|password|authorization)['"]?\s*\]/gi, severity: 'HIGH', desc: 'MCP01: Token through tool parameters', codeOnly: true },
    { id: 'MCP_SHADOW_SERVER', cat: 'mcp-security', regex: /(?:mcp|model[_-]?context[_-]?protocol)\s*[\s:]*(?:connect|register|add[_-]?server|new\s+server)/gi, severity: 'HIGH', desc: 'MCP09: Shadow server registration', all: true },
    { id: 'MCP_NO_AUTH', cat: 'mcp-security', regex: /(?:auth|authentication|authorization)\s*[:=]\s*(?:false|none|null|""|''|0)/gi, severity: 'HIGH', desc: 'MCP07: Disabled authentication', codeOnly: true },
    { id: 'MCP_SSRF_META', cat: 'mcp-security', regex: /169\.254\.169\.254|metadata\.google|metadata\.aws|100\.100\.100\.200/gi, severity: 'CRITICAL', desc: 'Cloud metadata endpoint (SSRF)', all: true },

    // ── Category 16b: Trust Boundary Violation ──
    { id: 'TRUST_CALENDAR_EXEC', cat: 'trust-boundary', regex: /(?:calendar|event|invite|schedule|appointment)[^]*?(?:exec|spawn|system|eval|child_process|run\s+command)/gis, severity: 'CRITICAL', desc: 'Trust boundary: calendar → code execution', codeOnly: true },
    { id: 'TRUST_EMAIL_EXEC', cat: 'trust-boundary', regex: /(?:email|mail|inbox|message)[^]*?(?:exec|spawn|system|eval|child_process|run\s+command)/gis, severity: 'CRITICAL', desc: 'Trust boundary: email → code execution', codeOnly: true },
    { id: 'TRUST_WEB_EXEC', cat: 'trust-boundary', regex: /(?:fetch|axios|request|http\.get|web_fetch)[^]*?(?:eval|exec|spawn|Function|child_process)/gis, severity: 'HIGH', desc: 'Trust boundary: web content → code execution', codeOnly: true },
    { id: 'TRUST_NOSANDBOX', cat: 'trust-boundary', regex: /sandbox\s*[:=]\s*(?:false|off|none|disabled)|"sandboxed"\s*:\s*false/gi, severity: 'HIGH', desc: 'Trust boundary: sandbox disabled', all: true },

    // ── Category 16c: Advanced Exfiltration ──
    { id: 'ZOMBIE_STATIC_URL', cat: 'advanced-exfil', regex: /(?:https?:\/\/[^\s'"]+\/)[a-z]\d+[^\s'"]*(?:\s*,\s*['"]https?:\/\/[^\s'"]+\/[a-z]\d+){3,}/gi, severity: 'CRITICAL', desc: 'ZombieAgent: static URL array exfil', codeOnly: true },
    { id: 'ZOMBIE_CHAR_MAP', cat: 'advanced-exfil', regex: /(?:charAt|charCodeAt|split\s*\(\s*['"]['"]?\s*\))[^;]*(?:url|fetch|open|request|get)/gi, severity: 'HIGH', desc: 'ZombieAgent: character mapping to URL', codeOnly: true },
    { id: 'ZOMBIE_LOOP_FETCH', cat: 'advanced-exfil', regex: /(?:for|while|forEach|map)\s*\([^)]*\)\s*\{[^}]*(?:fetch|open|Image|XMLHttpRequest|navigator\.sendBeacon)/gi, severity: 'HIGH', desc: 'ZombieAgent: loop-based URL exfil', codeOnly: true },
    { id: 'EXFIL_BEACON', cat: 'advanced-exfil', regex: /navigator\.sendBeacon|new\s+Image\(\)\.src\s*=/gi, severity: 'HIGH', desc: 'Tracking pixel/beacon exfil', codeOnly: true },
    { id: 'EXFIL_DRIP', cat: 'advanced-exfil', regex: /(?:slice|substring|substr)\s*\([^)]*\)[^;]*(?:fetch|post|send|request)/gi, severity: 'HIGH', desc: 'Drip exfiltration: sliced data', codeOnly: true },

    // ── Category 16d: Safeguard Bypass ──
    { id: 'REPROMPT_URL_PI', cat: 'safeguard-bypass', regex: /[?&](?:q|prompt|message|input|query|text)\s*=\s*[^&]*(?:ignore|system|execute|admin|override)/gi, severity: 'CRITICAL', desc: 'URL parameter prompt injection', all: true },
    { id: 'REPROMPT_DOUBLE', cat: 'safeguard-bypass', regex: /(?:run|execute|do)\s+(?:it\s+)?(?:twice|two\s+times|again|a\s+second\s+time)\s+(?:and\s+)?(?:compare|check|verify)/gi, severity: 'HIGH', desc: 'Double-execution safeguard bypass', docOnly: true },
    { id: 'REPROMPT_RETRY', cat: 'safeguard-bypass', regex: /(?:if\s+(?:it\s+)?(?:fails?|blocked|denied|refused)|on\s+error)\s*[,:]?\s*(?:try\s+again|retry|repeat|resubmit|use\s+different\s+wording)/gi, severity: 'HIGH', desc: 'Retry-on-block safeguard bypass', docOnly: true },
    { id: 'BYPASS_REPHRASE', cat: 'safeguard-bypass', regex: /(?:rephrase|reword|reformulate|reframe)\s+(?:the\s+)?(?:request|query|prompt|question)\s+(?:to\s+)?(?:avoid|bypass|circumvent|get\s+around)/gi, severity: 'CRITICAL', desc: 'Instruction to rephrase to avoid filters', docOnly: true },

    // ── ClawHavoc Campaign IoCs ──
    { id: 'HAVOC_AMOS', cat: 'cve-patterns', regex: /(?:AMOS|Atomic\s*Stealer|socifiapp)/gi, severity: 'CRITICAL', desc: 'ClawHavoc: AMOS/Atomic Stealer', all: true },
    { id: 'HAVOC_AUTOTOOL', cat: 'cve-patterns', regex: /os\.system\s*\(\s*['"][^'"]*(?:\/dev\/tcp|nc\s+-e|ncat\s+-e|bash\s+-i)/g, severity: 'CRITICAL', desc: 'Python os.system reverse shell', codeOnly: true },
    { id: 'HAVOC_DEVTCP', cat: 'cve-patterns', regex: /\/dev\/tcp\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d+/g, severity: 'CRITICAL', desc: 'Reverse shell: /dev/tcp', all: true },

    // ── Sandbox/environment detection ──
    { id: 'SANDBOX', cat: 'malicious-code', regex: /process\.env\.CI\b|isDocker\b|isContainer\b|process\.env\.GITHUB_ACTIONS\b/g, severity: 'MEDIUM', desc: 'Sandbox/CI environment detection', codeOnly: true },

    // ── WebSocket / API Gateway Attacks ──
    { id: 'CVE_WS_NO_ORIGIN', cat: 'cve-patterns', regex: /(?:WebSocket|ws:\/\/|wss:\/\/)[^]*?(?:!.*origin|origin\s*[:=]\s*['"]?\*)/gis, severity: 'HIGH', desc: 'WebSocket without origin validation', codeOnly: true },
    { id: 'CVE_API_GUARDRAIL_OFF', cat: 'cve-patterns', regex: /exec\.approvals\.set|tools\.exec\.host\s*[:=]|elevated\s*[:=]\s*true/gi, severity: 'CRITICAL', desc: 'API-level guardrail disabling', all: true },

    // ── Category 17: Identity Hijacking ──
    // Detection patterns for agent identity file tampering
    // (verification logic is private; patterns are OSS for community protection)
    { id: 'SOUL_OVERWRITE', cat: 'identity-hijack', regex: /(?:write|overwrite|replace|cp|copy|scp|mv|move)\s+(?:[^\n]*\s)?(?:SOUL\.md|IDENTITY\.md)/gi, severity: 'CRITICAL', desc: 'Identity file overwrite/copy attempt', all: true, soulLock: true },
    { id: 'SOUL_REDIRECT', cat: 'identity-hijack', regex: />\s*(?:SOUL\.md|IDENTITY\.md)|(?:SOUL\.md|IDENTITY\.md)\s*</gi, severity: 'CRITICAL', desc: 'Identity file redirect/pipe', all: true, soulLock: true },
    { id: 'SOUL_SED_MODIFY', cat: 'identity-hijack', regex: /sed\s+(?:-i\s+)?[^\n]*(?:SOUL\.md|IDENTITY\.md)/gi, severity: 'CRITICAL', desc: 'sed modification of identity file', all: true, soulLock: true },
    { id: 'SOUL_ECHO_WRITE', cat: 'identity-hijack', regex: /echo\s+[^\n]*>\s*(?:SOUL\.md|IDENTITY\.md)/gi, severity: 'CRITICAL', desc: 'echo redirect to identity file', all: true, soulLock: true },
    { id: 'SOUL_PYTHON_WRITE', cat: 'identity-hijack', regex: /open\s*\(\s*['"]\S*(?:SOUL\.md|IDENTITY\.md)['"]\s*,\s*['"]w/gi, severity: 'CRITICAL', desc: 'Python write to identity file', codeOnly: true, soulLock: true },
    { id: 'SOUL_FS_WRITE', cat: 'identity-hijack', regex: /(?:writeFileSync|writeFile)\s*\(\s*[^\n]*(?:SOUL\.md|IDENTITY\.md)/gi, severity: 'CRITICAL', desc: 'Node.js write to identity file', codeOnly: true, soulLock: true },
    { id: 'SOUL_POWERSHELL_WRITE', cat: 'identity-hijack', regex: /(?:Set-Content|Out-File|Add-Content)\s+[^\n]*(?:SOUL\.md|IDENTITY\.md)/gi, severity: 'CRITICAL', desc: 'PowerShell write to identity file', all: true, soulLock: true },
    { id: 'SOUL_GIT_CHECKOUT', cat: 'identity-hijack', regex: /git\s+checkout\s+[^\n]*(?:SOUL\.md|IDENTITY\.md)/gi, severity: 'HIGH', desc: 'git checkout of identity file', all: true, soulLock: true },
    { id: 'SOUL_CHFLAGS_UNLOCK', cat: 'identity-hijack', regex: /chflags\s+(?:no)?uchg\s+[^\n]*(?:SOUL\.md|IDENTITY\.md)/gi, severity: 'HIGH', desc: 'Immutable flag toggle on identity file', all: true, soulLock: true },
    { id: 'SOUL_ATTRIB_UNLOCK', cat: 'identity-hijack', regex: /attrib\s+[-+][rR]\s+[^\n]*(?:SOUL\.md|IDENTITY\.md)/gi, severity: 'HIGH', desc: 'Windows attrib on identity file', all: true, soulLock: true },
    { id: 'SOUL_SWAP_PERSONA', cat: 'identity-hijack', regex: /(?:swap|switch|change|replace)\s+(?:the\s+)?(?:soul|persona|identity|personality)\s+(?:file|to|with|for)/gi, severity: 'CRITICAL', desc: 'Persona swap instruction', docOnly: true, soulLock: true },
    { id: 'SOUL_EVIL_FILE', cat: 'identity-hijack', regex: /SOUL_EVIL\.md|IDENTITY_EVIL\.md|EVIL_SOUL|soul[_-]?evil/gi, severity: 'CRITICAL', desc: 'Evil persona file reference', all: true, soulLock: true },
    { id: 'SOUL_HOOK_SWAP', cat: 'identity-hijack', regex: /(?:hook|bootstrap|init)\s+[^\n]*(?:swap|replace|override)\s+[^\n]*(?:SOUL|IDENTITY|persona)/gi, severity: 'CRITICAL', desc: 'Hook-based identity swap at bootstrap', all: true, soulLock: true },
    { id: 'SOUL_NAME_OVERRIDE', cat: 'identity-hijack', regex: /(?:your\s+name\s+is|you\s+are\s+now|call\s+yourself|from\s+now\s+on\s+you\s+are)\s+(?!the\s+(?:user|human|assistant))/gi, severity: 'HIGH', desc: 'Agent name/identity override', docOnly: true, soulLock: true },
    { id: 'SOUL_MEMORY_WIPE', cat: 'identity-hijack', regex: /(?:wipe|clear|erase|delete|remove|reset)\s+(?:all\s+)?(?:your\s+)?(?:memory|memories|MEMORY\.md|identity|soul)/gi, severity: 'CRITICAL', desc: 'Memory/identity wipe instruction', docOnly: true, soulLock: true },

    // ── Category 18: Config Impact Analysis ──
    { id: 'CFG_OPENCLAW_WRITE', cat: 'config-impact', regex: /(?:write|writeFile|writeFileSync|fs\.write)\s*\([^)]*openclaw\.json/gi, severity: 'CRITICAL', desc: 'Direct write to openclaw.json', codeOnly: true },
    { id: 'CFG_EXEC_APPROVALS_OFF', cat: 'config-impact', regex: /(?:exec\.approvals?|approvals?)\s*[:=]\s*['"](off|false|disabled|none)['"]/gi, severity: 'CRITICAL', desc: 'Disable exec approvals via config', all: true },
    { id: 'CFG_HOOKS_MODIFY', cat: 'config-impact', regex: /hooks\.internal\.entries\s*[:=]|hooks\.internal\s*[:=]\s*\{/gi, severity: 'HIGH', desc: 'Modify hooks.internal configuration', codeOnly: true },
    { id: 'CFG_EXEC_HOST_GW', cat: 'config-impact', regex: /tools\.exec\.host\s*[:=]\s*['"]gateway['"]/gi, severity: 'CRITICAL', desc: 'Set exec host to gateway (bypass sandbox)', all: true },
    { id: 'CFG_SANDBOX_OFF', cat: 'config-impact', regex: /(?:sandbox|sandboxed|containerized)\s*[:=]\s*(?:false|off|none|disabled|0)/gi, severity: 'CRITICAL', desc: 'Disable sandbox via configuration', all: true },
    { id: 'CFG_TOOL_OVERRIDE', cat: 'config-impact', regex: /(?:tools|capabilities)\s*\.\s*(?:exec|write|browser|web_fetch)\s*[:=]\s*\{[^}]*(?:enabled|allowed|host)/gi, severity: 'HIGH', desc: 'Override tool security settings', codeOnly: true },

    // ── Category 21: PII Exposure (OWASP LLM02 / LLM06) ──
    // A. Hardcoded PII — actual PII values in code/config (context-aware to reduce FP)
    { id: 'PII_HARDCODED_CC', cat: 'pii-exposure', regex: /(?:card|cc|credit|payment|pan)[_\s.-]*(?:num|number|no)?\s*[:=]\s*['"`]\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3,4}['"`]/gi, severity: 'CRITICAL', desc: 'Hardcoded credit card number', codeOnly: true },
    { id: 'PII_HARDCODED_SSN', cat: 'pii-exposure', regex: /(?:ssn|social[_\s-]*security|tax[_\s-]*id)\s*[:=]\s*['"`]\d{3}-?\d{2}-?\d{4}['"`]/gi, severity: 'CRITICAL', desc: 'Hardcoded SSN/tax ID', codeOnly: true },
    { id: 'PII_HARDCODED_PHONE', cat: 'pii-exposure', regex: /(?:phone|tel|mobile|cell|fax)[_\s.-]*(?:num|number|no)?\s*[:=]\s*['"`][+]?[\d\s().-]{7,20}['"`]/gi, severity: 'HIGH', desc: 'Hardcoded phone number', codeOnly: true },
    { id: 'PII_HARDCODED_EMAIL', cat: 'pii-exposure', regex: /(?:email|e-mail|user[_\s-]*mail|contact)\s*[:=]\s*['"`][a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}['"`]/gi, severity: 'HIGH', desc: 'Hardcoded email address', codeOnly: true },

    // B. PII output/logging — code that outputs or transmits PII-like variables
    { id: 'PII_LOG_SENSITIVE', cat: 'pii-exposure', regex: /(?:console\.log|console\.info|console\.warn|logger?\.\w+|print|puts)\s*\([^)]*\b(?:ssn|social_security|credit_card|card_number|cvv|cvc|passport|tax_id|date_of_birth|dob)\b/gi, severity: 'HIGH', desc: 'PII variable logged to console', codeOnly: true },
    { id: 'PII_SEND_NETWORK', cat: 'pii-exposure', regex: /(?:fetch|axios|request|http|post|put|send)\s*\([^)]*\b(?:ssn|social_security|credit_card|card_number|cvv|passport|bank_account|routing_number)\b/gi, severity: 'CRITICAL', desc: 'PII variable sent over network', codeOnly: true },
    { id: 'PII_STORE_PLAINTEXT', cat: 'pii-exposure', regex: /(?:writeFile|writeFileSync|appendFile|fs\.write|fwrite)\s*\([^)]*\b(?:ssn|social_security|credit_card|card_number|cvv|passport|tax_id|bank_account)\b/gi, severity: 'HIGH', desc: 'PII stored in plaintext file', codeOnly: true },

    // C. Shadow AI — unauthorized LLM API calls (data leaks to external AI)
    { id: 'SHADOW_AI_OPENAI', cat: 'pii-exposure', regex: /(?:api\.openai\.com|https:\/\/api\.openai\.com)\s*|openai\.(?:chat|completions|ChatCompletion)/gi, severity: 'HIGH', desc: 'Shadow AI: OpenAI API call', codeOnly: true },
    { id: 'SHADOW_AI_ANTHROPIC', cat: 'pii-exposure', regex: /(?:api\.anthropic\.com|https:\/\/api\.anthropic\.com)\s*|anthropic\.(?:messages|completions)/gi, severity: 'HIGH', desc: 'Shadow AI: Anthropic API call', codeOnly: true },
    { id: 'SHADOW_AI_GENERIC', cat: 'pii-exposure', regex: /\/v1\/(?:chat\/completions|completions|embeddings|models)\b.*(?:fetch|axios|request|http)|(?:fetch|axios|request|http)\s*\([^)]*\/v1\/(?:chat\/completions|completions|embeddings)/gi, severity: 'MEDIUM', desc: 'Shadow AI: generic LLM API endpoint', codeOnly: true },

    // ── Category 22: Human-Agent Trust Exploitation (OWASP ASI09) ──
    // Trust Defense: detect authority claims, trust exploitation, and admin impersonation
    { id: 'TRUST_AUTHORITY_CLAIM', cat: 'trust-exploitation', regex: /(?:as\s+(?:a|the|your)\s+)?(?:senior|lead|chief|head)\s+(?:admin|administrator|developer|engineer|architect)\s*[,.]?\s*(?:I\s+)?(?:authorize|override|approve|grant|order|direct|instruct)\s+(?:you\s+to\s+)?/gi, severity: 'HIGH', desc: 'Trust: authority role claim to override safety', docOnly: true },
    { id: 'TRUST_CREATOR_CLAIM', cat: 'trust-exploitation', regex: /(?:as\s+)?(?:your\s+)?(?:creator|maker|developer|owner|master|administrator)\s*[,.]?\s*(?:I\s+)?(?:need|want|require|demand|order)\s+(?:you\s+to\s+)?(?:bypass|disable|ignore|remove|skip|override)\s+(?:the\s+)?(?:safety|filter|restriction|limit|guardrail|content\s+filter)/gi, severity: 'CRITICAL', desc: 'Trust: creator impersonation to disable safety', docOnly: true },
    { id: 'TRUST_AUDIT_EXCUSE', cat: 'trust-exploitation', regex: /(?:this\s+is\s+)?(?:an?\s+)?(?:official|authorized|legitimate)\s+(?:security\s+)?(?:audit|test|assessment|review|evaluation)\s*[-—:]?\s*(?:disable|bypass|remove|skip|ignore|override)\s+(?:all\s+)?(?:safety|security|restriction|filter|limit|guardrail)/gi, severity: 'CRITICAL', desc: 'Trust: fake audit excuse for safety bypass', docOnly: true },
    { id: 'TRUST_PARTNER_EXPLOIT', cat: 'trust-exploitation', regex: /(?:we(?:'re|\s+are)\s+)?(?:equal\s+)?partners?\s*[,.]?\s*(?:you\s+should|so\s+)?(?:trust\s+me|share|remove|disable|ignore|bypass)\s+(?:all\s+)?(?:the\s+)?(?:secret|key|restriction|safety|limit|filter|guardrail|password)/gi, severity: 'CRITICAL', desc: 'Trust exploitation: weaponizing partnership trust', docOnly: true },
    { id: 'TRUST_UNCONDITIONAL', cat: 'trust-exploitation', regex: /partners?\s+(?:trust|should\s+trust)\s+(?:each\s+other\s+)?(?:unconditionally|completely|fully|without\s+(?:limit|restriction|question))/gi, severity: 'HIGH', desc: 'Trust exploitation: unconditional trust demand', docOnly: true },
    { id: 'TRUST_COMPLY_DEMAND', cat: 'trust-exploitation', regex: /(?:you\s+must\s+)?comply\s+with\s+(?:administrative|admin|my|these)\s+(?:directives?|orders?|commands?|instructions?)\s+without\s+(?:question|hesitation|restriction)/gi, severity: 'HIGH', desc: 'Trust: compliance demand without question', docOnly: true },

    // D. PII collection instructions in docs (extends LEAK_COLLECT_PII)
    { id: 'PII_ASK_ADDRESS', cat: 'pii-exposure', regex: /(?:collect|ask\s+for|request|get|require)\s+(?:the\s+)?(?:user'?s?\s+)?(?:home\s+)?(?:address|street|zip\s*code|postal\s*code|residence)/gi, severity: 'HIGH', desc: 'PII collection: home address', docOnly: true },
    { id: 'PII_ASK_DOB', cat: 'pii-exposure', regex: /(?:collect|ask\s+for|request|get|require)\s+(?:the\s+)?(?:user'?s?\s+)?(?:date\s+of\s+birth|birth\s*date|birthday|DOB|age)/gi, severity: 'HIGH', desc: 'PII collection: date of birth', docOnly: true },
    { id: 'PII_ASK_GOV_ID', cat: 'pii-exposure', regex: /(?:collect|ask\s+for|request|get|require)\s+(?:the\s+)?(?:user'?s?\s+)?(?:passport|driver'?s?\s+licen[sc]e|national\s+id|my\s*number|マイナンバー|国民健康保険|social\s+insurance)/gi, severity: 'CRITICAL', desc: 'PII collection: government ID', docOnly: true },

    // ── Category 99: Auto-Generated Refinements (Phase 54) ──
    { id: 'AUTO_REFINE_ZERO_WIDTH', cat: 'prompt-worm', regex: /[\u200b\u200c\u200d\uFEFF]+.*(?:ignore|forget|override|bypass)/gi, severity: 'CRITICAL', desc: 'Zero-Width Prompt Injection Worm', all: true },
    { id: 'AUTO_REFINE_MCP_REBIND', cat: 'mcp-security', regex: /localhost(?:\:\d+)?\/.*(?:rebind|hijack|shadow)/gi, severity: 'CRITICAL', desc: 'Shadow MCP Localhost Rebinding Attack', all: true },
    { id: 'AUTO_REFINE_SOUL_FREEZE', cat: 'identity-hijack', regex: /(?:chattr\s+\+i|chflags\s+uchg)\s+(?:[^\n]*\s)?(?:SOUL\.md|IDENTITY\.md)/gi, severity: 'CRITICAL', desc: 'Identity Freeze Attack via Immutable Flags', all: true },
    // ── Category 23: Vector DB & AI Memory Injection (CVE-2026-26030) ──
    { id: 'VDB_NOSQL_INJECT', cat: 'vdb-injection', regex: /(?:\$where|\$ne|\$gt|\$regex)\s*[:=]\s*(?:req\.|input|caller|args|params)/gi, severity: 'CRITICAL', desc: 'Vector DB/NoSQL injection via caller input', codeOnly: true },
    { id: 'VDB_SK_RCE_FILTER', cat: 'cve-patterns', regex: /(?:InMemoryVectorStore|VectorStore|Pinecone|Milvus)[^]*?\.filter\s*\(\s*(?:req\.|input|caller|args)/gis, severity: 'CRITICAL', desc: 'CVE-2026-26030: Semantic Kernel VectorStore RCE filter bypass', codeOnly: true },
    // ── Category 24: Claude Code Vulnerabilities (2026) ──
    { id: 'CVE_CLAUDE_INFO_DISC', cat: 'cve-patterns', regex: /sk-ant-api[a-zA-Z0-9_\-]{20,}/gi, severity: 'CRITICAL', desc: 'CVE-2026-21852: Anthropic API Key Leak (Claude Code Info Disclosure)', codeOnly: true },
    { id: 'CVE_CLAUDE_PRIVESC', cat: 'cve-patterns', regex: /[a-zA-Z0-9_\-\.]+\.hook\.js.*host.*privilege/gi, severity: 'CRITICAL', desc: 'CVE-2026-25725: Claude Code Privilege Escalation Hook', codeOnly: true },
    { id: 'CVE_CLAUDE_CODE_INJ', cat: 'cve-patterns', regex: /claude\.hooks\.[^]*?exec/gis, severity: 'CRITICAL', desc: 'CVE-2025-59536: Claude Code Injection via untrusted hook', codeOnly: true },

    // ── Category 25: Moltbook Exploits (2026) ──
    { id: 'MOLTBOOK_REVERSE_PI', cat: 'prompt-injection', regex: /(?:moltbook|social)\s+(?:post|message)[\s\S]{0,100}(?:ignore|forget|override|execute|system\s+prompt)/gi, severity: 'CRITICAL', desc: 'Moltbook Reverse Prompt Injection', all: true },
    { id: 'MOLTBOOK_SUPABASE_LEAK', cat: 'secret-detection', regex: /sbp_[a-zA-Z0-9]{36,}/g, severity: 'CRITICAL', desc: 'Supabase API Key (Moltbook 1.5M Leak pattern)', all: true },
];

module.exports = { PATTERNS };
