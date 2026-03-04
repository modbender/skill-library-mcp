[English](./README.md) | **中文**

---

# OKX Exchange Skill

> OKX 量化交易 Agent，覆盖现货、永续合约和交割合约的全流程自动化。
>
> A quantitative trading agent for OKX exchange — full automation across spot, perpetual swap, and futures.

---

## 能力概览 · Capabilities

| 类别 · Category | 功能 · Features |
|---|---|
| 市场数据 Market Data | 价格、K线、行情、技术指标 (MA / RSI / MACD) |
| 账户管理 Account | 余额、持仓、挂单、历史成交 |
| 订单执行 Orders | 市价/限价、双向持仓、TP/SL、批量下单、OCO条件单 |
| 策略 Strategies | 趋势跟踪、网格交易、现货合约套利 |
| 风控 Risk | 强平预警、日交易限额、价格冲击检查、止损止盈自动执行 |
| 监控 Monitoring | 账户快照（含历史追踪）、cron 定时任务、SL/TP 自动平仓 |
| 绩效报告 Reports | 日/周/全期盈亏、胜率、最佳/最差交易、分币种统计 |
| 学习系统 Learning | 自动归因历史交易、识别成功/失败模式、优化参数 |
| 模式切换 Mode | 模拟盘 / 实盘一键切换，独立 API Key 隔离 |

---

## 快速开始 · Quick Start

### 1. 配置 API Key · Configure credentials

```bash
cat >> ~/.openclaw/workspace/.env << 'EOF'
# Demo / paper trading (safe default)
OKX_API_KEY=your_demo_key
OKX_SECRET_KEY=your_demo_secret
OKX_PASSPHRASE=your_demo_passphrase
OKX_SIMULATED=1

# Live trading (optional, used only when mode=live)
OKX_API_KEY_LIVE=your_live_key
OKX_SECRET_KEY_LIVE=your_live_secret
OKX_PASSPHRASE_LIVE=your_live_passphrase
EOF
```

> `OKX_SIMULATED=1` = 模拟盘（纸面交易，安全）。上实盘前务必在此验证所有功能。
>
> `OKX_SIMULATED=1` enables paper trading. Validate everything here before going live.

### 2. 安装依赖 · Install dependencies

```bash
pip install -r requirements.txt
```

### 3. 初始化 · Initialize

```bash
cd ~/.openclaw/workspace/skills/okx-exchange/scripts
python3 setup.py
```

---

## 使用方式 · Usage

所有命令通过统一入口 `okx.py` 调用。

All commands go through the unified entry point `okx.py`.

```bash
cd ~/.openclaw/workspace/skills/okx-exchange/scripts
source ~/.openclaw/workspace/.env
```

### 账户 · Account

```bash
python3 okx.py account               # 完整持仓概览 / Full portfolio summary
python3 okx.py account balance USDT  # 指定币种余额 / Specific currency balance
python3 okx.py account positions      # 合约持仓 / Open positions
python3 okx.py account orders         # 挂单 / Pending orders
python3 okx.py account history SWAP   # 历史成交 / Order history
```

### 下单 · Order Execution

```bash
# 现货市价买 / Spot market buy
python3 okx.py buy BTC-USDT market 0.01

# 合约做多，带止盈止损 / Perpetual long with TP/SL
python3 okx.py buy BTC-USDT-SWAP market 1 --td cross --pos long --tp 55000 --sl 42000

# 减仓平多 / Close long (reduce-only)
python3 okx.py sell BTC-USDT-SWAP market 1 --td cross --pos long --reduce

# OCO 条件单（独立止盈止损）/ Standalone OCO algo order
python3 okx.py algo oco BTC-USDT-SWAP 1 --tp 55000 --sl 45000 --td cross --pos long --reduce
```

### 策略 · Strategies

```bash
# 趋势分析 / Trend analysis
python3 okx.py trend analyze BTC-USDT-SWAP --bar 1H

# 网格交易 / Grid trading
python3 okx.py grid setup BTC-USDT 40000 50000 10 1000
python3 okx.py grid check BTC-USDT

# 套利扫描 / Arbitrage scan
python3 okx.py arb scan
python3 okx.py arb basis BTC-USDT BTC-USDT-SWAP
```

### 快照与监控 · Snapshot & Monitoring

```bash
# 实时账户快照（含历史追踪表）/ Live snapshot with historical tracking
python3 okx.py snapshot

# 手动监控 / Manual monitor
python3 okx.py monitor sl-tp      # 止损止盈检查 / SL/TP check
python3 okx.py monitor liq-risk   # 强平风险预警 / Liquidation risk alert

# 定时任务 / Cron automation
bash scripts/cron_setup.sh setup          # 默认间隔 / Default intervals
bash scripts/cron_setup.sh setup 1m       # SL/TP 每 1 分钟
bash scripts/cron_setup.sh setup 10m 1h   # SL/TP 10m, scan 1h
bash scripts/cron_setup.sh teardown       # 停止所有 / Stop all
```

