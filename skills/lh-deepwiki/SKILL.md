---
name: lh-deepwiki
description: Query DeepWiki MCP service via Streamable HTTP to get GitHub repository documentation, wiki structure, and AI-powered Q&A.
homepage: https://github.com/liuhedev/lh-openclaw-kit
---

# lh-deepwiki

这是由龙虾哥（liuhedev）维护的 DeepWiki MCP 技能。相比原版，本版本修复了 API 协议变动导致的问题，改用新的 `/mcp` 端点（Streamable HTTP），并优化了参数传递和超时处理。

## 主要变更
- **协议升级**: 从过时的 SSE 切换到新的 Streamable HTTP 端点。
- **参数修复**: 将旧版的 `repo` 参数统一更新为 `repoName`。
- **超时优化**: 默认超时时间增加至 120s，适配复杂问答场景。
- **开源维护**: 托管于 `lh-openclaw-kit`，支持自主迭代。

## 命令说明

### AI 问答 (Ask Question)
对 GitHub 公共仓库进行基于文档的 AI 问答。
```bash
node ./scripts/deepwiki.js ask <owner/repo> "你的问题"
```

### 读取 Wiki 结构 (Read Wiki Structure)
获取指定仓库的文档目录结构。
```bash
node ./scripts/deepwiki.js structure <owner/repo>
```

### 读取 Wiki 内容 (Read Wiki Contents)
查看指定路径的具体文档内容。
```bash
node ./scripts/deepwiki.js contents <owner/repo> <path>
```

## 使用示例

**问问 OpenClaw 是什么:**
```bash
node ./scripts/deepwiki.js ask openclaw/openclaw "What is OpenClaw?"
```

**获取 React 文档结构:**
```bash
node ./scripts/deepwiki.js structure facebook/react
```

## 注意事项
- 基础服务地址: `https://mcp.deepwiki.com/mcp`
- 仅支持公开 GitHub 仓库。
- 无需 API Key 或身份验证。
