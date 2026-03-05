---
name: web3-investor
description: AI-friendly Web3 investment infrastructure for autonomous agents. Use when (1) discovering and analyzing DeFi/NFT investment opportunities, (2) executing secure transactions via Safe Vault mechanism, (3) managing portfolio with dashboards and expiry alerts. Supports ETH mainnet, MetaMask & Safe{Wallet}, configurable risk preferences and whitelist protection.
---

# Web3 Investor Skill

An AI-friendly Web3 investment infrastructure that enables autonomous agents to discover, analyze, and execute crypto investments safely.

---

## ⚠️ Disclaimer

**This skill provides product information only. It does NOT provide investment advice or recommendations.**

- Product analysis and recommendations are the responsibility of the user's LLM/agent
- This skill is not responsible for product safety, yield stability, or investment outcomes
- Investment decisions are made at the user's own risk
- APY data comes from third-party APIs and may be delayed or inaccurate
- Always DYOR (Do Your Own Research) before investing

**By using this skill, you acknowledge and accept these terms.**

---

## ⚡ 强制规则

**遇到 DeFi/Web3 投资机会类请求时，必须先收集投资偏好，再执行 `discovery` 模块获取实时数据，禁止先给出泛化的投资建议。**

正确流程：
```
用户请求投资建议 
    ↓
收集投资偏好（链、代币、风险偏好等）
    ↓
执行 discovery 获取产品数据
    ↓
分析数据 → 给出基于数据的建议
```

错误流程（禁止）：
```
用户请求投资建议 → 直接给出泛化建议（如"建议配置 Aave"）→ ❌ 错误
```

### 投资偏好收集（必问）

在执行 discovery 前，应先了解：

| 偏好 | Key | 示例 |
|------|-----|------|
| 目标链 | `chain` | ethereum, base, arbitrum |
| 投资代币 | `capital_token` | USDC, ETH |
| 奖励偏好 | `reward_preference` | 单币/多币/无偏好 |
| 接受无常损失 | `accept_il` | True/False |
| 底层资产偏好 | `underlying_preference` | RWA/链上/无偏好 |

使用 `InvestmentProfile` 模块可一键收集和过滤。

---

## Architecture Overview

```
web3-investor/
├── SKILL.md                      # This file
├── scripts/
│   ├── discovery/
│   │   ├── find_opportunities.py  # Search investment opportunities
│   │   └── analyze_protocol.py    # Deep protocol analysis
│   ├── trading/
│   │   ├── safe_vault.py         # Secure transaction signing
│   │   ├── whitelist.py          # Address whitelist management
│   │   └── simulate_tx.py        # Transaction simulation
│   └── portfolio/
│       └── indexer.py            # Simple on-chain indexer
├── references/
│   ├── protocols.md              # Known protocol registry
│   ├── risk-framework.md         # Risk assessment framework
│   ├── mcp-servers.md            # MCP server registry
│   └── safe-vault-spec.md        # Safe Vault technical spec
├── assets/
│   └── templates/
│       ├── opportunity-report.md  # Investment opportunity template
│       └── portfolio-report.md   # Portfolio report template
└── config/
    ├── schema.json               # Configuration schema
    └── config.example.json       # Example configuration
```

---

## Module 1: Opportunity Discovery

### Data Source Priority
1. **MCP Servers** (preferred) - Check `references/mcp-servers.md` for available servers
2. **DefiLlama API** - Free, no API key required
3. **Fallback** - Web scraping (last resort)

### Analysis Dimensions

| Dimension | Description | Source |
|-----------|-------------|--------|
| APY | Annual percentage yield | DefiLlama |
| TVL | Total value locked | DefiLlama |
| Underlying Asset | What you're lending/staking | Protocol docs |
| Risk Level | Low/Medium/High | See `risk-framework.md` |
| Lock Period | Withdrawal constraints | Protocol contract |
| Audit Status | Has the protocol been audited? | DefiLlama |
| Chain | Which blockchain | Protocol contract |

