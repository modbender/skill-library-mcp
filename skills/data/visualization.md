# Visualization & Reporting

## Chart Selection

| Data Type | Comparison | Distribution | Trend | Part-to-Whole |
|-----------|------------|--------------|-------|---------------|
| Categorical | Bar chart | — | — | Pie (≤5 cats) |
| Continuous | Box plot | Histogram | — | — |
| Time series | Line chart | — | Line chart | Area chart |
| Two continuous | Scatter | 2D histogram | — | — |
| Cat × Continuous | Grouped bar | Violin | — | Stacked bar |

### Chart Anti-Patterns
- **Pie charts > 5 slices** — use bar chart instead
- **Dual y-axes** — misleading, use small multiples
- **3D charts** — distort perception, always use 2D
- **Truncated axes** — exaggerates differences
- **Too many colors** — limit to 6-8 distinguishable
- **Missing zero** — for bar charts, include zero baseline

## Publication-Ready Formatting

### Essential Elements
```
□ Clear, descriptive title
□ Axis labels with units
□ Legend (if multiple series)
□ Data source citation
□ Consistent color scheme
□ Appropriate font sizes
```

### Export Formats
- **PNG/JPEG** — presentations, web (300 DPI for print)
- **SVG** — publications, scalable, editable
- **PDF** — reports, preserves vectors
- **Interactive HTML** — dashboards, exploration

### Style Guidelines
- Use colorblind-friendly palettes (viridis, ColorBrewer)
- White or light gray background
- Minimal gridlines (light gray, if any)
- No chartjunk — data-ink ratio matters

## Dashboard Design

### Layout Principles
- Most important metric top-left (reading pattern)
- Group related charts together
- Use consistent time periods across charts
- Include last-updated timestamp

### Key Components
```
1. KPI cards — big numbers with trend
2. Trend chart — primary metric over time
3. Breakdown chart — by dimension (region, product, etc.)
4. Table — detailed data, sortable/filterable
5. Filters — date range, segment selectors
```

### Performance
- Aggregate data for display — don't query raw data live
- Cache expensive calculations
- Lazy-load below-the-fold charts
- Use appropriate granularity (daily vs hourly)

## Report Generation

### Structure
```
1. Executive Summary — 3-5 key findings
2. Methodology — data sources, period, definitions
3. Key Metrics — with context (vs target, vs last period)
4. Analysis — charts with interpretation
5. Recommendations — actionable next steps
6. Appendix — detailed tables, methodology notes
```

### Automated Reports
- Define report template once
- Schedule data refresh (daily, weekly, monthly)
- Generate charts from updated data
- Highlight changes from previous period
- Deliver via email, Slack, or shared folder

## Interpretation Guidelines

Every chart should answer:
1. **What:** What does this show?
2. **So what:** Why does it matter?
3. **Now what:** What action to take?

### Caption Writing
```
Bad: "Revenue by Region"
Good: "EMEA leads revenue growth at 23% YoY, while APAC declined 5%"
```

Captions should tell the story, not just label the data.
