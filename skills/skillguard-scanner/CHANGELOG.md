# Changelog

## 1.1.0 (2026-02-11)

- Added security policy engine with human-readable risk explanations per finding
- Each finding now includes "⚠ WHY this is risky" + "🛡 ACTION to take"
- Policy references real-world incidents (ClawHavoc, Atomic Stealer, memory poisoning)
- JSON output enriched with policy blurbs for programmatic consumption
- Thanks to @neynar on Moltbook for the suggestion!

## 1.0.0 (2026-02-11)

Initial release.

- Static code analysis: reverse shells, obfuscation, exfiltration, credential access
- Suspicious prerequisites detection (ClawHavoc attack vector)
- Memory poisoning detection (SOUL.md, MEMORY.md, AGENTS.md writes)
- Typosquatting check (Levenshtein distance ≤ 2)
- False positive likelihood per finding
- JSON + console output
- Modes: `--skill`, `--check-name`, `--fetch-clawhub`
