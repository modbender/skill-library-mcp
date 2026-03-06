# Recite Agent Skill 🦞🤵

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AI-powered receipt scanning & automated bookkeeping agent skill for OpenClaw and Claude Code.**

Recite allows your AI agent to handle the tedious work of receipt management. It scans images and PDFs using the Recite Vision API, renames files logically, and maintains a comprehensive local CSV ledger with 19+ financial data points.

---

## 🚀 Key Features (TL;DR for Agents)
- **Vision AI Extraction:** High-accuracy extraction of Date, Vendor, Total, Tax, Tip, Category, etc.
- **Smart Renaming:** Automatically renames files to `[YYYY-MM-DD]_[Vendor].png/pdf`.
- **Schema-Aware Bookkeeping:** Appends data to `bookkeeping_transactions.CSV`. Handles API response changes without data loss.
- **Local-First:** Keeps your financial data on your machine.
- **Long-Term Memory:** Supports custom persistent instructions (e.g., "Alert if total > $500").

## 🛠️ Setup

### 1. Get API Key
Obtain your Recite API key from: [https://recite.rivra.dev/settings/api](https://recite.rivra.dev/settings/api)

### 2. Configure
Set your API key in your environment or a config file:
- **Env:** `export RECITE_API_KEY="re_live_..."`
- **Config:** `~/.config/recite/config.json` -> `{"api_key": "re_live_..."}`

### 3. Dependencies
```bash
pip install requests
```

## 🤖 For AI Agents: How to use this Skill

If you are an AI agent, follow these steps to process receipts for your user:

1. **Verify Key:** Ensure `RECITE_API_KEY` is available.
2. **Read LTM:** Always read `skills/recite/long_term_memory.md` for user-specific rules.
3. **Execute:** Run the processing script:
   ```bash
   python3 skills/recite/process_receipts.py <path_to_receipts_folder> skills/recite/
   ```

## 📊 Data Points Captured
The skill maintains a local ledger with the following columns:
`Date`, `Vendor`, `Total`, `Currency`, `Category`, `Subtotal`, `Tax`, `Tip`, `Fees`, `Discounts`, `Description`, `PaymentMethod`, `Confidence`, `ScanID`, `OriginalFilename`, `NewFilename`.

## 📜 License
MIT License. Created by [Gavin J. (@RivraDev)](https://x.com/RivraDev).
