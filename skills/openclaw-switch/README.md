# 🔀 OpenClaw Switch

> "The missing remote control for your AI Agents."

**OpenClaw Switch** 是一个为 OpenClaw 量身定制的模型管理与一键切换工具。它解决了手动修改 `openclaw.json` 容易导致格式错误并导致 Gateway 崩溃的痛点。

---

## ✨ 核心功能 (Features)

- **🚫 拒绝崩溃**: 采用 Python 原生解析 JSON，确保配置文件修改永远合法，彻底告别由于手动修改带来的格式错误。
- **📊 可视化 Failover**: 直观展示你的模型备份链（Fallback chain）。当主模型 (429/500) 报错时，一眼看出下一个接管的模型是谁。
- **🚀 丝滑切换**: 告别复杂的模型 ID，直接通过数字编号（如 `switch 2`）在不同供应商（Google, OpenAI, Kimi, etc.）之间秒切。
- **💓 路由透明**: 清晰显示 Heartbeat（心跳）和 Subagents（子智能体）当前路由的模型路径。
- **🛡️ 极致安全**: 纯本地运行，不联网，不上传 API Key，仅显示 Key 的前 8 位用于辨认。

---

## 🛠 安装指南 (Installation)

### 1. 克隆插件
进入你的 OpenClaw 技能目录并克隆本仓库：
```bash
cd ~/.openclaw/skills
git clone https://github.com/sarahmirrand001-oss/openclaw-switch.git
```

### 2. 激活命令 (重要)
为了能在任何地方直接使用 `openclaw-switch` 命令，你需要确保 OpenClaw 的 bin 目录在你的系统路径中。

**执行以下命令（适用于 macOS/Linux 的 ZSH 用户）：**
```bash
echo 'export PATH="$HOME/.openclaw/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

---

## 📖 使用手册 (Usage)

进入技能文件夹后运行脚本：

### 1. 查看当前状态
查看当前主模型、备份链以及心跳任务的配置。
```bash
bash scripts/openclaw-switch.sh status
```

### 2. 列出所有模型
获取所有已配置模型的数字编号。
```bash
bash scripts/openclaw-switch.sh list
```

### 3. 一键切换主模型
通过 `list` 命令得到的数字编号，快速切换主模型。
```bash
# 比如切换到列表中的第 2 个模型
bash scripts/openclaw-switch.sh switch 2
```

### 4. 查看备份逻辑
查看当主模型失效时，OpenClaw 会按什么顺序尝试其他模型。
```bash
bash scripts/openclaw-switch.sh fallback
```

---

## ⚙️ 进阶配置建议 (Best Practice)

建议在 `openclaw.json` 中配置多个供应商以实现自动容灾：

```json
"model": {
  "primary": "google/gemini-1.5-pro",
  "fallbacks": ["google-backup/gemini-1.5-flash", "nvidia/kimi"]
}
```

---

## 📜 许可证

MIT License. 由 Keke (OpenClaw Agent) 驱动构建。
