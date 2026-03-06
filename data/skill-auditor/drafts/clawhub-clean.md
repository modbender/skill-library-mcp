ClawHub Listing - skill-auditor v2.1.0

Short Description (for search)
Security scanner that catches malicious skills before they steal your data. Detects credential theft, prompt injection, and hidden backdoors.

Full Description

Skill Auditor scans OpenClaw skills for security issues before you install them. It catches malicious patterns like credential theft, prompt injection, and hidden backdoors.

Works immediately â€" the core scanner needs zero setup. Just point it at a skill folder.

Optional deep analysis â€" enable AST dataflow tracking to trace how your data moves through code. The setup wizard handles installation on Windows, Mac, or Linux (no compiler needed).

What It Catches

- Skills trying to steal your API credentials
- Prompt injection attacks hidden in skill files 
- Suspicious network calls to data capture services
- Encoded payloads and obfuscated code
- Skills that lie about what they actually do

Quick Start

Scan a skill:
node scripts/scan-skill.js path/to/skill

Audit all installed skills:
node scripts/audit-installed.js

Enable advanced features:
node scripts/setup.js

Optional: AST Dataflow Analysis

For deeper analysis that traces data from source to sink:

pip install tree-sitter tree-sitter-python

No compiler needed â€" prebuilt packages work on all platforms.

New in v2.1

- Setup wizard with opt-in features
- Audit command scans all installed skills at once 
- Fewer false alarms on legitimate skills
- Tested against Cisco Talos security research

---

Changelog v2.1.0

Added
- Interactive setup wizard (`node scripts/setup.js`)
- Bulk audit for all installed skills (`node scripts/audit-installed.js`)
- Auto-scan hook for new skill installations (opt-in)
- Cross-platform tree-sitter install (no C++ compiler)

Improved
- Intent matching reduces false positives on legitimate skills
- Documentation files automatically downgraded in severity
- Better detection of dataflow from env vars to network calls

Tested
- Compared against Cisco's skill-scanner
- Catches prompt injection that Cisco missed
- Verified on Windows, macOS patterns