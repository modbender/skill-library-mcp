# Python Data Visualization Skill for OpenClaw

Professional data visualization using Python's leading visualization libraries (matplotlib, seaborn, plotly).

## Overview

Create publication-quality static charts, statistical visualizations, and interactive plots for OpenClaw agents. This skill provides comprehensive examples and best practices for data-driven graphics.

## Features

### Static Visualizations (matplotlib + seaborn)
- Bar charts (simple, grouped, horizontal, stacked)
- Line plots (single/multiple series, time series, confidence intervals)
- Scatter plots (simple, regression, categorical, bubble)
- Heatmaps (simple, correlation matrices, labeled, diverging)
- Distribution plots (histogram, KDE, box, violin)
- Publication-quality export (PNG, SVG, PDF at 300 DPI)

### Interactive Visualizations (plotly)
- Hover tooltips, zoom, pan
- 3D plots and animations
- Export to HTML or PNG

### Included Resources
- **6 example scripts** - Ready-to-run demonstrations
- **2 reference guides** - Color theory and statistical visualization best practices
- **SKILL.md** - Comprehensive OpenClaw skill guide

## Installation

### For OpenClaw Users

```bash
# Via ClawHub
clawhub install python-dataviz

# Or manually
cd ~/.openclaw/workspace/skills
unzip python-dataviz.skill
```

### Setup Environment

**With pip:**
```bash
cd ~/.openclaw/workspace/skills/python-dataviz
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

**With uv (faster):**
```bash
cd ~/.openclaw/workspace/skills/python-dataviz
uv venv
source .venv/bin/activate
uv pip install .
```

## Quick Start

### Run Example Scripts

```bash
cd ~/.openclaw/workspace/skills/python-dataviz
source .venv/bin/activate

# Generate all bar chart variations
python scripts/bar_chart.py

# Generate interactive HTML charts
python scripts/interactive.py

# Generate distribution plots
python scripts/distribution.py
```

### Create Your Own

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set professional style
sns.set_theme(style="whitegrid")

# Your data
data = {'Category A': 45, 'Category B': 62, 'Category C': 38}

# Create chart
plt.figure(figsize=(10, 6))
plt.bar(data.keys(), data.values(), color='#667eea', alpha=0.8)
plt.title('My Chart', fontsize=16, fontweight='bold')
plt.ylabel('Values', fontsize=12)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()

# Export
plt.savefig('output.png', dpi=300, bbox_inches='tight')
```

## Use Cases

### When to Use This Skill
- ✅ Data-driven charts from CSV, Excel, databases
- ✅ Statistical analysis and visualizations
- ✅ Complex datasets with multiple series
- ✅ Publication-quality graphics (papers, reports)
- ✅ Interactive web-ready charts

### When to Use SVG Instead
- ✅ Simple infographics
- ✅ Design-heavy graphics
- ✅ Full control over every visual element
- ✅ No data processing needed

## Example Output

The skill can generate professional charts like:
- Sales analysis dashboards
- Statistical distribution comparisons
- Correlation heatmaps
- Time series with confidence intervals
- Interactive 3D visualizations

See `scripts/` directory for complete examples.

## Documentation

- **SKILL.md** - OpenClaw skill guide (library comparison, chart selection, troubleshooting)
- **references/colors.md** - Color palettes, accessibility, best practices
- **references/statistical.md** - Statistical visualization patterns and anti-patterns

## Dependencies

- matplotlib >= 3.8.0
- seaborn >= 0.13.0
- plotly >= 5.18.0
- pandas >= 2.1.0
- numpy >= 1.26.0
- kaleido >= 0.2.1

## Contributing

This is an OpenClaw skill designed for AI agents. For issues or improvements:

1. Open an issue on GitHub
2. Publish improvements via ClawHub
3. Submit a pull request

## License

MIT License - See LICENSE file for details

## Author

Created for the OpenClaw ecosystem. Published on [ClawHub](https://clawhub.com).

## Links

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [ClawHub](https://clawhub.com)
- [OpenClaw Discord](https://discord.com/invite/clawd)
