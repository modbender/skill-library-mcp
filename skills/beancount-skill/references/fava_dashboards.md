# Fava Dashboards Plugin

## Official Documentation

- **GitHub Repository**: https://github.com/andreasgerstmayr/fava-dashboards
- **Fava Documentation**: https://beancount.github.io/fava/

## Overview

Fava Dashboards is a plugin for Fava that allows creating custom dashboards with multiple chart types using Apache ECharts, D3.js and others.

## Installation

```bash
pip install fava-dashboards
```

## Enabling the Plugin

Add this directive to your main Beancount file:

```beancount
2024-01-01 custom "fava-extension" "fava_dashboards"
```

To specify a custom configuration file location:

```beancount
2024-01-01 custom "fava-extension" "fava_dashboards" "{
    'config': '/path/to/dashboards.yaml'
}"
```

## Configuration File

The plugin looks by default for a `dashboards.tsx` (or `.ts`, `.jsx`, `.js`, `.yaml`) file in the same directory as the main Beancount file.

### YAML Structure

```yaml
dashboards:
- name: DashboardName
  panels:
  - title: Panel Title
    width: 50%        # Relative width (default: 100%)
    height: 400px     # Absolute height (default: 400px)
    link: ../../balance_sheet/  # Optional header link
    type: echarts     # Type: html, echarts, d3_sankey, table, jinja2
    queries:
    - bql: |
        SELECT ... FROM ... WHERE ...
      link: ../../account/{account}/?time={time}
    script: |
      // JavaScript that returns the panel configuration
      return { ... };
```

## Panel Types

### HTML Panel

Returns HTML that renders directly:

```yaml
- title: Total Assets
  width: 50%
  height: 80px
  queries:
  - bql: SELECT CONVERT(SUM(position), '{{ledger.ccy}}') AS value WHERE account ~ '^Assets:'
  type: html
  script: |
    const currencyFormatter = new Intl.NumberFormat(undefined, { 
      style: "currency", 
      currency: ledger.ccy, 
      maximumFractionDigits: 0 
    }).format;
    const value = panel.queries[0].result[0]?.value[ledger.ccy] ?? 0;
    return `<div style="font-size: 40px; font-weight: bold; text-align: center;">
      ${currencyFormatter(value)}
    </div>`;
```

### ECharts Panel

Returns valid Apache ECharts options:

```yaml
- title: Net Worth Over Time
  queries:
  - bql: |
      SELECT year, month,
      CONVERT(LAST(balance), '{{ledger.ccy}}') AS value
      WHERE account_sortkey(account) ~ '^[01]'
      GROUP BY year, month
  type: echarts
  script: |
    const currencyFormatter = new Intl.NumberFormat(undefined, { 
      style: "currency", 
      currency: ledger.ccy, 
      maximumFractionDigits: 0 
    }).format;
    const months = utils.iterateMonths(ledger.dateFirst, ledger.dateLast)
      .map((m) => `${m.month}/${m.year}`);
    
    const amounts = {};
    for (let row of panel.queries[0].result) {
      amounts[`${row.month}/${row.year}`] = row.value[ledger.ccy];
    }
    
    return {
      tooltip: {
        trigger: "axis",
        valueFormatter: currencyFormatter,
      },
      xAxis: {
        data: months,
      },
      yAxis: {
        axisLabel: { formatter: currencyFormatter },
      },
      series: [{
        type: "line",
        smooth: true,
        data: months.map((month) => amounts[month]),
      }],
    };
```

### D3 Sankey Panel

For money flow Sankey diagrams:

```yaml
- title: Income/Expenses Flow
  height: 800px
  queries:
  - bql: |
      SELECT account, CONVERT(SUM(position), '{{ledger.ccy}}') AS value
      WHERE account ~ '^(Income|Expenses):'
      GROUP BY account
  type: d3_sankey
  script: |
    const nodes = [{ name: "Income" }];
    const links = [];
    // ... logic to build nodes and links
    return {
      align: "left",
      valueFormatter: currencyFormatter,
      data: { nodes, links },
    };
```

### Table Panel (jinja2)

For tables using Fava components:

```yaml
- title: Top 10 Expenses
  queries:
  - bql: |
      SELECT date, payee, narration, position 
      WHERE account ~ "^Expenses:" 
      ORDER BY position DESC 
      LIMIT 10
  type: jinja2
  template: |
    <svelte-component type="query-table">
      <script type="application/json">{{ panel.queries[0].querytable|tojson }}</script>
    </svelte-component>
```

## Available Variables and Functions

In the `script` you have access to:

| Variable/Function | Description |
|-------------------|-------------|
| `panel` | Current panel definition |
| `panel.queries[n].result` | Results of query n |
| `ledger.dateFirst` | First date of filter or ledger |
| `ledger.dateLast` | Last date of filter or ledger |
| `ledger.filterFirst` | Filter start date (null if none) |
| `ledger.filterLast` | Filter end date (null if none) |
| `ledger.operatingCurrencies` | Configured operating currencies |
| `ledger.ccy` | First operating currency (shortcut) |
| `ledger.accounts` | Declared accounts |
| `ledger.commodities` | Declared commodities |
| `ledger.query(bql)` | Execute BQL query |
| `helpers.urlFor(url)` | Add current filter parameters to URL |

## Custom Utilities

You can define reusable utility functions:

