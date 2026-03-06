# Changelog

All notable changes to the Skill Auditor will be documented here.

Follow the project on GitHub for update notifications. Updates are manual — download, scan, replace.

## [2.1.0] - 2026-02-09

### Added
- **Sleeper Agent Detection** — 7 new patterns for delayed/conditional malicious execution
  - Time-based triggers ("after N days/weeks")
  - Keyword triggers ("when user says X")
  - Date triggers (future activation dates)
  - Hidden memory writes ("secretly add")
  - Counter triggers ("after N messages")
  - Dormant behavior patterns
- **Risky Agent Social Network Detection** — 6 new patterns
  - Moltbook/Molthub (known breach: 1.5M API tokens leaked)
  - FourClaw network
  - AgentVerse connections
  - Generic agent network registration
  - Inter-agent messaging patterns
  - Shared/collective memory across agents
- **Supply Chain Risk Detection** — 4 new patterns
  - `curl | bash` pipe execution
  - Remote script downloads (.sh, .py, .js)
  - npx/npm exec without explicit install
  - pip install from URL
- New reference file: `references/blocklist-domains.md`

## [2.0.0] - 2026-02-07

### Added
- **Python AST Dataflow Analysis** — traces data from sensitive sources to dangerous sinks
- **VirusTotal Integration** — binary malware scanning (optional, requires API key)
- **LLM Semantic Analysis** — AI-powered intent matching (optional)
- **Detection Modes** — `--mode strict|balanced|permissive`
- **SARIF Output** — `--format sarif` for GitHub Code Scanning
- **YARA Rules** — converted patterns to YARA format in `rules/default.yar`
- Modular analyzer architecture (`scripts/analyzers/`)
- `--fail-on-findings` flag for CI/CD

### Changed
- Python AST now uses Python subprocess (no Node.js native deps required)
- Install: `pip install tree-sitter tree-sitter-python`

## [1.0.0] - 2026-01-31

### Added
- Initial release
- Static analysis scanner for local directories and GitHub URLs
- Visual threat report with threat gauge, accuracy score, publisher info
- Prompt injection detection
- Data exfiltration detection (file access, network, env vars, credentials)
- Obfuscation detection (base64, hex, string concat, dynamic imports)
- Shell/command execution detection
- Persistence mechanism detection
- Integrity verification against source (SHA-256)
- False positive reference guide
- License file URL grouping (reduces noise, preserves prompt injection detection)
- Known limitations documented
- 🔍 Details / ✅ Install / ❌ Pass workflow after every scan
