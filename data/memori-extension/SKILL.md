---
name: memori-extension
description: Memory augmentation and LLM call interception using the Memori Python library with optional Zhipu API integration.
metadata: {
  "openclaw": {
    "emoji": "🧠",
    "user-invocable": false,
    "disable-model-invocation": false,
    "requires": {
      "pip": ["memori"],
      "anyBins": ["python3"],
      "env": {
        "optional": ["MEMORI_TECH_TERMS", "MEMORI_TECH_TERMS_FILE", "ZHIPUAI_API_KEY", "ZHIPUAI_MODEL", "MEMORI_DB_PATH"]
      }
    }
  }
}
---

# Memori Extension Skill

Memory augmentation and LLM call interception using the Memori Python library with optional Zhipu AI API integration.

## Overview

This skill provides memory augmentation and LLM call interception capabilities using the Memori Python library. It enables agents to retrieve relevant knowledge from a memory database and inject it into conversations.

## Security & Privacy Notice

⚠️ **Important**: This skill performs the following operations:

### File Operations (Always Enabled)
- **Read/Write**: Local SQLite database (default: `./memori.db`)
- **Read/Write**: Optional tech terms configuration file (default: `./config/tech_terms.txt`)
- These operations are entirely local and do not transmit data externally.

### External API Calls (Optional - Requires Explicit Configuration)
- **Condition**: Only if `ZHIPUAI_API_KEY` environment variable is set
- **Data Transmitted**: Conversation text (user messages, system prompts, and assistant responses) is sent to Zhipu AI's servers for analysis and augmentation
- **Purpose**: To enhance conversation understanding using Zhipu AI's language models
- **Control**: If `ZHIPUAI_API_KEY` is NOT set, the skill operates 100% locally with NO external network calls

### Recommendations
1. **Start Local-Only**: Test the skill without `ZHIPUAI_API_KEY` first to verify local functionality
2. **Explicit Consent**: Only set `ZHIPUAI_API_KEY` if you explicitly consent to sending conversation data to external services
3. **Review Data**: Consider what conversation data you're comfortable transmitting before enabling external API features
4. **Sandbox Testing**: If providing API keys, test in a sandbox environment first to understand the data flow

## Dependencies

This skill requires the following **Python packages**:

```bash
pip install memori
```

The **memori** library is licensed under **Apache License Version 2.0**.

### Optional Dependencies

For Zhipu API augmentation (optional):

```bash
pip install zhipuai
```

**Warning**: Installing `zhipuai` and providing `ZHIPUAI_API_KEY` enables conversation content to be sent to external servers.

## Environment Variables

### All Supported Environment Variables

| Variable | Description | Required | Default | Privacy Note |
|----------|-------------|-----------|---------|---------------|
| `ZHIPUAI_API_KEY` | Zhipu AI API key for conversation augmentation | **No** | - | ⚠️ **Enables external API calls** - conversation text will be sent to Zhipu AI servers |
| `ZHIPUAI_MODEL` | Zhipu AI model name | **No** | `glm-4.7` | Only used if `ZHIPUAI_API_KEY` is set |
| `MEMORI_TECH_TERMS` | Comma-separated technical terms for LLM interception | **No** | - | Local only |
| `MEMORI_TECH_TERMS_FILE` | Path to file containing technical terms (one per line) | **No** | `./config/tech_terms.txt` | Local only - read/write |
| `MEMORI_DB_PATH` | Path to Memori database | **No** | `./memori.db` | Local only - read/write |

**Privacy & Data Flow Notes**:
- ⚠️ **External API**: Only `ZHIPUAI_API_KEY` enables external network calls. All other variables control local file operations.
- ✅ **Local-Only Mode**: If you omit `ZHIPUAI_API_KEY`, the skill operates 100% locally with no external data transmission.
- 📁 **File Operations**: The skill reads/writes the database (`memori.db`) and optionally the tech terms file (`tech_terms.txt`). These are stored on your local filesystem.
- 🔒 **Best Practice**: Start without `ZHIPUAI_API_KEY` to test local functionality. Only enable external API if you need enhanced features and consent to the data transmission.

### Configuration Examples

**System environment:**
```bash
# Optional: Enable Zhipu API augmentation
export ZHIPUAI_API_KEY="your-api-key"
export ZHIPUAI_MODEL="glm-4.7"

# Optional: Customize technical terms
export MEMORI_TECH_TERMS="FFI,Rust,Linux,kernel,spinlock"

# Optional: Use custom database path
export MEMORI_DB_PATH="/path/to/memori.db"
```

**OpenClaw configuration (`openclaw.json`):**
```json
{
  "skills": {
    "entries": {
      "memori-extension": {
        "enabled": true,
        "env": {
          "ZHIPUAI_API_KEY": "your-api-key",
          "ZHIPUAI_MODEL": "glm-4.7",
          "MEMORI_TECH_TERMS": "FFI,Rust,Linux,kernel",
          "MEMORI_DB_PATH": "./memori.db"
        }
      }
    }
  }
}
```

