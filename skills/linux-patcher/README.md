# Linux Patcher - OpenClaw Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-orange)](https://openclaw.ai)

Automated Linux server patching with PatchMon integration for OpenClaw.

## 🎯 Features

- ✅ **Ubuntu fully tested** - Production-ready
- ⚠️ **10+ distributions supported** - Debian, RHEL, AlmaLinux, Rocky, CentOS, Amazon Linux, SUSE (untested)
- 🔒 **Security-focused** - Restricted sudo, SSH key auth
- 🤖 **PatchMon integration** - Automatic host detection
- 🐳 **Smart Docker detection** - Auto-detects and updates containers
- 📊 **Visual workflow diagrams** - Easy to understand
- 🚀 **Chat-based interface** - "Update my servers" just works
- 🔄 **Dry-run mode** - Preview changes before applying

## 🚀 Quick Start

### Installation

```bash
# Option 1: Install from file
openclaw skill install linux-patcher.skill

# Option 2: Install from ClawHub (when published)
clawhub install linux-patcher

# Option 3: Install from this repo
git clone https://github.com/JGM2025/linux-patcher-skill
cd linux-patcher-skill
openclaw skill install .
```

### Initial Setup

```bash
# 1. Read the setup guide
cd ~/.openclaw/workspace/skills/linux-patcher
cat SETUP.md

# 2. Configure SSH keys
ssh-keygen -t ed25519 -C "openclaw-patching" -f ~/.ssh/id_openclaw
ssh-copy-id -i ~/.ssh/id_openclaw.pub admin@targethost

# 3. Configure PatchMon credentials
cp scripts/patchmon-credentials.example.conf ~/.patchmon-credentials.conf
nano ~/.patchmon-credentials.conf
chmod 600 ~/.patchmon-credentials.conf

# 4. Test with dry-run
scripts/patch-auto.sh --dry-run
```

### Usage

**Via OpenClaw chat (recommended):**

```
You: "Update my servers"
→ Updates packages + Docker containers automatically

You: "Update my servers, excluding docker"
→ Updates packages only, containers keep running

You: "What servers need patching?"
→ Queries PatchMon for update status
```

**Direct command line:**

```bash
# Automatic mode (PatchMon)
scripts/patch-auto.sh

# Skip Docker updates
scripts/patch-auto.sh --skip-docker

# Dry-run (preview only)
scripts/patch-auto.sh --dry-run

# Manual single host
scripts/patch-host-only.sh admin@webserver.example.com
scripts/patch-host-full.sh admin@webserver.example.com /opt/docker
```

## 📋 Prerequisites

### Required

- **OpenClaw** installed and running
- **SSH client** with key authentication
- **curl** and **jq** for PatchMon integration
- **Passwordless sudo** on target hosts (restricted to patching commands)
- **PatchMon** installed (required to check which hosts need updating)
  - Does NOT need to be on the OpenClaw host
  - Download: https://github.com/PatchMon/PatchMon
  - Docs: https://docs.patchmon.net

### For Automatic Host Detection

- **PatchMon server** (required for automatic mode)
  - **Important:** Does NOT need to be on the same server as OpenClaw
  - Install on any accessible server (separate host recommended)
  - OpenClaw queries PatchMon via HTTPS API
  - Download: https://github.com/PatchMon/PatchMon

### Optional

- **Docker** on target hosts (for container updates)
- **Docker Compose** on target hosts

**Note:** You can use this skill without PatchMon by manually specifying hosts, but automatic detection of which hosts need updates requires PatchMon.

## 📖 Documentation

Complete documentation is included in the skill:

- **[SKILL.md](SKILL.md)** - Main usage guide and features
- **[SETUP.md](SETUP.md)** - Complete setup with security best practices
- **[WORKFLOWS.md](WORKFLOWS.md)** - Visual workflow diagrams
- **[references/patchmon-setup.md](references/patchmon-setup.md)** - PatchMon installation

## 🌍 Supported Distributions

| Distribution | Package Manager | Status |
|--------------|-----------------|--------|
| Ubuntu | apt | ✅ Fully tested |
| Debian | apt | ⚠️ Supported (untested) |
| Amazon Linux 2 | yum | ⚠️ Supported (untested) |
| Amazon Linux 2023 | dnf | ⚠️ Supported (untested) |
| RHEL 7 | yum | ⚠️ Supported (untested) |
| RHEL 8+ | dnf | ⚠️ Supported (untested) |
| AlmaLinux | dnf | ⚠️ Supported (untested) |
| Rocky Linux | dnf | ⚠️ Supported (untested) |
| CentOS 7 | yum | ⚠️ Supported (untested) |
| CentOS 8+ | dnf | ⚠️ Supported (untested) |
| SUSE/OpenSUSE | zypper | ⚠️ Supported (untested) |

**Testing needed!** If you use this skill on untested distributions, please report results via issues.

## 🔒 Security

This skill is designed with security as a priority:

- **No passwords stored** - SSH key authentication only
- **Restricted sudo** - Only specific commands allowed (no `NOPASSWD: ALL`)
- **Principle of least privilege** - Minimal permissions granted
- **Audit trail** - All actions logged via syslog
- **Safe testing** - Dry-run mode available

See [SETUP.md](SETUP.md) for complete security configuration.

## 🎓 Examples

### Example 1: Automatic updates via PatchMon
```bash
# Query PatchMon, detect hosts, update everything
scripts/patch-auto.sh
```

### Example 2: Skip Docker updates
```bash
# Update packages only, leave containers running
scripts/patch-auto.sh --skip-docker
```

### Example 3: Test before applying
```bash
# Preview what would be updated
scripts/patch-auto.sh --dry-run

# Review output, then apply
scripts/patch-auto.sh
```

### Example 4: Via OpenClaw chat
```
You: "Update my servers"
OpenClaw: Queries PatchMon → Updates 4 hosts → Reports "✓ All hosts updated successfully"
```

### Example 5: Schedule automated patching
```bash
# Run nightly at 2 AM
cron add --name "Nightly Patching" \
  --schedule "0 2 * * *" \
  --task "cd ~/.openclaw/workspace/skills/linux-patcher && scripts/patch-auto.sh"
```

## 🤝 Contributing

Contributions welcome! Especially:

- Testing on untested distributions
- Bug reports and fixes
- Documentation improvements
- Feature requests

Please open an issue or pull request.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation:** See SKILL.md, SETUP.md, WORKFLOWS.md
- **Issues:** https://github.com/JGM2025/linux-patcher-skill/issues
- **OpenClaw Community:** https://discord.com/invite/clawd
- **PatchMon:** https://github.com/PatchMon/PatchMon

## 🎉 Acknowledgments

- Built for [OpenClaw](https://openclaw.ai)
- Integrates with [PatchMon](https://github.com/PatchMon/PatchMon)
- Inspired by the need for simple, secure server patching

---

**Note:** Always test in a non-production environment first, especially on untested distributions.
