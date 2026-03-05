---
name: excel-translator
description: Translates Excel files (.xlsx) from English to Chinese while preserving all formatting, images, and charts. Use for any task where a user provides an Excel file and requests English-to-Chinese translation.
---

# Excel Translator Skill

## Overview

This skill translates the text content of an Excel file (.xlsx) from English to Chinese using `openpyxl`. The Chinese translation is placed directly below the original English text **in the same cell**, separated by a newline — no new rows or columns are inserted. Original formatting (merged cells, fonts, colors, images) is preserved.

## Workflow

1. Identify the input `.xlsx` file path from the user.
2. Run `scripts/translate.py` from the shell.
3. Deliver the output file to the user as an attachment.

## Running the Script

```bash
python3.11 /home/ubuntu/skills/excel-translator/scripts/translate.py "/path/to/input.xlsx"
```

The output file is saved automatically with a `_translated` suffix in the same directory.

**Custom output path:**
```bash
python3.11 /home/ubuntu/skills/excel-translator/scripts/translate.py "/path/to/input.xlsx" -o "/path/to/output.xlsx"
```

## Environment Variables

The script reads API credentials from environment variables. These are pre-configured in the Manus sandbox:

- `OPENAI_API_KEY` — API key for the translation model.
- `OPENAI_BASE_URL` — Base URL for the API endpoint (defaults to `https://api.openai.com/v1`).

## Bundled Resources

- **`scripts/translate.py`** — Core translation script. Scans all sheets, translates English text cells concurrently via OpenAI API, writes `"English\nChinese"` back into the same cell with `wrap_text=True`, and saves the result.