**Technical terms file** (optional):
```bash
# Create config directory
mkdir -p config

# Create terms file
cat > config/tech_terms.txt << EOF
FFI
Rust
Linux
kernel
spinlock
mutex
unsafe
EOF

# Set environment variable
export MEMORI_TECH_TERMS_FILE="config/tech_terms.txt"
```

## Quick Start

### Method 1: Direct Memori Library (Recommended)

```python
from memori import Memori

memori = Memori(
    db_path="memori.db",
    entity_id="knowledge-base"
)

# Search memories
memories = memori.search("query", limit=5)

# Augment query
context = memori.augment("How to handle spinlock conflicts?", limit=3)

# Store memory
memory_id = memori.store("New content")

# Get stats
stats = memori.get_stats()

# Close
memori.close()
```

### Method 2: Skill Convenience API

```python
from skills.memori_extension import search, augment, intercept_llm

# Search
memories = search("FFI bindings", limit=5)

# Augment
enhanced = augment("How to handle spinlock conflicts?")
if enhanced:
    print(enhanced)

# Intercept LLM
messages = [{"role": "user", "content": "FFI question"}]
enhanced = intercept_llm(messages)
```

## API Reference

### Memori Class

#### `__init__(db_path, entity_id)`

Initialize Memori instance.

**Parameters:**
- `db_path` (str | Path, optional): Database path
- `entity_id` (str, optional): Entity ID, default `"default"`

#### `search(query, limit, entity_id)`

Search for relevant memories.

**Returns:** `List[Memory]`

#### `augment(query, limit, entity_id)`

Augment query with retrieved memories.

**Returns:** `AugmentedContext`

#### `store(content, entity_id, metadata)`

Store a new memory.

**Returns:** `int` - Memory ID

#### `get_stats(entity_id)`

Get statistics.

**Returns:** `dict`

#### `close()`

Close database connection.

### Memory Class

Memory object with attributes:
- `id` (int): Memory ID
- `entity_id` (str): Entity ID
- `content` (str): Memory content
- `created_at` (str): Creation timestamp
- `metadata` (dict, optional): Metadata

### AugmentedContext Class

Augmented context with:
- `original_query` (str): Original query
- `retrieved_memories` (List[Memory]): Retrieved memories
- `enhanced_prompt` (str): Augmented prompt
- `has_memories` (bool): Whether memories were retrieved
- `memories_count` (int): Number of retrieved memories

## Configuration

### Database

Default database path: `./memori.db`

The skill will:
- ✅ **Read** from the database to retrieve memories
- ✅ **Write** to the database when storing new memories
- ✅ **Create** the database file if it doesn't exist

### Technical Terms

The skill uses configurable technical terms for LLM call interception. You can customize these via:

**1. Environment variable** (comma-separated):
```bash
export MEMORI_TECH_TERMS="FFI,Rust,Linux,kernel,spinlock,mutex,unsafe"
```

**2. Configuration file** (one term per line):
```bash
# Create config file
mkdir -p config
cat > config/tech_terms.txt << EOF
FFI
Rust
Linux
kernel
spinlock
mutex
unsafe
EOF

# Set environment variable
export MEMORI_TECH_TERMS_FILE="config/tech_terms.txt"
```

**Note**: If neither is set, the skill will still work but may not intercept technical queries as effectively.

## Security Considerations

### File Operations

This skill performs the following file operations:

| Operation | File | Description |
|-----------|------|-------------|
| Read | `./memori.db` (default) | Retrieve stored memories |
| Write | `./memori.db` (default) | Store new memories |
| Read | `MEMORI_TECH_TERMS_FILE` | Load technical terms |
| Write | `MEMORI_TECH_TERMS_FILE` | Persist terms (if enabled) |

### External API Calls

⚠️ **Important**: If `ZHIPUAI_API_KEY` is set, this skill may send conversation text to Zhipu AI's servers for augmentation.

**To disable external API calls**:
- Simply don't set `ZHIPUAI_API_KEY`
- The skill will work normally using local memory retrieval only

### Recommendations

1. **Review the code** before enabling external API features
2. **Test in a sandbox** first if providing API keys
3. **Use file permissions** to protect database and config files
4. **Only enable features** you explicitly need

## File Structure

```
skills/memori_extension/
├── __init__.py               # Skill entry
├── memori_extension.py       # Skill implementation
├── SKILL.md                  # This file
└── README.md                 # Quick start guide
```

## License

This skill is licensed under **Apache License Version 2.0**.

This skill uses the **memori** Python library, which is also licensed under **Apache License Version 2.0**.

## Attribution

This skill incorporates the Memori Python library, which is licensed under the **Apache License 2.0**.
See the [LICENSE](http://www.apache.org/licenses/LICENSE-2.0) file for the complete license text.

Memori Library:

- Copyright 2025 Memori Team
- License: Apache License 2.0
- Repository: <https://github.com/MemoriLabs/Memori>
