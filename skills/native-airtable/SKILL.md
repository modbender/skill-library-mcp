---
name: airtable
description: "Read Airtable bases, tables, and records directly via the Airtable API. Use when you need spreadsheet/database data from Airtable. Calls api.airtable.com directly with no third-party proxy."
metadata:
  openclaw:
    requires:
      env:
        - AIRTABLE_PAT
      bins:
        - python3
    primaryEnv: AIRTABLE_PAT
    files:
      - "scripts/*"
---

# Airtable

Read bases, tables, and records directly via `api.airtable.com`.

## Setup (one-time)

1. Go to https://airtable.com/create/tokens
2. Click **+ Create new token**, give it a name
3. Add scopes:
   - `data.records:read`
   - `schema.bases:read`
4. Under **Access**, select which bases to grant access to (or all)
5. Copy the token — it starts with `pat`
6. Set the environment variable:
   ```
   AIRTABLE_PAT=pat_your_token_here
   ```

## Commands

### List all accessible bases
```bash
python3 /mnt/skills/user/airtable/scripts/airtable.py list-bases
```

### List tables in a base
```bash
python3 /mnt/skills/user/airtable/scripts/airtable.py list-tables <base_id>
```

### List records in a table
```bash
python3 /mnt/skills/user/airtable/scripts/airtable.py list-records <base_id> "Table Name"
python3 /mnt/skills/user/airtable/scripts/airtable.py list-records <base_id> "Table Name" --limit 50
```

### Filter records with a formula
```bash
python3 /mnt/skills/user/airtable/scripts/airtable.py list-records <base_id> "Tasks" --filter "{Status}='Done'"
python3 /mnt/skills/user/airtable/scripts/airtable.py list-records <base_id> "Contacts" --filter "NOT({Email}='')"
```

### Filter to specific fields only
```bash
python3 /mnt/skills/user/airtable/scripts/airtable.py list-records <base_id> "People" --fields "Name,Email,Company"
```

### Use a specific view
```bash
python3 /mnt/skills/user/airtable/scripts/airtable.py list-records <base_id> "Tasks" --view "Active Tasks"
```

### Get a specific record
```bash
python3 /mnt/skills/user/airtable/scripts/airtable.py get-record <base_id> "Table Name" <record_id>
```

### Search records
```bash
python3 /mnt/skills/user/airtable/scripts/airtable.py search-records <base_id> "Contacts" "Smith"
python3 /mnt/skills/user/airtable/scripts/airtable.py search-records <base_id> "Contacts" "smith@acme.com" --field "Email"
```

## Notes

- Free plan: unlimited bases, 1,000 records per base. API reads work on free.
- Base IDs start with `app`, record IDs start with `rec`.
- Table names are case-sensitive and must match exactly. Use quotes if the name has spaces.
- Airtable deprecated old API keys in Feb 2024. Only Personal Access Tokens (PAT) work now.
