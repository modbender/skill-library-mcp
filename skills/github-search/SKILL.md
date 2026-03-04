---
name: github-research
description: GitHub 仓库深度搜索与分析。支持按关键词、语言、stars、更新时间筛选，获取细分领域最新开源项目。专为技术调研设计。
metadata:
  openclaw:
    emoji: "🐙"
    category: "research"
    tags: ["github", "opensource", "research", "repository"]
---

# GitHub Research 🐙

GitHub 仓库深度搜索与分析工具。专为技术细分领域调研设计，支持多维度筛选和详细数据分析。

## 功能特性

- 🔍 **精准搜索** - 按关键词搜索特定领域的 GitHub 仓库
- 📊 **多维度筛选** - Stars、语言、更新时间、Forks
- 📈 **趋势分析** - 识别活跃项目和新兴趋势
- 🏷️ **标签分类** - 自动提取项目标签和主题
- 📋 **结构化输出** - Markdown表格，易于整合到报告

## 使用方式

### 基础搜索

```bash
# 搜索特定领域
node scripts/github-search.mjs "agent memory"

# 指定编程语言
node scripts/github-search.mjs "rag" --language python

# 更多结果
node scripts/github-search.mjs "llm" --limit 20
```

### 高级筛选

```bash
# 筛选高星项目（>1000 stars）
node scripts/github-search.mjs "vector database" --min-stars 1000

# 最近更新的项目（30天内）
node scripts/github-search.mjs "embedding" --updated-within 30

# 组合筛选
node scripts/github-search.mjs "multi-agent" \
  --language python \
  --min-stars 500 \
  --updated-within 90 \
  --limit 15
```

### 获取详细信息

```bash
# 获取单个仓库的详细信息
node scripts/repo-detail.mjs "microsoft/autogen"

# 批量获取（从搜索结果）
cat search-results.json | node scripts/batch-detail.mjs
```

## 输出格式

### 搜索结果表格

```markdown
## 🔥 GitHub 热门项目: agent memory

| 排名 | 项目 | ⭐ Stars | 🍴 Forks | 💻 语言 | 📅 更新 | 🔗 链接 |
|-----|------|---------|---------|--------|--------|--------|
| 1 | microsoft/autogen | 32.5k | 4.8k | Python | 2天前 | [查看](https://github.com/microsoft/autogen) |
| 2 | langchain-ai/langchain | 89.2k | 14.1k | Python | 1天前 | [查看](https://github.com/langchain-ai/langchain) |
| 3 | ... | ... | ... | ... | ... | ... |

### 📊 统计摘要
- **总项目数**: 15
- **平均 Stars**: 5,230
- **主要语言**: Python (80%), TypeScript (13%), Go (7%)
- **活跃度**: 73% 最近30天有更新
```

### 详细报告

```markdown
## 📋 项目详情: microsoft/autogen

**全称**: AutoGen
**描述**: A programming framework for building AI agents
**🏷️ 标签**: ai-agents, multi-agent, llm, python

**📈 数据统计**
- Stars: 32,547 (+156 this week)
- Forks: 4,823
- Issues: 1,234 open
- Pull Requests: 89 open

**💻 代码信息**
- 主要语言: Python (98.2%)
- 代码行数: ~150k
- 许可证: MIT

**📅 活跃度**
- 最后提交: 2天前
- 提交频率: 日均 12 commits
- 贡献者: 234人

**🔗 链接**
- 仓库: https://github.com/microsoft/autogen
- 文档: https://microsoft.github.io/autogen/
- 示例: https://github.com/microsoft/autogen/tree/main/samples
```

## 参数说明

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `query` | 搜索关键词 | 必填 | `"agent memory"` |
| `--language` | 编程语言筛选 | 无 | `python`, `typescript`, `go` |
| `--min-stars` | 最小 stars 数 | 100 | `1000` |
| `--max-stars` | 最大 stars 数 | 无限制 | `50000` |
| `--updated-within` | 最近N天更新 | 365 | `30`, `90` |
| `--created-after` | 创建日期之后 | 无 | `2024-01-01` |
| `--sort` | 排序方式 | stars | `stars`, `updated`, `forks` |
| `--order` | 排序顺序 | desc | `asc`, `desc` |
| `--limit` | 返回结果数 | 10 | `20`, `50` |
| `--output` | 输出格式 | table | `table`, `json`, `csv` |

## 工作流集成

### 在 Multi-Agent Research 中使用

```python
# Intel Agent 调用 GitHub Research
subagent_task = """
你是情报分析师。使用 github-research skill 获取最新数据。

执行以下命令：
```bash
node ~/.openclaw/workspace/skills/github-research/scripts/github-search.mjs \
  "agent memory" \
  --language python \
  --min-stars 500 \
  --updated-within 90 \
  --limit 15 \
  --output json > /tmp/gh_results.json
```

基于结果生成报告表格...
"""
```

### 批量分析多个领域

```bash
#!/bin/bash
TOPICS=("agent memory" "rag" "vector database" "llm orchestration")

for topic in "${TOPICS[@]}"; do
  safe_topic=$(echo "$topic" | tr ' ' '-')
  node scripts/github-search.mjs "$topic" \
    --min-stars 1000 \
    --limit 15 \
    --output json > "results/${safe_topic}.json"
done
```

## API 限制

- **未认证请求**: 60次/小时
- **认证请求**: 5000次/小时
- **建议**: 对于大量查询，配置 GitHub Token

### 配置 GitHub Token（可选）

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

## 数据来源

- GitHub Search API v3
- GitHub REST API
- 官方 GitHub 网站（备用）

---

*专为技术细分领域调研设计 | GitHub Research v1.0*
