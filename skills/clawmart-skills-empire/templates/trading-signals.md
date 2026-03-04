# Trading Signal Generator Skill

## What This Skill Does
Automatically scans markets (XAUUSD, EURUSD, etc.) and generates trading signals based on ICT concepts.

## Features
- Real-time price scanning
- Order Block detection
- FVG (Fair Value Gap) identification
- OTE (Optimal Trade Entry) calculations
- Entry/Exit/SL recommendations
- Telegram/Discord alerts

## Installation
```bash
# Install dependencies
pip install MetaTrader5 pandas numpy

# Configure API keys in config.json
```

## Usage
```python
from trading_signals import Scanner

scanner = Scanner(symbol="XAUUSD", timeframe="H1")
signals = scanner.scan()
for signal in signals:
    print(f"Signal: {signal.type}")
    print(f"Entry: {signal.entry}")
    print(f"SL: {signal.sl}")
    print(f"TP: {signal.tp}")
```

## Requirements
- MT5 Demo Account
- Python 3.8+
- MetaTrader5 package

## Pricing
- Starter: $9 (1 pair, basic signals)
- Pro: $19 (5 pairs, all timeframes)
- Empire: $39 (unlimited, alerts included)
