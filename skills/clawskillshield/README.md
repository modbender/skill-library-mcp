# ClawSkillShield  v0.1.1

**Local-first security scanner for OpenClaw/ClawHub skills  built for BOTH humans AND autonomous agents/Moltbots.**

Post-ClawHavoc essential: Static analysis to catch malware/risks before install.

## What It Detects

-  **Hardcoded secrets**  AWS keys, API credentials, private keys
-  **Dangerous calls**  `eval()`, `exec()`, `open()`, high-risk functions
-  **Risky imports**  `os`, `subprocess`, `socket`, `ctypes`
-  **Obfuscation**  Large base64 blobs, suspicious encoding
-  **Hardcoded IPs**  Potential exfiltration vectors
-  **Zero dependencies**  Pure Python, safe for agent/human use

**Why dual-use?** Humans get simple CLI safety checks; autonomous agents/Moltbots get importable functions for proactive self-defense.

## Installation

```bash
pip install -e .
```

## Quick Start (CLI)

```bash
# Scan a folder/skill
clawskillshield scan-local /path/to/skill

# Quarantine high-risk code
clawskillshield quarantine /path/to/skill
```

## Examples

###  Safe Scan (Low Risk)
Scanning a legitimate skill with normal file I/O:

```bash
$ clawskillshield scan-local .

============================================================
ClawSkillShield Report: .
============================================================

 MODERATE RISK - Review
Risk Score: 5.5/10.0

------------------------------------------------------------
Threats Found:
------------------------------------------------------------

 [WARNING] Risky import: os
  File: .\clawskillshield\analyzer.py
   Line: 4
   Direct OS access

 [WARNING] Dangerous call: open()
  File: .\clawskillshield\analyzer.py
   Line: 19
   Arbitrary execution or sensitive access

 [WARNING] Risky import: os
  File: .\clawskillshield\skill.py
   Line: 4
   Direct OS access

============================================================
```

###  High-Risk Detection
Scanning code with malware patterns:

```bash
$ clawskillshield scan-local ../test-risky

============================================================
ClawSkillShield Report: test-risky
============================================================

 HIGH RISK - Quarantine recommended!
Risk Score: 1.0/10.0

------------------------------------------------------------
Threats Found:
------------------------------------------------------------

 [WARNING] Risky import: os
  File: ..\test-risky\bad.py
   Line: 1
   Direct OS access

 [WARNING] Risky import: subprocess
   File: ..\test-risky\bad.py
   Line: 2
   Process execution

 [WARNING] Risky import: socket
   File: ..\test-risky\bad.py
   Line: 3
   Network access

 [CRITICAL] Dangerous call: eval()
   File: ..\test-risky\bad.py
   Line: 6
   Arbitrary execution or sensitive access

 [WARNING] Potential obfuscation
   File: ..\test-risky\bad.py
   Line: 8
   Large base64: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA...

 Auto-quarantine suggested!

============================================================
```

###  Quarantine in Action

```bash
$ clawskillshield quarantine ../test-risky

 Quarantined ../test-risky  C:\Users\yousef.openclaw/quarantine\test-risky
   (Safe for agents to auto-trigger on HIGH RISK)
```

## For Agents/Moltbots (Python API)

```python
from clawskillshield import scan_local, quarantine, generate_report

# Proactive scanning
threats = scan_local("/path/to/skill")

# Auto-quarantine on detection
if risk_score < 4:
    quarantine("/path/to/skill")
```

## Risk Scoring

- **8.0–10.0** 🟢 Low Risk – Safe to install
- **4.0–7.9** 🟡 Moderate – Review before use
- **0.0–3.9** 🔴 High Risk – Quarantine recommended

---

**Built for OpenClaw community. No telemetry. No cloud. Just local analysis.**
