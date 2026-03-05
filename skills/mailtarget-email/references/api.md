# Mailtarget API Reference

Base URL: `https://transmission.mailtarget.co/v1`

Auth: `Authorization: Bearer <API_KEY>`

## Transmission

### Send Email
`POST /layang/transmissions`

```json
{
  "subject": "string (required)",
  "from": {
    "email": "sender@example.com (required)",
    "name": "Sender Name"
  },
  "replyTo": [{"email": "string", "name": "string"}],
  "to": [{"email": "string (required)", "name": "string"}],
  "cc": [{"email": "string", "name": "string"}],
  "bcc": [{"email": "string", "name": "string"}],
  "bodyText": "plain text fallback",
  "bodyHtml": "<p>HTML content</p>",
  "headers": [{"name": "string", "value": "string"}],
  "attachments": [{
    "contentId": "string",
    "disposition": "string",
    "filename": "string",
    "mimeType": "string",
    "value": "base64-encoded content"
  }],
  "metadata": {"key": "value"},
  "optionsAttributes": {
    "clickTracking": true,
    "openTracking": true,
    "transactional": true
  },
  "templateId": "string",
  "substitutionData": {"key": "value"}
}
```

**Success (200):**
```json
{"message": "Transmission received", "transmissionId": "abc123"}
```

**Error (400):**
```json
{"error": "string", "message": "string"}
```

## Templates

### List Templates
`GET /template?page=1&size=10&search=string`

**Response (200):**
```json
{"count": 1, "data": [{"id": "string", "name": "string", "createdAt": 0, "updatedAt": 0}]}
```

### Create Template
`POST /template`
```json
{"id": "my-template", "name": "My Template", "html": "<html>...</html>"}
```

## Sending Domains

### List Domains
`GET /domain/sending?page=1&size=10&search=string&status=string`

**Response (200):**
```json
{
  "count": 1,
  "sendingDomain": [{
    "id": 1, "domain": "example.com", "status": "verified",
    "default": true, "types": ["sending"], "assignment": "string",
    "companyId": 1, "subAccountID": 1, "subAccountName": "string"
  }]
}
```

### Create Sending Domain
`POST /domain/sending`
```json
{"domain": "example.com", "assignment": "Share with all Subaccounts", "note": "string"}
```

### Get Domain Detail
`GET /domain/sending/{id}`

### Delete Domain
`DELETE /domain/sending/{id}`

### Get Unverified SPF
`GET /domain/sending/unverified-spf`

### Get SPF Suggestion
`GET /domain/sending/{id}/spf-suggestion`

### Verify TXT Domain
`PUT /domain/sending/{id}/verify-txt`

## API Keys

### List Keys
`GET /api-key?page=1&size=10&search=string&sort=string&subAccountId=1&permissionType=string`

### Create Key
`POST /api-key`
```json
{"name": "string", "allowedIp": "123.123.123.123", "permissionIds": [1]}
```

### Get Key Detail
`GET /api-key/{id}`

### Update Key
`PUT /api-key/{id}`

### Delete Key
`DELETE /api-key/{id}`

## Sub Accounts

### List Sub Accounts
`GET /sub-account?page=1&size=10&search=string`

### Create Sub Account
`POST /sub-account`

### Get / Update / Delete Sub Account
`GET|PUT|DELETE /sub-account/{id}`

## Permissions

### List Permissions
`GET /permission`
