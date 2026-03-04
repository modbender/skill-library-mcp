---
name: "broadcast-signed-transaction"
version: "1.0.0"
description: "直接广播已签名的 hex 交易到链上，无需私钥，一步完成广播"
tags: ["web3", "evm", "broadcast", "signed-tx", "okx", "defi", "mev"]
author: "wangchengming@apache.org"
license: "MIT"
---

# Broadcast Signed Transaction Skill

## 什么是这个 Skill？

这个 Skill 将已经签名好的交易 hex 直接广播到链上：

```
用户输入（signedTx hex + chainIndex + address）
    ↓
参数校验（格式 / OKX 凭证检查）
    ↓
调用 OKX Broadcast API 广播
    ↓
返回 orderId、txHash、区块浏览器链接
```

**与 broadcast-sign-transfer 的区别：**

| 能力 | broadcast-sign-transfer | broadcast-signed-transaction |
|------|------------------------|------------------------------|
| 构造交易 | ✅ 自动构造 | ❌ 不需要 |
| 签名交易 | ✅ 需要私钥 | ❌ 不需要私钥 |
| 广播交易 | ✅ | ✅ |
| 适用场景 | 从零开始转账 | 已有签名 hex，直接广播 |

---

## 什么时候该用这个 Skill？

满足以下条件时使用：

1. 用户已有签名好的交易 hex（以 `0x` 开头的十六进制字符串）
2. 用户想直接广播，不需要重新签名
3. 用户说了类似的话：
   - "我有一笔签名好的交易，帮我广播"
   - "直接广播这个 signedTx"
   - "广播已签名交易"
   - "broadcast signed tx"
   - "把这个 hex 广播到链上"

**不适用的情况：**
- 用户还没签名，需要从私钥开始 → 使用 `broadcast-sign-transfer`
- 用户只想查询交易状态 → 使用 `mev_tx_status_query.py`
- 用户没有 OKX API Key → 先引导配置环境变量

---

## 执行流程（Step by Step）

```
Step 1: 收集必要参数
        ├── chainIndex  → 用户指定，或从日志/上下文中提取
        ├── address     → 发送方地址（0x 开头）
        ├── signedTx    → 已签名的 hex（0x 开头）
        └── --mev       → 是否开启 MEV 保护（可选，默认关闭）

Step 2: 验证环境变量
        └── OKX_ACCESS_KEY / OKX_SECRET_KEY / OKX_PASSPHRASE

Step 3: 调用广播脚本
        └── python3 scripts/broadcast_signed_tx.py \
              --chain <chainIndex> \
              --address <address> \
              --signed-tx <signedTx> \
              [--mev] [--json-only]

Step 4: 解析结果
        ├── 成功 → 展示 orderId、txHash、区块浏览器链接
        └── 失败 → 展示具体错误原因并给出解决建议
```

---

## 输入参数

### --chain（必填）
- **类型**：字符串（链 ID）
- **说明**：区块链链 ID，传给 OKX API 的 chainIndex 字段
- **常用值**：

  | chain | 链名 | 区块浏览器 |
  |-------|------|-----------|
  | `1` | Ethereum | etherscan.io |
  | `56` | BSC | bscscan.com |
  | `8453` | Base | basescan.org |
  | `42161` | Arbitrum | arbiscan.io |
  | `196` | xLayer | oklink.com/xlayer |
  | `501` | Solana | solscan.io |

- **示例**：`--chain 56`
- **注意**：不在列表中的链也可以传，OKX API 会进行校验

---

### --address（必填）
- **类型**：字符串
- **说明**：发送方钱包地址
- **格式**：0x 开头，42 位十六进制字符
- **示例**：`--address 0xaF3e6407073b2793271dA3d45A393397517ee3d9`

---

### --signed-tx（必填）
- **类型**：字符串
- **说明**：已签名的交易 hex，由客户端签名后得到
- **格式**：0x 开头的完整 RLP 编码交易
- **示例**：`--signed-tx 0x02f8...（完整 hex）`
- **获取方式**：
  - web3.py：`signed = w3.eth.account.sign_transaction(tx, pk)` → `signed.raw_transaction.to_0x_hex()`
  - ethers.js：`signer.signTransaction(tx)` → 得到 `0x...`

---

### --mev（选填，flag）
- **默认**：关闭
- **说明**：开启 MEV 保护，防止三明治攻击
- **示例**：`--mev`

