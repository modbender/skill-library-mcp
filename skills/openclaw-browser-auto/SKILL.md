# OpenClaw 浏览器自动化配置

配置OpenClaw连接远程Chrome/CDP浏览器进行自动化操作。

## 适用场景

- 连接远程服务器的Chrome浏览器
- 使用Docker容器运行的无头浏览器
- 连接browserless.io云服务

## 配置步骤

### 1. 启动CDP浏览器容器

推荐使用 `chromedp/headless-shell`（轻量且保持会话）：

```bash
docker run -d --name browser-auto -p 9222:9222 --shm-size=512m chromedp/headless-shell:latest
```

验证CDP可用：
```bash
curl http://127.0.0.1:9222/json/version
```

### 2. 配置OpenClaw

在 `~/.openclaw/openclaw.json` 中添加browser配置：

```json5
{
  "browser": {
    "enabled": true,
    "defaultProfile": "remote-chrome",
    "attachOnly": true,
    "profiles": {
      "remote-chrome": {
        "cdpUrl": "http://127.0.0.1:9222",
        "color": "#00AA00"
      }
    }
  }
}
```

### 3. 重启Gateway

```bash
systemctl --user restart openclaw-gateway
```

### 4. 验证

```bash
openclaw browser status
```

## 关键配置项

| 配置项 | 说明 |
|--------|------|
| `browser.enabled` | 启用浏览器 |
| `browser.defaultProfile` | 默认使用的浏览器配置名 |
| `browser.attachOnly` | true=不尝试启动本地浏览器，只连接远程 |
| `profiles.<name>.cdpUrl` | 远程CDP地址 |

## 云服务方案

### Browserless.io（付费）
```json5
{
  "browser": {
    "defaultProfile": "browserless",
    "profiles": {
      "browserless": {
        "cdpUrl": "https://production-sfo.browserless.io?token=<API_KEY>"
      }
    }
  }
}
```

## 常见问题

1. **端口被占用** - 设置 `attachOnly: true`
2. **标签页丢失** - 使用 chromedp/headless-shell 而非 browserless/chrome
3. **环境变量不生效** - 需要修改systemd服务配置
