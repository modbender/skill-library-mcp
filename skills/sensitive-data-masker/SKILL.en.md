---
name: sensitive-data-masker
description: Intelligent sensitive data detection and masking. Uses Microsoft Presidio + SQLite for automatic PII redaction with local restoration support.
homepage: https://gitee.com/subline/onepeace/tree/develop/src/skills/sensitive-data-masker
metadata:
  {
    "openclaw":
      {
        "emoji": "🔐",
        "events": ["message:received"],
        "requires": { 
          "bins": ["python3"],
          "python_packages": ["presidio-analyzer", "presidio-anonymizer", "spacy"]
        },
        "install": [
          {
            "id": "pip",
            "kind": "pip",
            "package": "presidio-analyzer presidio-anonymizer",
            "label": "Install Microsoft Presidio"
          },
          {
            "id": "spacy",
            "kind": "pip",
            "package": "spacy",
            "label": "Install spaCy NLP"
          },
          {
            "id": "spacy-model",
            "kind": "command",
            "command": "python3 -m spacy download zh_core_web_sm",
            "label": "Download Chinese NLP model"
          }
        ]
      }
  }
---

# Sensitive Data Masker

Intelligent sensitive data detection and masking using Microsoft Presidio with SQLite + LRU cache storage.

## Features

- ✅ **Intelligent detection** - Microsoft Presidio (NLP + rules)
- ✅ **Fast storage** - SQLite + LRU cache
- ✅ **Local restoration** - 7-day temporary mapping table
- ✅ **Auto cleanup** - Expired entries removed automatically
- ✅ **100% local** - No external API required
- ✅ **OpenClaw Hook** - Automatic masking on message received

## How It Works

```
User Message
    ↓
Channel Plugin (Feishu/Telegram/etc)
    ↓
OpenClaw Gateway (message:received)
    ↓
Sensitive Data Masker Hook ← Intercept here
    ↓
Presidio Detection (NLP + Rules)
    ↓
SQLite + Cache Store Mapping
    ↓
Masked Message
    ↓
Send to LLM API (Safe)
    ↓
Restore Before Task Execution
    ↓
Execute with Original Data
```

## Detection Types

| Type | Examples | Masked As |
|------|----------|-----------|
| **PASSWORD** | `password=MySecret123` | `[PASSWORD:xxx]` |
| **API_KEY** | `sk-abcdefghijklmnop` | `[API_KEY:xxx]` |
| **TOKEN** | `token=xyz123` | `[TOKEN:xxx]` |
| **SECRET** | `secret=abc+/==` | `[SECRET:xxx]` |
| **PRIVATE_KEY** | `BEGIN RSA PRIVATE KEY` | `[PRIVATE_KEY:xxx]` |
| **DB_CONNECTION** | `mongodb://user:pass@host` | `[DB_CONNECTION:xxx]` |
| **EMAIL_ADDRESS** | `user@example.com` | `[EMAIL_ADDRESS:xxx]` |
| **PHONE_NUMBER** | `13800138000` | `[PHONE_NUMBER:xxx]` |
| **CREDIT_CARD** | `4111111111111111` | `[CREDIT_CARD:xxx]` |
| **PERSON** | John Doe | `[PERSON:xxx]` |
| **LOCATION** | 123 Main St | `[LOCATION:xxx]` |
| **URL** | `https://example.com` | `[URL:xxx]` |

## Installation

```bash
# Install dependencies
pip install presidio-analyzer presidio-anonymizer
python3 -m spacy download zh_core_web_sm

# Enable Hook
openclaw hooks enable sensitive-data-masker

# Verify
openclaw hooks check
```

## Usage Examples

### User sends:
```
My password is MySecret123, email is user@example.com
```

### Masked (to API):
```
My password is [PASSWORD:f2ae1ea6], email is [EMAIL_ADDRESS:96770696]
```

### Mapping stored (7 days):
```json
{
  "f2ae1ea6": "password=MySecret123",
  "96770696": "user@example.com"
}
```

### Local restoration (for task execution):
```
My password is MySecret123, email is user@example.com
```

## Configuration

**File**: `~/.openclaw/data/sensitive-masker/config.json`

```json
{
  "enabled": true,
  "ttl_days": 7,
  "cache_size": 1000,
  "auto_cleanup": true,
  "cleanup_interval_hours": 1,
  "log_enabled": true,
  "encrypt_storage": false,
  "presidio": {
    "language": "zh",
    "entities": ["PHONE_NUMBER", "EMAIL_ADDRESS", ...],
    "custom_patterns": true
  }
}
```

## Management Commands

```bash
# Test masking
python3 sensitive-masker.py test "my password=123"

# View statistics
python3 sensitive-masker.py stats

# Cleanup expired
python3 sensitive-masker.py cleanup

# Clear all mappings
python3 sensitive-masker.py clear
```

## Performance

| Operation | Latency |
|-----------|---------|
| Hot query (cache) | < 0.1ms |
| Cold query (SQLite) | ~0.5ms |
| Write | < 2ms |
| Max records | 100,000+ |

**Cache hit rate**: > 90% typical

## Security Features

- ✅ File permissions: 600 (owner read/write only)
- ✅ SQLite transaction safety
- ✅ Auto-expiry cleanup
- ✅ LRU cache eviction
- ✅ Local storage only
- ✅ Optional encryption at rest

## Architecture

### Components

1. **PresidioDetector** - Microsoft Presidio integration
2. **SensitiveMappingStore** - SQLite + LRU cache
3. **ChannelSensitiveMasker** - Main masking logic
4. **OpenClaw Hook** - Gateway integration

### Database Schema

```sql
CREATE TABLE mappings (
    mask_id TEXT PRIMARY KEY,
    original TEXT NOT NULL,
    data_type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    usage_count INTEGER DEFAULT 0
);

CREATE INDEX idx_expires_at ON mappings(expires_at);
CREATE INDEX idx_data_type ON mappings(data_type);
```

## Files

```
sensitive-data-masker/
├── SKILL.md                    # This file (English)
├── SKILL.md                    # Chinese version
├── sensitive-masker.py         # Core script
├── handler.js                  # OpenClaw Hook
├── masker-wrapper.py           # Python wrapper
├── DESIGN.md                   # Design document
├── README.md                   # User guide
├── RESEARCH-EXISTING-SOLUTIONS.md  # Market research
└── _meta.json                  # Metadata
```

## Version History

### v1.0.0 (2026-03-03)
- Initial release
- Microsoft Presidio integration
- SQLite + LRU cache storage
- OpenClaw Hook support
- 7-day TTL mapping table
- Auto cleanup

## Repository

**Source**: https://gitee.com/subline/onepeace/tree/develop/src/skills/sensitive-data-masker

**License**: MIT

**Author**: TK

**Issues**: https://gitee.com/subline/onepeace/issues

## Credits

- **Microsoft Presidio** - https://github.com/microsoft/presidio
- **spaCy** - https://spacy.io/
- **OpenClaw** - https://github.com/openclaw/openclaw

## Related Skills

- `ssh-batch-manager` - Batch SSH key management
- `healthcheck` - Security hardening and audits
- `skill-creator` - Create new skills
