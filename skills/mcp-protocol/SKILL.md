# MCP Skill - Model Context Protocol 使用技能

## 概述

本技能用于配置和管理 MCP (Model Context Protocol) 服务器，让 AI 能够调用外部工具。

---

## 1. 安装 mcporter

```bash
npm install -g clawhub
```

确保 `uvx` 可用：

```bash
which uvx
# 如果没有：
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 2. 配置 MCP 服务器

### 2.1 创建配置文件

```bash
mkdir -p ~/.config/mcporter
```

### 2.2 MiniMax MCP 配置示例

```json
{
  "mcpServers": {
    "MiniMax": {
      "type": "stdio",
      "command": "uvx",
      "args": ["minimax-coding-plan-mcp"],
      "env": {
        "MINIMAX_API_KEY": "你的API密钥",
        "MINIMAX_MCP_BASE_PATH": "/tmp/mcporter-output",
        "MINIMAX_API_HOST": "https://api.minimaxi.com"
      }
    }
  }
}
```

保存到 `~/.config/mcporter/mcporter.json`

---

## 3. 验证配置

```bash
npx mcporter --config ~/.config/mcporter/mcporter.json list
```

成功会显示：
```
✔ Listed 1 server (1 healthy)
```

---

## 4. 调用工具

### 4.1 视觉理解

```bash
npx mcporter --config ~/.config/mcporter/mcporter.json call MiniMax.understand_image \
  "prompt: 描述图片内容" \
  "image_source: /path/to/image.jpg"
```

### 4.2 网络搜索

```bash
npx mcporter --config ~/.config/mcporter/mcporter.json call MiniMax.web_search \
  "query: 搜索内容"
```

---

## 5. 常用 MCP 服务器

| MCP 包名 | 功能 |
|----------|------|
| minimax-coding-plan-mcp | 视觉理解、网络搜索 |
| linear-mcp | Linear 项目管理 |
| filesystem-mcp | 文件系统操作 |
| github-mcp | GitHub 操作 |

---

## 6. 常见问题

### 6.1 MCP 服务器离线

- 检查 API Key 是否正确
- 检查网络连接
- 确认 MCP 包名正确

### 6.2 参数错误

查看可用参数：
```bash
npx mcporter list <服务器名> --schema
```

### 6.3 权限问题

- 确保目录存在
- 确保有写入权限

---

_最后更新: 2026-02-24_
