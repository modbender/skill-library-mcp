---
name: etf-finance
description: ETF and fund portfolio manager with price alerts, profit/loss tracking, and position management. Track your ETF/fund holdings, calculate gains/losses, set price alerts, and monitor performance in real-time using 腾讯财经 (Tencent Finance) for Chinese A-shares and Yahoo Finance for US stocks.
---

# ETF Finance Skill

A comprehensive ETF and fund portfolio management tool with real-time price tracking, profit/loss calculations, and price alert functionality.

## 功能概述

- 持仓管理：添加、删除、查看 ETF/基金持仓
- 盈亏计算：实时计算持仓盈亏和收益率
- 价格提醒：设置目标价格，达到时自动提醒
- 行情监控：实时获取 ETF/基金价格数据

## 使用方法

### 持仓管理

#### 添加持仓
```bash
cd ~/.openclaw/workspace/skills/etf-investor
python3 scripts/add_position.py SPY 150.50 100 "S&P 500 ETF"
```
参数：代码 | 买入价 | 数量 | 名称

#### 删除持仓
```bash
python3 scripts/remove_position.py SPY
```

#### 查看持仓列表
```bash
python3 scripts/list_positions.py
```

#### 查看持仓详情（含盈亏）
```bash
python3 scripts/portfolio_summary.py
```

### 价格提醒

#### 设置价格提醒
```bash
python3 scripts/add_alert.py SPY 160.00 "price_up"
# 或
python3 scripts/add_alert.py SPY 140.00 "price_down"
```

#### 查看所有提醒
```bash
python3 scripts/list_alerts.py
```

#### 删除提醒
```bash
python3 scripts/remove_alert.py SPY
```

#### 检查提醒状态
```bash
python3 scripts/check_alerts.py
```

### 行情查询

#### 查询单个 ETF/基金价格
```bash
python3 scripts/get_price.py SPY
```

#### 批量查询持仓价格
```bash
python3 scripts/update_prices.py
```

## 持仓数据格式

持仓存储在 `~/.clawdbot/etf_investor/positions.json`:
```json
[
  {
    "symbol": "SPY",
    "name": "S&P 500 ETF",
    "buy_price": 150.50,
    "quantity": 100,
    "buy_date": "2026-02-23",
    "current_price": 155.20,
    "last_updated": "2026-02-23T10:30:00Z"
  }
]
```

## 价格提醒数据格式

提醒存储在 `~/.clawdbot/etf_investor/alerts.json`:
```json
[
  {
    "symbol": "SPY",
    "target_price": 160.00,
    "condition": "price_up",
    "created_at": "2026-02-23T10:00:00Z",
    "triggered": false
  }
]
```

## 盈亏计算公式

- **持仓市值**: 当前价 × 数量
- **成本**: 买入价 × 数量
- **盈亏金额**: (当前价 - 买入价) × 数量
- **盈亏比例**: (当前价 - 买入价) / 买入价 × 100%

## 支持的代码格式

- **美股 ETF**: SPY, QQQ, VOO, VTI, IVV, IWM
- **国际 ETF**: EFA, VEA, VWO, VXUS
- **行业 ETF**: XLF, XLK, XLV, XLE, XLB
- **基金**: 使用 Yahoo Finance 支持的任何基金代码

## 安装与卸载

### 安装
```bash
cd ~/.openclaw/workspace/skills/etf-investor
bash scripts/install.sh
```

### 卸载
```bash
bash scripts/uninstall.sh
```

## 自动提醒

可以将 `check_alerts.py` 加入系统定时任务（如 cron）实现自动提醒：

```bash
# 每小时检查一次提醒
0 * * * * cd ~/.openclaw/workspace/skills/etf-investor && python3 scripts/check_alerts.py
```

## 注意事项

- 数据来源：Yahoo Finance (免费，无 API Key)
- 价格可能有 15 分钟延迟（美股）
- 建议定期备份数据文件
- 价格提醒仅在本地检查，不会推送通知

## 脚本说明

- `add_position.py` - 添加持仓
- `remove_position.py` - 删除持仓
- `list_positions.py` - 列出所有持仓
- `portfolio_summary.py` - 持仓摘要（含盈亏）
- `add_alert.py` - 添加价格提醒
- `remove_alert.py` - 删除价格提醒
- `list_alerts.py` - 列出所有提醒
- `check_alerts.py` - 检查提醒状态
- `get_price.py` - 获取单个价格
- `update_prices.py` - 批量更新价格
- `install.sh` - 安装脚本
- `uninstall.sh` - 卸载脚本
