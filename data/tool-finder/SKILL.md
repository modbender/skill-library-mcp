---
name: tool-finder
description: 统一搜索 ClawHub skills 和 Smithery MCP servers 的工具发现引擎。支持评分排序、推荐规则、来源标识。优先原词搜索，扩展补充。**自动触发：看到"找 skill"、"搜索工具"、"安装 skill"等关键词自动使用本技能**。
author: Boy
metadata:
  {
    "openclaw":
      {
        "emoji": "🔍",
        "requires": { "bins": ["clawhub", "curl", "jq"] },
        "install":
          [
            {
              "id": "node",
              "kind": "node",
              "package": "clawhub",
              "bins": ["clawhub"],
              "label": "Install ClawHub CLI (npm)",
            },
          ],
      },
  }
---

# Tool Finder 🦞

**统一搜索 ClawHub skills 和 Smithery MCP servers 的工具发现引擎。**

---

## 🎯 自动触发规则（AI 必读）

**安装本技能后，AI 会自动在以下场景使用 tool-finder：**

### 触发关键词

| 用户说 | AI 操作 |
|--------|--------|
| "找个...skill" / "找...工具" | `tool-finder search "<关键词>"` |
| "搜索 skill" / "搜索工具" | `tool-finder search "<关键词>"` |
| "有什么 MCP" / "MCP 推荐" | `tool-finder search "<关键词>" --type mcp` |
| "安装..." / "帮我装..." | `tool-finder install <name> --type skill\|mcp` |
| "ClawHub" / "Smithery" | `tool-finder search "<相关词>"` |
| "推荐工具" / "有哪些工具" | `tool-finder search "<功能>"` |
| "能...的 skill" | `tool-finder search "<功能>" --type skill` |

### 为什么不直接用 clawhub 命令？

| 对比项 | clawhub search | tool-finder |
|--------|---------------|-------------|
| 名称匹配 | ❌ 只看评分 | ✅ 名称匹配优先 |
| 结果过滤 | ❌ 无过滤 | ✅ 隐藏低质结果 |
| 推荐等级 | ❌ 无 | ✅ ⭐⭐⭐⭐⭐ 到 ❌ |
| 限流处理 | ❌ 直接失败 | ✅ 自动回退 |
| 来源标识 | ❌ 无 | ✅ ClawHub/Smithery |

**结论：tool-finder 是 clawhub 的智能封装，搜索结果更精准！**

---

---

## 🎯 何时使用（AI 必读）

**看到以下关键词 → 立即调用 tool-finder：**

| 关键词/短语 | 触发操作 |
|-------------|----------|
| "找个...skill" / "找...工具" | `tool-finder search "<关键词>"` |
| "有什么 MCP" / "MCP 推荐" | `tool-finder search "<关键词>" --type mcp` |
| "安装..." / "帮我装..." | `tool-finder install <name> --type skill\|mcp` |
| " ClawHub" / "Smithery" | `tool-finder search "<相关词>"` |
| "推荐工具" / "有哪些工具" | `tool-finder search "<功能>"` |
| "能...的 skill" | `tool-finder search "<功能>" --type skill` |

---

## ⚡ 快速命令参考

```bash
# 搜索（默认搜索全部来源，显示评分和推荐）
~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh search "<query>"

# 只搜索 skill（按评分降序排列）
~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh search "<query>" --type skill

# 只搜索 MCP
~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh search "<query>" --type mcp

# 限制数量
~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh search "<query>" --limit 5

# 精确搜索（知道技能名时）
~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh search "agent-orchestrator" --exact

# 显示详细错误信息
~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh search "<query>" --verbose

# 显示所有结果（包括低评分 < 2.0）
~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh search "<query>" --all

# 安装
~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh install <name> --type skill
~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh install <name> --type mcp
```

---

## 📋 激活条件详解

### ✅ 必须触发的场景

1. **用户明确要找工具**
   - "帮我找个能搜索 web 的 skill"
   - "有什么 MCP 可以连接 GitHub？"
   - "推荐一个数据库工具"

2. **用户提到工具市场**
   - "ClawHub 上有什么好工具？"
   - "Smithery 上有搜索 MCP 吗？"

3. **用户要安装/卸载**
   - "安装 tavily-search"
   - "帮我装个 GitHub MCP"

4. **当前技能不足**
   - 用户需要的功能当前没有合适 skill/MCP
   - 你需要推荐替代方案

### ❌ 不要触发的场景

1. **工具已存在，只是不会用**
   - "怎么用 weather skill？" → 直接教用法，别搜索

2. **通用问题**
   - "今天天气怎么样" → 直接用 weather 工具

3. **闲聊**
   - "你觉得哪个工具好用" → 先搜索再回答

---

## 📝 使用示例（完整对话）

### 配置自动触发（让 AI 默认使用 tool-finder）

**在 AGENTS.md 中添加以下内容：**

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

**效果：** AI 会自动在找 skill/MCP 时使用 tool-finder，无需每次指定！

---

### 示例 1：找 skill

```
用户：帮我找个能搜索 web 的 skill

AI：[执行 tool-finder search "web search" --type skill]

AI：找到以下 web 搜索 skill：
- tavily-search: Tavily Web Search
- baidu-search: baidu web search  
- multi-search-engine: Multi Search Engine

推荐 tavily-search，需要安装吗？
```

### 示例 2：找 MCP

