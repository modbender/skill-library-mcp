# HTML Templates Reference

## Complete CSS Template

```css
/* IBM Plex Mono Font Import */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');

/* CSS Variables */
:root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-tertiary: #21262d;
    --text-primary: #c9d1d9;
    --text-secondary: #8b949e;
    --text-muted: #6e7681;
    --accent-green: #3fb950;
    --accent-red: #f85149;
    --accent-blue: #58a6ff;
    --accent-orange: #d29922;
    --accent-purple: #a371f7;
    --border-color: #30363d;
}

/* Reset */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Body */
body {
    font-family: 'IBM Plex Mono', monospace;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    padding: 24px;
}

/* Container */
.container {
    max-width: 1200px;
    margin: 0 auto;
}
```

## Header Section

```html
<div class='header'>
    <h1>{{strategy_name}}</h1>
    <div class='subtitle'>
        Strategy Comparison Tearsheet | {{start_date}} to {{end_date}}
    </div>
    <div>
        <span class='regime-badge regime-{{regime_lower}}'>{{regime}}</span>
        <!-- Nautilus Verified Badge (conditional) -->
        <span class='verified-badge'>
            <svg width='12' height='12' viewBox='0 0 24 24' fill='currentColor'>
                <path d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z'/>
            </svg>
            Nautilus Verified
        </span>
    </div>
    <div class='subtitle' style='margin-top: 8px;'>
        Generated: {{timestamp}} | Mode: {{mode}} | Initial Capital: {{capital}}
    </div>
</div>
```

### Header CSS

```css
.header {
    text-align: center;
    padding: 32px 0;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 32px;
}

.header h1 {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
}

.header .subtitle {
    color: var(--text-secondary);
    font-size: 14px;
}

/* Regime Badges */
.regime-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    margin-top: 12px;
}

.regime-bull { background: rgba(63, 185, 80, 0.2); color: var(--accent-green); }
.regime-bear { background: rgba(248, 81, 73, 0.2); color: var(--accent-red); }
.regime-sideways { background: rgba(210, 153, 34, 0.2); color: var(--accent-orange); }
.regime-unknown { background: rgba(139, 148, 158, 0.2); color: var(--text-secondary); }

/* Verified Badge */
.verified-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    background: rgba(88, 166, 255, 0.1);
    border: 1px solid var(--accent-blue);
    border-radius: 12px;
    font-size: 11px;
    color: var(--accent-blue);
    margin-top: 12px;
    margin-left: 8px;
}
```

## Two-Column Metrics Grid

```html
<div class='metrics-grid'>
    <!-- Left Column: Trade Statistics -->
    <div class='card'>
        <div class='card-title'>Trade Statistics</div>
        <div class='metric-row'>
            <span class='metric-label'>Total Trades</span>
            <span class='metric-value value-neutral'>{{total_trades}}</span>
        </div>
        <div class='metric-row'>
            <span class='metric-label'>Win Rate</span>
            <span class='metric-value {{win_rate_class}}'>{{win_rate}}%</span>
        </div>
        <!-- ... more metrics ... -->
    </div>

    <!-- Right Column: Performance Summary -->
    <div class='card'>
        <div class='card-title'>Performance by Leverage</div>
        <div class='metric-row'>
            <span class='metric-label'>Fixed 1x Return</span>
            <span class='metric-value {{return_class}}'>{{fixed_1x_return}}%</span>
        </div>
        <!-- ... more metrics ... -->
    </div>
</div>
```

### Grid CSS

```css
.metrics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin-bottom: 32px;
}

.card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 20px;
}

.card-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-color);
}

.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid var(--bg-tertiary);
}

.metric-row:last-child {
    border-bottom: none;
}

.metric-label {
    color: var(--text-secondary);
    font-size: 12px;
    white-space: nowrap;
}

.metric-value {
    font-weight: 600;
    font-size: 13px;
    text-align: right;
    min-width: 80px;
}

/* Value Colors */
.value-positive { color: var(--accent-green); }
.value-negative { color: var(--accent-red); }
.value-neutral { color: var(--text-primary); }
.value-warning { color: var(--accent-orange); }
```

