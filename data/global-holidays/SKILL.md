---
name: global-holidays
description: |
  Use this skill whenever a task involves checking, generating, or working with public holidays — for any country or subdivision (state, province, region). Triggers include: "is [date] a holiday?", "list all holidays in [country/year]", "find holidays in [date range]", "working days", "business days", "skip holidays", "holiday calendar", or any task that requires knowing whether a date is a government-designated public holiday. Also use when combining public holidays with custom or personal holiday dates. Do NOT use for general date arithmetic, timezone conversion, or calendar rendering unless holidays are explicitly involved.
metadata: {"clawdbot":{"emoji":"🗓️","requires":{"bins":["python","pip"]}, "install":[{"id":"pip","kind":"pip","package":"holidays","label":"Install holidays package"}]}}
---

# holidays — Python Holiday Library

## Overview

`holidays` is a Python library that generates country- and subdivision-specific sets of government-designated holidays on the fly. It covers 249 countries (ISO 3166-1) and supports subdivisions (states, provinces, regions) via ISO 3166-2 codes.

The central object is `HolidayBase`, which behaves like a Python `dict` mapping `date → holiday name`. All examples below can be run directly in the shell:

```bash
python <<'EOF'
# your code here
EOF
# OR (if the package is installed via uv)
uv run - <<EOF
# your code here
EOF
```

---

## Installation

**IMPORTANT: Always use a virtual environment or `--break-system-packages` flag.**

```bash
pip install holidays --break-system-packages
```

**For production use, pin to a specific version:**

```bash
pip install holidays==0.58 --break-system-packages
```

---

## Quick Reference

| Task | Method |
|------|--------|
| All holidays for a country/year | `country_holidays('US', years=2024)` |
| Holidays for a subdivision | `country_holidays('US', subdiv='CA', years=2024)` |
| Holidays in a date range | `holidays_obj['2024-01-01':'2024-01-31']` |
| Check if a date is a holiday | `holidays_obj.get('2024-12-25')` → name or `None` |
| Add custom holidays | `holidays_obj.update({'2024-07-10': 'My Birthday!'})` |
| List all supported countries | `list_supported_countries()` |
| List countries with localization | `list_localized_countries()` |

---

## Core API

### `country_holidays()` — Main Function

```python
country_holidays(
    country,          # ISO 3166-1 alpha-2 code, e.g. 'US', 'GB', 'DE'
    subdiv=None,      # ISO 3166-2 subdivision code, e.g. 'CA', 'TX', 'BY'
    years=None,       # int or list of ints, e.g. 2024 or [2023, 2024]
    expand=True,      # auto-expand years when checking dates outside current range
    observed=True,    # include observed holidays (e.g. holiday on weekend → Monday)
    language=None,    # ISO 639-1 language code for holiday names, e.g. 'en', 'de'
    categories=None,  # filter to specific holiday categories (country-dependent)
)
```

Returns a `HolidayBase` object (dict-like: `{date: name}`).

---

## Common Tasks

### 1. Get All Holidays for a Country in a Year

```python
from holidays import country_holidays

us_holidays = country_holidays('US', years=2024)
for date, name in sorted(us_holidays.items()):
    print(date, name)
```

### 2. Get Holidays for a Subdivision (State / Province)

Use the ISO 3166-2 subdivision code (e.g. `'CA'` for California, `'BY'` for Bavaria).

```python
from holidays import country_holidays

ca_holidays = country_holidays('US', subdiv='CA', years=2024)
for date, name in sorted(ca_holidays.items()):
    print(date, name)
```

### 3. Get Holidays Within a Date Range

Slice the `HolidayBase` object with date strings (`'YYYY-MM-DD'`):

```python
from holidays import country_holidays

ca_holidays = country_holidays('US', subdiv='CA', years=2024)
for day in ca_holidays['2024-01-01':'2024-01-31']:
    print(f"{day}: {ca_holidays.get(day)}")
```

### 4. Check if a Specific Date is a Holiday

`.get()` returns the holiday name if the date is a holiday, or `None` if it is not.

