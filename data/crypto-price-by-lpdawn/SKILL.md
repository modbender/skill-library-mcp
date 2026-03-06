---
name: crypto-price-by-lpdawn
description: 获取比特币、以太坊等主流加密货币的实时美元价格。
version: 1.0.0
author: LPDawn
permissions: 网络访问权限
---

# Crypto Price Skill

## 1. Description
当用户询问加密货币的实时价格时，使用此技能。它通过 ccxt 库从 Binance 交易所获取最新价格，支持 BTC、ETH 等常见币种。

## 2. When to use
- 用户说：“比特币现在多少钱？”
- 用户说：“查一下 ETH 的价格”
- 用户说：“狗狗币 (DOGE) 实时行情”
- 用户说：“BTC 涨了多少？”
- 用户说：“SOL 现在的价格”
- 用户说：“莱特币 LTC 价格”
- 用户说：“用 crypto-price-by-lpdawn 查比特币”
- 用户说：“当前 BTC/USDT 价格”
- 用户说：“ETH 美元价格是多少？”

## 3. How to use
1. 从用户提问中提取要查询的加密货币符号（如 `BTC`、`ETH`、`DOGE`）。如果用户未指定，默认查询 `BTC`。
2. 调用 `agent.py` 脚本，将币种符号作为参数传入。
3. 脚本返回格式化的价格信息，直接回复给用户。

## 4. Edge cases
- 如果用户提到的币种无法查询，脚本返回错误，AI 回复：“抱歉，无法查询到该币种的信息，请确认符号是否正确。”
- 如果交易所 API 不可用，AI 回复：“暂时无法连接到交易所，请稍后重试。”
- 如果用户没有给出币种，AI 询问：“您想查询哪个币种的价格？例如 BTC 或 ETH。”
