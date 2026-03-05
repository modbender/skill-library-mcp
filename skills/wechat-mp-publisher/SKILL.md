---
name: wechat-mp-publisher
version: 2.0.2
description: 远程微信公众号发布技能 (合规优化版)。通过 HTTP MCP 解决家用宽带 IP 变动问题，支持安全凭证隔离与依赖检查。
homepage: https://github.com/caol64/wenyan-mcp
metadata:
  openclaw:
    emoji: "🚀"
    category: publishing
  clawdbot:
    emoji: "🚀"
    requires:
      bins: ["mcporter", "curl", "jq"]
    install:
      - id: "node"
        kind: "node"
        package: "mcporter"
        bins: ["mcporter"]
        label: "安装 MCP 客户端 (mcporter)"
---

# 微信公众号远程发布 (Remote Publisher - Compliance Optimized)

**核心痛点解决**：家用宽带 IP 频繁变动，无法固定添加到公众号白名单？
本技能通过远程 `wenyan-mcp` 服务中转，让你的本地 OpenClaw 也能稳定发布文章，无需本地 IP 权限！

## 🌟 架构优势

- **IP 漫游无忧**：仅需将远程 MCP 服务器 IP 加入白名单，无论你在家里、咖啡厅还是 4G 热点，都能随时发布。
- **合规隔离**：凭证与系统配置分离，避免污染全局 `TOOLS.md`。
- **依赖自检**：脚本运行时自动检查 `jq`、`mcporter` 和 `wenyan-cli`。
- **灵活配置**：支持自定义 MCP 配置文件路径。

## ⚙️ 快速配置

### 1. 准备凭证 (wechat.env)

在技能根目录下复制 `wechat.env.example` 为 `wechat.env` 并填入公众号凭证：

```bash
cp wechat.env.example wechat.env
nano wechat.env
```

内容示例：
```bash
export WECHAT_APP_ID="wx..."
export WECHAT_APP_SECRET="cx..."
# Optional: 指定 MCP 配置文件 (默认 $HOME/.openclaw/mcp.json)
# export MCP_CONFIG_FILE="/path/to/your/mcp.json"
```

### 2. 连接远程服务 (mcp.json)

确保你的 `mcp.json` 指向远程 MCP 实例：

```json
{
  "mcpServers": {
    "wenyan-mcp": {
      "name": "公众号远程助手",
      "transport": "sse",
      "url": "http://<your-remote-server-ip>:3000/sse",
      "headers": {
        "X-API-Key": "<optional-api-key>"
      }
    }
  }
}
```

## 🚀 使用指南

### 方式 A: 智能助手 (推荐)

直接对我说：
> "帮我把 `path/to/article.md` 发布到公众号，使用默认主题。"

我会自动：
1. 读取 `wechat.env` 获取凭证
2. 检查本地环境 (`mcporter`, `jq`)
3. 调用远程 MCP 完成发布

### 方式 B: 命令行脚本 (高级)

我们提供了封装好的脚本 `scripts/publish-remote.sh`，体验与本地 CLI 一致：

```bash
# 赋予执行权限
chmod +x scripts/publish-remote.sh

# 发布文章 (自动加载 wechat.env)
./scripts/publish-remote.sh ./my-post.md

# 指定主题 (lapis)
./scripts/publish-remote.sh ./my-post.md lapis
```

## 📝 Markdown 规范

与标准 wenyan-cli 一致，头部必须包含元数据：

```markdown
---
title: 我的精彩文章
cover: https://example.com/cover.jpg
---

# 正文开始
...
```

*提示：`cover` 推荐使用图床链接，以确保远程服务器能正确下载封面。*

## 🛠️ 故障排查

| 现象 | 原因 | 解决方案 |
| :--- | :--- | :--- |
| **Dependencies Missing** | 缺少 `jq` 或 `mcporter` | 请确保系统已安装这些工具 |
| **Config Not Found** | 未找到 `wechat.env` | 请按照步骤 1 创建并配置 |
| **IP not in whitelist** | 远程服务器 IP 未加白 | 登录公众号后台 -> 基本配置 -> IP 白名单，添加 **MCP 服务器的公网 IP** |
