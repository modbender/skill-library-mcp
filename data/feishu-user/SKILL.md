---
name: feishu-user
description: Feishu document operations (User Access Token version). Use user access token for authentication. When you need to read, create, write, or append Feishu documents.
---

# Feishishu document operations using useru User

Fe access token authentication. Call Feishu Open API directly via REST API.

## Install Dependencies

```bash
pip install requests
```

## Quick Start

```python
from feishu_client import FeishuClient

# Initialize client
client = FeishuClient(user_access_token="u-xxx")
```

## Get User Access Token

### Step 1: Get App Credentials from Feishu Open Platform

Prepare the following:
- **APP_ID** - App ID (from Feishu Open Platform app settings)
- **APP_SECRET** - App Secret (from Feishu Open Platform app settings)
- **REDIRECT_URI** - Authorization callback URL

Enable these permissions:
- `docx:document` - Document operations
- `drive:drive.search:readonly` - Cloud drive search
- `search:docs:read` - Document search

### Step 2: Generate Authorization URL

```
https://accounts.feishu.cn/open-apis/authen/v1/authorize?client_id={YOUR_APP_ID}&response_type=code&redirect_uri={YOUR_REDIRECT_URI}&scope=docx%3Adocument%20drive%3Adrive.search%3Areadonly%20search%3Adocs%3Aread
```

### Step 3: Exchange for Token

```bash
curl -X POST "https://open.feishu.cn/open-apis/authen/v1/access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "authorization_code",
    "code": "{YOUR_CODE}",
    "app_id": "{YOUR_APP_ID}",
    "app_secret": "{YOUR_APP_SECRET}"
  }'
```

The returned `access_token` is your `user_access_token`.

---

## Usage Examples

```python
from feishu_client import FeishuClient

# Initialize
client = FeishuClient(user_access_token="u-xxx")

# Read document
content = client.read_doc("doc_token")
print(content)

# Create document
new_token = client.create_doc("My New Document")
print(f"New document: {new_token}")

# Write document
client.write_doc("doc_token", "# Title\n\nContent")

# Append content
client.append_doc("doc_token", "## New Section\n\nMore content")

# List all blocks
blocks = client.list_blocks("doc_token")
for block in blocks:
    print(block)

# Get specific block
block = client.get_block("doc_token", "block_id")

# Update block
client.update_block("doc_token", "block_id", "New content")

# Delete block
client.delete_block("doc_token", "block_id")
```

---

## Convenience Functions

Don't want to create a client? Use functions directly:

```python
from feishu_client import read_document, create_document, write_document, append_document

# Read
content = read_document("doc_token", user_access_token="u-xxx")

# Create
new_token = create_document("Title", user_access_token="u-xxx")

# Write
write_document("doc_token", "# Content", user_access_token="u-xxx")

# Append
append_document("doc_token", "## More", user_access_token="u-xxx")
```

---

## API Reference

### FeishuClient

| Method | Description |
|--------|-------------|
| `read_doc(doc_token)` | Read document content |
| `create_doc(title, folder_token)` | Create new document |
| `write_doc(doc_token, content)` | Write document (overwrite) |
| `append_doc(doc_token, content)` | Append content to end |
| `list_blocks(doc_token)` | List all blocks |
| `get_block(doc_token, block_id)` | Get specific block |
| `update_block(doc_token, block_id, content)` | Update block content |
| `delete_block(doc_token, block_id)` | Delete block |

---

## Notes

1. `user_access_token` has an expiration time, needs periodic refresh
2. The `scope` in authorization URL must be enabled in Feishu Open Platform
3. This skill accesses personal cloud documents using user identity

---

## Related Links

- Feishu Open Platform: https://open.feishu.cn
- Document API: https://open.feishu.cn/document/ukTMukTMukTM/uADOwUjLwgDMzCM4ATm

---

## Token Auto Refresh

Use `feishu_token.py` script for automatic token refresh.

### Install Dependencies

```bash
pip install requests
```

### First Authorization

```bash
# 1. Generate authorization URL
python feishu_token.py --app-id YOUR_APP_ID --app-secret YOUR_SECRET --redirect-uri YOUR_REDIRECT_URI --url
```

After user authorizes, will callback to `YOUR_REDIRECT_URI?code=XXX`

```bash
# 2. Use authorization code to get token
python feishu_token.py --app-id YOUR_APP_ID --app-secret YOUR_SECRET --code AUTH_CODE
```

Token is automatically saved to `~/.config/claw-feishu-user/config.json`

### Refresh Token

```bash
python feishu_token.py --app-id YOUR_APP_ID --app-secret YOUR_SECRET --refresh
```

### In Code

```python
import json
import os

# Read cached token
config_path = os.path.expanduser("~/.config/claw-feishu-user/config.json")
with open(config_path) as f:
    config = json.load(f)

# Use token
client = FeishuClient(user_access_token=config["access_token"])
```
