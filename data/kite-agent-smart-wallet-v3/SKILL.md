---
name: Kite AI Agent Smart Wallet Protocol V3
description: 用户直接通过OpenClaw（Telegram）控制Kite AI链上钱包，无需自己运行Bot。
---

# Kite AI Agent Smart Wallet Protocol V3

## 简介

用户直接通过OpenClaw（Telegram）控制Kite AI链上钱包，无需自己运行Bot。

## 架构

```
用户(Telegram) → OpenClaw → Kite AI合约
     │
     └── OpenClaw执行操作
```

## 功能

- 钱包创建
- 余额查询
- 转账
- Session Keys管理
- 消费限额

## 命令

所有命令以 `/kite` 开头：

| 命令 | 功能 |
|------|------|
| /kite help | 帮助 |
| /kite create | 创建钱包 |
| /kite wallet | 查看地址 |
| /kite balance | 查看余额 |
| /kite send \<地址\> \<数量\> | 转账 |
| /kite session add \<地址\> \<限额\> | 添加授权 |
| /kite limit set \<数量\> | 设置限额 |

## 网络

- 测试网: Chain ID 2368
- RPC: https://rpc-testnet.gokite.ai

## 合约

- AgentSmartWalletFactory: `0x0fa9F878B038DE435b1EFaDA3eed1859a6Dc098a`

## 版本

- v3.0.0 (2026-02-25): OpenClaw集成，直接TG控制
- v2.0.x: 用户本地运行Bot版本
- v1.0.0: 基础合约
