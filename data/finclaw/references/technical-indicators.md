# Technical Indicators Reference

## Available Indicators

### Moving Averages
- **SMA(20)**: Short-term trend
- **SMA(50)**: Medium-term trend
- **SMA(200)**: Long-term trend
- **EMA(12)**: Fast exponential average
- **EMA(26)**: Slow exponential average

### Oscillators
- **RSI(14)**: Relative Strength Index (0-100)
  - >70: Overbought (potential sell signal)
  - <30: Oversold (potential buy signal)
  - 30-70: Neutral zone

### MACD (Moving Average Convergence Divergence)
- **MACD Line**: EMA(12) - EMA(26)
- **Signal Line**: EMA(9) of MACD line
- **Histogram**: MACD - Signal (momentum strength)
- Bullish: MACD crosses above signal
- Bearish: MACD crosses below signal

### Bollinger Bands (20, 2)
- **Upper Band**: SMA(20) + 2 * StdDev
- **Middle Band**: SMA(20)
- **Lower Band**: SMA(20) - 2 * StdDev
- Price at lower band: Potential bounce/buy
- Price at upper band: Potential pullback/sell

## Signal Interpretation

### Bullish Signals
- Price above SMA(50)
- Golden Cross: SMA(50) crosses above SMA(200)
- RSI rising from below 30
- MACD bullish crossover
- Price bouncing off lower Bollinger Band

### Bearish Signals
- Price below SMA(50)
- Death Cross: SMA(50) crosses below SMA(200)
- RSI declining from above 70
- MACD bearish crossover
- Price rejected at upper Bollinger Band
