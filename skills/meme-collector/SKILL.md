---
name: meme-collector
description: 自动搜集最新网络热梗并写入 Dify 知识库。用于定期更新热梗数据库，支持去重。触发词："收集热梗"、"更新热梗"、"热梗入库"、"meme collector"。当用户要求搜集/更新/补充网络热梗到 Dify 知识库时使用此 skill。
---

# Meme Collector - 热梗收集器

自动从网上搜集最新网络热梗，与 Dify 知识库去重后写入新梗。

## 配置

运行前需要以下信息（优先从 TOOLS.md 或用户消息获取）：

| 参数 | 说明 | 示例 |
|------|------|------|
| `DATASET_ID` | Dify 知识库 ID | `57bd8e53-b1bd-4124-8219-fff573733a40` |
| `API_KEY` | Dify API Key | `dataset-xxx` |
| `PROXY` | HTTP 代理（访问 Dify API） | `http://127.0.0.1:20171` |

如果用户未提供，询问。

## 工作流程

### Phase 1: 获取已有梗（去重基准）

运行脚本获取知识库中已有的梗名称列表：

```bash
python3 scripts/dify_ops.py --dataset-id $DATASET_ID --api-key $API_KEY --proxy $PROXY list
```

记住这个列表，后续搜集时跳过同名梗。

### Phase 2: 搜集新梗

用 `web_search` 搜索最新热梗。搜索策略：

1. 搜索关键词组合（根据时间间隔调整）：
   - `"2025年最新网络热梗 流行语"`
   - `"最近一周网络热梗 盘点"`
   - `"抖音 B站 最新流行梗"`
   - `"网络流行语 新梗 盘点"`
   - `"小红书 微博 热梗"`

2. 用 `web_fetch` 抓取搜索结果中的盘点文章，提取梗的详细信息

3. 目标：每次收集 10-20 条新梗（去重后）

### Phase 3: 结构化 & 去重

对每条搜集到的梗：

1. 检查是否与已有梗重名或含义相同（名称不同但实质相同也要去重）
2. 按标准格式结构化（见 `references/meme-format.md`）
3. 评估热度等级

### Phase 4: 批量写入

将去重后的新梗构造为 JSON 数组，用脚本批量写入：

```bash
# JSON 格式：[{"name": "梗名称", "text": "Markdown内容"}, ...]
python3 scripts/dify_ops.py --dataset-id $DATASET_ID --api-key $API_KEY --proxy $PROXY batch --json-file /tmp/new_memes.json
```

脚本会自动再次检查去重（双重保险）。

### Phase 5: 汇报结果

向用户汇报：
- 搜集到多少条梗
- 去重跳过多少条
- 成功写入多少条
- 列出新写入的梗名称

## 注意事项

- 搜索时用 `search_lang: "zh"` 和 `country: "CN"` 确保中文结果
- 热梗信息要准确，不确定的内容宁可不写也不要编造
- 每条梗的"剧本融入指南"要具体实用，不要泛泛而谈
- 写入间隔 1 秒，避免 API 限流
