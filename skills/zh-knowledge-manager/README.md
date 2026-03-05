# zh-knowledge-manager

**中文 AI 增强知识管理 | Chinese AI-Enhanced Knowledge Management for OpenClaw**

将 agent 日志自动沉淀为结构化知识库。核心流程确定性（PREFIX 分类 + hash 去重），可选 AI 增强（语义去重 + 自动标签 + 对话知识提取）。

Transform agent logs into a structured knowledge base. Deterministic core (PREFIX classification + hash dedup) with optional AI enhancements (semantic dedup + auto-tagging + LLM conversation extraction).

## Features / 特性

**Core (offline, zero API cost):**
- PREFIX-based log entry classification (PROJECT/ISSUE/INFRA/CONFIG/RESEARCH/KB)
- MD5 content hash deduplication
- Configurable PREFIX → kb/ directory mapping
- Daily sync with `km sync --days N`
- Knowledge digest with gap detection

**AI Enhanced (opt-in):**
- Semantic dedup via bge-m3 embedding (SiliconFlow / OpenAI compatible)
- Chinese auto-tagging via jieba word segmentation + TF-IDF
- Chinese synonym normalization (数据库/DB/database → unified term)
- LLM conversation knowledge extraction (DeepSeek / OpenAI compatible)

## Quick Start / 快速开始

### Install / 安装

```bash
# From ClawHub
clawhub install zh-knowledge-manager

# Or manually
git clone https://github.com/jgpy/zh-knowledge-manager.git ~/.openclaw/skills/zh-knowledge-manager
cd ~/.openclaw/skills/zh-knowledge-manager && npm install
```

### Initialize / 初始化

```bash
node ~/.openclaw/skills/zh-knowledge-manager/km.js init --workspace /path/to/your/workspace
```

This creates:
- `km.config.json` — configuration file
- `memory/kb/` — knowledge base directory structure

### Configure / 配置

Edit `km.config.json`:

```json
{
  "logDir": "memory",
  "kbDir": "memory/kb",
  "ai": {
    "embedding": {
      "provider": "siliconflow",
      "apiKey": "${SILICONFLOW_API_KEY}"
    },
    "llm": {
      "provider": "volcengine",
      "apiKey": "${ARK_API_KEY}",
      "endpoint": "https://your-endpoint/v1/chat/completions"
    }
  }
}
```

Set environment variables:
```bash
export SILICONFLOW_API_KEY=your-key    # for semantic dedup
export ARK_API_KEY=your-key            # for LLM extraction
```

## Usage / 使用

### Log Format / 日志格式

Write logs in `memory/YYYY-MM-DD.md`:

```markdown
### [PROJECT:DataReport] Automated report deployment
crontab + Python daily 8:00 push to Feishu. Use pandas chunksize for large tables.
#report #automation #pandas

### [ISSUE:DataReport] OOM on large CSV
pandas read_csv without chunksize causes OOM on 2GB+ files. Fixed with chunksize=50000.
#pandas #OOM #fix
```

### Commands / 命令

```bash
# Basic sync (offline)
km sync --days 7

# Preview without writing
km sync --days 7 --dry-run

# AI-enhanced sync
km sync --days 7 --semantic --auto-tag

# Extract knowledge from conversation dumps
km extract backups/session-dump.md

# Import reviewed draft
km import output/kb-draft-0227.md

# Knowledge digest
km digest

# Stats + update index
km stats

# Suggest tags for text
km suggest-tags "pandas 读取大表时需要 chunksize"
```

## Architecture / 架构

```
Input                      Core (Deterministic)              AI (Opt-in)
─────                      ────────────────────              ──────────
memory/YYYY-MM-DD.md  ──→  Parser (regex)                    
                           ↓                                 
                           Classifier (PREFIX → kb/ map)     
                           ↓                                 
                           Hash Dedup (MD5)  ──→  Semantic Dedup (bge-m3)
                           ↓                                 ↓
                           Writer (append)   ←──  Auto-Tag (jieba TF-IDF)
                           ↓
                           memory/kb/
                           
backups/*session*.md  ──→  ─────────────────────  Extract (LLM) → draft → import
```

## vs Official knowledge-management / 与官方技能对比

| Feature | Official | zh-knowledge-manager |
|---------|----------|---------------------|
| Classification | English keyword matching | PREFIX deterministic mapping |
| Dedup | Content hash | Hash + bge-m3 semantic |
| Chinese support | No | jieba + synonym normalization |
| Auto-tagging | No | TF-IDF keyword extraction |
| LLM extraction | No | Conversation → structured KB |
| Knowledge digest | No | Stats + gap detection |
| Offline core | Yes | Yes |

## Supported Providers / 支持的服务商

**Embedding (for semantic dedup):**
- SiliconFlow (bge-m3, recommended for Chinese)
- OpenAI (text-embedding-3-small)
- DashScope / Aliyun (通义千问)
- Any OpenAI-compatible API

**LLM (for conversation extraction):**
- Volcengine + DeepSeek
- OpenAI (GPT-4o)
- Anthropic (Claude)
- Any OpenAI-compatible API

## Requirements / 依赖

- Node.js >= 18.0.0
- `@node-rs/jieba` (auto-installed, Rust prebuilt binary)
- `commander` (auto-installed)

## License

MIT
