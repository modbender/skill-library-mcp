---
name: zhipu-search
description: 使用智谱 Web Search API 进行网络搜索。当用户需要搜索最新信息、查找实时数据、查询新闻、研究某个话题或获取网络上的信息时使用。支持多种搜索引擎（智谱基础版/高阶版、搜狗、夸克），可配置搜索范围、时间筛选、结果数量等参数。
tools: Bash, Write
required_env_vars: ZHIPUAI_API_KEY
---

# 智谱 Web Search Skill

使用智谱 AI 的 Web Search API 进行网络搜索，获取实时、结构化的搜索结果。

## 前置条件

1. 获取智谱 BigModel 开放平台的 API Key：https://bigmodel.cn/usercenter/apikeys
2. 配置 API Key（见下方说明）

## API Key 配置

在使用前，请设置您的智谱 API Key：

```bash
export ZHIPUAI_API_KEY="your-api-key-here"
```

**重要**: 请使用环境变量方式配置 API Key，不要将密钥硬编码在脚本或配置文件中。

## 快速开始

使用提供的 `search_util.py` 脚本进行搜索：

```bash
# 基本搜索
python search_util.py "搜索内容"

# 查看帮助
python search_util.py --help
```

## 搜索引擎选项

| 引擎编码 | 说明 |
|---------|------|
| `search_std` | 智谱基础版搜索引擎 |
| `search_pro` | 智谱高阶版搜索引擎（推荐） |
| `search_pro_sogou` | 搜狗搜索 |
| `search_pro_quark` | 夸克搜索 |

## 搜索参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| `search_query` | String | 是 | 搜索内容，建议不超过 70 字符 |
| `search_engine` | String | 是 | 搜索引擎编码 |
| `search_intent` | Boolean | 是 | 是否进行意图识别 |
| `count` | Int | 否 | 返回结果条数 (1-50, 默认 10) |
| `search_recency_filter` | String | 否 | 时间筛选: oneDay/oneWeek/oneMonth/oneYear/noLimit |
| `content_size` | String | 否 | 内容长度: medium/high |
| `search_domain_filter` | String | 否 | 限定域名 |

## API 概览

**请求地址**: `https://open.bigmodel.cn/api/paas/v4/web_search`

**认证方式**: 使用智谱 API Key，通过 Authorization header 传递

## 响应结构

```json
{
  "id": "任务ID",
  "created": 1748261757,
  "search_intent": [
    {
      "query": "原始搜索query",
      "intent": "SEARCH_ALL|SEARCH_NONE|SEARCH_ALWAYS",
      "keywords": "改写后的搜索关键词"
    }
  ],
  "search_result": [
    {
      "title": "标题",
      "content": "内容摘要",
      "link": "结果链接",
      "media": "网站名称",
      "icon": "网站图标",
      "refer": "角标序号",
      "publish_date": "网站发布时间"
    }
  ]
}
```

## 工作流程

1. 确认用户已配置 API Key
2. 根据用户需求选择合适的搜索参数
3. 执行搜索并以友好格式展示结果（标题、来源、日期、链接、摘要）

## 错误码

| 错误码 | 说明 |
|-------|------|
| 1701 | 网络搜索并发已达上限，请稍后重试 |
| 1702 | 系统未找到可用的搜索引擎服务 |
| 1703 | 搜索引擎未返回有效数据，请调整查询条件 |

## 更多信息

- [智谱 Web Search API 文档](https://bigmodel.cn/dev/api/search-tool/web-search)
- [产品价格](https://www.bigmodel.cn/pricing)
