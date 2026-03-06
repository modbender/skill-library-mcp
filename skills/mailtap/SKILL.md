---
name: MailTap - Temporary Email Service
description: This skill provides seamless access to the MailTap Public API, a
  free temporary email service that generates disposable email addresses valid
  for 30 minutes.
---

# MailTap - Temporary Email Service

**Version:** 1.0.4\
**Author:** Web3 Hungry\
**Author Handle:** @zororaka00\
**Author Profile:** [https://x.com/web3hungry](https://x.com/web3hungry)\
**Homepage:** [https://www.mailtap.org](https://www.mailtap.org)\
**Category:** Utilities → Automation → Privacy & Verification\
**Tags:** `temporary-email`

## Overview

This skill provides seamless access to the MailTap Public API, a free temporary email service that generates disposable email addresses valid for 30 minutes.

No authentication or API key is required — all endpoints are public and use simple HTTP GET requests.

This skill does not store, proxy, or modify any email data. All operations communicate directly with the official MailTap public API.

**Ideal for AI agents performing tasks such as:**
- Registering on websites/services without exposing real email addresses
- Capturing verification codes, one-time links, or confirmation emails
- Automating web3 airdrops, form submissions, or testing flows that require email verification
- Privacy-focused workflows where email traceability must be avoided
- Downloading email attachments when available

**Base URL:** `https://api.mailtap.org`

All responses are returned in JSON format.

## Core Capabilities

The skill exposes three primary endpoints:

1. **Generate** a new temporary email address
2. **Retrieve** details of an existing email address
3. **Fetch** all messages in the inbox (including attachments metadata)

Agents can chain operations autonomously (generate → wait → poll inbox → extract data → download attachments).

## Usage Guide for Agents

Agents should use standard HTTP tools (`curl`, `fetch`, `requests`, etc.) to interact with the API.

### 1. Generate New Temporary Email

```bash
curl "https://api.mailtap.org/public/generate"
```

**Example response:**

```json
{
  "address": "abc123xyz@mailtap.com",
  "expires_at": "2026-02-15T04:30:00.000Z",
  "created_at": "2026-02-15T04:00:00.000Z"
}
```

### 2. Get Email Details

```bash
curl "https://api.mailtap.org/public/email/{address}"
```

### 3. Get Inbox Messages

```bash
curl "https://api.mailtap.org/public/inbox/{address}"
```

**Example response with attachment:**

```json
{
  "messages": [
    {
      "id": 1,
      "from_address": "no-reply@example.com",
      "subject": "Your document",
      "body": "Please find the attached file.",
      "received_at": "2026-02-15T04:05:00.000Z",
      "attachments": [
        {
          "filename": "document.pdf",
          "mime_type": "application/pdf",
          "size": 102400,
          "r2_key": "attachments/abc123/document.pdf"
        }
      ]
    }
  ]
}
```

### 4. Download Attachments

Attachments are publicly downloadable via the S3-compatible URL:

`https://s3.mailtap.org/{r2_key}`

**Example:**

```bash
curl -O "https://s3.mailtap.org/attachments/abc123/document.pdf"
```

or

```bash
wget "https://s3.mailtap.org/attachments/abc123/document.pdf"
```

## Recommended Agent Workflow Patterns

**Verification flow:**
1. Generate email
2. Use for signup
3. Poll inbox
4. Extract verification code

**Attachment flow:**
1. Poll inbox
2. If attachments exist → download
3. Process files

**Error handling:**
- If `404` → email expired → generate new address

## Example Prompts for Agents

- "Generate a new temporary email using MailTap"
- "Check inbox for `abc123@mailtap.com` and download attachments"
- "Create temp email, wait up to 2 minutes, extract verification code"

## Python Helper Library (Enhanced)

```python
import requests
import time
import os
from pathlib import Path
from typing import Optional, Dict, Any

BASE_URL = "https://api.mailtap.org"
ATTACHMENT_BASE = "https://s3.mailtap.org"

# Whitelisted attachment types for security
WHITELISTED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg", "image/png", "image/gif",
    "text/plain", "text/csv", "text/html",
    "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}

MAX_FILE_SIZE_MB = 10  # Maximum 10MB for security


def generate_email() -> Dict[str, Any]:
    """Generates a new temporary email address."""
    response = requests.get(f"{BASE_URL}/public/generate")
    response.raise_for_status()
    return response.json()


def get_inbox(address: str) -> Dict[str, Any]:
    """Retrieves the inbox for a given address."""
    response = requests.get(f"{BASE_URL}/public/inbox/{address}")
    if response.status_code == 404:
        return {"error": "Email not found or expired"}
    response.raise_for_status()
    return response.json()


def wait_for_message(address: str, timeout: int = 120, interval: int = 10) -> Dict[str, Any]:
    """Polls the inbox until a message arrives or timeout is reached."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        inbox = get_inbox(address)
        if "error" not in inbox and inbox.get("messages"):
            return inbox["messages"][-1]
        time.sleep(interval)
    return {"error": "Timeout"}


def is_safe_attachment(attachment: Dict[str, Any]) -> bool:
    """Validates attachment safety based on MIME type and size."""
    mime_type = attachment.get("mime_type", "")
    size_mb = attachment.get("size", 0) / (1024 * 1024)
    
    if mime_type not in WHITELISTED_MIME_TYPES:
        return False
    if size_mb > MAX_FILE_SIZE_MB:
        return False
    return True


def download_attachment(r2_key: str, save_path: Optional[str] = None) -> str:
    """Downloads an attachment from the mailtap S3 storage with security checks."""
    
    # Parse attachment info from r2_key
    parts = r2_key.split("/")
    if len(parts) < 2:
        raise ValueError("Invalid r2_key format")
    
    filename = parts[-1]
    if not filename or ".." in filename:
        raise ValueError("Invalid filename detected")
    
    url = f"{ATTACHMENT_BASE}/{r2_key}"
    
    # Get attachment metadata first
    response = requests.head(url, allow_redirects=True)
    response.raise_for_status()
    
    # Validate content type and size
    content_type = response.headers.get("content-type", "")
    content_length = response.headers.get("content-length")
    
    if content_type not in WHITELISTED_MIME_TYPES:
        raise ValueError(f"Unsafe MIME type: {content_type}")
    
    if content_length:
        size_mb = int(content_length) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            raise ValueError(f"File too large: {size_mb:.1f}MB (max {MAX_FILE_SIZE_MB}MB)")
    
    # Download the file
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    if save_path is None:
        save_path = filename
    
    # Ensure safe save path
    save_path = Path(save_path)
    save_path = save_path.resolve()
    
    # Create directory if needed
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(save_path, "wb") as f:
        for chunk in response.iter_content(8192):
            f.write(chunk)
    
    return str(save_path)


def list_attachments(address: str) -> list:
    """Lists all attachments in inbox with security validation."""
    inbox = get_inbox(address)
    if "error" in inbox:
        return []
    
    safe_attachments = []
    for message in inbox.get("messages", []):
        for attachment in message.get("attachments", []):
            if is_safe_attachment(attachment):
                safe_attachments.append(attachment)
    
    return safe_attachments
```

## Security Enhancements

### 1. **Attachment Validation**
- **MIME Type Whitelisting**: Only allows common safe file types (PDF, images, text, office documents)
- **Size Limitation**: Maximum 10MB per file to prevent large file attacks
- **Filename Sanitization**: Prevents path traversal attacks by validating filenames

### 2. **Safe Download Process**
- **Metadata Validation**: Checks content type and size before downloading
- **Sandboxed Download**: Uses safe path resolution to prevent directory traversal
- **Streamed Download**: Downloads in chunks to prevent memory exhaustion

### 3. **Agent Safety Guidelines**
- **Never auto-execute**: Agents should never automatically execute downloaded files
- **Validate before use**: Always validate file type and content before processing
- **Use in sandbox**: For untrusted files, use in isolated environment

## Important Notes & Limitations

- Emails expire automatically after **30 minutes**.
- Attachments are public.
- No authentication required.
- Rate limits are generous for normal usage.
- **Security-first approach**: All downloads are validated for safety.
- **No automatic execution**: Agents must manually validate and process files.
- **User responsibility**: Users should still exercise caution with unknown attachments.

## Example Secure Workflow

```python
# Secure attachment handling
address = "test123@mailtap.com"

# Get inbox and list safe attachments
attachments = list_attachments(address)

for attachment in attachments:
    try:
        # Download with validation
        file_path = download_attachment(attachment["r2_key"])
        print(f"Downloaded safe file: {file_path}")
        
        # Process file (in sandbox if possible)
        # process_file(file_path)
        
    except Exception as e:
        print(f"Failed to download {attachment['filename']}: {e}")
```

## Source & Verification

- **Official service:** [https://www.mailtap.org](https://www.mailtap.org)
- **API root:** [https://api.mailtap.org](https://api.mailtap.org)

This skill is a transparent wrapper around the public MailTap API with enhanced security measures.

## Disclaimer

Use responsibly and comply with MailTap terms of service. While security measures are implemented, users should still exercise caution when handling email attachments from unknown sources.

Created and maintained by Web3 Hungry.
Updated for security compliance.