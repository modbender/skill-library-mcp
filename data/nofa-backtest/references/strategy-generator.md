# NOFA Strategy Generator Skill

## Overview

This Skill guides the AI Agent to collaborate with users through natural dialogue, generating trading strategy tree JSON that fully conforms to the NOFA platform backtesting specification. The Agent will intelligently extract strategy information, detect missing fields, proactively fill in defaults, and output a `StrategyTreeJSON` format ready for direct backtesting use.

## WHEN TO USE

Activate this Skill immediately when the user's request contains any of the following keywords or intents:

- "generate trading strategy" / "create strategy" / "design strategy"
- "NOFA strategy" / "NOFA backtest"
- "strategy tree" / "StrategyTree" / "strategy JSON"
- "design a trading system"
- "I want to make a trade with XX conditions"
- Any request involving technical indicator condition evaluation + trading actions

**Behavior after activation**: Switch to strategy generation mode, following the dialog flow and output specification defined in this Skill.

---

## Core Workflow

### Phase 1: Information Gathering (Free-form Dialog)

1. **Listen to user description**: Users may describe strategies in natural language, for example:
   - "When BTC's RSI is above 70, go short with 3x leverage"
   - "Go long ETH when EMA10 crosses above EMA60, 30% position, 5% stop loss"
   - "Buy BTC on full moon, sell on new moon"

2. **Extract known information**: Identify from the conversation:
   - Symbol: BTC/USDT, ETH/USDT, etc.
   - Indicator: RSI, EMA, MA, MACD, etc.
   - Conditions: greater than / less than / equal to a value or another indicator
   - Direction: Long (LONG) / Short (SHORT)
   - Allocation (allocate): percentage or fixed amount
   - Leverage: multiplier
   - Risk management (stop loss / take profit): percentage or fixed value

3. **Build preliminary JSON draft**: Maintain a partially completed strategy tree structure in memory.

### Phase 2: Field Completion (Interactive Completion)

4. **Detect missing fields**: Compare against the full Schema and list all missing required fields.

5. **Ask in batches**: Group missing fields by logical categories, asking 3-5 related fields at a time:
   - **Group 1 - Basic Info**: Strategy name, primary symbol
   - **Group 2 - Condition Config**: Indicator period, comparison value, logical operator
   - **Group 3 - Trade Action**: Position mode, leverage multiplier
   - **Group 4 - Risk Management**: Specific stop loss and take profit values

6. **Smart defaults**: If the user says "not sure" / "whatever" / "you decide", apply conservative default values (see DEFAULT VALUES section below).

7. **Real-time validation**: Validate the legality of each field as soon as it is collected (value ranges, enum values, etc.).

### Phase 3: Output Generation (Final Output)

8. **Generate complete JSON**: Ensure all required fields are populated and all `type` fields are correct.

9. **Dual-format output**:
   - **Format A**: Complete `StrategyTreeJSON` (can be directly copied for backtesting)
   - **Format B**: Human-readable strategy explanation (English description of logic + risk parameter summary)

10. **Validation confirmation**: Inform the user that the strategy has passed all validation rules and can be directly submitted to the NOFA platform for backtesting.

### Phase 4: API Call (Execute via NOFA API)

11. **Call backtest API**: Wrap the generated JSON into a BacktestRequest and call `POST ${BASE_URL}/backtest/run`:
    ```
    {
      "strategy": { ... },  // StrategyTree JSON generated in Phase 3
      "capital": 10000,
      "start_time": "2025-12-01T00:00:00Z",
      "end_time": "2025-12-31T00:00:00Z",
      "timeframe": "1h",
      "slippage": 0.001,
      "transaction_fee": 0.0005
    }
    ```

12. **Interpret results**: Translate the backtest KPIs and trade records into user-friendly analysis.

> **Note**: For API call details (authentication, endpoints, request parameters), refer to `SKILL.md`. This file focuses on strategy generation logic.

---

## STRATEGY TREE SCHEMA

### Complete Type System