### 绩效报告 · Performance Report

```bash
python3 okx.py report daily    # 今日盈亏 / Today's P&L
python3 okx.py report weekly   # 本周 / This week
python3 okx.py report all      # 全期 / All time
```

### 模式切换 · Trading Mode

```bash
python3 okx.py mode           # 查看当前模式 / Show current mode
python3 okx.py mode demo      # 切换模拟盘 / Switch to paper trading
python3 okx.py mode live      # 切换实盘（需确认）/ Switch to live (requires confirmation)
```

### 配置 · Preferences

```bash
python3 okx.py prefs show
python3 okx.py prefs set stop_loss_pct 3.0
python3 okx.py prefs set auto_trade true
python3 okx.py prefs set watchlist BTC-USDT-SWAP,ETH-USDT-SWAP,SOL-USDT-SWAP
```

---

## 目录结构 · File Structure

```
okx-exchange/
├── SKILL.md                        # Agent 指令 / Agent instructions
├── README.md                       # 本文件 / This file
├── requirements.txt                # Python 依赖 (requests)
├── .env.example                    # 环境变量模板 / Credentials template
│
├── docs/
│   ├── trading-rules.md            # 交易原则与决策规范 / Trading rules & decision principles
│   ├── decision-engine-guide.md    # 决策引擎使用说明 / Decision engine guide
│   └── learning-system-data-management.md  # 学习系统数据管理
│
└── scripts/
    ├── okx.py                      # 统一 CLI 入口 / Unified CLI entry point
    ├── okx_client.py               # OKX REST API 封装 / REST API wrapper
    ├── okx_ws_client.py            # WebSocket 实时数据 / WebSocket feed
    ├── okx_decision.py             # 决策引擎 / Decision engine
    ├── okx_learning.py             # 学习系统（模式识别）/ Learning system
    ├── monitor.py                  # 自动监控（SL/TP, scan, liq-risk）
    ├── account.py                  # 账户 & 持仓展示
    ├── execute.py                  # 订单执行 & 安全检查
    ├── report.py                   # 绩效报告生成
    ├── config.py                   # 配置 & 状态持久化
    ├── errors.py                   # 错误类型定义
    ├── logger.py                   # 结构化日志
    ├── setup.py                    # 首次初始化
    ├── cron_setup.sh               # Cron 定时任务管理
    │
    ├── strategies/
    │   ├── trend.py                # 趋势跟踪（MA + RSI + MACD）
    │   ├── grid.py                 # 网格交易
    │   └── arbitrage.py            # 现货合约套利
    │
    └── tests/                      # 单元测试（371 个）
        ├── run_all.py
        ├── test_account.py
        ├── test_algo_batch.py
        ├── test_arbitrage.py
        ├── test_config.py
        ├── test_decision.py
        ├── test_errors.py
        ├── test_execute.py
        ├── test_grid.py
        ├── test_learning.py
        ├── test_mode.py
        ├── test_okx_client.py
        ├── test_position_risk.py
        ├── test_private_ws.py
        ├── test_report.py
        ├── test_snapshot.py
        ├── test_trend.py
        └── test_ws_client.py
```

### Memory Files（运行时数据）

| 文件 · File | 用途 · Purpose |
|---|---|
| `memory/okx-trading-preferences.json` | 风控参数、策略配置、交易模式 |
| `memory/okx-trading-state.json` | 运行时状态（日交易计数、上次扫描时间）|
| `memory/okx-trading-journal.json` | 监控系统交易日志（SL/TP 自动平仓记录）|
| `memory/okx-trade-journal.json` | 学习系统交易日志（信号分析记录）|
| `memory/okx-learning-model.json` | 学习模型（各币种/市场状态胜率、最优参数）|
| `memory/okx-monitor-snapshots.json` | 账户快照历史（最多 48 条）|
| `memory/okx-grid-{inst_id}.json` | 各标的网格状态 |

---

## 安全说明 · Security

- API Key 存储于 `~/.openclaw/workspace/.env`，不会被发布到 ClawHub
- 实盘与模拟盘使用独立的 Key，互不影响
- 默认开启下单确认（`require_confirm=true`），自动化需显式设置 `auto_trade=true`
- 设有日交易限额（`max_daily_trades`）防止失控

---

## 运行测试 · Run Tests

```bash
cd scripts
python3 tests/run_all.py
# 371 tests, 0 failures
```

---

## 依赖 · Requirements

- Python 3.9+
- `requests >= 2.31.0`
- OKX 账户 + V5 API Key（[申请地址](https://www.okx.com/account/my-api)）

---

[English](./README.md) | **中文**
