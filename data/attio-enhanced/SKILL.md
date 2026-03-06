---
name: Enhanced Attio Skill
description: Enhanced Attio CRM API skill with batch operations.
---

# Enhanced Attio Skill

Enhanced Attio CRM API skill with batch operations.

## ⚠️ Required Setup

This skill requires Attio credentials. You must set these environment variables before use:

```bash
export ATTIO_API_KEY=your_api_key
export ATTIO_WORKSPACE_ID=your_workspace_id
```

Get API key from: https://app.attio.com/settings/api

Find workspace ID in your Attio URL: `app.attio.com/[workspace-id]/...`

## Features

- **Batch Operations**: Bulk create/update records
- **Retry Logic**: Exponential backoff for rate limits
- **Smart Field Mapping**: Auto-transforms fields to Attio format
- **Company & Person Support**: Create companies, people, deals

## Usage

### Python

```python
import os
os.environ['ATTIO_API_KEY'] = 'your_key'
os.environ['ATTIO_WORKSPACE_ID'] = 'your_workspace'

from lib.attio_enhanced import AttioEnhancedClient

async with AttioEnhancedClient() as client:
    # Create companies
    await client.batch_create_records('companies', [{'name': 'Gameye'}])
    
    # Create people
    await client.batch_create_records('people', [
        {'name': ['John Doe'], 'email_addresses': ['john@example.com']}
    ])
```

### CLI Test

```bash
python3 -c "from lib.attio_enhanced import AttioEnhancedClient; print('OK')"
```

## Field Mapping

- `first_name` + `last_name` → Attio name format
- `email` → email_addresses
- Org → companies