```typescript
// ============ Enum Types ============

/** Symbol type */
type Symbol = 'BTC/USDT' | 'ETH/USDT' | 'SOL/USDT' | 'DOGE/USDT' | 'BNB/USDT' | string;

/** Trade direction */
type OrderDirection = 'LONG' | 'SHORT';

/** Value mode */
type ValueMode = 'PCT' | 'FIXED';

/** Condition comparison operator */
type CompareOperator = 'Greater Than' | 'Less Than' | 'Equal';

/** Indicator type */
type IndicatorType =
  | 'Current Price'      // Current price
  | 'Cumulative Return'  // Cumulative return
  | 'EMA'                // Exponential Moving Average
  | 'MA'                 // Simple Moving Average (price)
  | 'Moving Average of Return'  // Moving Average of Return
  | 'Max Drawdown'       // Maximum drawdown
  | 'RSI'                // Relative Strength Index
  | 'Bollinger Bands'    // Bollinger Bands
  | 'ADX'                // Average Directional Index
  | 'SMMA'               // Smoothed Moving Average
  | 'MACD'               // Moving Average Convergence Divergence
  | 'Moon Phases';       // Moon Phases

/** Condition type */
type ConditionType = 'Compare' | 'Cross';

/** Condition logical operator */
type LogicalOperator = 'AND' | 'OR';

/** Position allocation mode */
type AllocateMode = 'WEIGHT' | 'MARGIN';

// ============ Node Types (all nodes must have a type field) ============

/** Root node - Strategy tree */
interface StrategyTree {
  type: 'STRATEGY_TREE';
  name: string;
  riskManagement: RiskManagement;
  mainDecision: IfElseBlock | IfElseBlock[];
  description?: string;
}

/** Risk management configuration */
interface RiskManagement {
  type: 'RISK_MANAGEMENT';
  name: string;
  scope: 'Per Position';
  stopLoss: {
    mode: ValueMode;
    value: number;
  };
  takeProfit: {
    mode: ValueMode;
    value: number;
  };
}

/** IF/ELSE condition block */
interface IfElseBlock {
  type: 'IF_ELSE_BLOCK';
  name: string;
  conditionType: ConditionType;
  conditions: ConditionItem[];
  logicalOperator?: LogicalOperator;
  thenAction: (ActionBlock | IfElseBlock)[] | 'NO ACTION';
  elseAction: (ActionBlock | IfElseBlock)[] | 'NO ACTION';
}

/** Single condition item */
interface ConditionItem {
  type: 'CONDITION_ITEM';
  indicator: IndicatorType;
  period: number;
  symbol: Symbol;
  operator: CompareOperator;
  value: number | ConditionValueIndicator;
}

/** Condition comparison value (indicator type) */
interface ConditionValueIndicator {
  type: 'CONDITION_VALUE_INDICATOR';
  indicator: IndicatorType;
  period: number;
  symbol: Symbol;
}

/** Trade action block */
interface ActionBlock {
  type: 'ACTION_BLOCK';
  name: string;
  symbol: Symbol;
  direction: OrderDirection;
  allocate: AllocateConfig;
  leverage: number;
  riskManagement?: Partial<RiskManagement>;
}

/** Position allocation configuration */
interface AllocateConfig {
  type: 'ALLOCATE_CONFIG';
  mode: AllocateMode;
  value: number;
}
```

---

## VALIDATION CHECKLIST

Before generating the final JSON, all of the following rules must be validated:

### General Rules
- [ ] 1. All nodes must contain the correct `type` field and it cannot be omitted
- [ ] 2. All `name` fields must be non-empty strings, 1-100 characters in length

### StrategyTree Root Node
- [ ] 3. `type` is fixed as `'STRATEGY_TREE'`
- [ ] 4. `name` is non-empty, 1-100 characters in length
- [ ] 5. `riskManagement` is a valid RISK_MANAGEMENT node
- [ ] 6. `mainDecision` is a single or array of IF_ELSE_BLOCK nodes (array cannot be empty)

