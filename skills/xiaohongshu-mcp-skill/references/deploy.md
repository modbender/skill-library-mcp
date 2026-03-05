# 首次部署 xiaohongshu-mcp

> Based on [xpzouying/xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)

## 环境要求

- macOS / Linux / Windows
- 首次运行自动下载 Chromium (~150MB)

## 部署步骤

### 1. 下载预编译二进制

从 [GitHub Releases](https://github.com/xpzouying/xiaohongshu-mcp/releases) 下载对应平台版本：

```bash
# macOS ARM64
gh release download --repo xpzouying/xiaohongshu-mcp \
  --pattern "xiaohongshu-mcp-darwin-arm64.tar.gz" --dir /tmp
mkdir -p ~/xiaohongshu-mcp/bin
tar -xzf /tmp/xiaohongshu-mcp-darwin-arm64.tar.gz -C ~/xiaohongshu-mcp/bin/

# macOS Intel: xiaohongshu-mcp-darwin-amd64.tar.gz
# Linux x64: xiaohongshu-mcp-linux-amd64.tar.gz
# Windows x64: xiaohongshu-mcp-windows-amd64.zip
```

解压后包含两个可执行文件：
- `xiaohongshu-login-*` — 登录工具
- `xiaohongshu-mcp-*` — MCP 服务

### 2. 登录小红书

```bash
cd ~/xiaohongshu-mcp
./bin/xiaohongshu-login-darwin-arm64
```

- 首次运行自动下载 Chromium 到 `~/.cache/rod/browser/`
- 浏览器弹出后扫码或手机号登录
- 登录成功后 `cookies.json` 保存在当前目录
- 后续无需重复登录（除非 cookies 过期）

### 3. 启动 MCP 服务 (nohup 后台)

```bash
cd ~/xiaohongshu-mcp
nohup ./bin/xiaohongshu-mcp-darwin-arm64 > mcp.log 2>&1 &
echo $! > mcp.pid
```

服务监听: `http://localhost:18060/mcp`

验证：
```bash
curl -s -X POST http://localhost:18060/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'
```

### 4. 配置 MCP 客户端

**Claude Code:**
```bash
claude mcp add --transport http xiaohongshu-mcp http://localhost:18060/mcp
```

**其他 MCP 客户端配置:**
```json
{
  "mcpServers": {
    "xiaohongshu-mcp": {
      "url": "http://localhost:18060/mcp",
      "transport": "http"
    }
  }
}
```

## 本机实际部署路径

项目目录: `/Users/handi7/Documents/agentic-coding-projects/projects/xiaohongshu-mcp`

启动服务:
```bash
cd /Users/handi7/Documents/agentic-coding-projects/projects/xiaohongshu-mcp
nohup ./bin/xiaohongshu-mcp-darwin-arm64 > mcp.log 2>&1 &
```

## 日常运维

| 操作 | 命令 |
|------|------|
| 启动服务 | `nohup ./bin/xiaohongshu-mcp-darwin-arm64 > mcp.log 2>&1 &` |
| 查看日志 | `tail -f mcp.log` |
| 停止服务 | `kill $(lsof -ti:18060)` 或 `kill $(cat mcp.pid)` |
| 重新登录 | `./bin/xiaohongshu-login-darwin-arm64` |
| 查看 PID | `lsof -ti:18060` |

## 注意事项

1. **同账号单端登录**：小红书不允许同一账号在多个 web 端登录，保持 MCP 独占访问
2. **Cookies 过期**：需重新运行登录工具
3. **实名认证**：新号可能触发实名认证提醒，建议先实名
4. **发帖限制**：每天 50 篇上限