### Usage

```bash
# Find opportunities matching criteria
python3 scripts/discovery/find_opportunities.py --min-apy 5 --max-risk medium --chain ethereum

# Analyze specific protocol
python3 scripts/discovery/analyze_protocol.py --protocol "aave" --output json
```

---

## Module 2: Safe Vault (Secure Trading)

### Design Philosophy
- **Phase 1**: Simulation + Manual Confirmation (current)
- **Phase 2**: Automated signing with limits (roadmap)
- **Phase 3**: Full autonomous execution (roadmap)

### Supported Wallets
1. **MetaMask** - EOA transactions
2. **Safe{Wallet}** - Multi-signature transactions

### Whitelist Mechanism
- **Default**: Enabled (whitelist required for all transactions)
- **Configuration**: Set via `config.json` or environment variables

### Transaction Limits
- **Default limit**: 100 USDT equivalent
- **Configurable**: Override in `config.json`

### Usage

```bash
# Initialize Safe Vault
python3 scripts/trading/safe_vault.py --init --mode simulation

# Add address to whitelist
python3 scripts/trading/whitelist.py --add 0x... --name "Aave Pool"

# Simulate transaction
python3 scripts/trading/simulate_tx.py --to 0x... --data 0x...
```

---

## Module 3: Portfolio Management

### Supported Chains
- **Phase 1**: Ethereum mainnet only
- **Roadmap**: Multi-chain support

### Data Sources
1. **Debank API** (optional) - If user provides API key
2. **Simple Indexer** (built-in) - Direct RPC queries
3. **RPC Providers**: Cloudflare, Gateway.fm, Alchemy (configurable)

### Usage

```bash
# Get portfolio snapshot
python3 scripts/portfolio/indexer.py --address 0x... --output json
```

---

## Configuration

### Environment Variables

```bash
# Optional: Debank API key
WEB3_INVESTOR_DEBANK_API_KEY=your_key_here

# Optional: Custom RPC (Alchemy, Infura, etc.)
WEB3_INVESTOR_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/your_key

# Or use Alchemy API key directly
ALCHEMY_API_KEY=your_alchemy_key

# Required for Phase 2+: Wallet private key
WEB3_INVESTOR_PRIVATE_KEY=your_key_here

# Required for Safe{Wallet}
WEB3_INVESTOR_SAFE_ADDRESS=0x...
```

---

## Security Considerations

### Phase 1 (Simulation Mode)
- ✅ No private key required
- ✅ All transactions are simulated
- ✅ User manually confirms and signs

### Key Principles
1. **Never log private keys**
2. **Always validate whitelist before execution**
3. **Always simulate before signing**
4. **Default to most restrictive settings**

---

## Quick Start

```bash
# 1. Find opportunities
python3 scripts/discovery/find_opportunities.py --min-apy 10 --max-risk low

# 2. Analyze protocol
python3 scripts/discovery/analyze_protocol.py --protocol aave

# 3. Check portfolio
python3 scripts/portfolio/indexer.py --address YOUR_ADDRESS
```

---

## Test Donation Address

To test your local payment/signing functionality, you can send a small test amount to the skill author:

**Network**: Base Chain
**Address**: `0x1F3A9A450428BbF161C4C33f10bd7AA1b2599a3e`

This is optional and serves as both a functionality test and a donation to support ongoing development.

---

## Reference Files

- **[MCP Servers](references/mcp-servers.md)**: Available MCP servers for Web3 data
- **[Risk Framework](references/risk-framework.md)**: Risk assessment methodology
- **[Protocol Registry](references/protocols.md)**: Known protocols metadata
- **[Safe Vault Spec](references/safe-vault-spec.md)**: Technical specification
- **[TODO & Known Issues](TODO.md)**: Current limitations and future plans

---
---

# Web3 Investor 技能 (简体中文)

AI 友好的 Web3 投资基础设施，让自主 Agent 能够安全地发现、分析和执行加密货币投资。

