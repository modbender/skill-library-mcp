---
name: qmt-strategy-autopilot
description: "一句话需求自动生成并执行QMT策略（封闭式澄清 + 双源数据 + 实盘语义）"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
      env: ["QMT_PATH", "QMT_ACCOUNT_ID", "QMT_SESSION_ID"]
---

# QMT Strategy Autopilot

将自然语言需求转换为 `StrategySpec`，按依赖顺序调用 QMT skills 执行策略。

## 功能

- 一句话解析策略需求
- 1-5 个封闭式澄清问题
- 统一 `StrategySpec` 生成
- 步骤幂等执行（`request_id` + `step_state`）
- 数据双源（xtdata 主源 + qgdata 补源）

## 命令

```bash
# 1) 生成策略计划（可能返回澄清问题）
python3 {baseDir}/scripts/qmt_autopilot.py plan "我持仓的股票里，60分钟5日线下穿10日线则卖出"

# 2) 提交澄清回答
python3 {baseDir}/scripts/qmt_autopilot.py clarify "我持仓的股票里，60分钟5日线下穿10日线则卖出" '{"confirm_mode":"收盘确认","price_mode":"买一价"}'

# 3) 执行StrategySpec
python3 {baseDir}/scripts/qmt_autopilot.py run '{"strategy_name":"demo","symbol_scope":"portfolio","symbols":[],"signal":{"period":"60m","type":"ma_cross","fast":5,"slow":10,"direction":"bearish"},"trigger":{"confirm_mode":"bar_close","cooldown_sec":0,"once_per_day":true},"execution":{"side":"SELL","qty_mode":"all","qty_ratio":1.0,"price_mode":"bid1","max_retries":1},"risk":{"max_order_count":20,"daily_loss_limit":0.05,"dup_signal_block":true},"runtime":{"interval_sec":3,"session":"trade_hours","broker_env":"sim"},"meta":{}}'
```

## 环境变量

- `BROKER_ENV=sim|live`：柜台环境切换（策略语义不变）
- `QGDATA_TOKEN`：启用历史分钟/资讯补源
- `CONNECTION_MANAGER_PATH`、`REALTIME_DATA_PATH`、`TRADING_EXECUTION_PATH`：可选自定义路径