```
用户：有什么 MCP 可以连接 GitHub？

AI：[执行 tool-finder search "github" --type mcp]

AI：找到 GitHub 相关 MCP：
- GitHub: GitHub is a code hosting platform for version control...

需要我帮你安装吗？
```

### 示例 3：直接安装

```
用户：安装 tavily-search

AI：[执行 tool-finder install tavily-search --type skill]

AI：正在安装 tavily-search...
[输出安装结果]
```

---

## 🔧 实现细节

### 路径

```bash
TOOL_FINDER="~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh"
```

### ClawHub 搜索

```bash
npx clawhub@latest search "<query>"
```

### Smithery 搜索

```bash
# MCPs
npx @smithery/cli@latest mcp search "<query>" --json

# Skills
npx @smithery/cli@latest skill search "<query>" --json
```

---

## ⚠️ 注意事项

### 0. 自动触发配置 ✅ 新增

**让 AI 默认使用 tool-finder：**

在 `AGENTS.md` 中添加：
```markdown
### 🔍 Tool Discovery — Use `tool-finder` First!

**When user asks to find/search/install skills or MCPs:**
1. ALWAYS use `tool-finder` skill first
2. DO NOT use `clawhub search` directly
```

**效果：** AI 会自动使用 tool-finder，无需每次指定！

**分享配置：** 将 AGENTS.md 和 TOOLS.md 分享给其他人，他们也能享受同样的智能搜索体验。

### 1. 搜索策略 ✅ v1.3.0 优化

**优先原词搜索**：先用原词搜索，保证基础结果；如果结果不足，再用同义词扩展补充。

**搜索流程**：
```
1. 原词搜索 → 返回 N 条结果
2. 如果 N < limit 且未限流 → 扩展搜索（补充结果）
3. 合并去重 → 按评分降序排列
```

**优势**：
- ✅ 原词结果优先，避免扩展词污染
- ✅ 限流时保证有结果
- ✅ 结果不足时自动补充

### 2. 推荐规则 ✅ v1.2.0 新增

**评分排序**：结果按 ClawHub 评分降序排列，高评分技能优先显示。

**推荐等级**：
| 等级 | 图标 | 条件 |
|------|------|------|
| 强烈推荐 | ⭐⭐⭐⭐⭐ | 评分 ≥ 3.5 + 名称高度匹配 |
| 推荐 | ⭐⭐⭐⭐ | 评分 ≥ 3.0 + 名称相关 |
| 一般 | ⭐⭐⭐ | 评分 ≥ 2.0 或 名称部分匹配 |
| 低相关 | ⭐⭐ | 评分 ≥ 1.0（模糊搜索常见） |
| 不推荐 | ❌ | 评分 < 1.0（默认隐藏） |

**过滤规则**：
- 默认隐藏评分 < 1.0 的技能（几乎无关）
- 使用 `--all` 显示所有结果（包括 < 1.0）
- **说明**：模糊搜索分数通常较低（1.0-2.0），这是正常的

### 2. 错误透明化 ✅ 新增

**改进**：遇到 API 限流或搜索失败时，会显示明确的警告信息，而不是内部消化。

**示例输出**：
```
⚠️  ClawHub API 限流 (Rate limit exceeded)
   建议：等待几分钟后重试，或登录 clawhub login

══════════════════════════════════════════════════════════════
⚠️  搜索警告
══════════════════════════════════════════════════════════════
• ClawHub: 2 次错误/限流

提示：结果可能不完整，建议:
  1. 等待几分钟后重试（限流情况）
  2. 使用精确模式：--exact（知道技能名时）
  3. 直接访问 https://clawhub.ai 搜索验证
  4. 使用 --verbose 查看详细错误
```

### 3. 结果可验证性 ✅ 新增

**问题**：搜索结果可能与 ClawHub 网页搜索有差异（向量搜索 vs 文本搜索）。

**解决方案**：
- 使用 `--verbose` 查看详细错误信息
- 重要技能建议访问 https://clawhub.ai 验证
- 使用 `clawhub inspect <skill-name>` 获取详细信息
- 对比多次搜索结果，确保没有遗漏

### 4. ClawHub 搜索限制

**问题**：ClawHub 使用向量搜索，有时搜功能词（如"RAG"）找不到名字包含该词的 skill（如 `clawrag`）。

**解决方案**：
- 知道名字 → 用 `--exact` 模式：`tool-finder search "clawrag" --exact`
- 不知道名字 → 多试几个关键词：`"rag"`, `"memory"`, `"retrieval"`
- 使用 `clawhub search` 直接搜索作为补充

### 5. ClawHub Rate Limit

未登录时可能遇到速率限制（60 次/小时）。

**解决**：
- 等待几分钟后重试
- `npx clawhub login` 登录后提高限制
- 使用 `--verbose` 确认是否限流

### 6. MCP 安装需要客户端

Smithery MCP 安装需指定客户端（claude-code/cursor/vscode 等）。

**解决**：输出指引让用户手动安装。

### 7. 搜索关键词

- 优先用英文（工具名多为英文）
- 中文可试，但效果可能较差
- 使用连字符的技能名要精确搜索（如 `agent-orchestrator`）

### 8. 路径问题

- 使用绝对路径：`~/.openclaw/workspace/skills/tool-finder/scripts/tool-finder.sh`
- 或确保 PATH 包含 scripts 目录

---

## 📦 依赖

- Node.js + npx
- curl
- jq

---

## 🦞 总结

**一句话：用户找工具 → 用 tool-finder search → 返回结果 → 问要不要安装**
