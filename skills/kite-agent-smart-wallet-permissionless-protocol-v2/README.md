# Kite AI Agent Smart Wallet Protocol

## 简介 / Introduction

这是一个让你在Telegram里管理加密货币钱包的工具。/ A tool to manage your crypto wallet from Telegram.

- 运行在你自己电脑上 / Bot runs on your machine
- 私钥你自己保管 / Your private key stays with you
- 在Kite AI测试网操作 / Operates on Kite AI testnet

## 快速开始 / Quick Start

### 1. 创建Telegram机器人 / Create Telegram Bot
1. 打开Telegram → @BotFather
2. 发送 /newbot
3. 给机器人起名 / Name your bot
4. 复制Token / Copy Token

### 2. 安装 / Install
```bash
git clone <repo>
cd kite-wallet
npm install
```

### 3. 配置 / Configure
```env
PRIVATE_KEY=你的私钥
TELEGRAM_BOT_TOKEN=你的Token
```

### 4. 运行 / Run
```bash
node telegram-bot.js
```

## 命令 / Commands

| 命令 | 功能 | Command | Function |
|------|------|---------|----------|
| /create | 创建钱包 | /create | Create wallet |
| /wallet | 查看地址 | /wallet | Get address |
| /balance | 查看余额 | /balance | Check balance |
| /session add | 添加授权 | /session add | Add key |
| /limit set | 设置限额 | /limit set | Set limit |
| /send | 转账 | /send | Send |

## 相关链接 / Links

- 网站 / Website: https://gokite.ai
- 浏览器 / Explorer: https://testnet.kitescan.ai
- 水龙头 / Faucet: https://faucet.gokite.ai
