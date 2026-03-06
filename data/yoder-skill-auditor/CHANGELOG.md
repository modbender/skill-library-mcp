# Changelog

## v3.1.0 (2026-02-16)

### Security Advisory Remediations
- **Removed self-allowlist entry** - skill-auditor no longer allowlists itself; the PATTERN_DEF_FILTER handles self-scan suppression transparently
- **Relocated test fixtures** - Malicious test fixtures moved from `test-skills/` to `tests/`; excluded from published package via `.clawignore`
- **Removed auto-install capability** - `inspect.sh` no longer accepts `--install-if-safe` or auto-installs skills; it audits and recommends only
- **Documented PATTERN_DEF_FILTER** - Added comprehensive inline documentation explaining what the filter does, why it exists, and how each regex component works
- **Added TEST-FIXTURES-WARNING.md** - Clear documentation that test fixtures are intentionally malicious for detection testing
- **Added .clawignore** - Excludes `tests/` from the distributed ClawHub package

### Other
- Version bump to 3.1.0 across SKILL.md, CHANGELOG.md
- All 28 tests passing, self-audit clean (0 criticals)

## v3.0.0 (2026-02-16)

### New Security Checks (5 new, 18 total)
- **Check 14: Prompt Injection Detection** (CRITICAL) - THE killer feature. Scans SKILL.md and .md files for agent manipulation: "ignore previous instructions," role hijacking, stealth directives, hidden HTML comment instructions, zero-width character obfuscation.
- **Check 15: Download-and-Execute** (CRITICAL) - Detects `curl | bash`, `wget | sh`, `eval $(curl)`, download+chmod+execute chains, unsafe pip/npm installs from arbitrary URLs.
- **Check 16: Hidden Files** (WARNING) - Flags suspicious dotfiles (excluding standard .gitignore, .editorconfig, .eslintrc, .prettierrc).
- **Check 17: Env Var Exfiltration** (CRITICAL) - Catches scripts reading sensitive env vars (OPENAI_API_KEY, AWS_SECRET, etc.) AND making outbound network calls.
- **Check 18: Privilege Escalation** (CRITICAL) - Detects sudo commands, chmod 777/setuid, writes to system paths (/usr/local/bin, /etc/), chown root.

### New Test Fixtures (4 new, 12 total)
- `malicious-prompt-injection` - HTML comment injection + override directives
- `malicious-download-exec` - curl|bash and wget download-execute chains
- `malicious-privilege-escalation` - sudo + setuid + system path writes
- `clean-with-dotfiles` - Clean skill with .gitignore and .editorconfig (should PASS)

### Improvements
- Expanded PATTERN_DEF_FILTER for self-audit compatibility with all new check patterns
- MIT LICENSE added
- Version consistency across all files
- 28 test assertions (was 20)

## v2.0.1 (2026-02-11)

### Context-Aware Detection (Critical Fix)
- **Pattern-definition awareness** - Scanner no longer flags its own detection patterns as threats. Lines containing regex variable assignments (e.g., `CRED_PATTERNS='...'`), grep expressions, and inline comments about patterns are correctly identified as scanner infrastructure, not malicious activity.
- **Case-sensitivity fix** - Credential line extraction now uses case-insensitive matching consistently, matching the file-level detection behavior.
- **Comment filtering fix** - Inline comments containing security keywords (e.g., `# credential access`) no longer trigger false positives.
- **Expanded allowlist** - Added n8n, Qdrant, Moltbook, MCP, and other API integration skills that legitimately need credential access.

### Results
- Self-audit: 0 criticals (was 3 false positives in v2.0.0)
- All 6 Yoder skills: 0 criticals (was 11 false positives)
- All 5 malicious test fixtures: still correctly detected as FAIL
- Test suite: 20/20 pass

## v2.0.0 (2026-02-10)

### New Detection Capabilities
- **Crypto wallet detection** - Flags hardcoded ETH/BTC wallet addresses (potential drain attacks)
- **Dependency confusion / typosquatting** - Checks package.json/requirements.txt for suspicious or misspelled packages
- **Excessive permission scope** - Flags skills requesting >15 bins/env/config items
- **Telemetry/tracking detection** - Flags analytics SDKs, tracking pixels, phone-home behavior
- **Post-install hook detection** - Flags npm postinstall, pip setup.py install hooks
- **Symlink attack detection** - Flags symlink creation targeting sensitive system paths
- **Time bomb detection** - Flags date/time comparison logic that could trigger delayed payloads
- **Network scope analysis** - Categorizes internal vs external calls, flags unusual ports

### Trust Score v2
- Added 5th dimension: **Behavioral Score** (max 10 points) - checks rate limiting, error handling, input validation
- Rebalanced scoring: Security 35, Quality 22, Structure 18, Transparency 15, Behavioral 10
- **Comparative scoring** (`--compare`) - side-by-side analysis of two skills
- **Trend tracking** (`--save-trend` / `--trend`) - stores scores over time in trust_trends.json

### New Tools
- **diff-audit.sh** - Compare skill versions, highlight new/resolved security issues
- **benchmark.sh** - Run auditor against a corpus of skills with aggregate statistics

### Test Suite
- Expanded from 12 to 20 assertions
- Added 4 new test fixtures (crypto, timebomb, symlink, clean-network)
- 8 test skills total (5 malicious, 3 clean)

### Other
- Self-audit clean (PASS verdict on itself)
- Full documentation update

## v1.1.0

- Context-aware detection (docs vs scripts)
- Allowlist system with auto-detect
- Trust score calculator (4-dimension, 0-100 scale)
- ClawHub pre-install inspector
- Markdown report generator
- JSON output mode for all tools
- Comprehensive test suite (12 assertions, 5 test skills)
- Fixed all false positives from v1.0

## v1.0.0

- Initial security and quality audit
- Credential harvesting detection
- Exfiltration URL detection
- Batch scanning
