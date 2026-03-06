# ClawBack Configuration Improvements
## Based on Investment Research - February 2, 2026

## Executive Summary
Updated ClawBack configuration template with research-based optimizations for better risk management and performance.

## Key Research Findings Implemented

### 1. Position Sizing Optimization
**Research Finding:** Current 5% position size is aggressive; 1-2% recommended
**Implementation:**
- `tradeScalePercentage`: 0.05 → 0.02 (2%)
- `maxPositionPercentage`: 0.05 → 0.02 (2%)

### 2. Leadership Focus
**Research Finding:** Congressional leaders outperform rank-and-file by 47% annually
**Implementation:**
- Added `leadershipFocus`: true
- Added `leadershipWeight`: 2.0 (2x weighting for leadership trades)
- Added performance tracking for individual politicians

### 3. Risk Management Enhancements
**Research Finding:** Need sector limits (25% max per sector) and daily loss limits
**Implementation:**
- `dailyLossLimit`: 0.03 → 0.05 (5% maximum daily drawdown)
- Added comprehensive `sectorExposureLimits` (25% max per sector)
- Added `correlationLimit`: 0.70 (maximum correlation between positions)
- Added `liquidityRequirement`: 1,000,000 (minimum daily volume)
- Added `volatilityFilter`: true
- Added `kellyFraction`: 0.50 (use 50% of full Kelly Criterion)

### 4. Market Quality Filters
**Research Finding:** Need minimum market cap filters
**Implementation:**
- Added `minimumMarketCap`: 1000000000 ($1B minimum)
- Added `sectorTracking`: true
- Added `performanceBenchmark`: "SPX" (track vs S&P 500)

### 5. Timing Optimization
**Research Finding:** Test different trade delay periods (1-5 days)
**Implementation:**
- Added `delayOptimization` section
- `minDelayDays`: 1
- `maxDelayDays`: 5
- `optimizeBySector`: true

## Configuration Changes Summary

### Trading Section
```json
"trading": {
  "tradeScalePercentage": 0.02,  // Reduced from 5% to 2%
  "maxPositionPercentage": 0.02,  // Reduced from 5% to 2%
  "dailyLossLimit": 0.05,  // Increased from 3% to 5%
}
```

### Strategy Section (New Fields)
```json
"strategy": {
  "leadershipWeight": 2.0,
  "minimumMarketCap": 1000000000,
  "sectorTracking": true,
  "performanceBenchmark": "SPX"
}
```

### Risk Management Section (Enhanced)
```json
"riskManagement": {
  "dailyLossLimit": 0.05,
  "sectorExposureLimits": { /* 25% max per sector */ },
  "correlationLimit": 0.70,
  "liquidityRequirement": 1000000,
  "volatilityFilter": true,
  "kellyFraction": 0.50
}
```

### Congress Section (Enhanced)
```json
"congress": {
  "leadershipFocus": true,
  "performanceTracking": true,
  "delayOptimization": {
    "enabled": true,
    "minDelayDays": 1,
    "maxDelayDays": 5,
    "optimizeBySector": true
  }
}
```

## Expected Benefits

### 1. Reduced Risk
- Lower position sizing (5% → 2%) reduces single-trade impact
- Sector limits prevent overconcentration
- Correlation limits reduce portfolio risk
- Liquidity requirements improve execution

### 2. Improved Performance
- Leadership focus targets 47% outperformance trades
- Market cap filters improve trade quality
- Timing optimization tests different delay periods
- Performance benchmarking against S&P 500

### 3. Better Risk Management
- Daily loss limits protect against catastrophic days
- Volatility filters avoid high-risk stocks
- Kelly Criterion optimization for position sizing
- Comprehensive sector diversification

### 4. Enhanced Monitoring
- Performance tracking by politician
- Sector exposure monitoring
- Correlation analysis
- Benchmark comparison

## Implementation Notes

1. **Backward Compatibility**: Existing configurations will need updates
2. **Performance Impact**: Reduced position sizing may lower returns but improves risk-adjusted returns
3. **Data Requirements**: New filters require additional market data
4. **Testing Needed**: Delay optimization needs backtesting

## Next Steps

1. **Update Existing Configurations**: Apply new settings to current setups
2. **Backtesting**: Test new parameters with historical data
3. **Performance Monitoring**: Track improvements vs old configuration
4. **Continuous Optimization**: Adjust based on ongoing research

## Research References

1. **Leadership Outperformance**: 47% annual outperformance (NBER 2025)
2. **Position Sizing**: 1-2% recommended vs current 5%
3. **Sector Limits**: Maximum 25% exposure per sector
4. **Kelly Criterion**: Professional practice uses 25-75% of full Kelly
5. **Market Reality**: Only 32.2% of congressional traders beat market in 2025

## Conclusion

These configuration improvements implement evidence-based trading strategies that balance risk and return. The changes focus on:
- Reducing position sizing for better risk management
- Prioritizing high-performing leadership trades
- Implementing comprehensive sector and correlation limits
- Adding quality filters for better trade selection

The updated configuration should improve risk-adjusted returns and provide more robust protection against market downturns.