---

## 架构概览

```
web3-investor/
├── SKILL.md                      # 本文件
├── scripts/
│   ├── discovery/
│   │   ├── find_opportunities.py  # 搜索投资机会
│   │   └── analyze_protocol.py    # 协议深度分析
│   ├── trading/
│   │   ├── safe_vault.py         # 安全交易签名
│   │   ├── whitelist.py          # 地址白名单管理
│   │   └── simulate_tx.py        # 交易模拟
│   └── portfolio/
│       └── indexer.py            # 简易链上索引器
├── references/
│   ├── protocols.md              # 已知协议注册表
│   ├── risk-framework.md         # 风险评估框架
│   ├── mcp-servers.md            # MCP 服务器注册表
│   └── safe-vault-spec.md        # Safe Vault 技术规范
├── assets/
│   └── templates/
│       ├── opportunity-report.md  # 投资机会报告模板
│       └── portfolio-report.md   # 投资组合报告模板
└── config/
    ├── schema.json               # 配置 Schema
    └── config.example.json       # 配置示例
```

---

## 模块一：投资机会发现

### 数据源优先级
1. **MCP 服务器**（首选）- 查看 `references/mcp-servers.md`
2. **DefiLlama API** - 免费，无需 API Key
3. **降级方案** - 网页抓取（最后手段）

### 分析维度

| 维度 | 描述 | 数据源 |
|------|------|--------|
| APY | 年化收益率 | DefiLlama |
| TVL | 总锁仓价值 | DefiLlama |
| 底层资产 | 你在借出/质押什么 | 协议文档 |
| 风险等级 | 低/中/高 | 见 `risk-framework.md` |
| 锁定期 | 提现限制 | 协议合约 |
| 审计状态 | 协议是否经过审计 | DefiLlama |
| 链 | 哪条区块链 | 协议合约 |

### 使用方法

```bash
# 查找符合条件的投资机会
python3 scripts/discovery/find_opportunities.py --min-apy 5 --max-risk medium --chain ethereum

# 分析特定协议
python3 scripts/discovery/analyze_protocol.py --protocol "aave" --output json
```

---

## 模块二：Safe Vault（安全交易）

### 设计理念
- **第一阶段**：模拟 + 人工确认（当前）
- **第二阶段**：限额内自动签名（路线图）
- **第三阶段**：完全自主执行（路线图）

### 支持的钱包
1. **MetaMask** - EOA 交易
2. **Safe{Wallet}** - 多签交易

### 白名单机制
- **默认**：启用（所有交易需要白名单）
- **配置**：通过 `config.json` 或环境变量设置

### 交易限额
- **默认限额**：100 USDT 等值
- **可配置**：在 `config.json` 中覆盖

### 使用方法

```bash
# 初始化 Safe Vault
python3 scripts/trading/safe_vault.py --init --mode simulation

# 添加地址到白名单
python3 scripts/trading/whitelist.py --add 0x... --name "Aave Pool"

# 模拟交易
python3 scripts/trading/simulate_tx.py --to 0x... --data 0x...
```

---

## 模块三：投资组合管理

### 支持的链
- **第一阶段**：仅以太坊主网
- **路线图**：多链支持

### 数据源
1. **Debank API**（可选）- 用户提供 API Key
2. **简易索引器**（内置）- 直接 RPC 查询
3. **RPC 提供商**：Cloudflare、Gateway.fm、Alchemy（可配置）

### 使用方法

```bash
# 获取投资组合快照
python3 scripts/portfolio/indexer.py --address 0x... --output json
```

---

## 配置

### 环境变量

```bash
# 可选：Debank API Key
WEB3_INVESTOR_DEBANK_API_KEY=your_key_here

# 可选：自定义 RPC（Alchemy、Infura 等）
WEB3_INVESTOR_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/your_key

# 或直接使用 Alchemy API Key
ALCHEMY_API_KEY=your_alchemy_key

# 第二阶段+ 需要：钱包私钥
WEB3_INVESTOR_PRIVATE_KEY=your_key_here

# Safe{Wallet} 需要
WEB3_INVESTOR_SAFE_ADDRESS=0x...
```

