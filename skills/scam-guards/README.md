# 🛡️ Scam Guards

**Real-time AI agent security guardian for OpenClaw.**

Scam Guards protects your agents from scams, malware, and prompt injection attacks by providing a continuous bodyguard service. It scans ClawHub skills before installation, verifies URLs and crypto wallets, and monitors agent behavior for psychological manipulation.

## 🚀 Installation

**Install globally via ClawHub:**
```bash
npx clawhub@latest install scam-guards
```

## 🛠️ Core Features

- **Skill Scanner**: `scripts/scan_skill.py` - Detects 341+ malicious patterns in ClawHub skills.
- **Phishing Detector**: `scripts/verify_url.py` - Offline domain and URL reputation verification.
- **Wallet Checker**: `scripts/check_wallet.py` - Validates crypto addresses against confirmed blacklists.
- **Behavior Monitor**: `scripts/monitor_agent.py` - Real-time PHI analysis for manipulation tactics.
- **Evidence Chain**: `scripts/evidence_chain.py` - SHA-256 linked audit trails for security incidents.
- **Report Generator**: `scripts/report_generator.py` - Structured Markdown security summaries.

## 📚 References
- [Scam Taxonomy](file://{baseDir}/references/scam-taxonomy.md)
- [Known Threat Patterns](file://{baseDir}/references/known-threats.md)
- [PHI Framework](file://{baseDir}/references/phi-dimensions.md)
- [Response Playbook](file://{baseDir}/references/response-playbook.md)

## ⚖️ License
Apache License 2.0
