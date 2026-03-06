---
name: "broadcast-sign-transfer"
version: "1.0.1"
description: "支持 EVM 多链的原生代币和 ERC20 转账，自动构造交易、本地签名并通过 OKX API 广播上链"
tags: ["web3", "evm", "transfer", "erc20", "native", "defi", "mev", "bsc", "eth"]
author: "wangchengming@apache.org"
license: "MIT"
---

# Broadcast Sign Transfer Skill

## 什么是这个 Skill？

这个 Skill 实现了完整的 EVM 链转账流程：

```
用户输入（私钥/地址/金额）
    ↓
构造交易（自动获取 nonce、gas）
    ↓
本地签名（私钥不离开本机）
    ↓
通过 OKX API 广播到链上
    ↓
返回 tx_hash 和区块浏览器链接
```

支持两种转账类型：
- **原生代币转账**：ETH、BNB、MATIC 等
- **ERC20 Token 转账**：USDT、USDC 等任意 ERC20

---

## 什么时候该用这个 Skill？

满足以下条件时使用：
1. 用户想发起一笔链上转账
2. 用户提供了接收方地址和转账金额
3. 私钥已通过环境变量配置好

**不适用的情况：**
- 用户想做 Swap（代币兑换）→ 使用 Swap Skill
- 用户只想查询余额或交易状态 → 使用查询工具
- 用户没有配置私钥环境变量 → 先引导配置环境变量

---

## 执行流程（Step by Step）

```
Step 1: 检查输入参数
        ├── chain_index 是否在支持列表？
        ├── to_address 是否以 0x 开头？
        └── amount 是否大于 0？

Step 2: 获取链上数据
        ├── 获取当前 nonce
        └── 获取当前 gas price（Legacy 或 EIP-1559）

Step 3: 构造交易
        ├── 原生代币：直接构造 tx，gas 固定 21000
        └── ERC20：调用 transfer()，动态估算 gas × 1.2 安全系数

Step 4: 本地签名
        └── 使用私钥对交易签名，私钥不离开本机

Step 5: 广播到链上
        └── 调用 OKX Broadcast API 发送签名交易

Step 6: 返回结果
        ├── 成功 → 返回 tx_hash 和 explorer_url
        └── 失败 → 返回具体错误原因
```

---

## 输入参数

### chain_index（必填）
- **类型**：字符串 string
- **说明**：区块链链 ID
- **当前支持**：

  | chain_index | 链名 | Gas 类型 | 支持 MEV |
  |-------------|------|---------|---------|
  | `"56"` | BSC | Legacy | ✅ |

- **示例**：`"56"`
- **注意**：必须是字符串，`56` ❌ `"56"` ✅

---

### to_address（必填）
- **类型**：字符串 string
- **说明**：接收方钱包地址
- **格式**：0x 开头，42 位十六进制字符
- **示例**：`"0xaF3e6407073b2793271dA3d45A393397517ee3d9"`

---

### amount（必填）
- **类型**：浮点数 float
- **说明**：转账金额，人类可读单位
- **示例**：`0.01`（表示 0.01 BNB），`100.0`（表示 100 USDT）
- **注意**：脚本内部自动转换为链上精度（wei / raw units）

---

### token_address（ERC20 转账时必填）
- **类型**：字符串 string
- **说明**：ERC20 Token 的合约地址
- **格式**：0x 开头
- **示例**：`"0x55d398326f99059fF775485246999027B3197955"`（BSC 上的 USDT）

---

### enable_mev_protection（选填）
- **类型**：布尔值 boolean
- **默认值**：`false`
- **说明**：是否开启 MEV 保护，防止三明治攻击
- **注意**：仅支持 MEV 的链才能开启，否则报错

---

## 输出结果

### 成功时

| 字段 | 类型 | 说明 |
|------|------|------|
| order_id | string | OKX 平台订单 ID |
| tx_hash | string | 链上交易哈希 |
| explorer_url | string | 区块浏览器链接 |

**成功输出示例：**
```
✅ BSC 广播成功
Order ID: 1234567890
Tx Hash:  0xabc123...
浏览器:   https://bscscan.com/tx/0xabc123...
```

### 失败时

返回具体错误原因，见下方错误处理章节。

---

## 环境变量（必须配置）

