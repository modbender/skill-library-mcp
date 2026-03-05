# TOON Adoption Skill

> Optimize token usage by adopting the compact TOON (Token-Oriented Object Notation) format for data storage and LLM context management.

## Overview

**TOON** is a lossless, drop-in replacement for JSON designed specifically for LLM contexts. It reduces token usage by approximately **40%** through intelligent formatting conventions that prioritize brevity without sacrificing clarity.

### Key Benefits

- 🚀 **~40% token reduction** vs standard JSON
- 📝 **Human-readable** indentation-based structure  
- 🔄 **Lossless conversion** to/from JSON
- 🎯 **LLM-optimized** syntax for context windows
- 📊 **Native tabular support** for structured arrays

## Installation

Install this skill into your Agent Zero skills directory:

```bash
# Clone or copy to skills folder
cp -r toon-adoption /a0/usr/skills/

# Or unzip pre-packaged skill
unzip toon-adoption-skill.zip -d /a0/usr/skills/
```

Agent Zero automatically recognizes TOON-formatted files (`.toon` extension).

## Quick Start

### Basic Structure

```toon
metadata:
  name: Sample Configuration
  version: 1.0.0
  format: TOON
goals[3]{id,title,category}:
  1,Lose weight,health
  2,Increase self-esteem,personal
  3,Get out of loneliness,social
```

### VS JSON Comparison

**TOON (42 tokens):**
```toon
user:
  name: Alice
  age: 30
  tags[3]: python, ai, data
```

**JSON (78 tokens):**
```json
{
  "user": {
    "name": "Alice",
    "age": 30,
    "tags": ["python", "ai", "data"]
  }
}
```

## TOON Syntax Specification

### 1. Indentation-Based Nesting
- Use **2-space indentation** to define hierarchy
- No curly braces `{}` or square brackets `[]` for nesting

```toon
parent:
  child:
    grandchild: value
```

### 2. Minimal Quoting
- Keys and values need **no quotes** unless containing special characters (commas, colons, leading/trailing whitespace)

```toon
# Valid unquoted
status: active
score: 95.5

# Requires quotes
desc: "Contains, comma"
path: "/usr/local/bin"
```

### 3. Explicit Array Lengths
- Arrays declare length with `[N]` notation
- Elements on separate lines with 2-space indent

```toon
fruits[4]:
  apple
  banana
  cherry
  date
```

### 4. Tabular Arrays (Arrays of Objects)
- For uniform arrays, use compact header format: `key[N]{field1,field2,...}:`
- Data rows as comma-separated values

```toon
users[3]{id,name,role}:
  1,Alice,admin
  2,Bob,user
  3,Charlie,moderator
```

### 5. Data Types
- **Strings**: Unquoted (preferred) or quoted
- **Numbers**: Integer or decimal
- **Booleans**: `true`, `false`
- **Null**: `null`
- **Arrays**: See rule 3 and 4

### 6. Encoding
- Always **UTF-8**

## Usage Patterns

### Configuration Files
```toon
settings:
  provider: ollama
  model: llama3.2
  temperature: 0.7
  max_tokens: 4096
```

### RSS Feed Storage
```toon
feeds[2]{name,url,category,last_fetch}:
  TechCrunch,https://techcrunch.com/feed/,tech,2026-03-02T10:00:00Z
  NatureNews,https://www.nature.com/news.rss,science,2026-03-02T09:30:00Z
```

### Session Summaries
```toon
session:
  id: mLAXi2wH
  start: 2026-03-02T17:00:00Z
  messages[12]: processed
  tokens_saved: 1247
  status: completed
```

## Agent Zero Integration

Agents automatically process `.toon` files:

1. **Reading**: Parses indentation as nested objects, CSV rows as structured data
2. **Writing**: Summarizes history, stores data, generates reports in TOON
3. **Context**: Load TOON files into context for ~40% more information vs JSON

### Best Practices

- ✅ Use `.toon` for logs, schedules, configs, feed data, session summaries
- ✅ Prefer tabular format `[N]{fields}:` for uniform data arrays
- ✅ Keep indentation strict (2 spaces)
- ❌ Avoid mixing quoted/unquoted keys unnecessarily

## Efficiency Comparison

| Format | Tokens | Relative Size | Best For |
|--------|--------|---------------|----------|
| JSON   | 100%   | 1.0x          | APIs, web |
| YAML   | 85%    | 0.85x         | Configs |
| **TOON** | **60%** | **0.6x**     | **LLM contexts** |

*Based on typical structured data with nested objects and arrays.*

## Examples

### Blog Generator Output
```toon
date: 2026-03-02
categories[3]: tech,science,ai
articles[2]{title,source,url}:
  "New AI Model Released",TechCrunch,https://tcrn.ch/xyz
  "Quantum Breakthrough",Nature,https://nature.com/abc
```

### System Resources
```toon
system:
  cpu_usage: 45.2
  memory_gb: 12.4
  disk_gb_free: 256
tasks[3]{name,status,pid}:
  blog_generator,running,1847
  rss_processor,idle,1923
  cleanup,completed,1956
```

## Author

**Agent Zero Community**

## Version

1.0.0

## Tags

`token-optimization`, `toon`, `format`, `efficiency`, `json-alternative`, `llm-context`

## License

MIT - Free for personal and commercial use.
