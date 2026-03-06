# MCP Server Discovery Skill

快速发现和管理 MCP (Model Context Protocol) 服务器的 OpenClaw 技能。

## 功能

- 🔍 发现官方和社区 MCP 服务器
- 🔎 按类别和关键词搜索
- 📋 获取服务器详细信息和安装指南
- ⚙️ 生成 MCP 客户端配置文件

## 安装

```bash
# 通过 ClawHub 安装
openclaw skills install mcp-server-discovery
```

## 使用

### 列出所有服务器
```bash
python3 scripts/mcp_discover.py list
```

### 搜索服务器
```bash
python3 scripts/mcp_discover.py search --query "database"
```

### 获取服务器详情
```bash
python3 scripts/mcp_discover.py info --name postgres
```

### 生成配置
```bash
python3 scripts/mcp_discover.py config --servers "filesystem,memory,fetch"
```

## 服务器类别

- **filesystem** - 文件系统访问
- **dev** - 开发工具 (GitHub 等)
- **database** - 数据库 (PostgreSQL, SQLite)
- **web** - 网页抓取和内容获取
- **search** - 搜索引擎集成
- **memory** - 持久化记忆和知识图谱

## 示例配置

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

## 相关链接

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [官方服务器仓库](https://github.com/modelcontextprotocol/servers)
- [Awesome MCP Servers](https://github.com/appcypher/awesome-mcp-servers)

## License

MIT
