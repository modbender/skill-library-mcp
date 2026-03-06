# OpenCode Skill 索引

完整的 OpenCode AI Skill 文档和资源。

## 📑 文档

| 文件 | 描述 |
|------|------|
| [SKILL.md](./SKILL.md) | **主文档** - OpenClaw 读取这个文件来学习如何使用 OpenCode |
| [README.md](./README.md) | 项目概述和快速开始 |
| [CHEATSHEET.md](./CHEATSHEET.md) | 快速参考卡片 - 常用命令速查 |
| [INSTALL.md](./INSTALL.md) | 安装指南 - 如何将 skill 集成到 OpenClaw |
| [INDEX.md](./INDEX.md) | 本文件 - 文档索引 |

## 🚀 快速开始

### 1. 安装 OpenCode
```bash
brew install opencode
```

### 2. 设置环境
```bash
export PATH="/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
echo 'export PATH="/usr/sbin:/usr/bin:/sbin:/bin:$PATH"' >> ~/.zshrc
```

### 3. 测试
```bash
./examples.sh
```

### 4. 安装 Skill
```bash
sudo cp -r /Users/wl/.openclaw/workspace/skills/opencode /usr/local/lib/node_modules/openclaw/skills/
```

## 🎯 核心功能

- **AI 辅助编码**: 通过自然语言指令生成和修改代码
- **会话管理**: 保持上下文，继续之前的工作
- **多模型支持**: OpenAI、Anthropic、Google、Z.AI 等
- **GitHub 集成**: 自动处理 PR
- **MCP 协议**: 扩展功能
- **Web 界面**: 可选的 GUI 模式

## 📖 使用场景

### 代码重构
```bash
opencode run "重构这个函数，使其更易读"
```

### 添加功能
```bash
opencode run "添加用户注册 API"
```

### 修复 Bug
```bash
opencode run -f error.log "修复错误"
```

### PR 工作流
```bash
opencode pr 123
```

### 继续工作
```bash
opencode run --continue
```

## 🔧 常用命令

| 命令 | 说明 |
|------|------|
| `opencode run "prompt"` | 运行 AI 任务 |
| `opencode` | 交互式 TUI |
| `opencode models` | 列出模型 |
| `opencode session list` | 列出会话 |
| `opencode stats` | 使用统计 |
| `opencode pr 123` | 处理 PR |

## 💡 最佳实践

1. **具体化提示**: 清晰的指令产生更好的结果
2. **提供上下文**: 使用 `-f` 附加相关文件
3. **利用会话**: 用 `--continue` 保持连续性
4. **尝试分支**: 用 `--fork` 安全实验
5. **监控成本**: 用 `opencode stats` 跟踪使用

## 🔗 相关资源

- **OpenCode**: 通过 Homebrew 安装的 AI 代码编辑器
- **OpenClaw**: AI agent 框架
- **ClawHub**: 技能市场 https://clawhub.com

## 📝 脚本

| 文件 | 描述 |
|------|------|
| [examples.sh](./examples.sh) | 测试脚本 - 验证所有功能 |

运行示例：
```bash
bash examples.sh
```

## 🛠️ 技术细节

- **版本**: 1.2.10
- **平台**: macOS Darwin x64
- **依赖**: `sysctl` (系统工具)
- **认证**: 已配置 Z.AI Coding Plan

## 📊 使用统计（当前）

```
Sessions: 22
Messages: 526
Days: 13
Total Cost: $0.00 (免费计划)
```

## 🤝 贡献

要改进此 skill：

1. 编辑工作区中的文件
2. 测试更改
3. 复制到 OpenClaw skills 目录
4. 重启 OpenClaw

```bash
# 开发流程
vim SKILL.md                    # 编辑
bash examples.sh                # 测试
sudo cp -r opencode /usr/local/lib/node_modules/openclaw/skills/
openclaw restart                # 重启
```

## 📞 支持

- OpenCode 帮助: `opencode --help`
- OpenClaw 文档: https://docs.openclaw.ai
- 社区: https://discord.com/invite/clawd

---

*OpenCode Skill - 让 OpenClaw 学会使用 AI 代码编辑器*

*Created: 2026-02-25*
*Last Updated: 2026-02-25*
