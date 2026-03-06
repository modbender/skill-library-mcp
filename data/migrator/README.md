# OpenClaw Migrator 📦

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## English

Securely migrate your OpenClaw Agent (config, memory, skills) between machines.

### 🚀 Features
- 🔒 **High Security**: Uses AES-256-GCM encryption with integrity verification.
- 🛣️ **Cross-Generation Compatibility (v1.1.0)**: Supports seamless migration from legacy `~/.clawdbot` to the new `~/.openclaw` standard.
- 🛣️ **Path Self-healing**: Automatically repairs absolute paths and workspace roots during restoration to ensure zero-config restarts.
- 📦 **Smart Packaging**: Captures host metadata (`node`, `platform`, `arch`) to prevent runtime mismatches on the new machine.

### 🆕 What's New in v1.1.0
- **Rebrand Ready**: Fully compatible with OpenClaw 2026.2.x rebrand and path migrations.
- **Security Hardening**: Integrated Path Traversal filtering in `restore.js` to prevent malicious archive extraction.
- **Environment Manifest**: Injects system context into `.oca` archives for smarter pre-flight checks.
- **Deep Path Healing**: Recursively repairs absolute paths in `openclaw.json` when `$HOME` changes.

### 🛠️ Installation
```bash
git clone https://github.com/anchor-jevons/openclaw-migrator
cd openclaw-migrator
npm install
npm link
```

### 📖 Usage
**Export (Old Machine):**
```bash
migrator export -o my-agent.oca --password "your-secret-password"
```

**Import (New Machine):**
```bash
migrator import -i my-agent.oca --password "your-secret-password"
```

---

<a name="中文"></a>
## 中文

安全地在不同机器之间迁移您的 OpenClaw 智能体（配置、记忆、技能）。

### 🚀 功能特性
- 🔒 **高安全性**：采用 AES-256-GCM 加密算法，并具备数据完整性校验。
- 🔄 **跨版本兼容 (v1.1.0)**：支持从旧版 `~/.clawdbot` 到新版 `~/.openclaw` 的平滑迁移。
- 🛣️ **路径自愈**：在恢复过程中自动修正绝对路径（如 workspace 根目录），确保迁移后无需手动修改配置。
- 📦 **环境感知**：自动捕获宿主机元数据（Node版本、平台、架构），防止目标环境不兼容。
- 🛡️ **安全加固**：内置路径遍历（Path Traversal）防御，拦截恶意归档文件。

### 🛠️ 安装方法
```bash
git clone https://github.com/anchor-jevons/openclaw-migrator
cd openclaw-migrator
npm install
npm link
```

### 📖 使用指南
**导出 (旧机器):**
```bash
migrator export -o my-agent.oca --password "你的加密密码"
```

**导入 (新机器):**
```bash
migrator import -i my-agent.oca --password "你的加密密码"
```

## ⚖️ License
MIT
