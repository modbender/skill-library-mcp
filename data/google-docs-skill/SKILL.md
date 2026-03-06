---
name: Google Docs API Integration
description: Direct access to the Google Docs API using OAuth 2.0. Create
  documents, insert and format text, and manage document content.
---

# Google Docs API Integration

Direct access to the Google Docs API using OAuth 2.0. Create documents, insert and format text, and manage document content.

## Prerequisites

1. **Google Cloud Project Setup**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing one
   - Enable the Google Docs API
   - Create OAuth 2.0 credentials (Desktop app or Web application)
   - Download the credentials JSON file

2. **Environment Setup**
   ```bash
   export GOOGLE_CLIENT_ID="your-client-id"
   export GOOGLE_CLIENT_SECRET="your-client-secret"
   export GOOGLE_REFRESH_TOKEN="your-refresh-token"
   ```

## Authentication

### Getting OAuth Tokens

Use the following Python script to obtain your refresh token (one-time setup):

```python
import urllib.request
import urllib.parse
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

# OAuth configuration
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8080'
SCOPES = 'https://www.googleapis.com/auth/documents'

# Step 1: Get authorization code
auth_url = (
    f"https://accounts.google.com/o/oauth2/v2/auth?"
    f"client_id={CLIENT_ID}&"
    f"redirect_uri={REDIRECT_URI}&"
    f"response_type=code&"
    f"scope={urllib.parse.quote(SCOPES)}&"
    f"access_type=offline&"
    f"prompt=consent"
)

print(f"Opening browser for authorization...")
webbrowser.open(auth_url)

# Step 2: Capture authorization code
auth_code = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        auth_code = params.get('code', [None])[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html><body><h1>Authorization successful!</h1><p>You can close this window.</p></body></html>')

server = HTTPServer(('localhost', 8080), OAuthHandler)
server.handle_request()

# Step 3: Exchange code for tokens
if auth_code:
    data = urllib.parse.urlencode({
        'code': auth_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }).encode()
    
    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
    response = json.load(urllib.request.urlopen(req))
    
    print(f"\nRefresh Token: {response['refresh_token']}")
    print(f"Access Token: {response['access_token']}")
    print(f"\nSet your refresh token:")
    print(f"export GOOGLE_REFRESH_TOKEN=\"{response['refresh_token']}\"")
```

### Getting Access Token

Before making API calls, get a fresh access token:

```python
import urllib.request
import urllib.parse
import json
import os

def get_access_token():
    """Get a fresh access token using refresh token"""
    data = urllib.parse.urlencode({
        'client_id': os.environ['GOOGLE_CLIENT_ID'],
        'client_secret': os.environ['GOOGLE_CLIENT_SECRET'],
        'refresh_token': os.environ['GOOGLE_REFRESH_TOKEN'],
        'grant_type': 'refresh_token'
    }).encode()
    
    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
    response = json.load(urllib.request.urlopen(req))
    return response['access_token']

# Store for reuse
access_token = get_access_token()
print(f"Access Token: {access_token}")
```

## Base URL

```
https://docs.googleapis.com/v1
```

All requests require the access token in the Authorization header:

```
Authorization: Bearer {access_token}
```

## Quick Start

```python
import urllib.request
import json
import os

# Get access token first (using function from above)
access_token = get_access_token()

# Get document
req = urllib.request.Request('https://docs.googleapis.com/v1/documents/{documentId}')
req.add_header('Authorization', f'Bearer {access_token}')
doc = json.load(urllib.request.urlopen(req))
print(json.dumps(doc, indent=2))
```

## API Reference

### Create Document

```python
import urllib.request
import json

access_token = get_access_token()

data = json.dumps({'title': 'My New Document'}).encode()
req = urllib.request.Request(
    'https://docs.googleapis.com/v1/documents',
    data=data,
    method='POST'
)
req.add_header('Authorization', f'Bearer {access_token}')
req.add_header('Content-Type', 'application/json')

response = json.load(urllib.request.urlopen(req))
doc_id = response['documentId']
print(f"Created document: {doc_id}")
print(f"URL: https://docs.google.com/document/d/{doc_id}/edit")
```

### Get Document

```python
req = urllib.request.Request(
    f'https://docs.googleapis.com/v1/documents/{doc_id}'
)
req.add_header('Authorization', f'Bearer {access_token}')
doc = json.load(urllib.request.urlopen(req))
```

### Batch Update Document

```python
# Insert text at beginning
updates = {
    'requests': [
        {
            'insertText': {
                'location': {'index': 1},
                'text': 'Hello, World!\n\n'
            }
        }
    ]
}

data = json.dumps(updates).encode()
req = urllib.request.Request(
    f'https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate',
    data=data,
    method='POST'
)
req.add_header('Authorization', f'Bearer {access_token}')
req.add_header('Content-Type', 'application/json')

response = json.load(urllib.request.urlopen(req))
```

## Common Operations

### Insert Text

```python
{
    'requests': [
        {
            'insertText': {
                'location': {'index': 1},
                'text': 'Your text here'
            }
        }
    ]
}
```

### Format Text (Bold, Italic, Font Size)

```python
{
    'requests': [
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': 10
                },
                'textStyle': {
                    'bold': True,
                    'italic': True,
                    'fontSize': {
                        'magnitude': 14,
                        'unit': 'PT'
                    }
                },
                'fields': 'bold,italic,fontSize'
            }
        }
    ]
}
```

