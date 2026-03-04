# Technical Analysis Indicators

## Moving Averages (MA)

**Simple Moving Average (SMA)**
- Calculation: Average of closing prices over N periods
- Usage: Trend identification, support/resistance levels
- Common periods: 20 (short-term), 50 (mid-term), 200 (long-term)

**Exponential Moving Average (EMA)**
- Calculation: Weighted average giving more weight to recent prices
- Usage: Faster response to price changes than SMA
- Formula: EMA_t = (Price_t × k) + (EMA_{t-1} × (1 - k)), where k = 2/(N+1)

## Bollinger Bands

**Definition**
- Middle band: 20-period SMA
- Upper band: SMA + (2 × 20-period standard deviation)
- Lower band: SMA - (2 × 20-period standard deviation)

**Trading Signals**
- Buy: Price touches lower band
- Sell: Price touches upper band
- Squeeze: Bands narrow (low volatility) - potential breakout imminent

## MACD (Moving Average Convergence Divergence)

**Components**
- MACD line: 12-period EMA - 26-period EMA
- Signal line: 9-period EMA of MACD line
- Histogram: MACD line - Signal line

**Trading Signals**
- Buy: MACD crosses above signal line
- Sell: MACD crosses below signal line
- Momentum: Histogram expands (increasing strength)

## RSI (Relative Strength Index)

**Calculation**
- Measures magnitude of recent price changes
- Range: 0-100
- Typical period: 14

**Trading Signals**
- Overbought: RSI > 70 (potential sell)
- Oversold: RSI < 30 (potential buy)
- Neutral: 30-70

## Stochastic Oscillator

**Components**
- %K: (Current Price - Low_14) / (High_14 - Low_14) × 100
- %D: 3-period SMA of %K

**Trading Signals**
- Overbought: %K and %D > 80
- Oversold: %K and %D < 20
- Cross: %K crosses %D

## Trading Signal Interpretation

**Strong Buy**
- MACD: MACD > Signal, Histogram positive
- RSI: RSI < 30 (oversold)
- Price: Below lower Bollinger band

**Buy**
- MACD: MACD crosses above signal
- RSI: 30-50 (recovering from oversold)
- Price: Approaching lower Bollinger band

**Hold/Neutral**
- MACD: MACD ≈ Signal
- RSI: 40-60 (neutral zone)
- Price: Within middle Bollinger bands

**Sell**
- MACD: MACD crosses below signal
- RSI: 50-70 (approaching overbought)
- Price: Approaching upper Bollinger band

**Strong Sell**
- MACD: MACD < Signal, Histogram negative
- RSI: RSI > 70 (overbought)
- Price: Above upper Bollinger band