## Scenario Comparison Table

```html
<h2 class='section-title'>Leverage Scenario Comparison</h2>
<div class='card'>
    <table class='scenario-table'>
        <thead>
            <tr>
                <th>Scenario</th>
                <th>Leverage</th>
                <th>Return</th>
                <th>Final Equity</th>
                <th>Max DD</th>
                <th>Sharpe</th>
                <th>Sortino</th>
                <th>Calmar</th>
                <th>CAGR</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class='scenario-name'>Buy & Hold</td>
                <td>1x fixed</td>
                <td class='value-positive'>+45.2%</td>
                <td>$14,520</td>
                <td class='value-negative'>-12.5%</td>
                <td class='value-positive'>2.45</td>
                <td>3.12</td>
                <td>3.62</td>
                <td>42.1%</td>
            </tr>
            <!-- ... more rows ... -->
        </tbody>
    </table>
</div>
```

### Table CSS

```css
.section-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 32px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-color);
}

.scenario-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 16px;
    font-size: 12px;
}

.scenario-table th,
.scenario-table td {
    padding: 10px 6px;
    text-align: right;
    border-bottom: 1px solid var(--border-color);
    white-space: nowrap;
}

.scenario-table th {
    color: var(--text-secondary);
    font-weight: 500;
    text-transform: uppercase;
    font-size: 10px;
    letter-spacing: 0.5px;
}

.scenario-table th:first-child,
.scenario-table td:first-child {
    text-align: left;
}

.scenario-table tr:hover {
    background: var(--bg-tertiary);
}

.scenario-name {
    font-weight: 600;
}
```

## MAE Analysis Section

```html
<h2 class='section-title'>MAE Percentile Analysis</h2>
<div class='card'>
    <div class='card-title'>Maximum Adverse Excursion Distribution</div>

    <!-- MAE Stats Grid -->
    <div class='mae-stats-grid'>
        <div class='mae-stat'>
            <span class='mae-label'>p50 (Median)</span>
            <span class='mae-value'>1.25%</span>
        </div>
        <div class='mae-stat'>
            <span class='mae-label'>p75</span>
            <span class='mae-value'>2.10%</span>
        </div>
        <div class='mae-stat'>
            <span class='mae-label'>p90</span>
            <span class='mae-value'>3.45%</span>
        </div>
        <div class='mae-stat highlight'>
            <span class='mae-label'>p95</span>
            <span class='mae-value'>4.80%</span>
        </div>
        <div class='mae-stat'>
            <span class='mae-label'>p99</span>
            <span class='mae-value'>7.25%</span>
        </div>
        <div class='mae-stat warning'>
            <span class='mae-label'>Max</span>
            <span class='mae-value'>9.85%</span>
        </div>
    </div>

    <!-- Leverage Recommendations -->
    <div class='leverage-recommendations'>
        <div class='card-title'>Recommended Leverage (Based on p95 MAE)</div>
        <table class='leverage-rec-table'>
            <thead>
                <tr>
                    <th>Buffer</th>
                    <th>Max Leverage</th>
                    <th>Effective Threshold</th>
                    <th>Safety Margin</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>10%</td>
                    <td class='value-positive'>18.75x</td>
                    <td>5.33%</td>
                    <td>0.53%</td>
                </tr>
                <tr>
                    <td>20%</td>
                    <td class='value-positive'>16.67x</td>
                    <td>6.00%</td>
                    <td>1.20%</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
```

### MAE Section CSS

