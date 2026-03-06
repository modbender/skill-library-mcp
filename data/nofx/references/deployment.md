# NOFX 部署指南

## 快速部署

### 一键安装 (Linux/macOS)

```bash
curl -fsSL https://raw.githubusercontent.com/NoFxAiOS/nofx/main/install.sh | bash
```

安装完成后访问: **http://127.0.0.1:3000**

### Docker Compose

```bash
# 下载并启动
curl -O https://raw.githubusercontent.com/NoFxAiOS/nofx/main/docker-compose.prod.yml
docker compose -f docker-compose.prod.yml up -d

# 管理命令
docker compose -f docker-compose.prod.yml logs -f      # 查看日志
docker compose -f docker-compose.prod.yml restart      # 重启
docker compose -f docker-compose.prod.yml down         # 停止
docker compose -f docker-compose.prod.yml pull && docker compose -f docker-compose.prod.yml up -d  # 更新
```

### Railway 一键云部署

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/nofx?referralCode=nofx)

## Windows 安装

### 方法 1: Docker Desktop (推荐)

1. 下载安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. 启动 Docker Desktop
3. PowerShell 运行:
```powershell
curl -o docker-compose.prod.yml https://raw.githubusercontent.com/NoFxAiOS/nofx/main/docker-compose.prod.yml
docker compose -f docker-compose.prod.yml up -d
```

### 方法 2: WSL2

1. 安装 WSL2:
```powershell
wsl --install
```

2. 安装 Ubuntu，然后在 WSL2 中运行一键安装脚本

## 手动安装 (开发者)

### 前置要求

- Go 1.21+
- Node.js 18+
- TA-Lib

```bash
# macOS
brew install ta-lib

# Ubuntu/Debian
sudo apt-get install libta-lib0-dev
```

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/NoFxAiOS/nofx.git
cd nofx

# 2. 安装后端依赖
go mod download

# 3. 安装前端依赖
cd web && npm install && cd ..

# 4. 构建并启动后端
go build -o nofx && ./nofx

# 5. 启动前端 (新终端)
cd web && npm run dev
```

## 服务器部署

### 快速部署 (HTTP)

默认禁用传输加密，可直接通过 IP 访问:

```bash
curl -fsSL https://raw.githubusercontent.com/NoFxAiOS/nofx/main/install.sh | bash
# 访问: http://YOUR_SERVER_IP:3000
```

### HTTPS (Cloudflare)

1. 添加域名到 Cloudflare
2. 创建 DNS A 记录指向服务器 IP，开启代理 (橙色云)
3. SSL/TLS 设置为 Flexible
4. 编辑 `.env` 设置 `TRANSPORT_ENCRYPTION=true`
5. 访问: `https://nofx.yourdomain.com`

## 更新

每日运行以获取最新版本:

```bash
curl -fsSL https://raw.githubusercontent.com/NoFxAiOS/nofx/main/install.sh | bash
```

## 初始配置

1. **配置 AI 模型** - 添加 API Key
2. **配置交易所** - 设置交易所 API
3. **创建策略** - 在 Strategy Studio 配置
4. **创建 Trader** - 组合 AI + 交易所 + 策略
5. **开始交易** - 启动 Trader
