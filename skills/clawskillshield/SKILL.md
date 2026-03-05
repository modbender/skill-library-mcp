# ClawSkillShield 🛡️

**Local-first security scanner for OpenClaw/ClawHub skills.**

## What It Does

- **Static analysis** for security risks and malware patterns
- **Detects**:
  - Hardcoded secrets (API keys, credentials, private keys)
  - Risky imports (`os`, `subprocess`, `socket`, `ctypes`)
  - Dangerous calls (`eval()`, `exec()`, `open()`)
  - Obfuscation (base64 blobs, suspicious encoding)
  - Hardcoded IPs
- **Risk scoring** (0–10) + detailed threat reports
- **Quarantine** high-risk skills automatically

## Dual-Use Design

- **CLI for humans**: Quick safety checks before installing skills
- **Agent API**: Importable functions for autonomous agents/Moltbots to proactively scan and quarantine risky skills (essential post-ClawHavoc)

## Quick Start

### CLI (Humans)
```bash
pip install -e .
clawskillshield scan-local /path/to/skill
clawskillshield quarantine /path/to/skill
```

### Python API (Agents)
```python
from clawskillshield import scan_local, quarantine

threats = scan_local("/path/to/skill")
if risk_score < 4:  # HIGH RISK
    quarantine("/path/to/skill")
```

## Zero Dependencies
Pure Python. No network calls. Runs entirely locally.

## Why This Matters
ClawHavoc demonstrated how easily malicious skills can slip into the ecosystem. ClawSkillShield provides a trusted, open-source defense layer—audit the code, run offline, stay safe.

---

**GitHub**: https://github.com/AbYousef739/clawskillshield  
**License**: MIT  
**Author**: Ab Yousef  
**Contact**: contact@clawskillshield.com
