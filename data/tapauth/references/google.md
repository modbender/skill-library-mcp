# Google Workspace via TapAuth

## Available Scopes

Use the Google scope name without the URL prefix. Full URLs also work.

| Scope | Access | Full URL |
|-------|--------|----------|
| `drive.readonly` | Read Google Drive files | `https://www.googleapis.com/auth/drive.readonly` |
| `drive.file` | Create & edit Drive files | `https://www.googleapis.com/auth/drive.file` |
| `calendar.readonly` | Read calendar events | `https://www.googleapis.com/auth/calendar.readonly` |
| `calendar.events` | Full calendar access | `https://www.googleapis.com/auth/calendar.events` |
| `spreadsheets.readonly` | Read Google Sheets | `https://www.googleapis.com/auth/spreadsheets.readonly` |
| `spreadsheets` | Full Sheets access | `https://www.googleapis.com/auth/spreadsheets` |
| `documents.readonly` | Read Google Docs | `https://www.googleapis.com/auth/documents.readonly` |
| `documents` | Full Docs access | `https://www.googleapis.com/auth/documents` |
| `contacts.readonly` | Read contacts | `https://www.googleapis.com/auth/contacts.readonly` |
| `contacts` | Full contacts access | `https://www.googleapis.com/auth/contacts` |
| `userinfo.email` | Read user email | `https://www.googleapis.com/auth/userinfo.email` |
| `userinfo.profile` | Read user profile | `https://www.googleapis.com/auth/userinfo.profile` |

## Example: List Drive Files

```bash
# 1. Get a token
./scripts/tapauth.sh google "drive.readonly" "Drive Reader"

# 2. List files
curl -H "Authorization: Bearer <token>" \
  "https://www.googleapis.com/drive/v3/files?pageSize=10"
```

## Example: Read a Google Sheet

```bash
curl -H "Authorization: Bearer <token>" \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values/Sheet1"
```

## Example: List Calendar Events

```bash
curl -H "Authorization: Bearer <token>" \
  "https://www.googleapis.com/calendar/v3/calendars/primary/events?maxResults=10&timeMin=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

## Gotchas

- **Scope names:** Use Google's actual scope names without the URL prefix (e.g. `drive.readonly`, not `drive_read`). Full URLs also work.
- **Token refresh:** Google access tokens expire after ~1 hour. TapAuth handles refresh automatically — just call the token endpoint again to get a fresh token.
- **Unverified app warning:** Users may see a "This app isn't verified" screen. They can click "Advanced" → "Go to TapAuth" to proceed.
- **Readonly preference:** Always prefer read-only scope variants unless you need write access. Higher approval rate.
- **Multiple scopes:** Pass as comma-separated: `"drive.readonly,calendar.readonly"`

## Recommended Minimum Scopes

| Use Case | Scopes |
|----------|--------|
| Browse Drive | `drive.readonly` |
| Read calendar | `calendar.readonly` |
| Read spreadsheet | `spreadsheets.readonly` |
| Full workspace | `drive.file`, `calendar.events`, `spreadsheets`, `documents` |
