# x402 协议参考

## 概述

x402 是 AgentXPay 定义的 HTTP 支付协议，借鉴了 HTTP 402 (Payment Required) 状态码，使 AI Agent 可以像处理 HTTP 重定向一样自动完成链上支付。

## 协议流程

```
Agent                          AI Service Provider             Monad Blockchain
  |                                   |                              |
  |  1. POST /api/chat                |                              |
  |  { prompt: "hello" }              |                              |
  | ─────────────────────────────────>|                              |
  |                                   |                              |
  |  2. HTTP 402 Payment Required     |                              |
  |  X-Payment-Address: 0x...         |                              |
  |  X-Payment-Amount: 10000000...    |                              |
  |  X-Payment-ServiceId: 1           |                              |
  |  X-Payment-ChainId: 10143        |                              |
  |<─────────────────────────────────|                              |
  |                                   |                              |
  |  3. payPerUse(serviceId, amount)  |                              |
  | ──────────────────────────────────────────────────────────────>  |
  |                                   |                              |
  |  4. txHash: 0xabc...             |                              |
  |<──────────────────────────────────────────────────────────────  |
  |                                   |                              |
  |  5. POST /api/chat (retry)       |                              |
  |  X-Payment-TxHash: 0xabc...      |                              |
  |  X-Payment-ChainId: 10143        |                              |
  | ─────────────────────────────────>|                              |
  |                                   |  6. Verify tx on-chain       |
  |                                   | ───────────────────────────> |
  |                                   |  7. tx confirmed             |
  |                                   |<─────────────────────────── |
  |  8. HTTP 200 OK                   |                              |
  |  { response: "AI answer..." }     |                              |
  |<─────────────────────────────────|                              |
```

## HTTP 402 响应头

| Header | 说明 | 示例 |
|--------|------|------|
| `X-Payment-Address` | 收款地址（服务提供者） | `0x1234...abcd` |
| `X-Payment-Amount` | 支付金额（wei） | `10000000000000000` |
| `X-Payment-Token` | 支付代币类型 | `native` |
| `X-Payment-ServiceId` | 链上服务 ID | `1` |
| `X-Payment-ChainId` | 区块链链 ID | `10143`（Monad Testnet） |

## 支付重试请求头

| Header | 说明 | 示例 |
|--------|------|------|
| `X-Payment-TxHash` | 链上支付交易哈希 | `0xabc...def` |
| `X-Payment-ChainId` | 支付所在链 | `10143` |

## 服务端验证逻辑

1. 检查 `X-Payment-TxHash` 是否存在
2. 通过 RPC 查询交易回执
3. 验证交易状态 (`receipt.status === 1`)
4. 验证发送者和金额
5. 防重放：确保 txHash 未被使用过
6. 验证通过后放行请求
