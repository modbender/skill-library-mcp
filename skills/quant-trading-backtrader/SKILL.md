# quant-trading-backtrader

A comprehensive skill for building, backtesting, and optimizing quantitative trading strategies using the Backtrader framework in Python.

## Features

- **Backtesting Engine**: Simulates trading strategies on historical data with support for multiple data feeds.
- **Strategy Development**: Provides a structured `Strategy` class to define indicators (SMA, EMA, RSI, etc.) and trading logic.
- **Risk Management**: Examples of implementing stop-loss, take-profit, and position sizing (e.g., fractional Kelly).
- **Data Handling**: Support for CSV data ingestion (customizable formats) and pandas DataFrame integration.
- **Reporting**: Generates transaction logs, trade analysis (PNL), and portfolio value tracking.

## Usage

This skill provides a foundation for creating quantitative trading bots. It includes templates and examples to get you started.

### 1. Installation

Ensure you have the required dependencies:

```bash
pip install backtrader matplotlib
```

### 2. Basic Strategy Template

Create a new strategy file (e.g., `my_strategy.py`) using the template structure:

```python
import backtrader as bt

class MyStrategy(bt.Strategy):
    params = (
        ('period', 15),
    )

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.period)

    def next(self):
        if self.sma > self.data.close:
            # Do something
            pass
```

### 3. Running a Backtest

Use `bt.Cerebro` to orchestrate the backtest:

```python
cerebro = bt.Cerebro()
cerebro.addstrategy(MyStrategy)
# ... add data ...
cerebro.run()
```

## Examples

Check the `examples/` directory for full working examples:
- `sma_crossover.py`: A classic Trend Following strategy with Stop-Loss.

## Best Practices

- **Avoid Overfitting**: Use Walk-Forward Analysis (train on past, test on unseen future data).
- **Risk Control**: Always implement stop-loss orders. Position sizing is critical for survival.
- **Data Quality**: Ensure your historical data is clean and representative.