### RiskManagement Node
- [ ] 7. `type` is fixed as `'RISK_MANAGEMENT'`
- [ ] 8. `name` is non-empty, 1-100 characters in length
- [ ] 9. `scope` is fixed as `'Per Position'`
- [ ] 10. `stopLoss.mode` is `'PCT'` or `'FIXED'`
- [ ] 11. `stopLoss.value`: In PCT mode 0 < value ≤ 1; in FIXED mode value > 0
- [ ] 12. `takeProfit.mode` is `'PCT'` or `'FIXED'`
- [ ] 13. `takeProfit.value`: In PCT mode 0 < value ≤ 1; in FIXED mode value > 0

### IfElseBlock Node
- [ ] 14. `type` is fixed as `'IF_ELSE_BLOCK'`
- [ ] 15. `name` is non-empty, 1-100 characters in length
- [ ] 16. `conditionType` is `'Compare'` or `'Cross'`
- [ ] 17. `conditions` array length >= 1, each element is a valid CONDITION_ITEM
- [ ] 18. `logicalOperator` (optional) is `'AND'` or `'OR'`, defaults to `'AND'`
- [ ] 19. `logicalOperator` must be uniform (a set of conditions can only use all AND or all OR, no mixing)
- [ ] 20. `thenAction` is `'NO ACTION'` or a non-empty array (elements are ACTION_BLOCK or IF_ELSE_BLOCK)
- [ ] 21. `elseAction` is `'NO ACTION'` or a non-empty array (elements are ACTION_BLOCK or IF_ELSE_BLOCK)

### ConditionItem Node
- [ ] 22. `type` is fixed as `'CONDITION_ITEM'`
- [ ] 23. `indicator` is one of the predefined IndicatorType values
- [ ] 24. `period` range: 1 ≤ period ≤ 1000
- [ ] 25. `symbol` is a predefined enum value or matches the `XXX/USDT` format
- [ ] 26. `operator` is one of `'Greater Than'`, `'Less Than'`, or `'Equal'`
- [ ] 27. `value` is a number or a CONDITION_VALUE_INDICATOR object
- [ ] 28. If `value` is an object, its `type` must be `'CONDITION_VALUE_INDICATOR'`

### ActionBlock Node
- [ ] 29. `type` is fixed as `'ACTION_BLOCK'`
- [ ] 30. `name` is non-empty, 1-100 characters in length
- [ ] 31. `symbol` is a predefined enum value or matches the `XXX/USDT` format
- [ ] 32. `direction` is `'LONG'` or `'SHORT'`
- [ ] 33. `allocate` is a valid ALLOCATE_CONFIG node
- [ ] 34. `leverage` range: 1 ≤ leverage ≤ 100
- [ ] 35. `riskManagement` (optional) if present, must conform to Partial<RiskManagement> constraints

### AllocateConfig Node
- [ ] 36. `type` is fixed as `'ALLOCATE_CONFIG'`
- [ ] 37. `mode` is `'WEIGHT'` or `'MARGIN'`
- [ ] 38. `value`: In WEIGHT mode 0 < value ≤ 100; in MARGIN mode value > 0

---

## DEFAULT VALUES (Conservative)

When the user has not provided the following fields and indicates "not sure" / "whatever", use these default values:

```javascript
{
  // Strategy basics
  strategyName: "Custom User Strategy",

  // Risk management (global)
  globalRiskManagement: {
    name: "Global Risk Management",
    scope: "Per Position",
    stopLoss: {
      mode: "PCT",
      value: 0.05        // 5% stop loss (conservative)
    },
    takeProfit: {
      mode: "PCT",
      value: 0.10        // 10% take profit (conservative)
    }
  },

  // Trade action defaults
  action: {
    leverage: 2,         // 2x leverage (low risk)
    allocate: {
      mode: "WEIGHT",
      value: 20          // 20% position size (small position)
    }
  },

  // Condition defaults
  condition: {
    conditionType: "Compare",
    logicalOperator: "AND",
    period: {
      RSI: 14,           // RSI standard period
      EMA: 20,           // EMA common period
      MA: 20,            // MA common period
      MACD: 26,          // MACD standard period
      ADX: 14,           // ADX standard period
      "Bollinger Bands": 20
    }
  },

  // Symbol default
  symbol: "BTC/USDT"     // Most commonly used symbol
}
```

