---
name: tv-strategy-settings
description: "Open and modify TradingView strategy settings on the current chart page. Use when: user wants to change strategy parameters, adjust inputs like stop-loss/take-profit/period/amount, modify strategy properties like initial capital/commission/slippage, or tune any strategy setting on TradingView. Supports natural language (e.g. '把止损改成2%') and exact parameter names. NOT for: creating new strategies, writing Pine Script code, or chart drawing."
---

# TradingView Strategy Settings

Modify strategy parameters on an already-open TradingView chart page via browser automation.

## Prerequisites

- TradingView chart page must be open in the managed browser with a strategy loaded
- Use `BrowserTool` with action `tabs` to find the TradingView tab first

## Core Workflow

### 1. Locate the TradingView Tab

```
BrowserTool action=tabs
```

Find the tab with "TradingView" in the title. If multiple tabs match, pick the one with a chart URL (`tradingview.com/chart/`). Focus it:

```
BrowserTool action=focus tabId=<id>
```

### 2. Take Page Snapshot

```
BrowserTool action=snapshot format=ai
```

Identify the strategy panel at the bottom of the chart. Look for the strategy name in the "Strategy Tester" panel area.

### 3. Open Strategy Settings Dialog

The settings gear icon is located near the strategy name in the Strategy Tester panel header, or on the strategy overlay on the chart itself. Locate it via the snapshot and click:

```
BrowserTool action=click ref=<gear-icon-ref>
```

**Alternative approaches if gear icon is not visible:**

- Double-click the strategy name on the chart overlay
- Right-click the strategy name → select "Settings..."
- Look for a "⚙" or settings icon adjacent to the strategy title in the Strategy Tester tab header

Wait for the dialog to appear:

```
BrowserTool action=wait type=text text="Inputs" timeout=5000
```

### 4. Navigate to the Correct Tab

The settings dialog has tabs: **Inputs**, **Properties**, **Style**, **Visibility**.

- **Inputs** tab: User-defined parameters (`input.*()` in Pine Script) — stop-loss, take-profit, period lengths, thresholds, etc.
- **Properties** tab: Strategy engine settings — initial capital, currency, order size, pyramiding, commission, slippage, margin, date range.
- **Style** tab: Visual appearance.
- **Visibility** tab: Timeframe visibility.

**Parameter routing:**

| User says | Target tab |
|-----------|------------|
| 止损 / stop loss / take profit / 周期 / period / length / threshold / amount | Inputs |
| 初始资金 / initial capital / commission / 手续费 / slippage / 滑点 / pyramiding / 加仓 / order size / margin | Properties |
| 颜色 / color / line width / plot style | Style |

Click the appropriate tab:

```
BrowserTool action=click ref=<tab-ref>
```

### 5. Snapshot the Settings Panel

```
BrowserTool action=snapshot format=ai
```

This reveals all parameter names and their current values. The dialog content is organized by groups with input fields (number inputs, checkboxes, dropdowns, color pickers).

### 6. Locate the Target Parameter

**For exact parameter names:** Match directly against input labels in the snapshot.

**For natural language:** Map the user's description to the closest matching label. Common mappings:

| Natural language (zh/en) | Likely parameter labels |
|--------------------------|----------------------|
| 止损 / stop loss | Stop Loss, SL, Stop Loss % |
| 止盈 / take profit | Take Profit, TP, Take Profit % |
| 周期 / period / length | Length, Period, Lookback |
| 初始资金 / initial capital | Initial Capital |
| 手续费 / commission | Commission |
| 滑点 / slippage | Slippage |
| 加仓 / pyramiding | Pyramiding |
| 订单大小 / order size | Order Size |

If ambiguous, take a snapshot and present the available parameters to the user for confirmation before modifying.

### 7. Modify the Parameter Value

For number/text inputs — triple-click to select all, then type new value:

```
BrowserTool action=click ref=<input-ref> clickCount=3
BrowserTool action=type ref=<input-ref> text="<new-value>"
```

For checkboxes:

```
BrowserTool action=click ref=<checkbox-ref>
```

For dropdowns — click to open, then click the desired option:

```
BrowserTool action=click ref=<dropdown-ref>
BrowserTool action=snapshot format=ai
BrowserTool action=click ref=<option-ref>
```

### 8. Apply Changes

Click the "Ok" or "确定" button to apply and close the dialog:

```
BrowserTool action=click ref=<ok-button-ref>
```

Or click "Apply" / "应用" to apply without closing (useful for batch changes).

### 9. Verify

Take a snapshot or screenshot to confirm the strategy has recalculated with the new parameters:

```
BrowserTool action=screenshot
```

## Batch Modifications

When the user requests multiple parameter changes at once:

1. Open settings dialog once
2. Modify each parameter sequentially (re-snapshot between changes if the dialog layout shifts)
3. Click "Ok" once at the end

## Error Handling

- **Dialog not opening**: Try double-clicking the strategy name on chart, or use keyboard shortcut
- **Parameter not found**: Snapshot the full Inputs/Properties tabs and present available parameters to the user
- **Value rejected**: TradingView may enforce min/max ranges — report the constraint to the user
- **Page loading**: Use `wait type=networkidle` if the chart is still loading

## Language Notes

- TradingView UI language depends on user settings — parameter labels may be in English or Chinese
- Always match against the actual labels shown in the snapshot, not assumed names
- The dialog buttons may show as "Ok"/"Cancel" or "确定"/"取消"