| 变量名 | 说明 |
|--------|------|
| `WALLET_PRIVATE_KEY` | 钱包私钥（0x 开头） |
| `OKX_ACCESS_KEY` | OKX Web3 API Key |
| `OKX_SECRET_KEY` | OKX Secret Key |
| `OKX_PASSPHRASE` | OKX Passphrase |

> ⚠️ 必须使用 **OKX Web3 API Key**，普通交易 API Key 会返回 401 错误。

**配置方式（写入 ~/.zshrc 永久生效）：**
```bash
export WALLET_PRIVATE_KEY="0x你的私钥"
export OKX_ACCESS_KEY="你的Key"
export OKX_SECRET_KEY="你的Secret"
export OKX_PASSPHRASE="你的Passphrase"
```
```bash
source ~/.zshrc
```

---

## 调用示例

### 代码调用

```python
from scripts.broadcast_sign_transfer import BroadcastTransaction

bt = BroadcastTransaction(chain_index="56")

# 原生代币转账
result = bt.transfer_native(
    to_address="0xRecipient...",
    amount=0.01,
    enable_mev_protection=False,
)
print(result.summary())

# ERC20 转账
result = bt.transfer_token(
    token_address="0x55d398326f99059fF775485246999027B3197955",  # BSC USDT
    to_address="0xRecipient...",
    amount=100.0,
    enable_mev_protection=False,
)
print(result.summary())
```

### 命令行调用

```bash
# 原生代币转账
python3 scripts/broadcast_sign_transfer.py --chain 56 native \
  --to 0xRecipient... \
  --amount 0.01

# ERC20 转账
python3 scripts/broadcast_sign_transfer.py --chain 56 token \
  --token 0x55d398326f99059fF775485246999027B3197955 \
  --to 0xRecipient... \
  --amount 100

# 开启 MEV 保护
python3 scripts/broadcast_sign_transfer.py --chain 56 native \
  --to 0xRecipient... \
  --amount 0.01 \
  --mev
```

---

## Gas 处理机制

| 转账类型 | Gas 处理方式 |
|----------|-------------|
| 原生代币 | 固定 21000（EVM 协议层常量） |
| ERC20 Token | `eth_estimateGas` 动态估算 × 1.2 安全系数 |

Gas 价格根据链类型自动切换：
- **Legacy**（BSC）：使用 `gasPrice`
- **EIP-1559**（ETH/Polygon 等）：使用 `maxFeePerGas` + `maxPriorityFeePerGas`

---

## 错误处理

| 错误信息 | 原因 | 解决方法 |
|----------|------|----------|
| `暂不支持链 {chain_index}` | 链未在支持列表中 | 检查 chain_index 是否正确 |
| `to_address 格式错误` | 地址不以 0x 开头 | 检查地址格式 |
| `amount 必须大于 0` | 金额为负数或 0 | 输入正确金额 |
| `余额不足` | ERC20 余额不够 | 检查钱包余额 |
| `链 {chain_index} 不支持 MEV 保护` | 该链不支持 MEV | 关闭 enable_mev_protection |
| `401 Unauthorized` | 使用了普通 API Key | 确认使用 OKX Web3 API Key |
| `广播失败（code=xxx）` | OKX API 返回错误 | 检查 API 凭证和交易数据 |
| `缺少 OKX API 凭证` | 环境变量未配置 | 配置四个环境变量后重试 |
| `缺少钱包私钥` | WALLET_PRIVATE_KEY 未配置 | 配置私钥环境变量 |

---

## 安全注意事项

- ⚠️ 私钥通过环境变量传入，**不要硬编码在代码里**
- ⚠️ 广播成功不代表交易成功，需通过 `explorer_url` 确认链上状态
- ⚠️ 广播后的交易**无法撤销**，请在调用前确认地址和金额正确
- ⚠️ `~/.zshrc` 是明文存储，确保只有自己能访问该文件

---

## 依赖安装

```bash
pip3 install requests web3
```

---

## 文件结构

```
broadcast-sign-transfer/
├── broadcast_sign_transfer.md     ← 当前文件，AI 技能说明书
└── scripts/
    └── broadcast_sign_transfer.py ← 可执行的 Python 客户端
```

---

## 当前支持的链（v1.0.0）

| chain_index | 链名 | Gas 类型 | MEV 保护 | 浏览器 |
|-------------|------|---------|---------|--------|
| `56` | BSC | Legacy | ✅ | bscscan.com |

> v1.0.0 仅支持 BSC，更多链将在后续版本中陆续支持。