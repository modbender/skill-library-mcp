# AgentSkills 规范说明

## 什么是 AgentSkills？

AgentSkills 是 Anthropic 在 2025年12月发布的开放标准，用于定义 AI 代理的技能。OpenClaw、Microsoft、GitHub、Cursor 等工具都采用了这个规范。

## 为什么要使用 AgentSkills 规范？

### 1. 跨平台兼容
- 一次编写，多平台使用
- 不绑定特定工具或平台
- 社区生态更丰富

### 2. 更好的安全性
- 明确声明 `allowed-tools`
- 可审计的权限系统
- 避免意外的危险操作

### 3. 更清晰的文档
- YAML frontmatter 包含元数据
- Markdown 文档人类可读
- AI 和人类都能理解

## OpenClaw Skill 的正确格式

### 文件结构

```
my-skill/
├── SKILL.md              # 必需：元数据 + 文档
├── prompts/              # 可选：提示词文件
│   ├── task1.md
│   └── task2.md
├── scripts/              # 可选：可执行脚本
│   └── helper.py
├── references/           # 可选：按需加载的文档
│   └── api-docs.md
├── assets/               # 可选：模板、文件
│   └── template.json
├── config.example.json   # 可选：配置示例
└── README.md             # 可选：详细说明
```

### SKILL.md 格式

```markdown
---
name: skill-name
version: 1.0.0
description: 简短描述
author: 作者名
license: MIT
keywords:
  - keyword1
  - keyword2
allowed-tools:
  - web_search
  - web_fetch
  - message
compatibility:
  - openclaw >= 2026.2.0
---

# Skill 标题

详细的使用说明...

## 何时使用此 Skill

列出触发条件...

## 功能说明

详细功能描述...
```

### YAML Frontmatter 字段说明

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | ✅ | Skill 唯一标识符 |
| `version` | ✅ | 版本号（语义化版本） |
| `description` | ✅ | 简短描述（1-2句话） |
| `author` | 推荐 | 作者或组织名 |
| `license` | 推荐 | 开源许可证 |
| `keywords` | 推荐 | 关键词列表 |
| `allowed-tools` | ✅ | 允许使用的工具列表 |
| `compatibility` | 可选 | 兼容性要求 |

## allowed-tools 安全说明

### 安全的工具

✅ **推荐使用：**
- `web_search` - 搜索公开网页
- `web_fetch` - 获取网页内容
- `message` - 发送消息
- `Read` - 读取文件（限定路径）

### 危险的工具

⚠️ **谨慎使用：**
- `Bash(command)` - 执行特定命令（需明确指定）
- `Write` - 写入文件（需限定路径）

❌ **避免使用：**
- `Bash(*)` - 执行任意命令（极度危险）
- `Bash` - 无限制的 shell 访问

### 示例

**安全的声明：**
```yaml
allowed-tools:
  - web_search
  - web_fetch
  - message
  - Bash(pdftotext:*)  # 只允许 pdftotext 命令
  - Read(./data/*)     # 只读取 data 目录
```

**危险的声明：**
```yaml
allowed-tools:
  - Bash(*)            # ❌ 可以执行任意命令
  - Bash               # ❌ 无限制访问
  - Write              # ❌ 可以写入任意文件
```

## 与旧格式的对比

### ❌ 旧格式（skill.json）

```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "description": "描述",
  "tools": ["web_search", "web_fetch"],
  "prompts": {
    "task1": {
      "name": "任务1",
      "prompt": "提示词内容..."
    }
  }
}
```

**问题：**
- 不符合 OpenClaw 规范
- 无法跨平台使用
- 缺少安全声明
- 文档和代码混在一起

### ✅ 新格式（SKILL.md）

```markdown
---
name: my-skill
version: 1.0.0
description: 描述
allowed-tools:
  - web_search
  - web_fetch
---

# My Skill

详细文档...

## 使用方法

...
```

**优势：**
- 符合 AgentSkills 规范
- 跨平台兼容
- 明确的安全声明
- 文档清晰易读

## 迁移指南

### 从 skill.json 迁移到 SKILL.md

1. **创建 SKILL.md 文件**
   ```bash
   touch SKILL.md
   ```

2. **添加 YAML frontmatter**
   - 从 skill.json 复制元数据
   - 添加 `allowed-tools` 声明
   - 添加 `compatibility` 要求

3. **编写文档内容**
   - 何时使用此 skill
   - 功能说明
   - 使用示例
   - 配置说明

4. **移动 prompts**
   - 如果 skill.json 中有内联 prompts
   - 创建 `prompts/` 目录
   - 每个 prompt 一个 .md 文件

5. **创建配置示例**
   - 如果有配置项
   - 创建 `config.example.json`

6. **删除 skill.json**
   ```bash
   rm skill.json
   ```

7. **测试**
   ```bash
   openclaw skills reload
   openclaw skills list
   ```

## 最佳实践

### 1. 最小权限原则

只声明必需的工具：

```yaml
# ✅ 好
allowed-tools:
  - web_search
  - message

# ❌ 不好
allowed-tools:
  - web_search
  - web_fetch
  - message
  - Bash(*)
  - Write
```

### 2. 明确的文档

在 SKILL.md 中清楚说明：
- 何时使用此 skill
- 需要什么配置
- 有什么限制
- 如何排查问题

### 3. 配置示例

提供 `config.example.json`：
```json
{
  "api_key": "your-api-key",
  "endpoint": "https://api.example.com"
}
```

### 4. 版本管理

使用语义化版本：
- `1.0.0` - 初始版本
- `1.1.0` - 新增功能
- `1.0.1` - Bug 修复
- `2.0.0` - 破坏性变更

### 5. 关键词优化

添加相关关键词，方便搜索：
```yaml
keywords:
  - brand
  - monitoring
  - sentiment
  - social-media
  - automotive
```

## 安全检查清单

在发布 skill 前，检查：

- [ ] 使用 SKILL.md 格式（不是 skill.json）
- [ ] 有 YAML frontmatter
- [ ] 明确声明 `allowed-tools`
- [ ] 不使用 `Bash(*)` 或无限制的 `Bash`
- [ ] 不使用无限制的 `Write`
- [ ] 有清晰的文档说明
- [ ] 有配置示例（如需要）
- [ ] 测试过所有功能
- [ ] 版本号正确

## 参考资源

- [AgentSkills 规范](https://github.com/anthropics/agentskills)
- [OpenClaw Skills 文档](https://openclaw.ai/docs/skills)
- [OpenClaw 安全最佳实践](https://openclaw.ai/docs/security)
- [社区 Skills 仓库](https://github.com/VoltAgent/awesome-openclaw-skills)

## 常见问题

### Q: 为什么我的 skill.json 不工作？

A: OpenClaw 使用 AgentSkills 规范，需要 SKILL.md 文件，不是 skill.json。

### Q: 如何声明需要 Bash 命令？

A: 使用 `Bash(command:*)` 格式，明确指定命令：
```yaml
allowed-tools:
  - Bash(pdftotext:*)
  - Bash(convert:*)
```

### Q: 可以不声明 allowed-tools 吗？

A: 不可以。这是安全要求，必须明确声明。

### Q: 如何测试 skill 是否符合规范？

A: 
```bash
openclaw skills validate brand-monitor
openclaw skills show brand-monitor
```

### Q: 旧的 skill.json 会被支持吗？

A: 不会。OpenClaw 只支持 AgentSkills 规范的 SKILL.md 格式。

---

**本文档适用于 OpenClaw v2026.2.0+**
