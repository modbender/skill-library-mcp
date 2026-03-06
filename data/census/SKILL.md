---
name: census
description: "US Census Bureau — population, demographics, ACS data, economic indicators, and geographic data."
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+ (stdlib only — no dependencies)
metadata: {"openclaw": {"emoji": "📊", "requires": {"env": ["CENSUS_API_KEY"]}, "primaryEnv": "CENSUS_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# 📊 Census API

US Census Bureau — population, demographics, ACS data, economic indicators, and geographic data.

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `CENSUS_API_KEY` | ✅ | Census API key (optional) |


## Quick Start

```bash
# ACS 5-Year estimates
python3 {{baseDir}}/scripts/census.py acs-5yr --get "NAME,B01003_001E" --for "state:*"

# ACS 1-Year estimates
python3 {{baseDir}}/scripts/census.py acs-1yr --get "NAME,B01003_001E" --for "state:*"

# 2020 Decennial Census
python3 {{baseDir}}/scripts/census.py decennial --get "NAME,P1_001N" --for "state:*"

# Population estimates
python3 {{baseDir}}/scripts/census.py population --get "NAME,POP_2022" --for "state:*"

# County Business Patterns
python3 {{baseDir}}/scripts/census.py cbp --get "NAME,ESTAB,EMP" --for "state:*" --naics "72"

# Poverty data
python3 {{baseDir}}/scripts/census.py poverty --get "NAME,B17001_001E,B17001_002E" --for "state:*"

# Median household income
python3 {{baseDir}}/scripts/census.py income --get "NAME,B19013_001E" --for "state:*"

# Housing data
python3 {{baseDir}}/scripts/census.py housing --get "NAME,B25001_001E,B25002_002E,B25002_003E" --for "state:*"

# List available datasets
python3 {{baseDir}}/scripts/census.py list-datasets --year "2022"

# List ACS variables
python3 {{baseDir}}/scripts/census.py list-variables

# List available geographies
python3 {{baseDir}}/scripts/census.py list-geographies
```

## Output Format

All commands output JSON by default.

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/census.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
