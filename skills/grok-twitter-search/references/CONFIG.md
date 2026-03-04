# Grok Twitter Search - 配置参考

## 快速开始

### 1. 获取 Grok API Key

访问 https://x.ai/api 注册并获取 API Key。

免费额度：$25/月（足够数千次搜索）

### 2. 配置方式选择

#### 方式 A: OpenClaw 配置文件（推荐）

编辑 `~/.openclaw/openclaw.json`：

```json5
{
  skills: {
    entries: {
      "grok-twitter-search": {
        enabled: true,
        apiKey: {
          source: "env",
          provider: "default",
          id: "GROK_API_KEY"
        },
        // 可选：显式设置代理
        env: {
          // SOCKS5_PROXY: "socks5://127.0.0.1:40000"
        }
      }
    }
  }
}
```

然后在系统环境变量中设置：
```bash
export GROK_API_KEY="your_api_key_here"
```

#### 方式 B: 纯环境变量

```bash
export GROK_API_KEY="your_api_key_here"
export SOCKS5_PROXY="socks5://127.0.0.1:40000"  # 可选，不设置则自动检测
```

添加到 `~/.bashrc` 或 `~/.zshrc` 使其永久生效。

#### 方式 C: Gateway 环境文件

```bash
# 写入 gateway.env
echo "GROK_API_KEY=your_api_key_here" >> ~/.openclaw/gateway.env
echo "SOCKS5_PROXY=socks5://127.0.0.1:40000" >> ~/.openclaw/gateway.env

# 重启 Gateway
openclaw gateway restart
```

## WARP 代理安装指南

### Ubuntu/Debian

```bash
# 添加 Cloudflare 仓库
curl -fsSL https://pkg.cloudflareclient.com/cloudflare-warp.asc | \
  sudo gpg --dearmor -o /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] \
  https://pkg.cloudflareclient.com/ $(lsb_release -cs) main" | \
  sudo tee /etc/apt/sources.list.d/cloudflare-client.list

# 安装
sudo apt update
sudo apt install cloudflare-warp

# 启动服务
sudo systemctl enable warp-svc
sudo systemctl start warp-svc

# 注册并连接
warp-cli registration new
warp-cli connect
```

### macOS

```bash
brew install --cask cloudflare-warp
# 在系统菜单栏启动 WARP 应用
```

### 验证 WARP 状态

```bash
bash scripts/check_warp.sh
```

## 代理优先级规则

脚本按以下优先级确定是否使用代理：

1. **用户显式配置** (`SOCKS5_PROXY` 环境变量)
2. **自动检测 WARP** (检查进程 + 端口连通性)
3. **直连** (如果 Grok API 可直接访问)

## 故障排查

### 检查清单

```bash
# 1. 检查 API Key
echo $GROK_API_KEY

# 2. 检查代理设置
echo $SOCKS5_PROXY

# 3. 检查 WARP 状态
bash scripts/check_warp.sh

# 4. 测试搜索
uv run scripts/search_twitter.py --query "test" --max-results 3
```

### 常见问题

**Q: 在中国大陆无法访问 Grok API**
- 必须安装 WARP 或其他出海代理
- 确保 WARP 已连接：`warp-cli status`

**Q: 提示 "API Key 无效"**
- 检查 Key 是否正确复制
- 确认账户有可用额度：https://x.ai/api

**Q: 返回结果为空**
- 尝试不同的搜索词
- 某些敏感内容可能被过滤

## 高级配置

### 自定义代理

如果使用其他 SOCKS5 代理（非 WARP）：

```bash
export SOCKS5_PROXY="socks5://user:pass@host:port"
```

### 禁用代理强制直连

```bash
export SOCKS5_PROXY=""
```

### 在 Docker 中使用

```dockerfile
ENV GROK_API_KEY=your_key
ENV SOCKS5_PROXY=socks5://host.docker.internal:40000
```
