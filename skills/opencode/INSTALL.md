# 安装 OpenCode Skill 到 OpenClaw

本指南说明如何将这个 skill 集成到 OpenClaw 中。

## 方法 1: 复制到 OpenClaw skills 目录（推荐）

### 1. 找到 OpenClaw skills 目录

```bash
# 查找 OpenClaw 安装位置
which openclaw

# 通常在这里
/usr/local/lib/node_modules/openclaw/skills/
```

### 2. 复制 skill 目录

```bash
# 创建备份（可选）
sudo cp -r /usr/local/lib/node_modules/openclaw/skills/opencode ~/opencode-skill-backup 2>/dev/null || true

# 复制新 skill
sudo cp -r /Users/wl/.openclaw/workspace/skills/opencode /usr/local/lib/node_modules/openclaw/skills/
```

### 3. 设置权限

```bash
sudo chown -R root:wheel /usr/local/lib/node_modules/openclaw/skills/opencode
sudo chmod -R 755 /usr/local/lib/node_modules/openclaw/skills/opencode
```

### 4. 验证安装

```bash
# 列出 skills
openclaw skills list

# 或者检查文件
ls -la /usr/local/lib/node_modules/openclaw/skills/ | grep opencode
```

## 方法 2: 使用符号链接（开发模式）

适合频繁更新 skill 的情况：

```bash
# 创建符号链接
sudo ln -sf /Users/wl/.openclaw/workspace/skills/opencode /usr/local/lib/node_modules/openclaw/skills/opencode
```

更新时只需修改工作区中的文件，无需重新复制。

## 方法 3: 通过 ClawHub 发布（推荐用于分享）

```bash
# 初始化 git 仓库（如果还没有）
cd /Users/wl/.openclaw/workspace/skills/opencode
git init
git add .
git commit -m "Initial OpenCode skill"

# 发布到 ClawHub（需要 ClawHub CLI）
clawhub publish
```

## 验证 Skill 工作

重启 OpenClaw 或重新加载配置：

```bash
# 重启 OpenClaw
openclaw restart

# 或在 OpenClaw 中测试
# 技能应该自动激活当用户提到 "opencode" 相关任务
```

## 测试 Skill

在 OpenClaw 聊天中测试：

```
使用 OpenCode 帮我重构这个函数
```

或者

```
用 opencode 审查这段代码
```

## Skill 元数据

SKILL.md 顶部的元数据：

```yaml
---
name: opencode
description: "OpenCode AI - AI-driven code editor/IDE (CLI/TUI version of Cursor/Windsurf). Use when: (1) AI-assisted coding tasks, (2) Code refactoring with AI, (3) GitHub PR review/fixes, (4) Multi-file edits requiring context, (5) Running AI agents on codebases."
metadata:
  {
    "openclaw": { "emoji": "🤖", "requires": { "bins": ["opencode"] } },
  }
---
```

这确保 OpenClaw 能正确识别和加载 skill。

## 故障排除

### Skill 未被识别

1. **检查文件位置**：
   ```bash
   ls -la /usr/local/lib/node_modules/openclaw/skills/opencode/SKILL.md
   ```

2. **检查语法**：
   ```bash
   # 验证 YAML frontmatter
   head -10 /usr/local/lib/node_modules/openclaw/skills/opencode/SKILL.md
   ```

3. **重启 OpenClaw**：
   ```bash
   openclaw restart
   ```

4. **检查日志**：
   ```bash
   openclaw logs
   ```

### opencode 命令未找到

确保 PATH 包含 `/usr/sbin`：

```bash
export PATH="/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# 测试
opencode --version
```

### 权限问题

```bash
# 修复权限
sudo chown -R root:wheel /usr/local/lib/node_modules/openclaw/skills/opencode
sudo chmod -R 755 /usr/local/lib/node_modules/openclaw/skills/opencode
```

## 更新 Skill

### 方法 1（复制）
```bash
# 重新复制
sudo cp -r /Users/wl/.openclaw/workspace/skills/opencode /usr/local/lib/node_modules/openclaw/skills/
```

### 方法 2（符号链接）
```bash
# 无需操作，符号链接自动指向最新文件
```

## 卸载

```bash
# 删除 skill
sudo rm -rf /usr/local/lib/node_modules/openclaw/skills/opencode

# 重启 OpenClaw
openclaw restart
```

## 文件结构

```
opencode/
├── SKILL.md          # 主 skill 文档（OpenClaw 读取这个）
├── README.md         # 说明文档
├── CHEATSHEET.md     # 快速参考
├── INSTALL.md        # 本文件
└── examples.sh       # 示例脚本
```

## 需要帮助？

- OpenClaw 文档: https://docs.openclaw.ai
- ClawHub: https://clawhub.com
- OpenCode 文档: `opencode --help`

---

*安装指南 - OpenCode Skill*
*Created: 2026-02-25*
