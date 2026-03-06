# Local Credential Sources (do not request in chat)

## Allowed Sources
1. Environment variables (preferred for automation)
2. Local credential file
3. Browser autofill in the attached Chrome profile

## Environment Variables
- `SF_LOGIN_URL` (example: https://mydomain.my.salesforce.com or https://test.salesforce.com)
- `SF_USERNAME`
- `SF_PASSWORD`
- `SF_SECURITY_TOKEN` (optional; required for some orgs)

## Local Credential File
Path: `~/.openclaw/credentials/salesforce.json`

Format:
```json
{
  "login_url": "https://mydomain.my.salesforce.com",
  "username": "user@example.com",
  "password": "your_password",
  "security_token": "optional_token"
}
```

## Browser Autofill
If a Chrome profile already has saved credentials:
- Navigate to the login page in the attached tab
- Click the username field and use Chrome autofill
- Never ask the user to paste credentials into chat
