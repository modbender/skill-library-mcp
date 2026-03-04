# GitHub Research 🐙

GitHub 仓库深度搜索与分析工具。专为技术细分领域调研设计。

## 快速开始

```bash
# 基础搜索
node scripts/github-search.mjs "agent memory"

# Python项目，最少1000 stars
node scripts/github-search.mjs "rag" --language python --min-stars 1000

# 最近30天更新的项目
node scripts/github-search.mjs "vector database" --updated-within 30 --limit 15

# 获取详细信息
node scripts/repo-detail.mjs "microsoft/autogen"
```

## 功能特性

- 🔍 **精准搜索** - 按关键词搜索特定领域的 GitHub 仓库
- 📊 **多维度筛选** - Stars、语言、更新时间、Forks
- 📈 **趋势分析** - 识别活跃项目和新兴趋势
- 🏷️ **标签分类** - 自动提取项目标签和主题
- 📋 **结构化输出** - Markdown表格，易于整合到报告

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `query` | 搜索关键词 | 必填 |
| `--language` | 编程语言筛选 | 无 |
| `--min-stars` | 最小 stars 数 | 100 |
| `--max-stars` | 最大 stars 数 | 无限制 |
| `--updated-within` | 最近N天更新 | 365 |
| `--created-after` | 创建日期之后 | 无 |
| `--sort` | 排序方式 | stars |
| `--order` | 排序顺序 | desc |
| `--limit` | 返回结果数 | 10 |
| `--output` | 输出格式 | table |

## 使用

```javascript
// Intel Agent 调用示例
const task = `
执行 GitHub 搜索：
\`\`\`bash
node ~/.openclaw/workspace/skills/github-research/scripts/github-search.mjs \\
  "${topic}" \\
  --language python \\
  --min-stars 500 \\
  --updated-within 90 \\
  --limit 15
\`\`\`

基于搜索结果生成报告...
`;
```

## 输出示例

```markdown
## 🔥 GitHub 热门项目: agent memory

| 排名 | 项目 | ⭐ Stars | 🍴 Forks | 💻 语言 | 📅 更新 | 🔗 链接 |
|-----|------|---------|---------|--------|--------|--------|
| 1 | microsoft/autogen | 32.5k | 4.8k | Python | 2天前 | [查看](https://github.com/microsoft/autogen) |
| 2 | langchain-ai/langchain | 89.2k | 14.1k | Python | 1天前 | [查看](https://github.com/langchain-ai/langchain) |

### 📊 统计摘要
- **总项目数**: 15
- **平均 Stars**: 5,230
- **主要语言**: Python (80%), TypeScript (13%)
- **活跃度**: 73% 最近30天有更新
```

## API 限制

- **未认证**: 60次/小时
- **认证**: 5000次/小时（配置 GITHUB_TOKEN）

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

---

*专为技术细分领域调研设计*
