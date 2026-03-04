# Memori Extension Skill

Memory augmentation and LLM call interception using the Memori Python library with optional Zhipu API integration.

## ⚠️ Security & Privacy Notice

**Important**: This skill performs the following operations:

1. **File Operations**: Reads and writes to a local SQLite database (default: `./memori.db`)
2. **Optional External API**: If `ZHIPUAI_API_KEY` is provided, conversation text may be sent to Zhipu AI's servers for analysis and augmentation
3. **Configurable Terms**: Loads technical terms from environment variables or config files

**Privacy Implications:**
- ⚠️ **If you set `ZHIPUAI_API_KEY`**: Conversation text (user messages, system prompts, and assistant responses) will be sent to Zhipu AI's external servers. Only set this if you explicitly consent to this data transmission.
- ✅ **If you do NOT set `ZHIPUAI_API_KEY`**: The skill operates entirely locally with no external network calls (except for fetching the Memori library itself during installation).
- 📁 **File Operations**: The skill creates and modifies a local SQLite database and optional configuration files. These are stored on your local machine.

**Recommendation**: Start without `ZHIPUAI_API_KEY` to test local-only functionality first. Only enable external API calls if you need the enhanced augmentation features and consent to the data transmission.

## License

This skill is licensed under the **Apache License Version 2.0**.

Copyright 2025

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Dependencies

This skill requires the **Memori Python library**:

```bash
pip install memori
```

The Memori library is licensed under the Apache License Version 2.0.

### Optional: Zhipu API

⚠️ **Warning**: For enhanced conversation augmentation, you can optionally install the Zhipu AI SDK:

```bash
pip install zhipuai
```

**Privacy Notice**: If `ZHIPUAI_API_KEY` is set, conversation content may be sent to Zhipu AI servers. Only set this if you explicitly consent.

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
          "ZHIPUAI_MODEL": "glm-4.7"
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

### Installation

```bash
# Install Memori library (required)
pip install memori

# Install Zhipu SDK (optional, only if needed)
pip install zhipuai
```

### Basic Usage

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

# Close
memori.close()
```

### Using the Skill API

```python
from skills.memori_extension import search, augment, intercept_llm

# Search memories
memories = search("query", limit=5)

# Augment query
enhanced = augment("query")
if enhanced:
    print(enhanced)

# Intercept LLM calls
messages = [{"role": "user", "content": "question"}]
enhanced_messages = intercept_llm(messages)
```

## Features

- ✅ **Memory retrieval** - Search knowledge database by keywords
- ✅ **Query augmentation** - Inject retrieved memories into conversation
- ✅ **LLM call interception** - Automatically enhance LLM calls
- ✅ **Configurable terms** - Customize technical keywords for interception
- ✅ **Optional Zhipu API** - Enhanced conversation analysis (requires API key)
- ⚠️ **External API calls** - Only if ZHIPUAI_API_KEY is set

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
5. **Monitor usage** if enabling external API calls

## Attribution

This skill incorporates the Memori Python library, which is licensed under the Apache License Version 2.0.

**Memori Library:**
- Copyright 2025 Memori Team
- License: Apache License 2.0
- Repository: https://github.com/MemoriLabs/Memori

**Full license text:** http://www.apache.org/licenses/LICENSE-2.0
