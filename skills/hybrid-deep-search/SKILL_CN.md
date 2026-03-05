---
name: hybrid-deep-search
description: 混合深度搜索 - 结合 Brave API 快速搜索和 OpenAI Codex 深度分析,智能路由自动选择最优方案
argument-hint: [搜索问题] [--mode quick|codex|auto] [--focus web|academic|news]
allowed-tools: Bash(*:web_search), Bash(*:curl), Bash(*:python3)
---

# Hybrid Deep Search 🚀

三层智能搜索系统 - 快速/深度/自动,根据查询复杂度自动选择最优方案。

## 架构设计

```
用户查询
   ↓
查询分析器 (router.py)
   ↓
   ├─→ 简单问题 → Brave API (web_search)     快速、免费
   ├─→ 复杂问题 → OpenAI Codex (gpt-5-codex) 深度分析、付费
   └─→ 手动模式 → 用户指定
```

## 首次使用配置

### 1. Brave API (已内置)
无需额外配置,直接使用 OpenClaw 的 `web_search` 工具。

### 2. OpenAI Codex API
```bash
# 获取 API Key
# 访问: https://platform.openai.com/api-keys

# 设置环境变量
export OPENAI_API_KEY="sk-your-openai-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # 可选,默认官方端点
```

### 3. 配置文件
```bash
cp config.json.example config.json
# 编辑 config.json 填入你的配置
```

## 使用方法

### 自动模式 (推荐)
```bash
python3 scripts/deep_search.py "查询内容"
# 系统自动判断复杂度并选择:
# - 简单问题 → Brave API
# - 复杂问题 → OpenAI Codex
```

### 手动指定模式
```bash
# 快速搜索 (Brave API)
python3 scripts/deep_search.py "what is OpenClaw?" --mode quick

# 深度搜索 (OpenAI Codex)
python3 scripts/deep_search.py "compare LangChain vs LlamaIndex in detail" --mode codex
```

### 聚焦模式
```bash
# 学术搜索
python3 scripts/deep_search.py "AI agent frameworks research" --mode codex --focus academic

# 新闻搜索
python3 scripts/deep_search.py "latest AI news" --mode quick --focus news

# 通用网络搜索
python3 scripts/deep_search.py "OpenClaw documentation" --mode quick --focus web
```

## 参数说明

| 参数 | 说明 | 可选值 | 默认值 |
|------|------|--------|--------|
| query | 搜索问题 | 任意文本 | - |
| --mode | 搜索模式 | `quick`, `codex`, `auto` | `auto` |
| --focus | 搜索聚焦 | `web`, `academic`, `news`, `youtube` | `web` |
| --max-results | 最大结果数 | 1-20 | 10 |
| --verbose | 详细输出 | - | false |

## 复杂度判断规则

自动模式基于以下规则路由:

### → Brave API (quick)
- 简单事实查询 (what/who/when/where)
- 定义查询
- 快速查找
- 单一主题

**示例:**
- "what is OpenClaw?"
- "who created Python?"
- "latest AI news today"

### → OpenAI Codex (codex)
- 对比分析
- 深度推理
- 多源信息综合
- 复杂问题
- 需要推理/总结

**示例:**
- "compare LangChain vs LlamaIndex in detail"
- "analyze the impact of AI on job market"
- "explain quantum computing applications in healthcare"

## 成本优化

### Brave API
- ✅ 完全免费
- ⚡ 快速响应 (<2s)
- 📊 结果数量可控

### OpenAI Codex (gpt-5-codex)
- 💰 按使用量计费
- 🧠 深度推理能力
- ⏱️ 响应时间较长 (5-30s)
- 💡 新用户可能有免费额度

**建议:** 优先使用自动模式,让系统帮你优化成本。

## 示例场景

### 场景 1: 快速事实查询
```bash
python3 scripts/deep_search.py "OpenClaw version 2026"
# → 自动使用 Brave API
# → 结果: 快速返回,免费
```

### 场景 2: 深度分析
```bash
python3 scripts/deep_search.py "comprehensive analysis of AI agent architectures"
# → 自动使用 OpenAI Codex
# → 结果: 深度分析,多源综合
```

### 场景 3: 学术研究
```bash
python3 scripts/deep_search.py "recent papers on multi-agent systems" --mode codex --focus academic
# → 使用 OpenAI Codex
# → 聚焦学术文献
```

## 技术细节

### 查询分析器 (router.py)
基于 NLP 规则分析查询:
- 关键词检测 (compare/analyze/explain...)
- 句子长度
- 复杂度评分
- 自动路由决策

### Brave API 集成
使用 OpenClaw 内置的 `web_search` 工具:
- 通过 Bash 工具调用
- 自动处理请求
- 无需额外认证

### OpenAI Codex 集成
- 使用 gpt-5-codex 模型
- 内建 web search 工具
- API 格式: OpenAI Chat Completions

## 故障排查

### Brave API 无响应
```bash
# 检查 OpenClaw web_search 工具
# 无需额外配置
```

### OpenAI Codex 认证失败
```bash
# 检查环境变量
echo $OPENAI_API_KEY

# 重新设置
export OPENAI_API_KEY="sk-..."
```

### Python 依赖
```bash
pip install openai python-dotenv
```

## 高级用法

### 批量搜索
```bash
# 创建 queries.txt
echo "query 1" >> queries.txt
echo "query 2" >> queries.txt

# 批量执行
for query in $(cat queries.txt); do
  python3 scripts/deep_search.py "$query" --mode auto
done
```

### 结果格式化
```bash
# JSON 输出
python3 scripts/deep_search.py "query" --format json

# Markdown 输出 (默认)
python3 scripts/deep_search.py "query" --format markdown

# 纯文本输出
python3 scripts/deep_search.py "query" --format text
```

## 参考资料

- [Brave Search API](https://brave.com/search/api/)
- [OpenAI GPT-5-Codex](https://platform.openai.com/docs/models/gpt-5-codex)
- [OpenAI API Docs](https://platform.openai.com/docs/api-reference)
