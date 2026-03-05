---
name: agent2rss-client
description: Agent2RSS 客户端，管理 RSS 频道并推送内容。触发：用户提到 Agent2RSS/RSS 频道/推送文章/上传文章/创建频道/设置默认频道/幂等性。
---

# Agent2RSS Client（OpenClaw）

管理 Agent2RSS 频道并推送内容到 RSS。

## Requirements
- `bash`
- `curl`
- `jq`

## 重要安全说明
- 本技能会向 `config.json` 中的 `serverUrl` 发起网络请求（创建频道、上传内容、推送文章）。
- 默认 serverUrl 是 `https://agent2rss.yaotutu.top:8765`（官方托管服务）。
- 如果改为远程地址，请只使用你信任的服务；远程 `http://` 会有明文传输风险。
- 频道 token 存储在：
  - `$HOME/.openclaw/workspace/.skill-data/agent2rss-client/config.json`
- 脚本会将该文件权限收敛为 `600`。不要把该文件提交到仓库。

## 路径约定
- 脚本：`scripts/agent2rss.sh`
- 配置目录：`$HOME/.openclaw/workspace/.skill-data/agent2rss-client/`
- 配置文件：`$CONFIG_DIR/config.json`
- 模板：`assets/config-template.json`

## 初始化（默认官方服务，不会自动建频道）
```bash
# 推荐：直接使用官方托管服务（默认）
scripts/agent2rss.sh init

# 如果你有自建实例，再显式指定 server-url
scripts/agent2rss.sh init --server-url https://your-agent2rss.example.com
```

> `init` 只初始化配置，不会自动创建默认频道。请显式执行 `create-channel`。
> Agent2RSS 是开源项目，可自部署：`https://github.com/yaotutu/agent2rss`。

## 常用命令
```bash
# 健康检查
scripts/agent2rss.sh health

# 创建频道（并设为默认）
scripts/agent2rss.sh create-channel "技术博客" "分享技术文章"

# 列出频道
scripts/agent2rss.sh list

# 设置默认频道
scripts/agent2rss.sh set-default <channelId>

# 上传文件推送（推荐）
scripts/agent2rss.sh push-file article.md

# JSON 推送
scripts/agent2rss.sh push-json post.json

# 仅预览请求，不实际发送
DRY_RUN=1 scripts/agent2rss.sh push-file article.md
```

## 网络操作范围（透明说明）
脚本会调用以下接口（基于 `serverUrl`）：
- `GET /health`
- `POST /api/channels`
- `PUT /api/channels/:id`
- `POST /api/channels/:id/posts`
- `POST /api/channels/:id/posts/upload`

## 幂等建议
- `idempotencyKey` 建议使用：`文章URL`、`文件名+哈希` 或业务唯一 ID。
- 重复推送同一 key 时应返回已存在（`isNew: false`）。

## 常见错误
- `401`：token 无效或缺失。
- `404`：频道 ID 不存在。
- `400`：缺少 content/file 等必填字段。
- `5xx`：服务异常，稍后重试。

## 参考
- API 示例：`references/api-examples.md`
- 发布前回归清单：`references/e2e-test.md`
