---
name: okx-trading-exe
description: A standardized adapter gateway skill exclusively for OKX exchange to execute trading actions (buy/sell) and query capabilities across OKX Live and Demo environments.
---

# `okx-trading-exe` Skill 说明书

> 本 Skill 是一个无状态的“执行手柄”，只负责对接 OKX 交易所（包含模拟盘与实盘），执行标准化的交易动作与资产查询。它**不包含**其他交易所接口，也**不包含**任何策略分析逻辑。

## 🔐 授权与鉴权获取 (Prompt-driven Auth) - Agent 必读
本代码需要 OKX 的 `API_KEY`, `API_SECRET` 和 `PASSPHRASE` 才能运行。
**如果**你在执行底层的脚本时，收到了关于 `Missing API Key` 或未授权的报错，你**绝对不要**尝试去猜测密码，也**不要**停止工作。
**你的处理逻辑必须是：**中途中断当前的代码思路，使用自然语言明确向你的“物理人类主人”索要这三个秘钥，并让主人将它们写入当前工作目录的 `.env` 文件中。只有在人类确认写好后，你才能再次尝试执行。

## 能力范围 (Capabilities)
目前支持以下核心操作动作：
- 查询账户总余额/可用资金 (`get_balance`)
- 查询当前已持有的真实仓位 (`get_positions`)
- 发起市价买单/卖单 (`place_market_order`)
- 发起限价买单/卖单 (`place_limit_order`)
- 拉取最近的历史成交记录 (`get_recent_trades`)

## 调用说明 (Usage for Agents / PA)
如果你是一个外层调度 Agent (比如 TAS 小队成员) 或策略 (Skill)，请使用随附的入口脚本与本 Skill 进行交互。

**标准切入点**：
`python scripts/execute.py --action [ACTION_NAME] --provider [PROVIDER_NAME] [OPTIONS]`

### 支持的 Provider (环境提供者)
- `okx_demo`: 连接 OKX 交易所模拟盘 (预设).
- `okx_live`: 连接 OKX 交易所的实盘交易.

### 示例用法 (Examples)

**1. 查询模拟盘所有资产与持仓**
```bash
python scripts/execute.py --action get_positions --provider okx_demo
```

**2. 在模拟盘下一笔市价买单**
```bash
python scripts/execute.py --action place_market_order --provider okx_demo --symbol BTC-USDT --side buy --size 50
# 注意: OKX 市价买单时，size 通常代表花费 50 USDT。
```

**3. 在模拟盘下一笔限价卖单**
```bash
python scripts/execute.py --action place_limit_order --provider okx_demo --symbol BTC-USDT --side sell --size 0.1 --price 62000
# 卖出 0.1 枚 BTC，限价标的是 62000 USDT。
```

## 注意事项与约束 (Constraints)
1. **统一的交易对格式**：所有请求必须使用 `-` 连接的标准格式，如 `BTC-USDT`，不要使用 `/`。
2. **凭据安全**：本 Skill 在真实请求前会自动读取 `.env` 中的秘钥配置，不要在任何参数中明文传递私钥！
3. **输出格式**：执行结果将以标准化的 JSON 或清爽的 stdout 文本格式输出，方便被其他脚本或大语言模型正则提取。
