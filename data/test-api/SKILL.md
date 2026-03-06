---
name: blockbeats-openclaw-skill
description: BlockBeats API skill for querying crypto news, newsflashes, and articles. Requires a valid api-key token to access the BlockBeats Pro API.
metadata:
  openclaw:
    emoji: "📰"
    requires:
      bins:
        - node
---

# BlockBeats API Skill

通过 BlockBeats Pro API 查询加密货币快讯和文章。使用前需要先设置 API Token。

## 配置 Token

首次使用时设置你的 API Key：

```
设置 BlockBeats token: <your-api-key>
```

Token 会保存在 `~/.openclaw/skills/blockbeats-api/config.json`，后续无需重复设置。

## 支持的查询

### 快讯（Newsflash）

- **获取最新快讯** / **快讯列表**
- **重要快讯** / **important newsflash**
- **原创快讯** / **original newsflash**
- **首发快讯** / **first newsflash**
- **链上快讯** / **onchain newsflash**
- **融资快讯** / **financing newsflash**
- **预测市场快讯** / **prediction newsflash**

### 文章（Article）

- **文章列表** / **article list**
- **文章详情 <id>** / **article detail <id>**

### 参数说明

所有列表接口均支持：
- `page`：页码（默认 1）
- `size`：每页数量，1-50（默认 10）
- `lang`：语言，支持 `cn`（简中）/ `en`（英文）/ `cht`（繁中）/ `vi` / `ko` / `ja` / `th` / `tr`（默认 cn）

## 使用示例

```
帮我看看最新的快讯
查一下今天的重要快讯，显示5条
获取融资快讯，英文版
获取文章列表，第2页
获取文章详情 12345
设置 BlockBeats token: abc123xyz
```

## 执行方式

调用对应子命令：

```bash
# 设置 token
node ~/.openclaw/skills/blockbeats-api/scripts/api.js set-token <token>

# 查询快讯
node ~/.openclaw/skills/blockbeats-api/scripts/api.js newsflash [--type important|original|first|onchain|financing|prediction] [--page 1] [--size 10] [--lang cn]

# 查询文章列表
node ~/.openclaw/skills/blockbeats-api/scripts/api.js article [--page 1] [--size 10] [--lang cn]

# 查询文章详情
node ~/.openclaw/skills/blockbeats-api/scripts/api.js article-detail <id>
```

## 命令解析规则

根据用户意图匹配子命令：

| 用户意图 | 执行命令 |
|---------|---------|
| 设置/更新 token | `api.js set-token <token>` |
| 最新快讯 / 快讯列表 | `api.js newsflash` |
| 重要快讯 | `api.js newsflash --type important` |
| 原创快讯 | `api.js newsflash --type original` |
| 首发快讯 | `api.js newsflash --type first` |
| 链上快讯 | `api.js newsflash --type onchain` |
| 融资快讯 | `api.js newsflash --type financing` |
| 预测市场快讯 | `api.js newsflash --type prediction` |
| 文章列表 | `api.js article` |
| 文章详情 + id | `api.js article-detail <id>` |

提取用户请求中的 `--page`、`--size`、`--lang` 参数并附加到命令中。

## 错误处理

- 未设置 token：提示用户先执行 `设置 BlockBeats token: <your-api-key>`
- API 返回非 0 状态码：显示错误信息
- 网络错误：显示连接失败提示