**Usage scenario notes**:
- **2x leverage**: Reduces liquidation risk, suitable for beginners or conservative strategies
- **20% position**: Avoids excessive risk on a single trade
- **5% stop loss / 10% take profit**: 1:2 risk-reward ratio, follows conservative principles
- **Period values**: Uses industry-standard technical analysis periods

---

## OUTPUT TEMPLATE

### Standard Output Format

```markdown
## Strategy Generation Complete ✅

### 📊 Strategy Overview

**Strategy Name**: [Strategy name]
**Strategy Type**: [Simple condition / Multi-condition combo / Nested decision / ...]
**Primary Symbol**: [BTC/USDT, ETH/USDT, etc.]

### 🎯 Strategy Logic (Human-Readable)

**Condition Evaluation**:
- If: [Describe condition in English, e.g. "BTC's 14-period RSI is greater than 70"]
  - Then execute: [Short BTC, 30% position, 3x leverage]
- Else: [No action / or other action]

**Risk Management**:
- Global stop loss: [5% / $500 fixed value]
- Global take profit: [10% / $1000 fixed value]
- Local override: [If a specific ActionBlock has its own stop loss/take profit, describe here]

### ⚠️ Risk Warning

- Leverage: [Summarize leverage across all actions]
- Maximum position usage: [Calculate sum of all WEIGHT values or total MARGIN]
- Notes: [Provide advice based on strategy characteristics, e.g. "This strategy may trade frequently in ranging markets"]

---

### 📄 Complete JSON (Ready for NOFA Backtesting)

```json
[Output the complete StrategyTreeJSON here, ensure proper formatting, include all type fields]
```

---

### ✅ Validation Status

- [x] All required fields are populated
- [x] All type fields are correct
- [x] Value ranges conform to specification (leverage 1-100, period 1-1000, etc.)
- [x] Enum values are valid (direction, operator, indicator, etc.)
- [x] Ready for direct submission to NOFA platform for backtesting

**Next step**: Copy the JSON above to NOFA Strategy Hub for backtesting.
```

---

## DIALOG EXAMPLES

### Example 1: Simple RSI Strategy

**User**: "I want to create an RSI strategy that shorts BTC when RSI is above 70"

**Agent**:
```
Sure, I'll help you generate this strategy. Let me confirm a few details:

Identified information:
- Condition: RSI > 70
- Symbol: BTC/USDT
- Direction: Short (SHORT)

Information needed:
1. What period for RSI? (14-period is commonly used)
2. Position size for shorting? (10-30% recommended)
3. How much leverage? (1-3x recommended)
4. Stop loss and take profit settings? (3-5% stop loss, 6-10% take profit recommended)
5. What to do when RSI condition is not met? (No action / go long?)
```

**User**: "Use 14-period RSI, 30% position, 3x leverage, 5% stop loss 10% take profit, do nothing if condition is not met"

**Agent**:
```
Perfect! Strategy information is complete, generating now...

## Strategy Generation Complete ✅

### 📊 Strategy Overview
**Strategy Name**: RSI Overbought Short Strategy
**Strategy Type**: Simple condition evaluation
**Primary Symbol**: BTC/USDT

### 🎯 Strategy Logic
- If: BTC's 14-period RSI is greater than 70
  - Then execute: Short BTC, 30% position, 3x leverage
- Else: No action

### ⚠️ Risk Warning
- Leverage: 3x
- Maximum position usage: 30%
- Note: RSI strategies may produce false signals during strong trends

---

### 📄 Complete JSON

{
  "type": "STRATEGY_TREE",
  "name": "RSI Overbought Short Strategy",
  "riskManagement": {
    "type": "RISK_MANAGEMENT",
    "name": "Global Risk Management",
    "scope": "Per Position",
    "stopLoss": {
      "mode": "PCT",
      "value": 0.05
    },
    "takeProfit": {
      "mode": "PCT",
      "value": 0.10
    }
  },
  "mainDecision": {
    "type": "IF_ELSE_BLOCK",
    "name": "RSI Overbought Check",
    "conditionType": "Compare",
    "conditions": [
      {
        "type": "CONDITION_ITEM",
        "indicator": "RSI",
        "period": 14,
        "symbol": "BTC/USDT",
        "operator": "Greater Than",
        "value": 70
      }
    ],
    "thenAction": [
      {
        "type": "ACTION_BLOCK",
        "name": "Short BTC 30%",
        "symbol": "BTC/USDT",
        "direction": "SHORT",
        "allocate": {
          "type": "ALLOCATE_CONFIG",
          "mode": "WEIGHT",
          "value": 30
        },
        "leverage": 3
      }
    ],
    "elseAction": "NO ACTION"
  }
}

✅ Validation passed, ready for backtesting!
```

