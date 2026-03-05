# Google Suite Skill

**Version:** 1.0.0
**Category:** Productivity
**Description:** Unified access to Gmail, Google Calendar, and Google Drive APIs for sending, reading, deleting emails, managing calendar events, and handling files.

## Features

### Gmail
- Send emails
- Read emails (list, search, get details)
- Delete emails
- Mark as read/unread

### Google Calendar
- List events
- Create events
- Update events
- Delete events

### Google Drive
- List files
- Upload files
- Download files
- Delete files
- Search files

## Setup

### Prerequisites
- Python 3.8+
- Google Cloud project with OAuth2 credentials
- Enable Gmail, Calendar, and Drive APIs in Google Cloud Console

### Environment Variables
- `GOOGLE_OAUTH_CLIENT_ID` - OAuth2 client ID
- `GOOGLE_OAUTH_CLIENT_SECRET` - OAuth2 client secret
- `GOOGLE_OAUTH_REDIRECT_URI` - OAuth2 redirect URI (e.g., http://localhost:8080/callback)

### Required Scopes
- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/gmail.send`
- `https://www.googleapis.com/auth/gmail.modify`
- `https://www.googleapis.com/auth/calendar`
- `https://www.googleapis.com/auth/drive`

### Token Storage
- Tokens are stored in `google_suite_tokens.json` (by default)

### Installation
```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Usage

### Authentication
1. On first use, the skill will prompt for OAuth2 authentication.
2. Visit the provided URL, log in, and paste the authorization code.
3. Tokens will be saved for future use.

### Example Calls

#### Send Email
```python
skill.execute({
    "service": "gmail",
    "action": "send",
    "to": "user@example.com",
    "subject": "Test Email",
    "body": "Hello from OpenClaw!"
})
```

#### List Emails
```python
skill.execute({
    "service": "gmail",
    "action": "list",
    "query": "from:boss@company.com"
})
```

#### Delete Email
```python
skill.execute({
    "service": "gmail",
    "action": "delete",
    "message_id": "XYZ123..."
})
```

#### List Calendar Events
```python
skill.execute({
    "service": "calendar",
    "action": "list",
    "days": 7
})
```

#### Create Calendar Event
```python
skill.execute({
    "service": "calendar",
    "action": "create",
    "summary": "Team Meeting",
    "start": "2024-03-01T10:00:00",
    "end": "2024-03-01T11:00:00"
})
```

#### List Drive Files
```python
skill.execute({
    "service": "drive",
    "action": "list",
    "query": "name contains 'report'"
})
```

#### Upload File to Drive
```python
skill.execute({
    "service": "drive",
    "action": "upload",
    "file_path": "./myfile.pdf"
})
```

## Security
- OAuth2 tokens are stored securely and never logged.
- All credentials are loaded from environment variables.
- No sensitive data is printed or logged.

## Troubleshooting
- Ensure all required APIs are enabled in Google Cloud Console.
- Check that OAuth2 credentials are correct and match the redirect URI.
- Delete `google_suite_tokens.json` to force re-authentication if needed.

## References
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)
- [Gmail API Docs](https://developers.google.com/gmail/api)
- [Calendar API Docs](https://developers.google.com/calendar/api)
- [Drive API Docs](https://developers.google.com/drive/api)
