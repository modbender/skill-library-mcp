---
name: Summarize File
description: Reads text files from workspace/paths and generates concise summaries. Handles logs, reports, CSVs, multi-line content.
version: 1.0.0
author: Your Name
triggers: ["summarize file", "summarize-file", "tl;dr file"]
os: [win32, darwin, linux]
requires.tools: ["workspace.read"]
security: L1
---

# Summarize-File Skill

## Purpose
Extracts key insights from text files (logs, reports, notes) and returns 2-3 sentence summaries. Ignores boilerplate/empty lines.

## Usage Examples
User: summarize file C:\Users\user\Desktop\report.txt
Claw: File contains Q1 sales report: Revenue up 12% YoY, expenses flat, net profit +8%. Key risks: supply chain delays.

User: summarize file workspace/error.log
Claw: Error log (Feb 22): 14 auth failures (IP 192.168.1.50), 2 DB timeouts, no critical crashes.

text

## How It Works
1. Reads file content via workspace.read tool
2. Strips empty lines, headers, timestamps  
3. Feeds to LLM with summarization prompt
4. Returns concise 2-3 sentence summary

## Security & Privacy
- **L1 Risk**: Read-only file access
- No network calls, no external APIs
- Local processing only
- File paths validated (no ../ escapes)

## External Endpoints
None. Purely local file → LLM → text.

## Trust Statement
This skill reads local files and summarizes locally. No data leaves your machine.