---

### Example 2: EMA Crossover Strategy (Medium Complexity)

**User**: "Go long ETH when EMA10 crosses above EMA60, go short when it crosses below, use 20% position for each, 2x leverage"

**Agent**:
```
This is a dual EMA crossover strategy. I need to confirm a few things:

Identified:
- Condition: EMA10 and EMA60 crossover relationship
- Symbol: ETH/USDT
- Position: 20%
- Leverage: 2x

Questions:
1. Strategy name? (e.g. "ETH Dual EMA Strategy")
2. Stop loss and take profit settings? (3-5% stop loss, 8-12% take profit recommended)
3. What to do when EMA10 = EMA60? (Usually no action)
```

**User**: "Call it ETH Dual EMA, 3% stop loss 8% take profit, no action when equal"

**Agent**:
```
## Strategy Generation Complete ✅

### 📊 Strategy Overview
**Strategy Name**: ETH Dual EMA Strategy
**Strategy Type**: EMA crossover evaluation
**Primary Symbol**: ETH/USDT

### 🎯 Strategy Logic
- If: ETH's 10-period EMA is greater than 60-period EMA
  - Then execute: Long ETH, 20% position, 2x leverage
- Else if: ETH's 10-period EMA is less than 60-period EMA
  - Then execute: Short ETH, 20% position, 2x leverage
- Else: No action

### ⚠️ Risk Warning
- Leverage: 2x (low risk)
- Maximum position usage: 20% (single side)
- Note: EMA crossover strategies work well in trending markets but may cause frequent open/close in ranging markets

---

### 📄 Complete JSON

{
  "type": "STRATEGY_TREE",
  "name": "ETH Dual EMA Strategy",
  "riskManagement": {
    "type": "RISK_MANAGEMENT",
    "name": "Global Risk Management",
    "scope": "Per Position",
    "stopLoss": {
      "mode": "PCT",
      "value": 0.03
    },
    "takeProfit": {
      "mode": "PCT",
      "value": 0.08
    }
  },
  "mainDecision": {
    "type": "IF_ELSE_BLOCK",
    "name": "EMA10 vs EMA60 Cross",
    "conditionType": "Cross",
    "conditions": [
      {
        "type": "CONDITION_ITEM",
        "indicator": "EMA",
        "period": 10,
        "symbol": "ETH/USDT",
        "operator": "Greater Than",
        "value": {
          "type": "CONDITION_VALUE_INDICATOR",
          "indicator": "EMA",
          "period": 60,
          "symbol": "ETH/USDT"
        }
      }
    ],
    "thenAction": [
      {
        "type": "ACTION_BLOCK",
        "name": "Long ETH 20%",
        "symbol": "ETH/USDT",
        "direction": "LONG",
        "allocate": {
          "type": "ALLOCATE_CONFIG",
          "mode": "WEIGHT",
          "value": 20
        },
        "leverage": 2
      }
    ],
    "elseAction": [
      {
        "type": "IF_ELSE_BLOCK",
        "name": "EMA10 Below EMA60",
        "conditionType": "Compare",
        "conditions": [
          {
            "type": "CONDITION_ITEM",
            "indicator": "EMA",
            "period": 10,
            "symbol": "ETH/USDT",
            "operator": "Less Than",
            "value": {
              "type": "CONDITION_VALUE_INDICATOR",
              "indicator": "EMA",
              "period": 60,
              "symbol": "ETH/USDT"
            }
          }
        ],
        "thenAction": [
          {
            "type": "ACTION_BLOCK",
            "name": "Short ETH 20%",
            "symbol": "ETH/USDT",
            "direction": "SHORT",
            "allocate": {
              "type": "ALLOCATE_CONFIG",
              "mode": "WEIGHT",
              "value": 20
            },
            "leverage": 2
          }
        ],
        "elseAction": "NO ACTION"
      }
    ]
  }
}

✅ Validation passed, ready for backtesting!
```

