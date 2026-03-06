# Chart Guidelines

## Selection Rules
- Use line charts for trends over time.
- Use bar charts for category comparisons.
- Use stacked bars only for part-to-whole by period.
- Avoid pie charts unless <=5 categories and static share view is required.

## Formatting Rules
- Titles must answer a question (e.g., "How revenue changed by month").
- Label axes with units ($, %, count).
- Sort categorical bars descending by value.
- Keep consistent color mapping across charts.
- Add data labels when category count <= 10.

## Data Quality Handling
- If time fields are missing, skip trend chart and note limitation.
- If required numeric fields are missing, stop and request mapping.
- If outliers exist, mention them in analysis and optionally show clipped variant.

## Minimum Visual Set
- 1 trend chart
- 1 category comparison chart
- 1 table of top/bottom contributors
