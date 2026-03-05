---
name: wolfram-alpha
description: Perform complex mathematical calculations, physics simulations, data analysis, and scientific queries via the Wolfram|Alpha LLM API. Use this skill when you need exact answers to quantitative questions.
metadata:
  {
    "openclaw": {
      "emoji": "🔢",
      "requires": { 
        "bins": ["python3"], 
        "pip": ["requests"],
        "env": ["WOLFRAM_APP_ID"]
      }
    }
  }
---

# Wolfram|Alpha Skill

This skill leverages the Wolfram|Alpha LLM API to provide accurate answers to scientific and mathematical questions.

## Usage

Call the script with your query as an argument:

```bash
python3 wolfram_query.py "integrate x^2 from 0 to 3"
```

## Features

- **Mathematics**: Calculus, algebra, statistics.
- **Science**: Physics, chemistry, astronomy.
- **Data**: Economic data, geographic facts, demographics.
- **Units**: Unit conversions and currency exchange.

## Configuration

Requires a `WOLFRAM_APP_ID` in the environment variables (typically set in your `.env` file).
