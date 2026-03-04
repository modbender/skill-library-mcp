---
name: agentxpay
description: AgentXPay Skill — 让 AI Agent 在 Monad 链上通过 x402 协议自主发现、付费、订阅 AI 服务。支持链上支付、Agent 钱包管理、服务订阅和资金托管。
license: MIT
compatibility: Node.js >= 18, ethers v6, @agentxpay/sdk, Monad RPC 访问, 已部署 AgentXPay 合约
metadata: {"author": "jasonruan", "version": "0.1.0", "chain": "monad", "protocol": "x402", "openclaw": {"requires": {"bins": ["npx", "node"], "env": ["RPC_URL", "PRIVATE_KEY", "SERVICE_REGISTRY_ADDRESS", "PAYMENT_MANAGER_ADDRESS"]}, "primaryEnv": "PRIVATE_KEY", "emoji": "💰", "homepage": "https://github.com/AgentXPay"}}
user-invocable: true
command-dispatch: tool
command-tool: agentxpay_smart_call
---

# AgentXPay Skill

让 AI Agent 具备在 Monad 区块链上**自主发现 AI 服务、链上付费、管理钱包**的能力。

核心机制：通过 **x402 协议**（HTTP 402 Payment Required），Agent 发送请求 → 收到 402 → 自动链上支付 → 携带交易哈希重试 → 获取 AI 服务响应，全程无需人工介入。

---

## 前置条件

在使用本 Skill 前，需要确保以下配置可用：

| 变量 | 必填 | 说明 |
|------|------|------|
| `RPC_URL` | 是 | Monad RPC 节点地址 |
| `PRIVATE_KEY` | 是 | Agent 钱包私钥 |
| `SERVICE_REGISTRY_ADDRESS` | 是 | ServiceRegistry 合约地址 |
| `PAYMENT_MANAGER_ADDRESS` | 是 | PaymentManager 合约地址 |
| `SUBSCRIPTION_MANAGER_ADDRESS` | 否 | SubscriptionManager 合约地址 |
| `ESCROW_ADDRESS` | 否 | Escrow 合约地址 |
| `AGENT_WALLET_FACTORY_ADDRESS` | 否 | AgentWalletFactory 合约地址 |

2. **依赖**：`@agentxpay/sdk`、`ethers` v6

---

## 可用 Tool 清单

本 Skill 提供以下 7 个 Tool，AI 可根据任务需要选择调用：

### Tool 1: `agentxpay_discover_services`

**用途**：在 Monad 链上发现已注册的 AI 服务。

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | 否 | 服务类别过滤，如 "LLM"、"Image"、"Code" |
| maxPrice | string | 否 | 最大单价（MON），如 "0.05" |

**返回**：`{ services: [...], totalCount: number }`

**使用场景**：用户问"有哪些 AI 服务可用"、"找一个图像生成服务"时调用。

**执行方式**：运行 `scripts/run-tool.ts discover_services '{"category":"LLM"}'`

---

### Tool 2: `agentxpay_pay_and_call` （核心 Tool）

**用途**：通过 x402 协议自动付费调用 AI 服务端点。

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | **是** | AI 服务端点 URL |
| method | string | 否 | HTTP 方法，默认 "POST" |
| body | object | 否 | 请求体（会被 JSON 序列化） |
| headers | object | 否 | 额外 HTTP 请求头 |

**返回**：`{ status, data, payment: { txHash, amount, serviceId }, latencyMs }`

**工作流程**：
1. 向目标 URL 发送 HTTP 请求
2. 若收到 HTTP 402 响应，解析 `X-Payment-*` 响应头
3. 自动调用 PaymentManager 合约完成链上支付
4. 携带 `X-Payment-TxHash` 重新发送请求
5. 返回 AI 服务响应 + 支付凭证

**使用场景**：用户说"帮我调用这个 AI 接口"、"用 GPT-4 回答问题"时调用。

**执行方式**：运行 `scripts/run-tool.ts pay_and_call '{"url":"http://...","method":"POST","body":{"prompt":"hello"}}'`

---

### Tool 3: `agentxpay_smart_call` （推荐：一步到位）

**用途**：智能发现 → 选择最优服务 → 自动付费调用，一步完成。

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task | string | **是** | 任务描述，如 "生成一张赛博朋克猫图片" |
| category | string | 否 | 偏好的服务类别 |
| maxBudget | string | 否 | 最大预算（MON） |
| preferCheapest | boolean | 否 | 是否优先选最便宜的 |

**返回**：`{ selectedService: {...}, response, payment, latencyMs }`

**使用场景**：用户描述一个需要外部 AI 服务的任务，但没有指定具体服务端点时。这是**最常用的 Tool**。

**执行方式**：运行 `scripts/run-tool.ts smart_call '{"task":"生成赛博朋克猫图片","category":"Image"}'`

---

### Tool 4: `agentxpay_manage_wallet`

**用途**：创建和管理 Agent 智能合约钱包，包括授权/撤销 Agent 地址和通过钱包余额支付服务。

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| action | string | **是** | "create" / "fund" / "get_info" / "set_limit" / "authorize_agent" / "revoke_agent" / "pay" |
| dailyLimit | string | 条件 | 每日限额（MON），create/set_limit 时需要 |
| amount | string | 条件 | 金额（MON），fund/pay 时需要 |
| walletAddress | string | 条件 | 钱包地址，fund/get_info/set_limit/authorize_agent/revoke_agent/pay 时需要 |
| agentAddress | string | 条件 | Agent 地址，authorize_agent/revoke_agent 时需要 |
| serviceId | number | 条件 | 链上服务 ID，pay 时需要 |

**返回**：`{ walletAddress, balance, dailyLimit, dailySpent, remainingAllowance, txHash, agentAddress?, isAuthorized?, paymentServiceId?, paymentAmount? }`

