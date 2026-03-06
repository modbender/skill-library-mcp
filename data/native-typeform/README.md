# typeform

OpenClaw skill for reading Typeform forms and responses via the official Typeform API.

Calls `api.typeform.com` directly — no third-party proxy, no maton dependency.

## Setup

1. Go to https://admin.typeform.com/account#/section/tokens
2. Generate a personal access token with scopes: `Forms: Read`, `Responses: Read`, `Insights: Read`
3. Set the environment variable:
   ```
   TYPEFORM_TOKEN=tfp_your_token_here
   ```

## Commands

```bash
# List all forms
python3 scripts/typeform.py list-forms

# Search forms
python3 scripts/typeform.py list-forms --search "feedback"

# Get form definition
python3 scripts/typeform.py get-form <form_id>

# Get responses
python3 scripts/typeform.py responses <form_id>
python3 scripts/typeform.py responses <form_id> --limit 100
python3 scripts/typeform.py responses <form_id> --since 2026-01-01T00:00:00Z

# Form insights (views, completions, completion rate)
python3 scripts/typeform.py insights <form_id>

# Account info
python3 scripts/typeform.py me
```

## Requirements

- Python 3 (stdlib only, no pip dependencies)
- A Typeform account (free plan works)
