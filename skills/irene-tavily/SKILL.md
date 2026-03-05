---
name: tavily-search
description: "使用Tavily API进行智能网络搜索。无需信用卡，每月1000次免费查询。支持AI增强的搜索结果和深度研究模式。Use when: 需要高质量搜索结果、学术研究、或不想绑定信用卡的场景。"
homepage: https://tavily.com
metadata:
  {
    "openclaw":
      { "emoji": "🔍", "requires": { "bins": ["curl", "python3"] } },
  }
---

# Tavily Search - 智能搜索工具

基于Tavily API的网络搜索skill，提供高质量的AI增强搜索结果。

## Features

- ✅ **无需信用卡** - 每月1000次免费查询
- 🤖 **AI增强** - 自动提取关键信息，生成摘要
- 🔬 **深度研究模式** - 多源综合分析
- 📚 **学术友好** - 适合研究和信息收集
- 🌐 **多语言支持** - 中英文搜索优化

## Setup

### 1. 获取API Key

1. 访问 https://tavily.com/
2. 注册账号（邮箱即可，无需绑卡）
3. 在Dashboard复制API Key

### 2. 配置OpenClaw

```bash
# 设置环境变量
export TAVILY_API_KEY="tvly-..."

# 或者写入配置文件
echo 'TAVILY_API_KEY=tvly-...' >> ~/.openclaw/.env
```

## Usage

### 基础搜索

```bash
# 搜索最新AI新闻
python3 ~/.openclaw/skills/tavily-search/scripts/search.py "AI artificial intelligence news today"

# 中文搜索
python3 ~/.openclaw/skills/tavily-search/scripts/search.py "人工智能最新进展" --lang zh
```

### Python调用

```python
import subprocess
import json

result = subprocess.run(
    ['python3', '~/.openclaw/skills/tavily-search/scripts/search.py', 
     '你的搜索词', '--json'],
    capture_output=True, text=True
)
data = json.loads(result.stdout)
```

## Parameters

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `query` | 搜索关键词 | 必填 |
| `--max-results` | 返回结果数量 (1-20) | 5 |
| `--search-depth` | 搜索深度 (basic/advanced) | basic |
| `--include-answer` | 包含AI生成的答案 | True |
| `--include-images` | 包含相关图片 | False |
| `--days` | 时间范围（天） | 无限制 |
| `--lang` | 语言偏好 (zh/en) | auto |
| `--json` | JSON格式输出 | False |

## Examples

### AI新闻搜索
```bash
python3 scripts/search.py "OpenAI GPT-5 release" --days 7 --include-answer
```

### 学术研究
```bash
python3 scripts/search.py "transformer architecture survey" \
  --search-depth advanced --max-results 10
```

### 技术问题
```bash
python3 scripts/search.py "Docker compose networking tutorial" \
  --include-answer --lang zh
```

## Free Tier Limits

- 每月1000次API调用
- 每次最多20个结果
- 基础搜索深度
- 学生可申请更多额度

## Response Format

```json
{
  "query": "搜索词",
  "answer": "AI生成的综合答案（可选）",
  "results": [
    {
      "title": "标题",
      "url": "链接",
      "content": "内容摘要",
      "score": 0.95,
      "published_date": "2024-03-01"
    }
  ],
  "images": [...]
}
```

## Notes

- 首次使用需要先配置TAVILY_API_KEY
- 建议将API key添加到~/.openclaw/.env
- 超过免费额度后会返回错误提示
