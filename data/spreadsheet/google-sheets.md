# Google Sheets — Spreadsheet Skill

## Authentication

```python
# Service Account (automation)
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
service = build('sheets', 'v4', credentials=creds)
```

## Common Operations

```python
# Read
result = service.spreadsheets().values().get(
    spreadsheetId=ID, range='Sheet1!A1:D10'
).execute()

# Write
service.spreadsheets().values().update(
    spreadsheetId=ID, range='Sheet1!A1',
    valueInputOption='USER_ENTERED',
    body={'values': [['A', 'B'], [1, 2]]}
).execute()

# Append
service.spreadsheets().values().append(
    spreadsheetId=ID, range='Sheet1!A:D',
    valueInputOption='USER_ENTERED',
    body={'values': [['new', 'row']]}
).execute()
```

## Best Practices

| Practice | Why |
|----------|-----|
| Batch operations | Avoid rate limits (100 req/100s) |
| `valueInputOption='USER_ENTERED'` | Parses dates, formulas |
| Cache metadata | Reduce API calls |

## Traps

- **Service account needs Editor access** — Share sheet with service email
- **Range notation** — `A:A` (col), `1:1` (row), `A1:D10` (range)
- **Empty cells** — Returned as missing, not null
- **Rate limits** — 300 write req/minute
