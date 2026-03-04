# Tool Finder 配置指南

让 OpenClaw 默认使用 tool-finder 搜索技能和工具。

---

## 🚀 快速开始

### 1. 安装 tool-finder

```bash
clawhub install tool-finder
```

或手动克隆：
```bash
git clone <repo-url> ~/.openclaw/workspace/skills/tool-finder
```

### 2. 更新 AGENTS.md

在 `AGENTS.md` 的 **Tools** 章节添加以下内容：

```markdown
### 🔍 Tool Discovery — Use `tool-finder` First!

**When user asks to find/search/install skills or MCPs:**

1. **ALWAYS use `tool-finder` skill first**
2. **DO NOT use `clawhub search` directly**
3. **Search command:**
   ```bash
   ~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh search "<query>" --type skill
   ```
4. **Install command:**
   ```bash
   ~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh install <name> --type skill
   ```

**Why tool-finder?**
- ✅ Name matching priority (relevant skills appear first)
- ✅ Rating-based filtering (hides irrelevant low-quality results)
- ✅ Clear recommendation levels (⭐⭐⭐⭐⭐ to ❌)
- ✅ Rate limit handling with fallback
- ✅ Shows source (ClawHub vs Smithery)
```

### 3. 更新 TOOLS.md

在 `TOOLS.md` 添加 tool-finder 的详细配置和使用说明（参考主 TOOLS.md 中的完整内容）。

---

## 📋 验证配置

测试搜索是否正常：

```bash
# 测试搜索
~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh search "agent create" --type skill --limit 5

# 预期输出：
# - 显示评分和推荐等级
# - 名称相关的技能排在前面
# - 没有高评分但不相关的结果
```

---

## 🎯 使用示例

### 示例 1：搜索技能

**用户：** "帮我找个能搜索 web 的 skill"

**AI 操作：**
```bash
~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh search "web search" --type skill
```

**AI 回复：**
```
找到以下 web 搜索 skill：
- tavily-search (⭐⭐⭐⭐⭐ 3.5+)
- baidu-search (⭐⭐⭐⭐ 3.0+)

推荐 tavily-search，需要安装吗？
```

### 示例 2：安装技能

**用户：** "安装 tavily-search"

**AI 操作：**
```bash
~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh install tavily-search --type skill
```

### 示例 3：搜索 MCP

**用户：** "有什么 MCP 可以连接 GitHub？"

**AI 操作：**
```bash
~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh search "github" --type mcp
```

---

## 📊 评分系统说明

| 等级 | 图标 | 条件 | 说明 |
|------|------|------|------|
| 强烈推荐 | ⭐⭐⭐⭐⭐ | ≥ 3.5 + 名称匹配 | 精确搜索 |
| 推荐 | ⭐⭐⭐⭐ | ≥ 3.0 + 名称相关 | 精确搜索 |
| 一般 | ⭐⭐⭐ | ≥ 2.0 | 模糊搜索高分 |
| 低相关 | ⭐⭐ | ≥ 1.0 | 模糊搜索常见 |
| 不推荐 | ❌ | < 1.0 | 默认隐藏 |

---

## ⚠️ 常见问题

### Q: 为什么搜索结果都是低评分（1.0-2.0）？

**A:** ClawHub 评分是向量相似度，模糊搜索分数通常较低。这是正常的！

**解决：**
- 使用 `--exact` 模式精确搜索（知道技能名时）
- 优先看名称匹配，而不是评分
- 使用 `--all` 显示完整结果

### Q: 遇到 API 限流怎么办？

**A:** ClawHub 未登录时限制为 60 次/小时。

**解决：**
- 等待几分钟后重试
- 登录提高限制：`npx clawhub login`
- 使用 `--all` 查看缓存结果

### Q: 如何分享给其他人？

**A:** 分享以下文件：
1. `AGENTS.md` — 包含 tool-finder 使用规则
2. `TOOLS.md` — 包含详细配置
3. 或整个 `skills/tool-finder/` 目录

---

## 📦 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v1.6.0 | 2026-03-03 | 修复扩展搜索污染 |
| v1.5.0 | 2026-03-03 | 名称匹配优先 |
| v1.4.0 | 2026-03-03 | 降低过滤阈值 |
| v1.3.0 | 2026-03-03 | 优先原词搜索 |
| v1.0.0 | 2026-03-03 | 初始版本 |

---

## 🔗 相关链接

- **ClawHub:** https://clawhub.ai
- **tool-finder Skill:** `~/.openclaw/workspace/skills/tool-finder/`
- **ClawHub CLI:** `npx clawhub@latest`

---

*Last updated: 2026-03-03*
