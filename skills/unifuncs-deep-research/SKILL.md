---
name: unifuncs-deep-research
description: 使用 UniFuncs API 进行深度研究，生成万字报告，支持多种输出格式。当用户需要深度研究、研究报告、深研时使用。
argument-hint: [研究主题] [--model u2|u1|u1-pro] [--output-type report|summary|wechat-article]
allowed-tools: Bash(curl:*)
---

# UniFuncs 深度研究 Skill

深度分析，产出万字报告，支持多种输出格式。

## 首次使用配置

1. 前往 https://unifuncs.com/account 获取 API Key
2. 设置环境变量：`export UNIFUNCS_API_KEY="sk-your-api-key"`

## 使用方法

执行深度研究：
```bash
curl -X POST "https://api.unifuncs.com/deepresearch/v1/chat/completions" \
  -H "Authorization: Bearer $UNIFUNCS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "u2", "messages": [{"role": "user", "content": "$ARGUMENTS"}]}'
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| messages | 研究主题 | 必填 |
| model | `u2`/`u1`/`u1-pro` | u2 |
| output_type | 输出格式 | report |

## 输出格式

- `report` - 万字报告
- `summary` - 精炼摘要
- `wechat-article` - 微信公众号
- `xiaohongshu-article` - 小红书
- `zhihu-article` - 知乎文章

## 更多信息

- 详细 API 文档见 [api.md](references/api.md)
