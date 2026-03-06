# OpenCode Skill for OpenClaw

这个 skill 让 OpenClaw 能够使用 **OpenCode AI** - 一个 AI 驱动的代码编辑器（类似 Cursor/Windsurf 的 CLI 版本）。

## 📦 安装

OpenCode 通过 Homebrew 安装：
```bash
brew install opencode
```

## ⚙️ 前置条件

**重要**：OpenCode 需要 `sysctl` 命令来检测系统架构。确保 `/usr/sbin` 在 PATH 中：

```bash
export PATH="/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
```

永久添加到 `~/.zshrc`：
```bash
echo 'export PATH="/usr/sbin:/usr/bin:/sbin:/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## 🚀 快速开始

### 1. 测试安装
```bash
./examples.sh
```

### 2. 简单任务
```bash
opencode run "Add error handling to my code"
```

### 3. 交互模式
```bash
opencode
```

## 📚 主要功能

- ✅ AI 辅助编码和重构
- ✅ GitHub PR 自动修复
- ✅ 会话管理（继续之前的工作）
- ✅ 多模型支持（OpenAI、Anthropic、Google 等）
- ✅ MCP 协议支持
- ✅ Web 界面模式

## 🔧 常用命令

| 命令 | 说明 |
|------|------|
| `opencode run "prompt"` | 运行单条 AI 指令 |
| `opencode --continue` | 继续上次会话 |
| `opencode models` | 列出可用模型 |
| `opencode session list` | 列出所有会话 |
| `opencode pr 123` | 处理 GitHub PR |
| `opencode web` | 启动 Web 界面 |
| `opencode stats` | 查看使用统计 |

## 📖 完整文档

详见 [SKILL.md](./SKILL.md)

## 🔍 测试示例

运行示例脚本测试所有功能：
```bash
bash examples.sh
```

## 💡 提示

1. **具体化提示**：清晰的提示产生更好的结果
2. **附加文件**：使用 `-f` 参数为 AI 提供上下文
3. **利用会话**：使用 `--continue` 在之前的基础上继续工作
4. **尝试分支**：使用 `--fork` 安全地尝试变体

---

*Created: 2026-02-25*