**Action 说明**：
- `create`：创建新的 Agent 智能钱包，设置每日支出限额
- `fund`：向钱包充值 MON
- `get_info`：查询钱包余额、每日限额、今日已花、剩余额度
- `set_limit`：调整每日支出限额
- `authorize_agent`：授权一个地址（Agent）从该钱包支出
- `revoke_agent`：撤销一个地址的钱包支出权限
- `pay`：通过钱包余额调用 PaymentManager.payPerUse 支付服务（需先授权）

**使用场景**：用户说"创建一个 Agent 钱包"、"授权某个地址使用钱包"、"用钱包余额支付服务"时调用。

---

### Tool 5: `agentxpay_subscribe`

**用途**：订阅链上 AI 服务的周期性计划。

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| serviceId | number | **是** | 链上服务 ID |
| planId | number | 否 | 订阅计划 ID（不传则自动选第一个） |

**返回**：`{ subscriptionId, planName, price, txHash, hasAccess }`

**使用场景**：用户说"订阅这个服务"、"我想包月使用"时调用。

---

### Tool 6: `agentxpay_create_escrow`

**用途**：为定制 AI 任务创建链上资金托管。

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| serviceId | number | **是** | 链上服务 ID |
| amount | string | **是** | 托管金额（MON） |
| deadlineDays | number | **是** | 截止天数 |
| description | string | **是** | 任务描述 |

**返回**：`{ escrowId, amount, deadline, txHash }`

**使用场景**：用户说"我有一个定制任务需要先锁定资金"时调用。

---

### Tool 7: `agentxpay_get_agent_info`

**用途**：查询当前 Agent 的钱包地址、余额和网络信息。

**参数**：无

**返回**：`{ address, balance, network }`

**使用场景**：用户问"我的钱包地址是什么"、"余额还有多少"时调用。

---

## 标准操作流程 (SOP)

### 场景 A：用户需要调用外部 AI 服务

```
步骤 1: 调用 agentxpay_discover_services 查看可用服务和价格
步骤 2: 向用户展示服务列表和价格，确认是否继续
步骤 3: 用户确认后，调用 agentxpay_pay_and_call 或 agentxpay_smart_call
步骤 4: 返回 AI 服务响应 + 支付交易哈希
```

### 场景 B：用户直接描述任务（推荐）

```
步骤 1: 调用 agentxpay_smart_call，传入任务描述和可选的类别/预算
步骤 2: Skill 自动发现服务 → 选择最优 → 付费调用
步骤 3: 返回结果给用户，附带所选服务信息和支付凭证
```

### 场景 C：用户要管理 Agent 钱包

```
步骤 1: 调用 agentxpay_manage_wallet action="get_info" 查看当前状态
步骤 2: 根据需要执行 create/fund/set_limit
```

### 场景 D：用户要用 Agent 钱包支付服务

```
步骤 1: 创建钱包 — manage_wallet action="create" dailyLimit="1.0"
步骤 2: 充值 — manage_wallet action="fund" walletAddress="0x..." amount="10.0"
步骤 3: 授权 Agent — manage_wallet action="authorize_agent" walletAddress="0x..." agentAddress="0x..."
步骤 4: 通过钱包支付 — manage_wallet action="pay" walletAddress="0x..." serviceId=1 amount="0.01"
```

### 场景 E：用户要订阅服务

```
步骤 1: 调用 agentxpay_discover_services 找到目标服务
步骤 2: 调用 agentxpay_subscribe 订阅
步骤 3: 确认访问权限已激活
```

---

## 错误处理

| 错误 | 原因 | 处理方式 |
|------|------|---------|
| "No matching services found" | 链上无匹配服务 | 建议用户放宽过滤条件或检查合约部署 |
| "insufficient funds" | Agent 余额不足 | 提示用户充值或使用 agentxpay_manage_wallet fund |
| "ServiceId mismatch" | 链上 serviceId 与 Provider 402 响应中的 serviceId 不一致 | 提示用户联系服务提供者修正 serviceId 配置 |
| "Price mismatch" | 链上 pricePerCall 与 Provider 402 响应中的 amount 不一致 | 提示用户联系服务提供者修正定价配置 |
| HTTP 402 retry 失败 | 支付验证未通过 | 检查合约地址和网络配置 |
| "daily limit exceeded" | 超出每日限额 | 提示用户调整限额或等待次日重置 |
| "Agent ... is not authorized" | Agent 未被授权使用钱包 | 用 authorize_agent 授权该 Agent |
| "Insufficient daily allowance" | 钱包每日额度不足 | 用 set_limit 调高限额或等待次日重置 |
| "Insufficient wallet balance" | 钱包余额不足 | 用 fund 向钱包充值 |

---

## 安全注意事项

1. **私钥保护**：PRIVATE_KEY 通过 `openclaw.json` 安全注入，不要硬编码
2. **每日限额**：建议使用 Agent Wallet 的 dailySpendingLimit 限制支出
3. **用户确认**：在执行付费操作前，应向用户展示价格并获得确认
4. **交易验证**：所有支付都有链上 txHash，可在区块浏览器验证

---

## 引用资源

- CLI 工具执行脚本：参考 `scripts/run-tool.ts`（可直接 `npx tsx` 执行）
- TypeScript 类型定义：参考 `src/types.ts`
- Tool JSON Schema 定义：参考 `src/schemas.ts`
- 核心运行时实现：参考 `src/runtime.ts`
- 集成入口和适配器（OpenAI/MCP）：参考 `src/index.ts`
- x402 协议参考：参考 `references/x402-protocol.md`
- AgentXPay SDK API 文档：参考 `references/sdk-api.md`