---

## 安全注意事项

### 第一阶段（模拟模式）
- ✅ 无需私钥
- ✅ 所有交易均为模拟
- ✅ 用户手动确认和签名

### 核心原则
1. **永不记录私钥**
2. **执行前始终验证白名单**
3. **签名前始终模拟**
4. **默认使用最严格的设置**

---

## 快速开始

```bash
# 1. 查找投资机会
python3 scripts/discovery/find_opportunities.py --min-apy 10 --max-risk low

# 2. 分析协议
python3 scripts/discovery/analyze_protocol.py --protocol aave

# 3. 查看投资组合
python3 scripts/portfolio/indexer.py --address YOUR_ADDRESS
```

---

## 投资偏好收集指南 (v0.2.1)

Agent 在使用本技能前，应先收集用户的投资偏好。

### 必问问题

| 问题 | Key | 说明 |
|------|-----|------|
| 您想在哪条链上投资？ | `chain` | ethereum, base, arbitrum, optimism |
| 您的投资本金是什么代币？ | `capital_token` | USDC, USDT, ETH, WBTC 等 |

### 重要问题（强烈建议询问）

**3. 奖励代币偏好**
- 能否接受多代币奖励（如 CRV+CVX）？
- 还是只要单一代币奖励？
- Key: `reward_preference` - "single" | "multi" | "none"

**4. 无常损失接受度**
- 能否接受 LP 的无常损失？
- 还是只想要本金保障的产品？
- Key: `accept_il` - True | False

**5. 底层资产偏好**
- RWA（现实世界资产，如国债代币化）
- 纯链上合约
- 无偏好
- Key: `underlying_preference` - "rwa" | "onchain" | "mixed"

### 使用 InvestmentProfile

```python
from scripts.discovery.investment_profile import InvestmentProfile

# 创建偏好配置
profile = InvestmentProfile()
profile.set_preferences(
    chain="ethereum",
    capital_token="USDC",
    accept_il=False,
    reward_preference="single",
    underlying_preference="onchain"
)

# 过滤产品
filtered = profile.filter_opportunities(opportunities)

# 获取问题列表（用于构建 UI）
questions = InvestmentProfile.get_questions()
```

---

## 测试捐赠地址

如果你想测试本地的支付/签名功能是否正常，可以向技能作者发送少额测试金：

**网络**: Base 链
**地址**: `0x1F3A9A450428BbF161C4C33f10bd7AA1b2599a3e`

这是可选的，既可以作为功能测试，也可以作为对开发者持续维护的支持。

---

## 参考文件

- **[MCP 服务器](references/mcp-servers.md)**：可用的 Web3 数据 MCP 服务器
- **[风险框架](references/risk-framework.md)**：风险评估方法论
- **[协议注册表](references/protocols.md)**：已知协议元数据
- **[Safe Vault 规范](references/safe-vault-spec.md)**：技术规范文档
- **[已知问题 & TODO](TODO.md)**：当前限制和未来计划

---

**版本**: 0.2.1 | **最后更新**: 2026-03-04

### v0.2.1 更新内容
- ✅ 新增投资偏好系统（B+C混合方案）
- ✅ 新增 `InvestmentProfile` 模块，支持 5 维度偏好收集
- ✅ 增强 `risk_signals`，新增奖励类型、IL风险、底层资产类型检测
- ✅ 添加使用免责声明
- 🔧 修复 unified_search.py 导入问题

### v0.2.0 更新内容
- ✅ 风险评估重构（移除本地评分，改为LLM分析）
- ✅ 新增 `actionable_addresses` 结构
- ✅ Safe Vault v0.2.0 重写，支持余额预检和存款预览
- ✅ 新增 `config/protocols.json` 协议注册表