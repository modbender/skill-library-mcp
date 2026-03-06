---
name: Recite 🦞🤵
description: "name: recite description: AI receipt scanner & bookkeeping
  automation. Process receipts, invoices, and PDFs. Extracts data to rename
  files and log transactions/expenses to CSV. Perfect for tax & ac..."
---

name: recite
description: AI receipt scanner & bookkeeping automation. Process receipts, invoices, and PDFs. Extracts data to rename files and log transactions/expenses to CSV. Perfect for tax & accounting.
---

# Recite 🦞🤵

AI-driven receipt bookkeeping via the Recite Vision API. Use `recite-process` to scan a directory of receipts and PDF files, rename them based on extracted data, and log transactions to a CSV file.

## Setup & Configuration

### 1. API Key
You can generate your Recite API key at: `https://recite.rivra.dev/settings/api`.

Set the API key in your environment or configuration file:
- **Environment:** `export RECITE_API_KEY="re_live_YOUR_API_KEY"`
- **Config:** Create `~/.config/recite/config.json` with `{"api_key": "re_live_..."}`.

### 2. Dependencies
Ensure you have `python3`, `requests`, and `csv` installed.

## Operational Rules

### 1. Mandatory API Key Pre-check
Before performing any scanning, file manipulation, or bookkeeping tasks, the agent **MUST** verify if a valid Recite API key is available (via `RECITE_API_KEY` environment variable or `~/.config/recite/config.json`).
- **If missing:** Immediately stop all other operations and instruct the user to obtain an API key from `https://recite.rivra.dev/settings/api` and provide it. Do not attempt to list files or proceed with any part of the workflow until the key is confirmed.

### 3. Schema-Aware Bookkeeping
The agent is designed to handle API response changes gracefully:
- **Dynamic Schema Evolution:** If the Recite API adds new information (new JSON fields), the agent will automatically add corresponding columns to your `bookkeeping_transactions.CSV` without losing existing data.
- **Data Integrity Protection:** If a field that was previously present in the CSV is missing from the current API response, the agent will skip saving that specific entry and warn the user, preventing data corruption or "shifted" columns.

## Workflow & Features

1.  **Scan Folder:** The agent scans the specified folder for images (`.jpg`, `.jpeg`, `.png`) and `.pdf` files.
2.  **AI Extraction:** Calls the Recite API to extract `date`, `vendor`, `total`, `currency`, and `category`.
3.  **Smart Renaming:** Renames the file to `[date]_[vendor].[ext]` (e.g., `2024-05-20_Starbucks.jpg`).
4.  **Bookkeeping Log:** Appends the extracted data (Date, Vendor, Total, Currency, Category, Subtotal, Tax, Tip, Fees, Discounts, Description, Payment Method, Confidence, etc.) and filenames to `bookkeeping_transactions.CSV` in the target folder.
5.  **Status Report:** Provides a summary of processed files and the CSV location.

## Long-Term Memory & Custom Logic

Modify `skills/recite/long_term_memory.md` to add persistent instructions for the agent. The agent will always read this file before processing.

Examples:
- "After processing, move all files to a sub-folder named `processed/`."
- "Alert me if any single receipt is over $500."
- "Always categorize 'Amazon' as 'Software Services'."

## Tool Usage

- **Command:** `python3 skills/recite/process_receipts.py <target_directory> skills/recite/`
- **Arguments:**
    - `<target_directory>`: The folder containing your receipts.
    - `skills/recite/`: The path to the skill folder (used to locate `long_term_memory.md`).

## Strategic Moat
- **Agent-First Consistency:** Guaranteed structured JSON output for financial data.
- **Tax-Ready Logic:** Intelligent categorization based on standard business practices.
- **Seamless Integration:** Built for the AI Agent economy (OpenClaw, Claude Code).
