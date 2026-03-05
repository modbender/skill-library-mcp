# Computed Signals Guide

## Overview

Computed signals enable automated detection of trading opportunities based on technical indicators and price patterns. Signals are defined in YAML configuration files.

## YAML Schema

### Required Keys
- `name` - Signal identifier (string)
- `type` - Signal type: crossover, threshold, expression, range
- Type-specific parameters (see below)

### Optional Keys
- `description` - Human-readable explanation
- `timeframe` - Chart interval: "1D", "1W", "1M", etc.
- `min_volume` - Minimum daily volume filter
- `sector` - Sector filter (stocks only)

## Signal Types

### 1. Crossover Signals

Detects when one indicator crosses above/below another.

**Parameters:**
- `fast` - Fast-moving indicator field name
- `slow` - Slow-moving indicator field name
- `direction` - "up", "down", or "both"

**Example: Golden Cross**
```yaml
name: golden_cross
type: crossover
description: SMA50 crosses above SMA200 (bullish)
fast: SIMPLE_MOVING_AVERAGE_50
slow: SIMPLE_MOVING_AVERAGE_200
direction: up
timeframe: 1D
```

**Example: Death Cross**
```yaml
name: death_cross
type: crossover
description: SMA50 crosses below SMA200 (bearish)
fast: SIMPLE_MOVING_AVERAGE_50
slow: SIMPLE_MOVING_AVERAGE_200
direction: down
timeframe: 1D
```

### 2. Threshold Signals

Triggers when a field meets a threshold condition.

**Parameters:**
- `field` - Field name to evaluate
- `op` - Operator: ">", ">=", "<", "<=", "==", "!="
- `value` - Threshold value (numeric or string)

**Example: Oversold RSI**
```yaml
name: rsi_oversold
type: threshold
description: RSI below 30 indicates oversold
field: RELATIVE_STRENGTH_INDEX_14
op: "<"
value: 30
timeframe: 1D
```

**Example: High Volume**
```yaml
name: high_volume
type: threshold
description: Volume exceeds 10-day average by 50%
field: VOLUME
op: ">"
value: 1.5 * AVERAGE_VOLUME_10_DAY
```

**Example: Technology Sector**
```yaml
name: tech_sector
type: threshold
description: Technology sector stocks only
field: SECTOR
op: "=="
value: "Technology"
```

### 3. Expression Signals

Custom logic using pandas eval() with whitelist validation.

**Parameters:**
- `expr` - Expression string using column names and allowed operators

**Allowed in Expressions:**
- Column names (must exist in screener data)
- Operators: `+`, `-`, `*`, `/`, `>`, `<`, `>=`, `<=`, `==`, `!=`
- Logical: `and`, `or`, `not`
- Numeric literals: `1`, `2.5`, `100`
- Methods: `.mean()`, `.std()`

**NOT Allowed:**
- Function calls (except `.mean()`, `.std()`)
- Imports or external references
- String operations
- Assignment operations

**Example: Price Momentum**
```yaml
name: price_momentum
type: expression
description: Price above both SMAs with positive change
expr: (PRICE > SIMPLE_MOVING_AVERAGE_50) and (PRICE > SIMPLE_MOVING_AVERAGE_200) and (CHANGE_PERCENT > 0)
timeframe: 1D
```

**Example: Volume Surge**
```yaml
name: volume_surge
type: expression
description: Volume exceeds 30-day average by 2x
expr: VOLUME > (AVERAGE_VOLUME_30_DAY * 2)
```

### 4. Range Signals

Detects values within a numeric range.

**Parameters:**
- `field` - Field name to evaluate
- `min` - Minimum value (inclusive)
- `max` - Maximum value (inclusive)

**Example: Neutral RSI**
```yaml
name: rsi_neutral
type: range
description: RSI in neutral zone (40-60)
field: RELATIVE_STRENGTH_INDEX_14
min: 40
max: 60
timeframe: 1D
```

**Example: Mid-Cap Stocks**
```yaml
name: midcap_stocks
type: range
description: Market cap between 2B and 10B
field: MARKET_CAPITALIZATION
min: 2000000000
max: 10000000000
```

## Combining Multiple Signals

Create complex strategies by combining signal files:

```yaml
# signals/momentum-breakout.yaml
name: momentum_breakout
type: expression
description: Combined momentum and volume breakout
expr: (PRICE > SIMPLE_MOVING_AVERAGE_50) and (RELATIVE_STRENGTH_INDEX_14 > 50) and (VOLUME > AVERAGE_VOLUME_10_DAY * 1.5)
timeframe: 1D
min_volume: 1000000
```

## Expression Whitelist Validation

The skill validates expressions before evaluation:

✅ **Valid:**
```python
PRICE > SIMPLE_MOVING_AVERAGE_50
(PRICE > 100) and (VOLUME > 1000000)
RELATIVE_STRENGTH_INDEX_14 < 30
CHANGE_PERCENT > CHANGE_PERCENT.mean()
```

❌ **Invalid:**
```python
import os  # No imports
eval("malicious code")  # No eval/exec
PRICE.apply(lambda x: x * 2)  # No lambda
open("/etc/passwd")  # No file operations
```

## Common Patterns

### Bullish Momentum
```yaml
name: bullish_momentum
type: expression
expr: (PRICE > SIMPLE_MOVING_AVERAGE_50) and (SIMPLE_MOVING_AVERAGE_50 > SIMPLE_MOVING_AVERAGE_200) and (RELATIVE_STRENGTH_INDEX_14 > 50)
```

### Bearish Reversal
```yaml
name: bearish_reversal
type: expression
expr: (PRICE < SIMPLE_MOVING_AVERAGE_50) and (RELATIVE_STRENGTH_INDEX_14 > 70) and (CHANGE_PERCENT < -2)
```

### Volume Confirmation
```yaml
name: volume_confirmation
type: expression
expr: (CHANGE_PERCENT > 2) and (VOLUME > AVERAGE_VOLUME_30_DAY * 1.5)
```

### Breakout Setup
```yaml
name: breakout_setup
type: expression
expr: (PRICE > SIMPLE_MOVING_AVERAGE_50 * 1.02) and (VOLUME > AVERAGE_VOLUME_10_DAY * 2)
```
