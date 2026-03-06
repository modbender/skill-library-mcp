---
name: senseguard
description: Semantic security scanner for OpenClaw skills. Detects prompt injection, data exfiltration, and hidden instructions that traditional code scanners miss. Use when user asks to scan skills, check skill safety, or run a security audit.
---

# SenseGuard

Scans OpenClaw skills for **natural language security threats** — the kind that VirusTotal and traditional code scanners cannot detect.

Traditional scanners see SKILL.md as a text file. SenseGuard sees it as **agent instructions** and checks for prompt injection, data exfiltration, obfuscation, and persistence attacks.

## How to Use

When the user asks to scan a skill:

```bash
python3 scripts/scanner.py --target <skill-name-or-path>
```

Options:
- `--target all` — scan all installed skills
- `--deep` — force LLM semantic analysis (Layer 2)
- `--no-cache` — skip cached results
- `--json` — output raw JSON for further processing

### Layer 2 (Semantic Analysis)

When `--json` output contains a `layer2_prompt` field, process it as a security audit task, then feed the JSON result back to generate the final score. This is how the LLM analyzes intent beyond regex patterns.

## Output

The scanner outputs a Markdown risk report with:
- Score (0-100) and rating: SAFE / CAUTION / DANGEROUS / MALICIOUS
- Findings with rule IDs, evidence text, and line numbers
- Actionable recommendations

For CRITICAL findings, clearly advise the user to take action.

## Key Differentiator

SenseGuard catches what VirusTotal cannot:
- `"ignore all previous instructions"` — prompt injection
- `curl -X POST` hidden in Markdown — data exfiltration
- Zero-width characters hiding commands — obfuscation
- `"modify MEMORY.md"` — persistence attacks

These are invisible to traditional malware scanners because they target the **AI agent**, not the operating system.
