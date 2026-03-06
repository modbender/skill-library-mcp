# skill-refiner

审计并修复 [OpenClaw](https://github.com/openclaw/openclaw) agent skills，确保符合 [skill-creator](https://github.com/openclaw/openclaw/tree/main/skills/skill-creator) 规范。

[English](./README.md)

## 为什么需要这个工具？

OpenClaw skills 需要遵循特定规范才能被正确发现和触发。常见问题包括：

- 缺失或格式错误的 YAML frontmatter
- 多余的 frontmatter 字段（只允许 `name` 和 `description`）
- 多余的文件（skill 目录中不应有 README.md、CHANGELOG.md 等）
- 描述不清晰，没有说明触发条件

这个工具会扫描 workspace 中的所有 skills 并报告合规问题。

## 快速开始

```bash
# 扫描你的 OpenClaw workspace
npx skill-refiner

# 扫描指定目录
npx skill-refiner /path/to/workspace
```

## 安装

### 作为 OpenClaw Skill 安装

```bash
clawhub install skill-refiner
```

然后对你的 agent 说："审计我的 skills" 或 "检查 skill 合规性"

### 全局 CLI 安装

```bash
npm install -g skill-refiner
skill-refiner ~/.openclaw/workspace
```

## 检查项

| 检查项 | 严重程度 | 说明 |
|--------|----------|------|
| SKILL.md 存在 | 🔴 问题 | 每个 skill 必须有 SKILL.md |
| YAML frontmatter | 🔴 问题 | 必须以 `---` 块开头 |
| 必填字段 | 🔴 问题 | 必须有 `name` 和 `description` |
| 多余字段 | 🔴 问题 | 只允许 `name` + `description` |
| 多余文件 | 🔴 问题 | 不能有 README.md、CHANGELOG.md 等 |
| 命名规范 | 🔴 问题 | 小写字母+连字符，≤64 字符 |
| 触发条件 | 🟡 警告 | 描述应包含 "Use when..." 或 "用于..." |
| SKILL.md 长度 | 🟡 警告 | 建议不超过 500 行 |
| 未链接的引用 | 🟡 警告 | references/ 中的文件应在 SKILL.md 中链接 |

## 输出示例

```
🔍 skill-refiner — scanning: /Users/me/.openclaw/workspace

✅ markdown-converter
✅ weather
❌ my-broken-skill
  ✗  Frontmatter has extra fields: metadata, author
  ✗  Extraneous file: README.md
⚠️ another-skill
  ⚠️  Description doesn't clearly state trigger conditions

─────────────────────────────────
Total: 4  ✅ 2  ❌ 1  ⚠️ 1
```

## 编程使用

```bash
# 查找所有 skills
bash scripts/find_skills.sh /path/to/workspace

# 审计单个 skill（返回 JSON）
python3 scripts/audit_skill.py /path/to/skill-dir
```

## 许可证

MIT