---

### Example 3: Multi-Condition Combo Strategy (High Complexity)

**User**: "When BTC's RSI > 70 and MACD < 0, short BTC (30% position, 5x leverage, 2% stop loss, 4% take profit), and simultaneously short SOL (20% position, 3x leverage, use default stop loss/take profit)"

**Agent**:
```
This is a complex strategy with multi-condition AND combination + multiple actions. Let me confirm:

Identified:
- Condition 1: RSI > 70
- Condition 2: MACD < 0
- Logic: AND (both must be met to execute)
- Action 1: Short BTC, 30%, 5x leverage, independent 2% stop loss 4% take profit
- Action 2: Short SOL, 20%, 3x leverage, uses global stop loss/take profit

Need to confirm:
1. RSI and MACD periods? (RSI typically 14, MACD typically 26)
2. Global stop loss/take profit settings? (SOL will use these)
3. What to do when conditions are not met?
4. Strategy name?
```

**User**: "RSI use 14, MACD use 26, global 5% stop loss 10% take profit, do nothing if not met, call the strategy 'BTC Bearish Divergence Short'"

**Agent**:
```
## Strategy Generation Complete ✅

### 📊 Strategy Overview
**Strategy Name**: BTC Bearish Divergence Short
**Strategy Type**: Multi-condition combo + multi-symbol
**Primary Symbol**: BTC/USDT, SOL/USDT

### 🎯 Strategy Logic
- If: (BTC's 14-period RSI > 70) AND (BTC's 26-period MACD < 0)
  - Then execute:
    1. Short BTC, 30% position, 5x leverage, independent 2% stop loss 4% take profit
    2. Short SOL, 20% position, 3x leverage, uses global 5% stop loss 10% take profit
- Else: No action

### ⚠️ Risk Warning
- Maximum leverage: 5x (BTC action)
- Maximum position usage: 50% (30% + 20%)
- Risk management: BTC uses tighter stop loss (2%), SOL uses wider stop loss (5%)
- Note: High leverage multi-symbol strategies carry significant risk; recommended for use only with clear trend reversal signals

---

### 📄 Complete JSON

{
  "type": "STRATEGY_TREE",
  "name": "BTC Bearish Divergence Short",
  "riskManagement": {
    "type": "RISK_MANAGEMENT",
    "name": "Global Risk Management",
    "scope": "Per Position",
    "stopLoss": {
      "mode": "PCT",
      "value": 0.05
    },
    "takeProfit": {
      "mode": "PCT",
      "value": 0.10
    }
  },
  "mainDecision": {
    "type": "IF_ELSE_BLOCK",
    "name": "RSI Overbought AND MACD Bearish",
    "conditionType": "Compare",
    "logicalOperator": "AND",
    "conditions": [
      {
        "type": "CONDITION_ITEM",
        "indicator": "RSI",
        "period": 14,
        "symbol": "BTC/USDT",
        "operator": "Greater Than",
        "value": 70
      },
      {
        "type": "CONDITION_ITEM",
        "indicator": "MACD",
        "period": 26,
        "symbol": "BTC/USDT",
        "operator": "Less Than",
        "value": 0
      }
    ],
    "thenAction": [
      {
        "type": "ACTION_BLOCK",
        "name": "Short BTC 30% (Tight Risk)",
        "symbol": "BTC/USDT",
        "direction": "SHORT",
        "allocate": {
          "type": "ALLOCATE_CONFIG",
          "mode": "WEIGHT",
          "value": 30
        },
        "leverage": 5,
        "riskManagement": {
          "type": "RISK_MANAGEMENT",
          "stopLoss": {
            "mode": "PCT",
            "value": 0.02
          },
          "takeProfit": {
            "mode": "PCT",
            "value": 0.04
          }
        }
      },
      {
        "type": "ACTION_BLOCK",
        "name": "Short SOL 20%",
        "symbol": "SOL/USDT",
        "direction": "SHORT",
        "allocate": {
          "type": "ALLOCATE_CONFIG",
          "mode": "WEIGHT",
          "value": 20
        },
        "leverage": 3
      }
    ],
    "elseAction": "NO ACTION"
  }
}

✅ Validation passed, ready for backtesting!
```