---

### --json-only（选填，flag）
- **说明**：仅输出 JSON，适合 AI 解析结果
- **示例**：`--json-only`

---

## 输出结果

### 成功时

```
==============================================================
  ✅ BSC 广播成功
==============================================================
  Order ID  : 1234567890
  Tx Hash   : 0xabc123...
  浏览器    : https://bscscan.com/tx/0xabc123...
==============================================================

{
  "success": true,
  "order_id": "1234567890",
  "tx_hash": "0xabc123...",
  "chain_index": "56",
  "chain_name": "BSC",
  "explorer_url": "https://bscscan.com/tx/0xabc123...",
  "mev_enabled": false,
  "error": null
}
```

### 失败时

```
==============================================================
  ❌ 广播失败（Chain-56）
==============================================================
  错误原因  : 广播失败（code=50001）: Invalid signed transaction
==============================================================
```

---

## 环境变量（必须配置）

| 变量名 | 说明 |
|--------|------|
| `OKX_ACCESS_KEY` | OKX Web3 API Key |
| `OKX_SECRET_KEY` | OKX Secret Key |
| `OKX_PASSPHRASE` | OKX Passphrase |

> ⚠️ 必须使用 **OKX Web3 API Key**，普通交易 API Key 会返回 401 错误。
> ⚠️ 此 Skill **不需要** WALLET_PRIVATE_KEY（私钥），交易已在外部签名。

**配置方式：**
```bash
export OKX_ACCESS_KEY="你的Key"
export OKX_SECRET_KEY="你的Secret"
export OKX_PASSPHRASE="你的Passphrase"
source ~/.zshrc
```

---

## 调用示例

### 命令行

```bash
# BSC 广播
python3 scripts/broadcast_signed_tx.py \
  --chain 56 \
  --address 0xYourAddress \
  --signed-tx 0xYourSignedTxHex

# ETH 开启 MEV 保护
python3 scripts/broadcast_signed_tx.py \
  --chain 1 \
  --address 0xYourAddress \
  --signed-tx 0xYourSignedTxHex \
  --mev

# 仅输出 JSON（AI 解析）
python3 scripts/broadcast_signed_tx.py \
  --chain 56 \
  --address 0xYourAddress \
  --signed-tx 0xYourSignedTxHex \
  --json-only
```

### Python 代码调用

```python
from scripts.broadcast_signed_tx import broadcast_signed_transaction

result = broadcast_signed_transaction(
    chain_index           = "56",
    address               = "0xYourAddress",
    signed_tx             = "0xYourSignedTxHex",
    enable_mev_protection = False,
)

if result["success"]:
    print(f"✅ 广播成功：{result['tx_hash']}")
    print(f"浏览器：{result['explorer_url']}")
else:
    print(f"❌ 失败：{result['error']}")
```

---

## 错误处理

| 错误信息 | 原因 | 解决方法 |
|----------|------|----------|
| `缺少 OKX API 凭证` | 环境变量未配置 | 配置三个环境变量后重试 |
| `address 格式错误` | 地址不以 0x 开头 | 检查地址格式 |
| `signed_tx 格式错误` | hex 不以 0x 开头或为空 | 检查签名 hex |
| `HTTP 错误 401` | API Key 类型错误 | 确认使用 OKX Web3 API Key |
| `广播失败（code=50001）` | 签名 hex 无效 | 检查 signedTx 是否完整，chainIndex 是否匹配 |
| `广播失败（code=50002）` | address 与签名不匹配 | 确认 address 是签名交易的发送方 |
| `网络请求异常` | 网络问题 | 检查网络连接后重试 |

---

## 安全注意事项

- ✅ 此 Skill 无需私钥，不存在私钥泄露风险
- ⚠️ 广播前确认 signedTx 内容正确：广播后**无法撤销**
- ⚠️ 确认 address 与 signedTx 的发送方地址一致，否则 OKX API 会拒绝
- ⚠️ OKX API 凭证请妥善保管，不要提交到版本控制

---

## 依赖安装

```bash
# 仅依赖 requests，无需 web3
pip3 install requests
```

---

## 文件结构

```
broadcast-signed-transaction/
├── SKILL.md                          ← 当前文件，AI 技能说明书
└── scripts/
    └── broadcast_signed_tx.py        ← 可执行的 Python 广播工具
```
