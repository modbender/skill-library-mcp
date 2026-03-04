# Sensitive Data Masker - Design Document

## 🎯 Project Overview

Intelligent sensitive data detection and masking at OpenClaw Gateway layer, protecting user privacy while supporting local restoration for task execution.

---

## 🏗️ Architecture

### Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Message                          │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Channel Plugin (Feishu/Telegram/etc)        │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│           OpenClaw Gateway (message:received)           │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│        Sensitive Data Masker Hook (Intercept Point)     │
│  ┌───────────────────────────────────────────────────┐  │
│  │  1. Presidio Intelligent Detection (NLP + Rules)  │  │
│  │  2. SQLite + Cache Store Mapping                  │  │
│  │  3. Masking Processing                            │  │
│  └───────────────────────────────────────────────────┘  │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Masked Message                              │
│         "[PASSWORD:xxx], help me configure database"     │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Send to LLM API (Safe)                      │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              LLM Returns Result                          │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│         Restore Sensitive Data Before Task Execution    │
│         "password=MySecret123, help me configure"        │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Execute Task with Restored Data             │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Technology Selection

### 1️⃣ Detection Engine: Microsoft Presidio

**Reasons**:
- ✅ Microsoft open-source, enterprise-grade
- ✅ NLP + rules dual detection
- ✅ 100% local execution
- ✅ Support 50+ languages
- ✅ MIT license, completely free

**Detection Capabilities**:
- Names, addresses, phone numbers
- Email, ID cards, credit cards
- Passwords, API Keys, Tokens
- Database connection strings
- Custom detectors

### 2️⃣ Storage: SQLite + LRU Cache

**Reasons**:
- ✅ Query speed O(log n) vs JSON O(n)
- ✅ Support indexes and transactions
- ✅ Auto-expiry cleanup
- ✅ Zero configuration, Python built-in
- ✅ Concurrent safe

**Performance Metrics**:
- Hot query: < 0.1ms (memory cache)
- Cold query: ~0.5ms (SQLite)
- Write: < 2ms
- Support: 100,000+ records

### 3️⃣ Integration: OpenClaw Hook

**Event**: `message:received`

**Benefits**:
- ✅ No need to modify Channel plugins
- ✅ Unified handling for all channels
- ✅ Easy maintenance and upgrade

---

## 📦 Component Design

### Component 1: Presidio Detector

```python
class PresidioDetector:
    """Use Microsoft Presidio for intelligent detection."""
    
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self._load_custom_patterns()
    
    def detect(self, text: str, language='zh') -> list:
        """Detect sensitive information."""
        results = self.analyzer.analyze(
            text=text,
            language=language,
            entities=self.entities
        )
        return results
    
    def _load_custom_patterns(self):
        """Load custom detection patterns (API Key, etc.)."""
        # Alibaba Cloud AccessKey
        # GitHub Token
        # Database connection strings
        # ...
```

### Component 2: Mapping Store

```python
class SensitiveMappingStore:
    """SQLite + LRU cache storage."""
    
    def __init__(self, db_path: str, cache_size: int = 1000):
        self.db_path = db_path
        self.cache = {}
        self.cache_max_size = cache_size
        self._init_db()
    
    def add(self, original: str, data_type: str, ttl_days: int = 7) -> str:
        """Add mapping, return mask_id."""
        mask_id = self._generate_id()
        self._write_db(mask_id, original, data_type, ttl_days)
        self.cache[mask_id] = original
        return mask_id
    
    def get(self, mask_id: str) -> Optional[str]:
        """Get original data (with cache)."""
        if mask_id in self.cache:
            return self.cache[mask_id]
        
        original = self._query_db(mask_id)
        if original:
            self.cache[mask_id] = original
            self._lru_evict()
        return original
    
    def cleanup_expired(self) -> int:
        """Clean expired data."""
        # DELETE FROM mappings WHERE expires_at < now()
```

### Component 3: Masker

```python
class ChannelSensitiveMasker:
    """Channel-level masker."""
    
    def __init__(self):
        self.detector = PresidioDetector()
        self.store = SensitiveMappingStore()
    
    def mask_message(self, text: str) -> tuple:
        """Mask message."""
        # 1. Detect
        results = self.detector.detect(text)
        
        # 2. Create mapping and mask
        replacements = []
        masked_text = text
        
        for result in results:
            original = text[result.start:result.end]
            mask_id = self.store.add(original, result.entity_type)
            masked = f"[{result.entity_type}:{mask_id}]"
            masked_text = masked_text.replace(original, masked)
            replacements.append(...)
        
        return masked_text, replacements
    
    def restore_message(self, text: str) -> str:
        """Restore message."""
        # Restore all [TYPE:mask_id] markers from mapping table
```

### Component 4: OpenClaw Hook

```javascript
// handler.js
async function handler(event) {
    if (event.type !== 'message' || event.action !== 'received') {
        return;
    }
    
    const content = event.context.content;
    const masker = new ChannelSensitiveMasker();
    
    // Mask
    const [masked, replacements] = masker.mask_message(content);
    
    // Update event
    event.context.content = masked;
    
    // Log
    if (replacements.length > 0) {
        console.log(`[sensitive-masker] Masked ${replacements.length} items`);
    }
}
```

