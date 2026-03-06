# Skill Security Scanner 🔍

**Security scanning tool for OpenClaw skills - detect malware, analyze permissions, and get trust scores before installing.**

[![OpenClaw](https://img.shields.io/badge/OpenClaw-Security-blue)](https://openclaw.ai)
[![ClawHub](https://img.shields.io/badge/Available-ClawHub-green)](https://clawhub.com)
[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange)](https://github.com/Steffano198/skill-security-scanner)
[![GitHub stars](https://img.shields.io/github/stars/Steffano198/skill-security-scanner)](https://github.com/Steffano198/skill-security-scanner/stargazers)

> **NEW**: Now available on ClawHub! Install directly with `clawhub install skill-security-scanner`

---

## ⚡ Quick Start

```bash
# Option 1: Install via ClawHub (recommended)
clawhub install skill-security-scanner

# Option 2: Clone manually
git clone https://github.com/Steffano198/skill-security-scanner.git ~/.openclaw/skills/skill-security-scanner

# Scan a skill
./scripts/scan-skill.sh ~/.openclaw/skills/github
```

---

## 🔐 What is Skill Security Scanner?

**Skill Security Scanner** is a security tool for [OpenClaw](https://openclaw.ai) users to verify skills before installing them.

After the [ClawHavoc incident](https://www.authmind.com/post/openclaw-malicious-skills-agentic-ai-supply-chain) (February 2026, where 341 malicious skills were discovered), security is more critical than ever.

This scanner helps you:

- 📊 **Calculate Trust Score** (0-100)
- 🔍 **Detect Suspicious Patterns** 
- 📋 **Analyze Permissions** (bins, env vars)
- ⚠️ **Identify Risk Levels**
- 💡 **Get Clear Recommendations**

**No more blind trust** - scan every skill before you install.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Trust Score** | 0-100 score based on permissions, patterns, documentation |
| **Risk Level** | 🟢 Low / 🟡 Medium / 🟠 High / 🔴 Critical |
| **Permission Analysis** | Lists required bins and environment variables |
| **Pattern Detection** | Finds suspicious code patterns (network calls, obfuscation, etc.) |
| **Recommendations** | Clear advice on whether to use the skill |
| **OpenClaw Compatible** | Works seamlessly with your OpenClaw installation |

---

## 📊 Trust Score System

| Score | Risk | Action |
|-------|------|--------|
| 80-100 | 🟢 Low | Safe to use |
| 60-79 | 🟡 Medium | Review before use |
| 40-59 | 🟠 High | Use with caution |
| 0-39 | 🔴 Critical | Don't use |

### Score Factors

| Factor | Weight |
|--------|--------|
| Permission Scope | 30% |
| Code Patterns | 25% |
| Documentation Quality | 20% |
| Author Reputation | 15% |
| Update Frequency | 10% |

---

## 🚨 What It Detects

### High Risk Patterns
- 🌐 Network exfiltration attempts
- 🔑 Credential harvesting
- 💥 Destructive file operations
- 🔒 Obfuscated commands (base64, eval)

### Medium Risk Patterns
- 📦 Excessive permissions
- 🔗 Unknown third-party dependencies
- ⏰ Outdated (6+ months no updates)

### Green Flags ✅
- 🏷️ Official OpenClaw skill
- 🔓 Minimal permissions
- 📚 Clear documentation
- 👤 Known author

---

## 💻 Usage

### Basic Scan

```bash
# Scan any skill
./scripts/scan-skill.sh ~/.openclaw/skills/github

# Scan before installing from ClawHub
clawhub install cool-new-skill
./scripts/scan-skill.sh ~/.openclaw/skills/cool-new-skill
```

### Example Output

```
🔍 Scanning: github
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Trust Score: 95/100 (🟢 Low)

📋 Permissions:
   • bins: gh

✅ Positive Signs:
   • Official OpenClaw skill
   • Has proper metadata
   • Well documented

💡 Recommendation:
   Safe to use - well documented, standard permissions
```

---

## 📁 Project Structure

```
skill-security-scanner/
├── SKILL.md              # OpenClaw skill definition
├── README.md             # This file
├── LICENSE               # MIT License
├── scripts/
│   └── scan-skill.sh    # Main scanner script
└── examples/
    ├── scan-output.md   # Example outputs
    └── report.md        # Example reports
```

---

## 🛠️ Installation

### Option 1: ClawHub (Recommended)

```bash
# Install directly
clawhub install skill-security-scanner

# Update
clawhub update skill-security-scanner
```

### Option 2: Manual

```bash
# Clone to your OpenClaw skills folder
git clone https://github.com/Steffano198/skill-security-scanner.git ~/.openclaw/skills/skill-security-scanner
```

---

## 🔧 Configuration

No configuration needed! Just run the scanner on any skill path.

---

## 🤝 Contributing

Contributions are welcome! Here's how to help:

1. **Fork** the repo
2. **Create** a feature branch
3. **Submit** a pull request
4. **Report** issues

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 👤 Author

**Steff** (@Steffano198 / @DevSef)
- OpenClaw enthusiast
- Building tools for the community 🦞

---

## 🔗 Related Links

- [OpenClaw Official Site](https://openclaw.ai)
- [OpenClaw Documentation](https://docs.openclaw.ai)
- [ClawHub - Skill Registry](https://clawhub.com)
- [ClawHavoc Security Incident](https://www.authmind.com/post/openclaw-malicious-skills-agentic-ai-supply-chain)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [Awesome OpenClaw Skills](https://github.com/VoltAgent/awesome-openclaw-skills)

---

## 📈 SEO Keywords

OpenClaw, ClawHub, skill security, OpenClaw skills, AI assistant security, malware detection, OpenClaw malware, skill scanner, AI agent tools, OpenClaw plugins, AI assistant plugins, Claude Code, OpenAI automation, AI workflow, productivity tools, security scanner, trust score, skill verification, AI safety

---

## ⚠️ Disclaimer

This tool provides automated security analysis but cannot guarantee 100% accuracy. Always:

- Review skills manually before installing
- Check the author's reputation
- Start with sandboxed environments
- Monitor skill behavior after installation

**Stay safe** 🔒

---

*Built with ❤️ for the OpenClaw community*
