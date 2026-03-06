# MistTrack Skills

[中文](#chinese) · [English](#english)

---

<a name="chinese"></a>

# MistTrack Skills（中文）

MistTrack OpenAPI 的 AI Agent 技能包，用于加密货币地址风险分析、AML 合规检测和链上交易追踪。

## 简介

[MistTrack](https://misttrack.io/) 是由 [SlowMist](https://www.slowmist.com/en/) 开发的反洗钱追踪工具（AML），收录超过 4 亿个地址和 50 万条威胁情报。

- 支持 OpenClaw、Claude Code 等主流工具
- 兼容 **Bitget Wallet Skill** 和 **Trust Wallet Skills**，在安装对应 Skills 并执行交易时可自动调用 MistTrack Skills 进行地址安全检测

## 安装

```bash
npx skills add slowmist/misttrack-skills
```

## 提问技巧

### 🔍 快速风险检测（KYT）

- 帮我检测 `0x6487B5006904f3Db3C4a3654409AE92b87eD442f` 这个 ETH 地址的风险评分
- 这个 TRX 地址 `TNfK1r5jb8Wa1Ph1MApjqJobsY8SPwj3Yh` 安全吗？有没有洗钱记录？
- 帮我查一下这笔交易 `0xabc123...` 的风险评分，看看是否涉及制裁实体

### 🧑‍💼 地址完整画像调查

- 对 `0x6487B5006904f3Db3C4a3654409AE92b87eD442f` 做一个完整的链上调查，包括标签、余额概览、风险评分、平台交互历史和主要交易对手
- 这个 BTC 地址 `1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf` 的资金来源和流向是什么？
- 帮我分析 `0xd90e2f925da726b50c4ed8d0fb90ad053324f31b` 的行为模式，它主要在 DEX、混币器还是交易所之间活动？

### 💸 转账前安全检测

> 配合 **Bitget Wallet Skill** 或 **Trust Wallet Skills** 使用，转账前自动检测收款地址

- 将我的 0.1 ETH 兑换成 USDT 到 `0x6487B5006904f3Db3C4a3654409AE92b87eD442f`（会自动检测目标地址风险）
- 将我的 100 TRX 发送到 `TNfK1r5jb8Wa1Ph1MApjqJobsY8SPwj3Yh` 这个地址
- 帮我把 500 USDT 从 BNB Chain 转到 `0x28C6c06298d514Db089934071355E5743bf21d60`

### 🔗 交易溯源与资金流向

- 追踪 `0x6487B5006904f3Db3C4a3654409AE92b87eD442f` 的资金去向，重点看转出到哪些地址
- 这个地址跟 Tornado Cash 有没有过直接或间接交互？
- 帮我查 `TNfK1r5jb8Wa1Ph1MApjqJobsY8SPwj3Yh` 最近的交易对手，看看主要资金来自哪里

### ℹ️ 状态与支持查询

- MistTrack 支持 Solana 上的 USDT 吗？
- 帮我列出 MistTrack 目前支持的所有代币

## 支持的 API

| API 端点 | 功能 |
|----------|------|
| `v1/status` | 获取 API 状态和支持代币列表 |
| `v1/address_labels` | 获取地址标签（实体名称、地址类型） |
| `v1/address_overview` | 获取地址余额和统计数据 |
| `v2/risk_score` | 获取地址/交易风险评分（同步） |
| `v2/risk_score_create_task` | 创建风险评分任务（异步） |
| `v2/risk_score_query_task` | 查询风险评分任务结果（异步） |
| `v1/transactions_investigation` | 交易调查（转入/转出流向分析） |
| `v1/address_action` | 地址行为分析（DEX/Exchange/Mixer 占比） |
| `v1/address_trace` | 地址画像（平台交互、恶意事件、关联信息） |
| `v1/address_counterparty` | 交易对手分析 |

## 支持的区块链

Bitcoin、Ethereum、TRON、BNB Smart Chain、Polygon、Arbitrum、Optimism、Base、Avalanche、zkSync Era、Toncoin、Solana、Litecoin、Dogecoin、Bitcoin Cash、Merlin Chain、HashKey Chain、Sui、IoTeX

## 快速开始

1. 在 [MistTrack 控制台](https://dashboard.misttrack.io/upgrade) 使用邮箱验证码登录，然后订阅标准版套餐（新用户可以选择 10 美金的限时体验套餐），付款后即可[创建 API Key](https://dashboard.misttrack.io/apikeys)
2. 设置环境变量（推荐）：
   ```bash
   export MISTTRACK_API_KEY=your_api_key_here
   ```
3. 参考 `SKILL.md` 中的完整 API 文档
4. 参考 `scripts/` 目录中的示例脚本

## 示例脚本

```bash
export MISTTRACK_API_KEY=your_api_key_here

# 单个地址风险评分
python scripts/risk_check.py --address 0x... --coin ETH

# 批量异步风险评分
python scripts/batch_risk_check.py --input addresses.txt --coin ETH

# 完整地址调查
python scripts/address_investigation.py --address 0x... --coin ETH

# 转账前安全检测（Bitget Wallet / Trust Wallet 集成）
python scripts/transfer_security_check.py --address 0x... --chain eth
```

## 速率限制

| 套餐 | 速率 | 每日限额 |
|------|------|----------|
| Standard | 1 次/秒 | 10,000 次/天 |
| Compliance | 5 次/秒 | 50,000 次/天 |
| Enterprise | 无限制 | 无限制 |

## 文档

- [完整 API 文档](./SKILL.md)
- [MistTrack 官方文档](https://docs.misttrack.io/)
- [常见错误消息](https://docs.misttrack.io/support/common-error-messages)

---

<a name="english"></a>

# MistTrack Skills (English)

An AI Agent skill pack for the MistTrack OpenAPI — cryptocurrency address risk analysis, AML compliance checks, and on-chain transaction tracing.

## Overview

[MistTrack](https://misttrack.io/) is an AML tracking tool developed by [SlowMist](https://www.slowmist.com/en/), covering 400M+ addresses and 500K+ threat intelligence entries.

- Works with OpenClaw, Claude Code, and other major agent platforms
- Integrates with **Bitget Wallet Skill** and **Trust Wallet Skills** — automatically runs MistTrack address security checks before any transfer

## Installation

```bash
npx skills add slowmist/misttrack-skills
```

## Example Prompts

### 🔍 Quick Risk Check (KYT)

- Check the risk score for ETH address `0x6487B5006904f3Db3C4a3654409AE92b87eD442f`
- Is TRX address `TNfK1r5jb8Wa1Ph1MApjqJobsY8SPwj3Yh` safe? Any money laundering history?
- What's the risk score for transaction `0xabc123...`? Does it involve any sanctioned entities?

### 🧑‍💼 Full Address Investigation

- Run a complete on-chain investigation on `0x6487B5006904f3Db3C4a3654409AE92b87eD442f` — labels, balance, risk score, platform interactions, and counterparties
- Where did the funds in BTC address `1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf` come from and go to?
- Analyze the behavior of `0xd90e2f925da726b50c4ed8d0fb90ad053324f31b` — is it mostly interacting with DEXes, mixers, or exchanges?

### 💸 Pre-Transfer Security Check

> Works with **Bitget Wallet Skill** or **Trust Wallet Skills** — automatically checks the recipient address before any transfer

- Swap my 0.1 ETH to USDT and send to `0x6487B5006904f3Db3C4a3654409AE92b87eD442f` (auto-checks recipient risk)
- Send 100 TRX to `TNfK1r5jb8Wa1Ph1MApjqJobsY8SPwj3Yh`
- Bridge 500 USDT from BNB Chain to `0x28C6c06298d514Db089934071355E5743bf21d60`

### 🔗 Transaction Tracing

- Trace where funds from `0x6487B5006904f3Db3C4a3654409AE92b87eD442f` went — focus on outgoing transfers
- Has this address ever interacted with Tornado Cash, directly or indirectly?
- Show me the main counterparties for `TNfK1r5jb8Wa1Ph1MApjqJobsY8SPwj3Yh` — where did most funds originate?

### ℹ️ Status & Support

- Does MistTrack support USDT on Solana?
- List all tokens currently supported by MistTrack

## Supported APIs

| Endpoint | Description |
|----------|-------------|
| `v1/status` | API status & supported token list |
| `v1/address_labels` | Address labels (entity name, type) |
| `v1/address_overview` | Address balance & statistics |
| `v2/risk_score` | Address / tx risk score (sync) |
| `v2/risk_score_create_task` | Create risk score task (async) |
| `v2/risk_score_query_task` | Query task result (async, no rate limit) |
| `v1/transactions_investigation` | Transaction flow analysis (in/out) |
| `v1/address_action` | Behavior analysis (DEX/Exchange/Mixer ratio) |
| `v1/address_trace` | Address profile (platforms, events, relations) |
| `v1/address_counterparty` | Counterparty analysis |

## Supported Blockchains

Bitcoin, Ethereum, TRON, BNB Smart Chain, Polygon, Arbitrum, Optimism, Base, Avalanche, zkSync Era, Toncoin, Solana, Litecoin, Dogecoin, Bitcoin Cash, Merlin Chain, HashKey Chain, Sui, IoTeX

## Quick Start

1. Log in to the [MistTrack Dashboard](https://dashboard.misttrack.io/upgrade) using email verification code, then subscribe to the Standard Plan (new users can choose the limited-time trial plan for $10). After payment, you can [create an API Key](https://dashboard.misttrack.io/apikeys)
2. Set the environment variable (recommended):
   ```bash
   export MISTTRACK_API_KEY=your_api_key_here
   ```
3. See `SKILL.md` for full API documentation
4. See `scripts/` for example scripts

## Example Scripts

```bash
export MISTTRACK_API_KEY=your_api_key_here

# Single address risk score
python scripts/risk_check.py --address 0x... --coin ETH

# Batch async risk scoring
python scripts/batch_risk_check.py --input addresses.txt --coin ETH

# Full address investigation
python scripts/address_investigation.py --address 0x... --coin ETH

# Pre-transfer security check (Bitget Wallet / Trust Wallet integration)
python scripts/transfer_security_check.py --address 0x... --chain eth
```

## Rate Limits

| Plan | Rate | Daily Limit |
|------|------|-------------|
| Standard | 1 req/sec | 10,000/day |
| Compliance | 5 req/sec | 50,000/day |
| Enterprise | Unlimited | Unlimited |

## Documentation

- [Full API Docs](./SKILL.md)
- [MistTrack Official Docs](https://docs.misttrack.io/)
- [Common Error Messages](https://docs.misttrack.io/support/common-error-messages)