```python
from holidays import country_holidays

ca_holidays = country_holidays('US', subdiv='CA')

# Is December 25 a holiday?
name = ca_holidays.get('2024-12-25')
print(name)   # → 'Christmas Day'

# Is December 26 a holiday?
name = ca_holidays.get('2024-12-26')
print(name)   # → None
```

**Tip:** Use `if date in holidays_obj:` for a boolean check (faster than `.get()`).

### 5. Working with Custom Holidays

**SECURITY NOTE:** Only use custom holidays if the user explicitly provides or requests them. Never assume a file location exists.

**ALWAYS ask the user for the file path** rather than using a default location. If they don't have a custom holidays file, skip this feature.

Example workflow:
1. Ask user: "Do you have a custom holidays JSON file you'd like to include?"
2. If yes, ask: "What's the full path to your custom holidays file?"
3. Only then load and merge:

```python
import json
from pathlib import Path
from holidays import country_holidays

# ONLY use this if user explicitly provided the path
custom_file = Path("/path/user/provided/custom-holidays.json")

# Verify file exists before reading
if custom_file.exists():
    with open(custom_file) as f:
        custom_data = json.load(f)

    holidays_2024 = country_holidays('US', years=2024)
    holidays_2024.update(custom_data)

    print(holidays_2024.get('2024-07-10'))  # → 'My Birthday!' (if defined)
else:
    print(f"File not found: {custom_file}")
```

**Custom holidays file format:**
```json
{
  "2024-07-10": "My Birthday!",
  "2024-10-01": "Family Celebration"
}
```

### 6. List All Supported Countries and Subdivisions

```python
from holidays import list_supported_countries

# include_aliases=True also returns common aliases (e.g. 'UK' for 'GB')
supported = list_supported_countries(include_aliases=True)
print(supported['US'])   # → list of supported US subdivision codes
```

### 7. Use Localized (Translated) Holiday Names

**Language codes:**
- Use ISO 639-1 codes (e.g., `en`, `de`, `fr`)
- Some countries use locale-specific codes (e.g., `en_US`, `zh_CN`)
- If an unsupported language is requested, the library falls back to the default language

**Step 1: Find countries with localization support**

```python
from holidays import list_localized_countries

# Get all countries that support multiple languages
localized = list_localized_countries(include_aliases=True)

# Check if a specific country supports localization
if 'MY' in localized:
    print(f"Malaysia supports: {localized['MY']}")
    # Output: Malaysia supports: ['en_MY', 'ms_MY', 'zh_CN', ...]
```

**Step 2: Generate holidays in a specific language**

```python
from holidays import country_holidays

# Malaysia holidays in Malay language
my_holidays_ms = country_holidays('MY', years=2025, language='ms_MY')
for date, name in sorted(my_holidays_ms.items())[:3]:
    print(f"{date}: {name}")

# Same holidays in English
my_holidays_en = country_holidays('MY', years=2025, language='en_MY')
for date, name in sorted(my_holidays_en.items())[:3]:
    print(f"{date}: {name}")
```

---

## Key Behaviours to Know

- **`observed=True` (default):** When a holiday falls on a weekend, the observed date (typically Monday) is included. Set `observed=False` to get only the statutory date.
- **`expand=True` (default):** If you check a date outside the `years` range, the library automatically adds that year. Set `expand=False` to prevent this.
- **Multiple years:** Pass a list to `years` to load several years at once: `years=[2023, 2024, 2025]`.
- **Date keys:** The `HolidayBase` dict accepts `datetime.date`, `datetime.datetime`, or `'YYYY-MM-DD'` strings interchangeably as keys.
- **Country codes:** Use ISO 3166-1 alpha-2 (e.g. `'US'`, `'GB'`, `'DE'`). Aliases like `'UK'` are supported when `include_aliases=True`.

---

## Dependencies

- **Python:** 3.10+
- **Package:** `holidays` (PyPI). Install with: `pip install holidays --break-system-packages`
- **No external system dependencies required**

## Security Considerations

1. **Package installation:** Use `--break-system-packages` flag (required in this environment) and consider pinning to a specific version
2. **Custom holidays files:** Only load custom holidays when explicitly requested by the user with a user-provided path
3. **File access:** Verify file existence before reading to avoid exposing directory structure
