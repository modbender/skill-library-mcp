# Google Drive via TapAuth

## Provider Key

Use `google_drive` as the provider name. This is a focused variant of the `google` provider — it only offers Drive-related scopes for a simpler approval flow.

## Available Scopes

| Scope | Access |
|-------|--------|
| `drive.readonly` | View files in Google Drive |
| `drive.file` | Create & edit files in Google Drive |

## Example: Create a Grant

```bash
./scripts/tapauth.sh google_drive "drive.readonly" "Drive Browser"
```

## Example: List Files

```bash
curl -H "Authorization: Bearer <token>" \
  "https://www.googleapis.com/drive/v3/files?pageSize=10"
```

## Example: Download a File

```bash
curl -H "Authorization: Bearer <token>" \
  "https://www.googleapis.com/drive/v3/files/FILE_ID?alt=media" -o output.pdf
```

## Example: Upload a File

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart" \
  -F "metadata={\"name\":\"test.txt\"};type=application/json" \
  -F "file=@test.txt"
```

## Gotchas

- **Use `google_drive` vs `google`:** If you only need Drive access, prefer `google_drive` — the user sees a simpler consent screen with fewer scopes.
- **`drive.file` scope:** Only grants access to files created by or explicitly opened with TapAuth, not the user's entire Drive.
- **Token refresh:** Google tokens expire after ~1 hour. Call the TapAuth token endpoint again to get a fresh one.
- **Export formats:** Google-native files (Docs, Sheets) must be exported. Use `?alt=media&mimeType=application/pdf` for PDF export.

## Recommended Minimum Scopes

| Use Case | Scopes |
|----------|--------|
| Browse files | `drive.readonly` |
| Create & edit files | `drive.file` |