### Insert Table

```python
{
    'requests': [
        {
            'insertTable': {
                'location': {'index': 1},
                'rows': 3,
                'columns': 4
            }
        }
    ]
}
```

### Replace Text

```python
{
    'requests': [
        {
            'replaceAllText': {
                'containsText': {
                    'text': '{{placeholder}}',
                    'matchCase': True
                },
                'replaceText': 'Actual value'
            }
        }
    ]
}
```

### Delete Content

```python
{
    'requests': [
        {
            'deleteContentRange': {
                'range': {
                    'startIndex': 1,
                    'endIndex': 50
                }
            }
        }
    ]
}
```

### Insert Page Break

```python
{
    'requests': [
        {
            'insertPageBreak': {
                'location': {'index': 1}
            }
        }
    ]
}
```

### Update Paragraph Style

```python
{
    'requests': [
        {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': 50
                },
                'paragraphStyle': {
                    'namedStyleType': 'HEADING_1',
                    'alignment': 'CENTER'
                },
                'fields': 'namedStyleType,alignment'
            }
        }
    ]
}
```

## Complete Example: Create and Format Document

```python
import urllib.request
import urllib.parse
import json
import os

def get_access_token():
    """Get fresh access token"""
    data = urllib.parse.urlencode({
        'client_id': os.environ['GOOGLE_CLIENT_ID'],
        'client_secret': os.environ['GOOGLE_CLIENT_SECRET'],
        'refresh_token': os.environ['GOOGLE_REFRESH_TOKEN'],
        'grant_type': 'refresh_token'
    }).encode()
    
    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
    response = json.load(urllib.request.urlopen(req))
    return response['access_token']

def create_document(title, access_token):
    """Create a new document"""
    data = json.dumps({'title': title}).encode()
    req = urllib.request.Request(
        'https://docs.googleapis.com/v1/documents',
        data=data,
        method='POST'
    )
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Content-Type', 'application/json')
    
    response = json.load(urllib.request.urlopen(req))
    return response['documentId']

def batch_update(doc_id, requests, access_token):
    """Apply batch updates to document"""
    data = json.dumps({'requests': requests}).encode()
    req = urllib.request.Request(
        f'https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate',
        data=data,
        method='POST'
    )
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Content-Type', 'application/json')
    
    return json.load(urllib.request.urlopen(req))

# Main workflow
access_token = get_access_token()

# Create document
doc_id = create_document('Project Report', access_token)
print(f"Created: https://docs.google.com/document/d/{doc_id}/edit")

# Add content with formatting
requests = [
    # Insert title
    {
        'insertText': {
            'location': {'index': 1},
            'text': 'Project Report\n\n'
        }
    },
    # Format title as heading
    {
        'updateParagraphStyle': {
            'range': {'startIndex': 1, 'endIndex': 15},
            'paragraphStyle': {'namedStyleType': 'HEADING_1'},
            'fields': 'namedStyleType'
        }
    },
    # Add body text
    {
        'insertText': {
            'location': {'index': 16},
            'text': 'Executive Summary\n\nThis report covers...\n\n'
        }
    },
    # Format section header
    {
        'updateParagraphStyle': {
            'range': {'startIndex': 16, 'endIndex': 34},
            'paragraphStyle': {'namedStyleType': 'HEADING_2'},
            'fields': 'namedStyleType'
        }
    }
]

batch_update(doc_id, requests, access_token)
print("Document updated successfully!")
```

## Key Concepts

### Document Indexing
- Indices are 1-based (document starts at index 1)
- Each character (including newlines) occupies one index
- To append at the end, use `endOfSegmentLocation`

### Batch Updates
- Multiple requests are applied atomically
- Requests are processed in order
- Get the document first to determine correct indices

### Field Masks
- When updating styles, specify which fields to update
- Use comma-separated field names: `'fields': 'bold,fontSize,foregroundColor'`

## Error Handling

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad Request - Invalid request format |
| 401 | Unauthorized - Invalid or expired access token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Document doesn't exist |
| 429 | Rate Limited - Too many requests |

### Token Refresh
Access tokens expire after 1 hour. If you get a 401 error, refresh the token:

```python
try:
    # Make API call
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {access_token}')
    response = urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    if e.code == 401:
        # Refresh token and retry
        access_token = get_access_token()
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Bearer {access_token}')
        response = urllib.request.urlopen(req)
```

## Best Practices

1. **Token Management**
   - Cache access tokens (valid for 1 hour)
   - Store refresh token securely
   - Implement automatic token refresh

2. **Batch Operations**
   - Combine multiple updates into single batch call
   - Reduces API calls and improves performance

3. **Index Calculation**
   - Always get current document state before updates
   - Account for newline characters (\n)
   - Use `endOfSegmentLocation` for appending

4. **Rate Limits**
   - Google Docs API has quotas (check Cloud Console)
   - Implement exponential backoff for rate limit errors

## Resources

- [Google Docs API Documentation](https://developers.google.com/docs/api)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Document Structure](https://developers.google.com/docs/api/concepts/structure)
- [Request Types Reference](https://developers.google.com/docs/api/reference/rest/v1/documents/request)
- [Python Quickstart](https://developers.google.com/docs/api/quickstart/python)