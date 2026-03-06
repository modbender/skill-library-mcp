# Gmail via TapAuth

## Available Scopes

Use the Google scope name without the URL prefix. Full URLs also work.

| Scope | Access | Full URL |
|-------|--------|----------|
| `gmail.readonly` | Read emails and labels | `https://www.googleapis.com/auth/gmail.readonly` |
| `gmail.send` | Send emails only | `https://www.googleapis.com/auth/gmail.send` |
| `gmail.modify` | Read, send, and modify (labels, archive) | `https://www.googleapis.com/auth/gmail.modify` |
| `gmail.compose` | Create and send drafts | `https://www.googleapis.com/auth/gmail.compose` |
| `gmail.labels` | Manage labels | `https://www.googleapis.com/auth/gmail.labels` |

For full Gmail access, use the full URL: `https://mail.google.com/`

## Example: Read Recent Emails

```bash
# 1. Get a token
./scripts/tapauth.sh google "gmail.readonly" "Email Reader"

# 2. List messages
curl -H "Authorization: Bearer <token>" \
  "https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=5"

# 3. Read a specific message
curl -H "Authorization: Bearer <token>" \
  "https://gmail.googleapis.com/gmail/v1/users/me/messages/MSG_ID?format=full"
```

## Example: Send an Email

```bash
# Base64url-encode the email
EMAIL=$(printf "To: recipient@example.com\r\nSubject: Hello\r\nContent-Type: text/plain\r\n\r\nHello from my agent!" | base64 | tr '+/' '-_' | tr -d '=')

curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  "https://gmail.googleapis.com/gmail/v1/users/me/messages/send" \
  -d "{\"raw\": \"$EMAIL\"}"
```

## Gotchas

- **Provider name:** Use `google` as the provider — Gmail scopes are part of the Google provider in TapAuth. There is no separate `gmail` provider.
- **Scope names:** Use Google's actual scope names without the URL prefix (e.g. `gmail.readonly`, not `gmail_read`). Full URLs also work.
- **Token refresh:** Same as Google — tokens expire after ~1 hour. Re-call the token endpoint for a fresh one.
- **Sensitive scopes:** Gmail scopes are classified as "sensitive" by Google. Users will see an extra confirmation screen.
- **Email format:** The Gmail API expects RFC 2822 formatted emails, base64url-encoded. Use the raw format.
- **Rate limits:** 250 quota units/second per user. Most operations cost 5-10 units.

## Recommended Minimum Scopes

| Use Case | Scopes |
|----------|--------|
| Read inbox | `gmail.readonly` |
| Send emails | `gmail.send` |
| Read + send | `gmail.readonly`, `gmail.send` |
| Full management | `gmail.modify` |