```css
.mae-stats-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 12px;
    margin-bottom: 24px;
}

.mae-stat {
    background: var(--bg-tertiary);
    padding: 12px;
    border-radius: 6px;
    text-align: center;
}

.mae-stat.highlight {
    border: 1px solid var(--accent-blue);
    background: rgba(88, 166, 255, 0.1);
}

.mae-stat.warning {
    border: 1px solid var(--accent-orange);
    background: rgba(210, 153, 34, 0.1);
}

.mae-label {
    display: block;
    font-size: 10px;
    color: var(--text-secondary);
    text-transform: uppercase;
    margin-bottom: 4px;
}

.mae-value {
    display: block;
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
}

.leverage-recommendations {
    margin-top: 16px;
}

.leverage-rec-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}

.leverage-rec-table th,
.leverage-rec-table td {
    padding: 10px 12px;
    text-align: center;
    border-bottom: 1px solid var(--border-color);
}

.leverage-rec-table th {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    font-weight: 500;
    text-transform: uppercase;
    font-size: 10px;
}
```

## Monthly Heatmap

```html
<h2 class='section-title'>Monthly Returns Heatmap</h2>
<div class='card'>
    <div class='heatmap-container'>
        <div class='heatmap'>
            <!-- Header Row -->
            <div class='heatmap-cell heatmap-header'></div>
            <div class='heatmap-cell heatmap-header'>Jan</div>
            <div class='heatmap-cell heatmap-header'>Feb</div>
            <!-- ... Dec ... -->

            <!-- Data Rows -->
            <div class='heatmap-cell heatmap-year'>2024</div>
            <div class='heatmap-cell heat-positive'>+5.2%</div>
            <div class='heatmap-cell heat-strong-positive'>+12.3%</div>
            <div class='heatmap-cell heat-negative'>-3.1%</div>
            <!-- ... more cells ... -->
        </div>
    </div>
</div>
```

### Heatmap CSS

```css
.heatmap-container {
    overflow-x: auto;
}

.heatmap {
    display: grid;
    grid-template-columns: auto repeat(12, 1fr);
    gap: 2px;
    font-size: 11px;
}

.heatmap-cell {
    padding: 8px 4px;
    text-align: center;
    border-radius: 4px;
    min-width: 50px;
}

.heatmap-header {
    color: var(--text-secondary);
    font-weight: 500;
}

.heatmap-year {
    color: var(--text-secondary);
    font-weight: 600;
    padding-right: 8px;
}

/* Heat Colors */
.heat-strong-positive { background: rgba(63, 185, 80, 0.4); color: var(--accent-green); }
.heat-positive { background: rgba(63, 185, 80, 0.2); color: var(--accent-green); }
.heat-neutral { background: var(--bg-tertiary); color: var(--text-secondary); }
.heat-negative { background: rgba(248, 81, 73, 0.2); color: var(--accent-red); }
.heat-strong-negative { background: rgba(248, 81, 73, 0.4); color: var(--accent-red); }
```

## Copyable Config Box

```html
<h2 class='section-title'>Strategy Configuration</h2>
<div class='card'>
    <div class='card-title'>Python Configuration (Click to Copy)</div>
    <div class='config-box' onclick='copyConfig(this)'>
        <pre><code># Strategy Configuration
STRATEGY_CONFIG = {
    'slow_tf': '2h',
    'fast_tf': '30m',
    'slow_fast_ema': 17,
    'slow_slow_ema': 34,
    'fast_fast_ema': 4,
    'fast_slow_ema': 10,
    'use_ha_for_ema': False,
    'slow_state_mode': 'slope',
    'long_exit': 'slope_negative',
    'short_exit': 'slope_positive',
}</code></pre>
        <div class='copy-indicator'>Click to copy</div>
    </div>
</div>

<script>
function copyConfig(element) {
    const code = element.querySelector('code').textContent;
    navigator.clipboard.writeText(code);
    const indicator = element.querySelector('.copy-indicator');
    indicator.textContent = 'Copied!';
    setTimeout(() => indicator.textContent = 'Click to copy', 2000);
}
</script>
```

### Config Box CSS

```css
.config-box {
    position: relative;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 16px;
    cursor: pointer;
    transition: border-color 0.2s;
}

.config-box:hover {
    border-color: var(--accent-blue);
}

.config-box pre {
    margin: 0;
    overflow-x: auto;
}

.config-box code {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    line-height: 1.5;
    color: var(--text-primary);
}

.copy-indicator {
    position: absolute;
    top: 8px;
    right: 8px;
    font-size: 10px;
    color: var(--text-muted);
    padding: 2px 8px;
    background: var(--bg-secondary);
    border-radius: 4px;
}
```

