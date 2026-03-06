---
description: "Implementation rules for charts"
---
# Charts

SWIFT CHARTS:
- import Charts; use Chart { } container
- BarMark, LineMark, AreaMark, PointMark, RuleMark for data visualization
- .foregroundStyle(by: .value("Category", item.category)) for color coding
- chartXAxis { AxisMarks() }, chartYAxis { AxisMarks() } for custom axis labels
- Extract Chart into a separate computed property to avoid body complexity
- Use .chartScrollableAxes(.horizontal) for large datasets
