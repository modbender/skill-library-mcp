# Personal Finance with Beancount & Fava

A professional AI assistant skill for personal finance management using plain-text accounting with [Beancount](https://beancount.github.io/docs/index.html) and [Fava](https://beancount.github.io/fava/).

**Downloads:** https://github.com/barcia/beancount-skill/releases
**Beancount MCP:** https://github.com/barcia/beancount-mcp

## Overview

This skill enables AI assistants to help users with:

- **Financial Analysis**: Interpret spending patterns, calculate metrics (net worth, savings rate, expense ratios)
- **Beancount Expertise**: Syntax help, transaction entry, account structure, and file organization
- **Fava Mastery**: Query creation, report generation, and visualization optimization
- **Investment Guidance**: Educational recommendations on asset allocation, risk assessment, and portfolio strategy
- **Budget & Planning**: Goal setting, cash flow management, and financial optimization

## Contents

```
├── SKILL.md                          # Main skill definition and instructions
├── scripts/
│   └── analyze_beancount.py          # Python script for quick financial analysis
└── references/
    ├── beancount_syntax.md           # Complete Beancount syntax reference
    ├── beancount_query.md            # BQL (Beancount Query Language) reference
    ├── fava_features.md              # Fava interface, options, and budgets
    ├── fava_dashboards.md            # Fava Dashboards plugin reference
    └── financial_analysis.md         # Financial metrics and analysis guide
```

## Usage

### As an AI Skill

The `SKILL.md` file contains the complete skill definition that can be used with AI assistants that support custom skills or system prompts. It provides:

- Workflow guidelines for financial analysis
- Professional standards and disclaimers
- Common use case patterns
- Reference to supporting documentation

### Analysis Script

The included Python script provides quick financial insights from Beancount files:

```bash
# Install beancount first
pip install beancount

# Run analysis
python scripts/analyze_beancount.py your_finances.beancount --all

# Specific reports
python scripts/analyze_beancount.py your_finances.beancount --net-worth
python scripts/analyze_beancount.py your_finances.beancount --savings-rate --year 2024
python scripts/analyze_beancount.py your_finances.beancount --top-expenses 10
python scripts/analyze_beancount.py your_finances.beancount --monthly-expenses
```

## Reference Documentation

The `references/` folder contains comprehensive documentation:

| File | Description |
|------|-------------|
| `beancount_syntax.md` | Complete syntax reference with all directives and examples |
| `beancount_query.md` | BQL query patterns for common financial questions |
| `fava_features.md` | Fava configuration, budgets, and workflow tips |
| `fava_dashboards.md` | Creating custom dashboards with fava-dashboards plugin |
| `financial_analysis.md` | Financial metrics, benchmarks, and optimization strategies |

## Key Features

### Multi-Language Support

The skill adapts to the user's language automatically - if the user writes in Spanish, it responds in Spanish; if in English, it responds in English.

### Professional Standards

The skill maintains clear boundaries:
- Provides financial **education and analysis**, not licensed financial advice
- Recommends consulting professionals for major financial decisions
- Includes appropriate disclaimers for investment discussions

### Practical Focus

- Actionable recommendations based on actual user data
- Concrete examples and working Beancount syntax
- Benchmarks and healthy financial ranges for comparison

## Requirements

For the analysis script:
- Python 3.8+
- beancount (`pip install beancount`)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Beancount](https://github.com/beancount/beancount) - Double-entry bookkeeping computer language
- [Fava](https://github.com/beancount/fava) - Web interface for Beancount
- [fava-dashboards](https://github.com/andreasgerstmayr/fava-dashboards) - Custom dashboards for Fava
