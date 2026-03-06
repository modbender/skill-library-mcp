---
name: bocha-web-search
description: 统一封装博查（Bocha）全系搜索接口（Web Search / AI Search / Agent Search / Reranker），使用 Node.js 脚本调用并支持标准参数与原始 JSON 透传。用户提到“博查搜索/联网搜索/AI 搜索/Agent 搜索/重排/rerank/事实核查/行业研报检索”时使用。
---

# bocha-web-search

统一封装 Bocha API（Web / AI / Agent / Reranker），适合中文互联网检索、问答增强与结果重排。

## 前置配置

二选一：

1) 环境变量（推荐）

```bash
export BOCHA_API_KEY="你的博查API Key"
```

2) 本地配置文件（仅本机）

在技能目录创建 `config.json`：

```json
{
  "apiKey": "你的博查API Key"
}
```

## 统一调用入口

优先使用：`scripts/bocha.sh`

```bash
cd skills/bocha-web-search

# Web Search
bash scripts/bocha.sh web --query "中国最火 app 研报" --count 10 --freshness oneYear --summary true --pretty

# AI Search
bash scripts/bocha.sh ai --query "总结中国移动互联网最新趋势" --count 8 --summary true --timeout 45

# Agent Search
bash scripts/bocha.sh agent --query "给我可追溯来源的回答" --count 8 --freshness oneMonth

# Reranker（通常配合 --raw-json 传 documents）
bash scripts/bocha.sh rerank --query "中国最火app" --raw-json '{"documents":["...","..."]}'
```

## 子命令

- `web`：Web Search API
- `ai`：AI Search API
- `agent`：Agent Search API
- `rerank`：Semantic Reranker API

## 参数

- `--query`：查询词（除纯重排场景外通常必填）
- `--count`：返回条数（默认 10，脚本内限幅 1~50）
- `--freshness`：时间过滤（默认 `noLimit`）
- `--summary`：是否返回摘要（默认 `true`）
- `--page` / `--offset`：分页参数（若接口支持）
- `--language` / `--region` / `--site`：语言、地区、站点过滤（若接口支持）
- `--raw-json`：原始 JSON 透传（用于覆盖/补充高级参数）
- `--timeout`：请求超时秒数（默认 30）
- `--pretty`：Node 端 JSON 美化输出（无需 `jq`）

## 输出规则

- 默认输出 API 原始 JSON。
- 若提供 `--raw-json`，会与标准参数合并后发送，且 `--raw-json` 字段优先。

## 使用建议

1. 先宽搜拿候选（例：`2025 中国移动互联网 报告`）。
2. 再加限定词二次检索（例：`QuestMobile`、`CNNIC`、`CTR`）。
3. 回答时优先引用机构来源，避免只用自媒体榜单。
