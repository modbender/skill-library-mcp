---
name: Cloudflare MCP
description: 使用 Cloudflare Code Mode MCP 调用 Cloudflare API。支持
  Workers、DNS、R2、D1、KV、Vectorize 等 2500+ 端点。
---

# Cloudflare MCP

使用 Cloudflare Code Mode MCP 调用 Cloudflare API。支持 Workers、DNS、R2、D1、KV、Vectorize 等 2500+ 端点。

## 触发词

- "Cloudflare"
- "CF"
- "DNS"
- "Workers"
- "R2"
- "D1"
- "KV"

## 前置要求

在 openclaw.json 中配置 MCP：

```json
{
  "mcpServers": {
    "cloudflare-api": {
      "url": "https://mcp.cloudflare.com/mcp"
    }
  }
}
```

然后重启 Gateway。首次使用时会跳转到 Cloudflare 授权页面。

## 可用操作

| 操作 | 说明 |
|------|------|
| 列出 Workers | 列出所有 Workers 脚本 |
| 查看 DNS 记录 | 获取域名的 DNS 记录 |
| 创建 DNS 记录 | 添加新的 DNS 记录 |
| 创建 KV 命名空间 | 创建新的 KV 存储 |
| 创建 R2 存储桶 | 创建 R2 对象存储 |
| 查看账户信息 | 获取账户详情和配额 |

## 使用示例

- "列出我所有的 Workers"
- "查看 example.com 的 DNS 记录"
- "创建一个叫 my-cache 的 KV 命名空间"
- "给 api.example.com 添加一条 A 记录指向 1.2.3.4"

## 注意事项

- Code Mode 模式下，模型会自动搜索 API 端点并执行调用
- 首次使用需要 OAuth 授权
- 所有操作通过 Cloudflare MCP 的 search() 和 execute() 工具完成
