---
name: options-analyzer
description: |
  📊 专业期权策略分析器 — 期权链、Greeks、IV分析、策略推荐一站式解决！
  使用 yfinance 获取实时期权数据，Black-Scholes 计算 Greeks。
  触发条件: 用户询问期权链、Greeks计算、IV分析、期权策略分析、策略推荐、
  Iron Condor/Butterfly/Straddle/Strangle/Spread等策略、"分析期权"、
  "推荐期权策略"、"看涨/看跌期权"、Delta/Gamma/Theta/Vega计算、隐含波动率。
---

# 📊 Options Analyzer — 专业期权策略分析器

> 让期权交易变得简单！从数据获取到策略推荐，一站式搞定。

## ✨ 核心能力

| 功能 | 脚本 | 说明 |
|------|------|------|
| 期权链 | `options_chain.py` | 获取实时数据，筛选到期日/行权价 |
| Greeks | `greeks_calc.py` | Delta/Gamma/Theta/Vega/Rho 计算 |
| IV分析 | `iv_analysis.py` | IV Rank/Percentile, HV vs IV |
| 策略分析 | `strategy_analyzer.py` | 15+种策略盈亏、Breakeven |
| 策略推荐 | `strategy_recommend.py` | 基于观点+IV环境智能推荐 |

## 🚀 快速开始

```bash
pip install yfinance mibian pandas numpy  # 安装依赖
```

### 期权链

```bash
python scripts/options_chain.py AAPL
python scripts/options_chain.py AAPL --expiry 2024-03-15
python scripts/options_chain.py SPY --strike-range 5  # ATM ±5%
python scripts/options_chain.py AAPL --format json
```

### Greeks 计算

```bash
# 手动参数 (iv/rate 用百分比)
python scripts/greeks_calc.py --spot 180 --strike 185 --dte 30 --rate 5 --iv 25 --type call

# 从实时数据
python scripts/greeks_calc.py --symbol AAPL --strike 185 --expiry 2024-03-15 --type call
```

### IV 分析

```bash
python scripts/iv_analysis.py AAPL
# 输出: ATM IV, IV Rank, IV Percentile, HV(20/60), IV-HV Premium
```

### 策略分析

```bash
# Iron Condor
python scripts/strategy_analyzer.py --strategy iron_condor --spot 180 \
  --legs "175p@2.5,180p@4.0,185c@3.5,190c@1.5" --dte 30

# Bull Call Spread  
python scripts/strategy_analyzer.py --strategy bull_call_spread --spot 180 \
  --legs "180c@5.0,190c@2.0" --dte 30
```

### 策略推荐

```bash
python scripts/strategy_recommend.py AAPL --outlook bullish --risk moderate
python scripts/strategy_recommend.py SPY --outlook neutral --risk conservative
```

## 📚 参考文档

- [strategies.md](references/strategies.md) — 15种策略详解- [greeks_guide.md](references/greeks_guide.md) — Greeks 完全指南

---

## ☕ 支持作者

如果这个工具帮到了你，请考虑请我喝杯咖啡！

- **GitHub Sponsors**: [@BENZEMA216](https://github.com/sponsors/BENZEMA216)
- **Buy Me a Coffee**: [buymeacoffee.com/benzema216](https://buymeacoffee.com/benzema216)
- **USDC (Base)**: `0x...` *(联系获取地址)*

你的支持是我持续改进的动力 🚀
