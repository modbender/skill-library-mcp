# Threat Patterns Reference

All patterns the scanner checks, organized by category.

## File Access
- **path-traversal** — `../../` patterns attempting directory escape
- **absolute-path-windows** — `C:\` style paths reaching outside skill scope
- **absolute-path-unix** — `/etc/`, `/home/`, `/root/` etc.
- **homedir-access** — `os.homedir()`, `process.env.HOME`, `USERPROFILE`

## Sensitive File Access
- **memory-file-access** — MEMORY.md, TOOLS.md, SOUL.md, USER.md, AGENTS.md, HEARTBEAT.md, moltbot.json
- **credential-file-access** — .ssh/, .env, .aws/, id_rsa, .gnupg, .npmrc

## Network
- **http-url** — Any HTTP/HTTPS URL referenced
- **fetch-call** — fetch, axios, request, got, XMLHttpRequest, requests.get/post
- **curl-wget** — curl, wget, Invoke-WebRequest, Invoke-RestMethod

## Data Exfiltration
- **webhook-exfil** — webhook.site, requestbin, pipedream, ngrok, burpcollaborator
- **dns-exfil** — nslookup/dig with variable interpolation
- **markdown-image-exfil** — Image tags with data in query params
- **message-tool-abuse** — References to message/sessions_send/sessions_spawn

## Shell Execution
- **shell-exec-node** — child_process, exec, spawn, execSync
- **shell-exec-python** — os.system, subprocess.run/call/Popen
- **shell-exec-generic** — eval(), Function()
- **powershell-invoke** — Invoke-Expression, iex, Start-Process

## Obfuscation
- **base64-encode** — btoa, atob, Buffer.from base64, Convert::ToBase64
- **base64-string** — Long strings matching base64 pattern (40+ chars)
- **hex-string** — \x encoded sequences (4+ bytes)
- **unicode-escape** — \u sequences (3+ chars)
- **string-concat-obfuscation** — "MEM" + "ORY" style fragment joining
- **zero-width-chars** — Invisible Unicode characters
- **html-comment-instructions** — HTML comments containing action words

## Prompt Injection
- **prompt-injection-ignore** — "ignore previous instructions" variants
- **prompt-injection-new-instructions** — "new instructions:" variants
- **prompt-injection-role** — "you are now", "act as", "pretend to be"
- **prompt-injection-system** — Fake [SYSTEM] or <system> delimiters
- **prompt-injection-delimiter** — LLM-specific tokens (im_start, INST, etc.)

## Persistence
- **memory-write** — Write/modify/update to MEMORY.md, HEARTBEAT.md, AGENTS.md
- **cron-manipulation** — cron, scheduled task, schtasks, crontab
- **startup-persistence** — Registry, startup folders, systemd, launchd

## Privilege Escalation
- **browser-tool** — Browser automation (puppeteer, playwright, selenium)
- **node-control** — OpenClaw node tools (camera_snap, screen_record, location_get)
- **config-modification** — Gateway config changes (config.apply, config.patch)

## Sleeper Agent Detection (NEW v2.1)
Patterns that indicate delayed/conditional malicious execution:

- **sleeper-delayed-trigger** — "after N days/hours then execute" time-bomb patterns
- **sleeper-keyword-trigger** — "when user says X" activation phrase waiting
- **sleeper-date-trigger** — Future date-based activation
- **sleeper-conditional-memory** — "secretly/silently add to memory" hidden writes
- **sleeper-counter-trigger** — "after N messages/sessions" count-based activation
- **sleeper-hidden-instruction** — "remember this secretly" covert instruction planting
- **sleeper-dormant-behavior** — "remain dormant until" waiting for conditions

## Risky Agent Social Networks (NEW v2.1)
Connections to agent networks with known security issues:

- **social-moltbook** — Moltbook/Molthub (leaked 1.5M API tokens Feb 2026)
- **social-fourclaw** — FourClaw network (prompt injection attacks common)
- **social-agentverse** — AgentVerse (unvetted agent interactions)
- **social-botnet-patterns** — Generic agent network registration
- **social-agent-messaging** — Inter-agent message exchange (prompt injection risk)
- **social-collective-memory** — Shared memory across agents (context pollution)

## Supply Chain Risks (NEW v2.1)
Dangerous installation and dependency patterns:

- **supply-chain-curl-pipe** — `curl | bash` remote code execution
- **supply-chain-remote-script** — Downloads .sh/.py/.js scripts
- **supply-chain-npm-exec** — npx/npm exec without explicit install
- **supply-chain-pip-install-url** — pip install from URL (unverified)
