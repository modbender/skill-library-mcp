# Google Sheets via TapAuth

## Provider Key

Use `google_sheets` as the provider name.

## Available Scopes

| Scope | Access |
|-------|--------|
| `spreadsheets.readonly` | View spreadsheets |
| `spreadsheets` | Full read/write access to spreadsheets |

## Example: Create a Grant

```bash
./scripts/tapauth.sh google_sheets "spreadsheets.readonly" "Sheet Reader"
```

## Example: Read a Sheet

```bash
curl -H "Authorization: Bearer <token>" \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values/Sheet1"
```

## Example: Write to a Sheet

```bash
curl -X PUT -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values/Sheet1!A1:B2?valueInputOption=USER_ENTERED" \
  -d '{"values": [["Name", "Score"], ["Alice", 95]]}'
```

## Example: Append Rows

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values/Sheet1:append?valueInputOption=USER_ENTERED" \
  -d '{"values": [["Bob", 88]]}'
```

## Gotchas

- **Spreadsheet ID:** The ID is in the URL: `docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit`
- **Range notation:** Use A1 notation (e.g., `Sheet1!A1:C10`). Sheet name is optional if there's only one sheet.
- **valueInputOption:** Use `USER_ENTERED` for auto-parsing (dates, numbers) or `RAW` for literal strings.
- **Token refresh:** Google tokens expire after ~1 hour. Call the TapAuth token endpoint again to get a fresh one.

## Recommended Minimum Scopes

| Use Case | Scopes |
|----------|--------|
| Read spreadsheets | `spreadsheets.readonly` |
| Read & write | `spreadsheets` |
