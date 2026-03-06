---
name: stock-monitor
description: 股票价格实时监控。支持多只股票监控，使用 Yahoo Finance API 获取实时股价，自定义涨跌阈值提醒。当股价波动超过设定阈值时自动发送提醒，支持首次预警和续警机制。用于：(1) 监控持仓股票价格波动 (2) 设置价格提醒 (3) 定期检查股价变化
---

# 股票价格监控

实时监控多只股票价格，当波动超过阈值时自动提醒。

## 快速开始

### 1. 配置股票列表

创建配置文件 `~/.openclaw/workspace/memory/stocks_config.json`：

```json
{
  "stocks": {
    "贵州茅台": {"symbol": "600519.SS", "base_price": 1600.0, "currency": "¥"},
    "腾讯控股": {"symbol": "0700.HK", "base_price": 512.0, "currency": "HK$"},
    "拼多多": {"symbol": "PDD", "base_price": 120.0, "currency": "$"}
  }
}
```

配置说明：
- `symbol`: Yahoo Finance 股票代码
  - A股: `600519.SS` (茅台)
  - 港股: `0700.HK` (腾讯)
  - 美股: `PDD` (拼多多), `AAPL` (苹果)
- `base_price`: 基准价（昨日收盘或参考价）
- `currency`: 货币符号

### 2. 运行监控

```bash
python3 ~/.openclaw/skills/stock-monitor/scripts/stocks_monitor.py
```

### 3. 设置定时任务

```bash
# 每5分钟检查一次
openclaw cron add --name "股票监控" --cron "*/5 * * * *" --tz "Asia/Shanghai" --message "运行 python3 ~/.openclaw/workspace/skills/stock-monitor/scripts/stocks_monitor.py 并把输出发给我" --channel discord
```

## 预警规则

- **首次预警**: 涨跌超过 2%
- **续警**: 同一天内，再波动超过 1%
- **重置**: 新一天自动重置基准价为前一天收盘价

## 常用股票代码

| 股票 | 港股代码 | 美股代码 |
|------|----------|----------|
| 腾讯控股 | 0700.HK | TCEHY |
| 阿里巴巴 | 9988.HK | BABA |
| 美团 | 3690.HK | MPNG |
| 小米 | 1810.HK | XI |
| 茅台 | - | 600519.SS |

## 状态文件

脚本会自动在 `~/.openclaw/workspace/memory/stocks_alert.json` 保存监控状态，包括是否已预警、预警日期等。
