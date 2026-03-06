---
name: crypto-4h-trade-brief
description: 每4小时输出一次 BTC/ETH 行情复盘与可执行建议。基于 crypto-market-analyzer 的最新4h+1d数据，给出欧易（OKX）合约与现货网格的手填参数（区间、触发条件、止损止盈、仓位建议）。当用户要求“每4小时分析”“给欧易手填参数”“合约+网格参数建议”时使用。
---

# Crypto 4H Trade Brief

## 执行步骤

1. 运行分析脚本，获取最新 BTC/ETH 数据：
```bash
python3 /home/hmzo/.openclaw/workspace/skills/public/crypto-market-analyzer/scripts/fetch_crypto_data.py --output json
```

2. 先给 2-4 句市场结论（趋势、动能、是否仅反弹非反转）。

3. 做“执行闸门”判断（先判断，后给参数）：

### A) 数据可用性闸门（任一命中则暂停参数）
- `data_quality.errors` 非空。
- `intraday_candle_count < 12` 或 `daily_candle_count < 120`。
- 最新数据时间戳滞后明显（超过 8 小时）。

命中后必须输出：
- `本轮数据不完整/滞后，暂停给参数。`

### B) 交易质量闸门（任一命中则仅给观察方案，不给可执行入场）
- `long_breakout.status == standby` 且 `short_breakdown.status == standby`。
- `volume_ratio < 0.5`（极缩量）。

命中后必须输出：
- `当前信号质量不足，仅观察，不建议执行新仓。`
- 仍可提供关键位与触发条件，但标记为“观察模板”。

4. 若通过闸门，再输出欧易手填参数，分两块：

### A) 合约（永续）
- 方向建议：只给“做多条件”与“做空条件”，不要无条件喊单。
- 触发确认：必须写明“按 4h 收盘确认突破/跌破，不接受瞬时插针触发”。
- 必给参数：
  - 入场触发价（基于支撑/阻力突破确认）
  - 止损价（结构位）
  - 止盈1/止盈2（至少 1:1.5 和 1:2.5）
  - 建议杠杆（小白默认 3x-5x）
  - 单笔风险上限（默认总资金 0.8%-1%）

### B) 现货网格
- 必给参数：
  - 价格区间（下沿/上沿）
  - 网格数量（使用统一推导规则）
  - 单格利润预期（区间与网格推导）
  - 终止条件（跌破下沿如何处理、突破上沿如何处理）
- 若当前偏空，优先“防守型区间”（下沿留缓冲）。

5. 仓位系数规则（强制执行）

以基础仓位 `base_size` 为 1：
- `volume_ratio >= 1.0` -> `size_factor = 1.0`
- `0.7 <= volume_ratio < 1.0` -> `size_factor = 0.5`
- `0.5 <= volume_ratio < 0.7` -> `size_factor = 0.3`
- `volume_ratio < 0.5` -> `size_factor = 0.0`（暂停合约开仓）

必须明确提示：
- 当 `volume_ratio < 1`：`信号可靠性偏弱，降低仓位。`
- 当 `volume_ratio < 0.5`：`量能过低，本轮不执行合约新仓。`

6. 网格数量与单格利润统一公式（强制）

- `range_pct = (upper - lower) / mid * 100`，`mid = (upper + lower)/2`
- `grid_count = clamp(int(range_pct / 0.8), 12, 40)`
- `single_grid_profit_pct ~= range_pct / grid_count`

输出时四舍五入到 2 位小数，并写明“为估算值，需扣除手续费”。

7. 最后给“可直接照抄”的欧易手填模板（字段必须完整）：

```text
[BTC 合约]
模式: 逐仓
杠杆: Xx
方向: 条件触发
触发确认: 4h收盘确认
入场: xxxx
止损: xxxx
止盈1: xxxx
止盈2: xxxx
单笔风险: 0.8%-1%
仓位系数: x.xx

[ETH 合约]
...

[BTC 现货网格]
区间: xxxx - xxxx
网格数: xx
单格利润预估: x.xx%
投入: xxx USDT
触发条件: ...
终止条件: ...

[ETH 现货网格]
...
```

若模板字段缺失，必须输出：
- `本轮参数不完整，暂停执行，请补齐字段后再下单。`

## 输出要求

- 中文，面向小白，先结论后参数。
- 每次都注明：`这不是财务建议，先小仓位试运行。`
- 任何暂停/观察场景，语气要明确，不给模糊建议。
- 优先使用分析脚本产出的结构化字段，不手工臆测价位。