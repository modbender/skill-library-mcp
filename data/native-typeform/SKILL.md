---
name: typeform
description: "Read Typeform forms and responses directly via the Typeform API. Use when you need to list forms, retrieve survey responses, or get form performance stats. Calls api.typeform.com directly with no third-party proxy."
metadata:
  openclaw:
    requires:
      env:
        - TYPEFORM_TOKEN
      bins:
        - python3
    primaryEnv: TYPEFORM_TOKEN
    files:
      - "scripts/*"
---

# Typeform

Read forms and responses directly via `api.typeform.com`.

## Setup (one-time)

1. Go to https://admin.typeform.com/account#/section/tokens
2. Click **Generate a new token**, give it a name, select scopes:
   - `Forms: Read`
   - `Responses: Read`
   - `Insights: Read`
3. Copy the token and set it:
   ```
   TYPEFORM_TOKEN=tfp_your_token_here
   ```

## Commands

### List your forms
```bash
python3 /mnt/skills/user/typeform/scripts/typeform.py list-forms
```

### Search forms by title
```bash
python3 /mnt/skills/user/typeform/scripts/typeform.py list-forms --search "customer survey"
```

### Get form definition (questions, logic, fields)
```bash
python3 /mnt/skills/user/typeform/scripts/typeform.py get-form <form_id>
```

### Get responses for a form
```bash
python3 /mnt/skills/user/typeform/scripts/typeform.py responses <form_id>
```

### Get last 100 responses
```bash
python3 /mnt/skills/user/typeform/scripts/typeform.py responses <form_id> --limit 100
```

### Filter responses by date range
```bash
python3 /mnt/skills/user/typeform/scripts/typeform.py responses <form_id> \
  --since 2026-01-01T00:00:00Z \
  --until 2026-02-01T00:00:00Z
```

### Get form insights (views, completions, completion rate)
```bash
python3 /mnt/skills/user/typeform/scripts/typeform.py insights <form_id>
```

### Get your account info
```bash
python3 /mnt/skills/user/typeform/scripts/typeform.py me
```

## Notes

- Free plan: 10 responses/month across all forms. API reads still work regardless.
- Rate limit: 2 requests/second.
- Form IDs look like `abc123XY` — find them in your Typeform dashboard URL or via `list-forms`.
- Webhooks require a PRO plan and are not supported by this skill.
