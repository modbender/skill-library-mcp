# wechat-mp-publisher

**Remote WeChat Official Account Publisher via HTTP MCP**

OpenClaw 技能，用于将 Markdown 文章一键发布到微信公众号草稿箱。
专为解决家用宽带动态 IP 痛点而生，通过远程 `wenyan-mcp` 服务中转，让你的本地环境无需繁琐配置即可稳定发文。

## ✨ 核心特性

- **IP 漫游**: 仅需一次配置远程 MCP 服务器 IP 白名单，无论在哪都能发。
- **大文件传输**: 优化的 `upload_file` 协议，稳定支持长图文。
- **完全兼容**: 支持 wenyan-cli 所有排版主题与 Frontmatter 语法。
- **安全隔离**: 敏感凭证 (AppID/Secret) 仅在运行时传递，不落地存储。

## 📦 快速安装

1. 下载并解压 `wechat-mp-publisher.zip` 到 OpenClaw `skills/` 目录。
2. 配置 `/root/.openclaw/mcp.json` 指向远程服务。
3. 运行 `./scripts/publish-remote.sh` 或直接与 Agent 对话发布。

## 📚 文档索引

- [使用说明 (SKILL.md)](SKILL.md)
- [排版主题预览](references/themes.md)
- [故障排查指南](references/troubleshooting.md)

## 🔗 相关项目

- [wenyan-mcp](https://github.com/caol64/wenyan-mcp): 本技能依赖的后端服务
- [wenyan-cli](https://github.com/caol64/wenyan-cli): 核心排版引擎
