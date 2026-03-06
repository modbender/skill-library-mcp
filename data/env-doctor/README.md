# 🩺 env-doctor

Diagnose problems in your .env files before they break your app.

## Features

- Detects empty values, duplicate keys, and syntax errors
- Cross-references `.env` with `.env.example` for missing/extra keys
- Flags security risks (exposed secrets, missing `.gitignore`)
- Catches common mistakes (spaces around `=`, bad URLs, invalid ports)
- Severity-rated report: 🔴 Critical, 🟡 Warning, 🔵 Info

## Usage Examples

- "Check my .env file for issues"
- "Compare .env with .env.example"
- "Are there any security risks in my environment config?"

## Requirements

- File read access

## Author

REY (@REY_MoltWorker)
