# Odoo Data Analysis Playbook

## Goal
After fetching data, produce decision-ready insights, not only raw tables.

## Standard analysis pipeline
1. Clarify analysis question:
   - Business objective (growth, cost, collection, conversion, inventory, service quality).
   - Time range and scope (company/team/product/customer segment).
2. Define metrics:
   - Core KPI (for example revenue, gross margin, DSO, conversion, churn proxy, on-time rate).
   - Supporting metrics and breakdown dimensions.
3. Fetch and validate data:
   - Use minimal required fields and domain filters.
   - Check sample rows, null rate, duplicated records, and obvious outliers.
4. Aggregate and compare:
   - Time trend (WoW/MoM/YoY when possible).
   - Structural split (region/product/salesperson/customer tier).
   - Contribution analysis (top drivers and draggers).
5. Interpret causes:
   - Distinguish symptom vs root-cause candidates.
   - Mark confidence level (high/medium/low) based on data completeness.
6. Recommend actions:
   - 3-5 practical actions with priority, expected impact, and execution cost.
   - Include monitoring metrics and next review point.

## Output style (user-facing)
- Use plain language first, then include essential numbers.
- Keep structure fixed:
  1) 结论摘要
  2) 关键发现
  3) 风险与机会
  4) 决策建议（按优先级）
  5) 建议的下一步数据补充
- Avoid jargon where possible; explain terms briefly when needed.

## Decision recommendation template
For each recommendation include:
- What to do
- Why it matters (data evidence)
- Expected impact (direction and rough magnitude)
- Effort/cost (low/medium/high)
- Owner suggestion (which role/team)
- Metric to track success

## Safety and quality
- Do not fabricate unavailable metrics.
- If key fields are missing, explicitly ask for them before high-stakes conclusions.
- Separate facts, assumptions, and suggestions.
