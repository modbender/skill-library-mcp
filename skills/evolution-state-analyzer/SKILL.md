---
name: evolution-state-analyzer
description: Analyzes the evolution memory graph for stagnation patterns, recurring failures, and success plateaus. Generates actionable insights to guide future evolution cycles.
---

# Evolution State Analyzer

This skill provides meta-analysis of the evolution process itself by examining the `memory_graph.jsonl` file.

## Capabilities

- **Stagnation Detection**: Identifies repetitive cycles without improvement.
- **Gene Efficacy Analysis**: Tracks which genes yield the highest success rates.
- **Failure Cluster Analysis**: Groups failure reasons to pinpoint systemic issues.
- **Trend Reporting**: Visualizes evolution score trends over time.

## Usage

```javascript
const analyzer = require('./index');
const insights = await analyzer.analyzeState();
console.log(JSON.stringify(insights, null, 2));
```

## Example Output

```json
{
  "total_cycles": 120,
  "success_rate": 0.75,
  "stagnation_detected": true,
  "top_genes": [
    { "id": "gene_repair_v2", "success_rate": 0.95 },
    { "id": "gene_innovate_v1", "success_rate": 0.40 }
  ],
  "recommendations": [
    "Switch to INNOVATE intent (stagnation streak: 5)",
    "Deprecate gene_innovate_v1 (success rate < 0.5)"
  ]
}
```
