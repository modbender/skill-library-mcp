# Sensitive Data Masker - README

## 🚀 Quick Start

### Installation

```bash
# Install Microsoft Presidio
pip install presidio-analyzer presidio-anonymizer

# Install spaCy NLP
python3 -m spacy download zh_core_web_sm

# Enable OpenClaw Hook
openclaw hooks enable sensitive-data-masker
```

### How It Works

```
User Message → Presidio Detection → Mask → Send to API
                                            ↓
                                    Store Mapping (7 days)
                                            ↓
                                    Restore Before Execution
```

### Example

**Input**:
```
My password is MySecret123, email is user@example.com
```

**Masked** (sent to API):
```
My password is [PASSWORD:xxx], email is [EMAIL_ADDRESS:yyy]
```

**Restored** (for local execution):
```
My password is MySecret123, email is user@example.com
```

---

## 🔍 Detection Types

- 🔐 PASSWORD
- 🔑 API_KEY
- 📧 EMAIL_ADDRESS
- 📞 PHONE_NUMBER
- 💳 CREDIT_CARD
- 🔗 DB_CONNECTION
- And 20+ more entity types

---

## ⚙️ Configuration

File: `~/.openclaw/data/sensitive-masker/config.json`

```json
{
  "enabled": true,
  "ttl_days": 7,
  "cache_size": 1000,
  "auto_cleanup": true
}
```

---

## 📊 Performance

| Operation | Latency |
|-----------|---------|
| Hot query | < 0.1ms |
| Cold query | ~0.5ms |
| Write | < 2ms |

---

## 📖 Full Documentation

See [SKILL.md](SKILL.md) for complete usage guide and API reference.

See [DESIGN.md](DESIGN.md) for architecture details.

---

*Version: 1.0.0 | Author: TK | Source: https://gitee.com/subline/onepeace*