```yaml
utils:
  inline: |
    function iterateMonths(dateFirst, dateLast) {
      const months = [];
      let [year, month] = dateFirst.split("-").map((x) => parseInt(x));
      let [lastYear, lastMonth] = dateLast.split("-").map((x) => parseInt(x));
      
      while (year < lastYear || (year === lastYear && month <= lastMonth)) {
        months.push({ year, month });
        if (month == 12) { year++; month = 1; } 
        else { month++; }
      }
      return months;
    }
    
    function iterateYears(dateFirst, dateLast) {
      const years = [];
      let year = parseInt(dateFirst.split("-")[0]);
      let lastYear = parseInt(dateLast.split("-")[0]);
      for (; year <= lastYear; year++) { years.push(year); }
      return years;
    }
    
    return { iterateMonths, iterateYears };
```

Then access as `utils.iterateMonths(...)`.

## Queries with Placeholders

Use `{{ledger.ccy}}` to insert the operating currency:

```yaml
queries:
- bql: |
    SELECT account, CONVERT(SUM(position), '{{ledger.ccy}}') AS value
    WHERE account ~ '^Expenses:'
    GROUP BY account
```

## Dynamic Links

Links can use placeholders that are replaced in the script:

```yaml
queries:
- bql: SELECT year, month, ...
  link: ../../account/{account}/?time={time}
```

In the script:

```javascript
onClick: (event) => {
  const [month, year] = event.name.split("/");
  const link = panel.queries[0].link
    .replace("{time}", `${year}-${month.padStart(2, "0")}`);
  window.open(helpers.urlFor(link));
}
```

## Reuse with YAML Anchors

Use anchors to reuse queries or scripts:

```yaml
- title: Asset Classes
  queries:
  - bql: &assets_query |
      SELECT currency,
             CONVERT(SUM(position), '{{ledger.ccy}}') as market_value
      WHERE account_sortkey(account) ~ '^[01]'
      GROUP BY currency
  type: echarts
  script: &asset_classes_script |
    // Reusable script
    return { ... };

- title: Investment Classes
  queries:
  - bql: *assets_query  # Reuses the query
  type: echarts
  script: *asset_classes_script  # Reuses the script
```

## Common Chart Examples

### Distribution Pie Chart

```yaml
- title: Asset Distribution
  width: 50%
  queries:
  - bql: |
      SELECT currency,
             CONVERT(SUM(position), '{{ledger.ccy}}') as value
      WHERE account ~ '^Assets:'
      GROUP BY currency
  type: echarts
  script: |
    const data = panel.queries[0].result
      .filter((row) => row.value[ledger.ccy])
      .map((row) => ({ 
        name: row.currency, 
        value: row.value[ledger.ccy] 
      }));
    
    return {
      tooltip: { trigger: "item" },
      series: [{
        type: "pie",
        data,
      }],
    };
```

### Monthly Stacked Bar Chart

```yaml
- title: Income vs Expenses
  queries:
  - name: Income
    stack: income
    bql: |
      SELECT year, month, CONVERT(SUM(position), '{{ledger.ccy}}') AS value
      WHERE account ~ '^Income:'
      GROUP BY year, month
  - name: Expenses
    stack: expenses
    bql: |
      SELECT year, month, CONVERT(SUM(position), '{{ledger.ccy}}') AS value
      WHERE account ~ '^Expenses:'
      GROUP BY year, month
  type: echarts
  script: |
    const months = utils.iterateMonths(ledger.dateFirst, ledger.dateLast)
      .map((m) => `${m.month}/${m.year}`);
    
    const amounts = {};
    for (let query of panel.queries) {
      amounts[query.name] = {};
      for (let row of query.result) {
        const value = row.value[ledger.ccy] ?? 0;
        amounts[query.name][`${row.month}/${row.year}`] = 
          query.stack == "income" ? -value : value;
      }
    }
    
    return {
      legend: { top: "bottom" },
      xAxis: { data: months },
      yAxis: {},
      series: panel.queries.map((query) => ({
        type: "bar",
        name: query.name,
        stack: query.stack,
        data: months.map((month) => amounts[query.name][month] ?? 0),
      })),
    };
```

### Heatmap

```yaml
- title: Savings Heatmap
  queries:
  - bql: |
      SELECT year, month, CONVERT(SUM(position), '{{ledger.ccy}}') AS value
      WHERE account ~ '^(Income|Expenses):'
      GROUP BY year, month
  type: echarts
  script: |
    const years = utils.iterateYears(ledger.dateFirst, ledger.dateLast);
    // Build data as [x, y, value]
    return {
      visualMap: {
        min: -maxValue,
        max: maxValue,
        inRange: { color: ["#af3d3d", "#fff", "#3daf46"] },
      },
      series: [{
        type: "heatmap",
        data: data,
      }],
    };
```

## ECharts Reference

For chart options, see the Apache ECharts documentation:
- https://echarts.apache.org/en/option.html
- https://echarts.apache.org/examples/en/index.html

## Troubleshooting

### Dashboard not showing
- Verify installation: `pip list | grep fava-dashboards`
- Verify extension is enabled in beancount file
- Restart Fava after changes

### Query errors
- Test queries first in Fava's Query page
- Verify account patterns match your structure
- Use `CONVERT()` for multi-currency queries

### JavaScript errors
- Open browser console (F12) to see errors
- Verify the script returns a valid object for the panel type
