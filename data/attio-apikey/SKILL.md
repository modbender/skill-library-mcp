---
name: attio-apikey
description: |
  Direct Attio CRM integration for OpenClaw with full CRUD capabilities.
  Query, create, update, and delete companies, people, and notes in real-time.
  Uses Attio API key directly - no OAuth or proxy server required.
compatibility: OpenClaw with exec tool
credentials:
  requiredEnv:
    - ATTIO_API_KEY
metadata:
  author: felixwithoutx
  version: "1.0.1"
  tags:
    - attio
    - crm
    - sales
    - pipeline
  license: MIT
---

# Attio Direct Skill

Direct Attio CRM integration with full CRUD (Create, Read, Update, Delete) operations.

## Setup

1. Get API key from https://app.attio.com/settings/api
2. Copy `.env.example` to `.env` and add your key

## Quick Commands

```bash
# Read data
python3 attio_client.py companies
python3 attio_client.py people

# Create
python3 attio_client.py companies --create --data '{"name": "Acme"}'

# Update
python3 attio_client.py companies --update --id RECORD_ID --data '{"funnel_stage": "Nurture"}'

# Delete
python3 attio_client.py companies --delete --id RECORD_ID

# Add note
python3 attio_client.py companies --note "Title|Content" --id RECORD_ID
```

## Features

- Full CRUD on companies and people
- Add notes to any record
- Query with pagination (default 5000)
- Direct API - no OAuth overhead

## Files

```
attio-direct/
├── attio_client.py    # Main CLI
├── .env.example       # API key template
├── README.md          # Setup instructions
└── SKILL.md          # This file
```
