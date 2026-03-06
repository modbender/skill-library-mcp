# VibeTrading Code Generator

生成Hyperliquid交易所的可执行交易策略代码。

## 📁 目录结构

```
vibetrading-code-gen/
├── SKILL.md                    # 技能说明文档
├── README.md                   # 本文件
├── api_wrappers/               # API封装层
│   └── hyperliquid_api.py      # Hyperliquid API包装器
├── scripts/                    # 核心脚本
│   ├── strategy_generator_with_prices.py  # 主生成器（带价格集成）
│   ├── price_fetcher.py        # 价格查询工具
│   ├── template_manager.py     # 模板管理
│   ├── prompt_parser.py        # 提示解析器
│   ├── code_formatter.py       # 代码格式化
│   ├── code_validator.py       # 代码验证器
│   ├── backtest_runner.py      # 回测运行器
│   └── check_python_version.py # 版本检查
├── templates/                  # 策略模板
│   └── grid_trading.py         # 网格交易模板
├── examples/                   # 示例代码
│   ├── grid_trading_example.py # 网格交易示例
│   ├── rsi_strategy_example.py # RSI策略示例
│   ├── configs/                # 示例配置
│   └── README.md               # 示例说明
├── generated_strategies/       # 生成的策略（用户文件）
│   └── HYPE_grid_strategy_20260213_153606/  # 示例策略
├── backtest_engine/            # 回测引擎
├── data/                       # 数据目录
├── logs/                       # 日志目录（自动创建）
├── sessions/                   # 会话目录（自动创建）
└── simulation_results/         # 模拟结果（自动创建）
```

## 🚀 快速开始

### 查看示例策略
```bash
# 运行网格交易示例
python examples/grid_trading_example.py

# 运行RSI策略示例
python examples/rsi_strategy_example.py
```

### 查询价格数据
```bash
# 查询HYPE和BTC的当前价格
python scripts/price_fetcher.py --symbols HYPE BTC --report
```

### 生成策略（带价格集成）
```bash
# 自动查询价格并生成策略
python scripts/strategy_generator_with_prices.py "Generate HYPE grid trading strategy with 10 grids"
```

### 查看生成的策略
最新的策略在 `generated_strategies/` 目录下：
```bash
cd generated_strategies/HYPE_grid_strategy_20260213_153606
ls -la
```

### 运行策略
```bash
cd generated_strategies/HYPE_grid_strategy_20260213_153606
python HYPE_grid_strategy_20260213_153606.py
```

## 📊 已生成的策略

### HYPE网格交易策略
- **位置**: `generated_strategies/HYPE_grid_strategy_20260213_153606/`
- **参数**: 
  - 价格区间: $28.00 - $34.00 USDC
  - 网格数量: 10
  - 每网格: 10 HYPE
- **回测结果**: +0.47% (90天模拟)

## 🔧 维护说明

### 清理临时文件
```bash
# 清理日志和临时文件
rm -rf logs/* simulation_results/* sessions/*
```

### 保留的文件
- `generated_strategies/` - 用户生成的策略（重要！）
- `scripts/` - 核心代码
- `templates/` - 策略模板
- `SKILL.md` - 技能文档

### 可以安全删除的
- `logs/` 中的日志文件
- `simulation_results/` 中的临时结果
- `sessions/` 中的旧会话

## 📞 支持

如有问题，请参考：
1. `SKILL.md` - 详细技能说明
2. 生成的策略中的 `README.md`
3. 策略配置文件 `configs/strategy_config.json`

---
*最后清理时间: 2026-02-13 16:35*
*当前版本: 1.0.2*