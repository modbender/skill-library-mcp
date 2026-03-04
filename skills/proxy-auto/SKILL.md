# Proxy Auto - 自动代理切换

## 功能

当需要访问外网时自动启用 SOCKS5 代理。

## 使用方法

### 在命令前添加代理环境变量

```bash
source /root/.openclaw/proxy-auto.sh <command>
```

### 或者手动设置环境变量

```bash
export http_proxy=http://127.0.0.1:10808
export https_proxy=http://127.0.0.1:10808
export ALL_PROXY=socks5://127.0.0.1:10808
```

## 代理配置

- **类型**: VMess over WebSocket
- **地址**: 127.0.0.1:10808 (SOCKS5)
- **后端**: 新加坡节点 (Netflix/Disney+/OpenAI 优化)

## 测试命令

```bash
# 测试 Google
curl -s --socks5 127.0.0.1:10808 https://www.google.com

# 测试 GitHub
curl -s --socks5 127.0.0.1:10808 https://api.github.com

# 测试 OpenAI
curl -s --socks5 127.0.0.1:10808 https://api.openai.com
```

## 自动使用场景

- 访问 GitHub API
- 调用 OpenAI/Claude 等 AI 服务
- 抓取境外网站数据
- 安装 npm/pip 境外包

---
_最后更新：2026-03-02_
