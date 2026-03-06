# NOFX Browser Automation Guide

## Prerequisites

- Browser profile `clawd` should be logged into nofxai.com
- Use `browser` tool with `profile: "clawd"`

## Page Navigation

| Page | URL | Purpose |
|------|-----|---------|
| Dashboard | /traders | Main dashboard, trader list |
| Data | /data | Real-time data terminal |
| Market | /market | Market charts |
| Config | /config | AI models & exchanges |
| Strategy | /strategy | Strategy studio |
| Leaderboard | /leaderboard | Competition ranking |
| Arena | /debate | AI debate sessions |
| Backtest | /backtest | Backtest lab |

## Common Actions

### List Traders

```javascript
// Navigate to dashboard
browser.navigate("https://nofxai.com/traders")
browser.snapshot()
// Parse trader cards from snapshot
```

### Start/Stop Trader

```javascript
// Find trader card by name
// Look for "Start" or "Stop" button ref
browser.act({kind: "click", ref: "startButtonRef"})
```

### Create New Trader

1. Navigate to /traders
2. Click "Create Trader" button
3. Fill in form:
   - Select AI Model (dropdown)
   - Select Exchange (dropdown)
   - Select Strategy (dropdown)
   - Enter name
4. Click Create

### View Dashboard

1. Navigate to /dashboard
2. Select trader from dropdown
3. Read equity, P/L, positions from snapshot

### Create Strategy

1. Navigate to /strategy
2. Click "New Strategy"
3. Fill in:
   - Strategy name
   - Description
   - Strategy type (AI Trading / Grid Trading)
   - Coin source configuration
   - Indicators
   - Risk control
   - Custom prompt
4. Click Save

### Export Strategy

1. Navigate to /strategy
2. Find strategy in list
3. Click Export button
4. Strategy JSON is downloaded

### Import Strategy

1. Navigate to /strategy
2. Click Import button
3. Paste or upload JSON
4. Click Import

### Create Debate

1. Navigate to /debate
2. Click "New Debate"
3. Select symbol
4. Configure AI models and roles
5. Start debate

### Run Backtest

1. Navigate to /backtest
2. Click "New Backtest"
3. Select AI model
4. Select strategy (optional)
5. Enter symbols
6. Set time range
7. Click Run

## Element Reference Patterns

### Navigation Buttons

```
button "Data" [ref=eXX]
button "Market" [ref=eXX]
button "Config" [ref=eXX]
button "Dashboard" [ref=eXX]
button "Strategy" [ref=eXX]
button "Leaderboard" [ref=eXX]
button "Arena" [ref=eXX]
button "Backtest" [ref=eXX]
```

### Trader Card Actions

```
button "View" [ref=eXX]
button "Edit" [ref=eXX]
button "Start" [ref=eXX]
button "Stop" [ref=eXX]
```

### Form Elements

```
textbox [ref=eXX]: Input field
combobox [ref=eXX]: Dropdown select
button [ref=eXX]: Action button
```

## Tips

1. Always use `snapshot()` after navigation to get current page state
2. Look for `[active]` attribute to identify selected items
3. Check for `[disabled]` before clicking buttons
4. Use `maxChars` parameter to limit snapshot size for large pages
5. Parse text content from snapshot to extract data