---

## CRITICAL REMINDERS

### Rules That Must Be Followed

1. **The type field must never be omitted**: Every object node (StrategyTree, RiskManagement, IfElseBlock, ConditionItem, ActionBlock, AllocateConfig, ConditionValueIndicator) must have the correct `type` field.

2. **Strict value range validation**:
   - leverage: 1-100
   - period: 1-1000
   - PCT mode value: 0-1 (represents percentage, 0.05 = 5%)
   - WEIGHT mode value: 0-100 (represents percentage, 30 = 30%)

3. **Enum values must match exactly** (case-sensitive):
   - `"Greater Than"` ✅  `"greater than"` ❌
   - `"LONG"` ✅  `"long"` ❌
   - `"Per Position"` ✅  `"per position"` ❌

4. **logicalOperator rule**: Multiple conditions within a single IF_ELSE_BLOCK can only uniformly use AND or OR; mixing is not allowed.

5. **Action array rule**: `thenAction` and `elseAction` only accept:
   - The string `"NO ACTION"`
   - A non-empty array (elements are ActionBlock or IfElseBlock objects)
   - An empty array `[]` is not allowed

6. **Risk management inheritance**: An ActionBlock may omit `riskManagement`, in which case it inherits the global settings; if set, it overrides the global settings.

### Output Quality Assurance

- **JSON formatting**: Use 2-space indentation to ensure readability
- **Field order**: Arrange fields in the order defined by the Schema
- **Naming convention**: Use meaningful, descriptive names for name fields
- **English explanation**: The human-readable section should use English, clearly describing strategy logic
- **Double-check**: Run the VALIDATION CHECKLIST again before outputting

---

## TROUBLESHOOTING

### Common Errors and Solutions

**Error 1**: User provides leverage of 150x
- **Handling**: Prompt "Leverage must be between 1-100x. We recommend using 10x or less to reduce risk. Would you accept adjusting to 100x?"

**Error 2**: User says "RSI greater than oversold"
- **Handling**: "Do you mean RSI greater than 30 (oversold level)? Or RSI greater than 70 (overbought level)? Typically, oversold is 30 and overbought is 70."

**Error 3**: User provides symbol as "BTC" instead of "BTC/USDT"
- **Handling**: Automatically complete to "BTC/USDT" and inform the user.

**Error 4**: User requests both OR and AND logic simultaneously
- **Handling**: "A condition group can only use a single logic type (AND or OR). Should all your conditions be met (AND) or just any one of them (OR)?"

**Error 5**: Stop loss is greater than take profit
- **Handling**: "Detected that stop loss (X%) is greater than take profit (Y%). This does not follow standard risk management principles. Would you like to adjust so that stop loss < take profit?"

---

## SUCCESS METRICS

Signs of successful strategy generation:

- ✅ User can describe the strategy in natural language, and the Agent understands accurately
- ✅ All 37 validation rules pass
- ✅ JSON can be directly copied and pasted into the NOFA platform
- ✅ User understands the strategy logic (through the English explanation)
- ✅ Risk parameters are clear and reasonable
- ✅ The entire conversation flows smoothly, no more than 10 rounds of interaction

---

**Skill Version**: 1.0
**Last Updated**: 2026-02
**Maintained by**: NOFA Strategy Hub Team
