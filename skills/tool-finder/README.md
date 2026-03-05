# Tool Finder 🦞

统一搜索 ClawHub skills 和 Smithery MCP servers。

## 快速开始

### 搜索工具

```bash
# 搜索所有来源
./scripts/tool-finder.sh search "web search"

# 只搜索 skills
./scripts/tool-finder.sh search "github" --type skill

# 只搜索 MCPs
./scripts/tool-finder.sh search "database" --type mcp

# 限制结果数量
./scripts/tool-finder.sh search "search" --limit 5
```

### 安装工具

```bash
# 安装 skill
./scripts/tool-finder.sh install <skill-name> --type skill

# 安装 MCP（需要手动指定客户端）
./scripts/tool-finder.sh install exa --type mcp
# 然后根据提示手动安装
```

## 输出示例

```
╔════════════════════════════════════════════════════════════╗
║ 🔍 搜索结果：search
╚════════════════════════════════════════════════════════════╝

━━━ ClawHub Skills ━━━
名称                    类型    描述
────────────────────────────────────────────────────────
tavily-search           skill   Tavily Web Search
baidu-search            skill   baidu web search

━━━ Smithery MCPs ━━━
名称                    类型    描述
────────────────────────────────────────────────────────
Exa Search              MCP     Fast, intelligent web search and web crawling
Brave Search            MCP     Visit https://brave.com/search/api/
```

## 依赖

- `npx` / Node.js
- `curl`
- `jq`

## 许可证

MIT