## Trade List Table

```html
<h2 class='section-title'>Full Trade List</h2>
<div class='card'>
    <div class='card-title'>Trade History ({{n_trades}} trades)</div>
    <div class='trade-list-container'>
        <table class='trade-list-table'>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Entry Time</th>
                    <th>Exit Time</th>
                    <th>Side</th>
                    <th>Entry</th>
                    <th>Exit</th>
                    <th>P&L</th>
                    <th>Return</th>
                    <th>MAE</th>
                    <th>MFE</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>2024-01-15 10:30</td>
                    <td>2024-01-15 14:45</td>
                    <td class='side-long'>LONG</td>
                    <td>$95.50</td>
                    <td>$98.25</td>
                    <td class='value-positive'>$275.00</td>
                    <td class='value-positive'>+2.88%</td>
                    <td class='value-warning'>1.25%</td>
                    <td class='value-positive'>3.50%</td>
                </tr>
                <!-- ... more rows ... -->
            </tbody>
        </table>
    </div>
</div>
```

### Trade List CSS

```css
.trade-list-container {
    max-height: 500px;
    overflow-y: auto;
}

.trade-list-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
}

.trade-list-table th,
.trade-list-table td {
    padding: 8px 6px;
    text-align: right;
    border-bottom: 1px solid var(--border-color);
    white-space: nowrap;
}

.trade-list-table th {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    font-weight: 500;
    text-transform: uppercase;
    font-size: 9px;
    position: sticky;
    top: 0;
}

.trade-list-table th:first-child,
.trade-list-table td:first-child {
    text-align: center;
}

.side-long {
    color: var(--accent-green);
    font-weight: 600;
}

.side-short {
    color: var(--accent-red);
    font-weight: 600;
}

/* Alternating row colors */
.trade-list-table tbody tr:nth-child(even) {
    background: rgba(33, 38, 45, 0.3);
}
```

## Risk Level Badges

```html
<span class='risk-badge risk-low'>LOW</span>
<span class='risk-badge risk-medium'>MEDIUM</span>
<span class='risk-badge risk-high'>HIGH</span>
<span class='risk-badge risk-extreme'>EXTREME</span>
```

### Badge CSS

```css
.risk-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
}

.risk-low { background: rgba(63, 185, 80, 0.2); color: var(--accent-green); }
.risk-medium { background: rgba(210, 153, 34, 0.2); color: var(--accent-orange); }
.risk-high { background: rgba(248, 81, 73, 0.2); color: var(--accent-red); }
.risk-extreme { background: rgba(248, 81, 73, 0.4); color: #ff6b6b; }
```

## Footer

```html
<div class='footer'>
    <p>QuantusMaximus Strategy Tearsheet | Generated by strategy_tearsheet.py</p>
    <p>Mode: {{mode}} | {{n_scenarios}} scenarios analyzed</p>
</div>
```

### Footer CSS

```css
.footer {
    text-align: center;
    padding: 24px 0;
    margin-top: 32px;
    border-top: 1px solid var(--border-color);
    color: var(--text-muted);
    font-size: 12px;
}
```

## Responsive Breakpoints

```css
@media (max-width: 768px) {
    .metrics-grid {
        grid-template-columns: 1fr;
    }

    .mae-stats-grid {
        grid-template-columns: repeat(3, 1fr);
    }

    .scenario-table {
        font-size: 10px;
    }

    .scenario-table th,
    .scenario-table td {
        padding: 6px 4px;
    }
}

@media (max-width: 480px) {
    body {
        padding: 12px;
    }

    .header h1 {
        font-size: 20px;
    }

    .mae-stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}
```

## Print Styles

```css
@media print {
    body {
        background: white;
        color: black;
    }

    .card {
        background: white;
        border: 1px solid #ccc;
    }

    .heatmap-cell {
        border: 1px solid #eee;
    }

    .footer {
        page-break-after: avoid;
    }
}
```