---

## 🗄️ Database Design

### Table Schema

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

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| **mask_id** | TEXT | 16-character hash, primary key |
| **original** | TEXT | Original sensitive data (encrypted storage) |
| **data_type** | TEXT | Data type (PASSWORD, API_KEY, etc.) |
| **created_at** | TIMESTAMP | Creation time |
| **expires_at** | TIMESTAMP | Expiry time (7 days later) |
| **usage_count** | INTEGER | Usage count (for audit) |

---

## 🔐 Security Design

### 1️⃣ File Permissions

```bash
# Database file
chmod 600 ~/.openclaw/data/sensitive-masker/mapping.db

# Configuration file
chmod 600 ~/.openclaw/config/sensitive-masker.json
```

### 2️⃣ Data Encryption

```python
from cryptography.fernet import Fernet

# Encrypt original data
key = load_key()
f = Fernet(key)
encrypted = f.encrypt(original.encode())

# Store to database
cursor.execute('INSERT ... VALUES (?, ?, ...)', (mask_id, encrypted, ...))
```

### 3️⃣ Auto-Expiry

```python
# Background thread cleans every hour
def cleanup_loop():
    while True:
        time.sleep(3600)
        store.cleanup_expired()  # DELETE WHERE expires_at < now()
```

---

## ⚙️ Configuration Design

### Configuration File

```json
{
  "enabled": true,
  "ttl_days": 7,
  "cache_size": 1000,
  "auto_cleanup": true,
  "cleanup_interval_hours": 1,
  "log_enabled": true,
  "encrypt_storage": true,
  "presidio": {
    "language": "zh",
    "entities": ["PHONE_NUMBER", "EMAIL_ADDRESS", ...],
    "custom_patterns": true
  }
}
```

### Configuration Location

- `~/.openclaw/config/sensitive-masker.json` - Main config
- `~/.openclaw/data/sensitive-masker/` - Data directory

---

## 📊 Performance Optimization

### 1️⃣ LRU Cache

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached(mask_id: str) -> str:
    return store.get(mask_id)
```

### 2️⃣ Batch Write

```python
def batch_add(self, items: list):
    cursor.executemany('INSERT ...', items)
    conn.commit()
```

### 3️⃣ Async Cleanup

```python
thread = threading.Thread(target=cleanup_loop, daemon=True)
thread.start()
```

---

## 🧪 Testing Strategy

### Unit Tests

```python
def test_mask_password():
    masker = ChannelSensitiveMasker()
    masked, _ = masker.mask_message("password=MySecret123")
    assert "[PASSWORD:" in masked

def test_restore():
    masker = ChannelSensitiveMasker()
    masked, _ = masker.mask_message("password=123")
    restored = masker.restore_message(masked)
    assert restored == "password=123"

def test_cache_performance():
    store = SensitiveMappingStore()
    # Test cache hit rate > 90%
```

### Integration Tests

```python
def test_hook_integration():
    # Simulate OpenClaw event
    event = {
        'type': 'message',
        'action': 'received',
        'context': {'content': 'password=123'}
    }
    
    # Call Hook
    handler(event)
    
    # Verify masking
    assert "[PASSWORD:" in event.context.content
```

### Performance Tests

```python
def test_performance():
    masker = ChannelSensitiveMasker()
    
    # Test 1000 queries
    start = time.time()
    for i in range(1000):
        masker.mask_message(f"password=secret{i}")
    elapsed = time.time() - start
    
    assert elapsed < 1.0  # < 1ms/query
```

---

## 📝 Deployment Checklist

### 1️⃣ Install Dependencies

```bash
pip install presidio-analyzer presidio-anonymizer
python -m spacy download zh_core_web_sm
```

### 2️⃣ Create Hook

```bash
mkdir -p ~/.openclaw/workspace/hooks/sensitive-masker
# Copy handler.js, masker-wrapper.py, etc.
```

### 3️⃣ Enable Hook

```bash
openclaw hooks enable sensitive-masker
openclaw hooks check
```

### 4️⃣ Test

```bash
# Send test message
# "My password is MySecret123"

# View logs
# [sensitive-masker] Masked 1 sensitive item
```

---

## 🎯 Key Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| **Detection Engine** | Presidio | Industry-leading, NLP+rules |
| **Storage** | SQLite + Cache | Performance + zero config |
| **Integration** | OpenClaw Hook | No plugin modification |
| **TTL** | 7 days | Balance security and availability |
| **Encryption** | Optional | Performance vs security |
| **Cache Size** | 1000 | Memory usage < 1MB |

---

## 📋 Future Extensions

1. **Support image OCR masking**
2. **Support structured data (JSON/XML)**
3. **Multi-tenant isolation**
4. **Audit log export**
5. **Custom masking policies**

---

*Design completed: 2026-03-03*
