# Architecture

## System Overview
claw-compactor is a modular compression pipeline with a single entry point (`mem_compress.py`) that routes to specialized compressors, all sharing a common library layer.

```
 ┌──────────────────────┐
 │ mem_compress.py │
 │ 553 lines │
 │ │
 │ • CLI argument parsing │
 │ • Command routing │
 │ • Pipeline orchestrator│
 │ • Progress reporting │
 └──────────┬─────────────┘
 │
 ┌──────────┬───────────┬───┴────┬──────────┬──────────┬─────────┐
 ▼ ▼ ▼ ▼ ▼ ▼ ▼
 ┌─────────┐ ┌────────┐ ┌────────┐ ┌──────┐ ┌────────┐ ┌───────┐ ┌──────┐
 │compress │ │dict_ │ │observ- │ │dedup │ │generate│ │audit │ │estim-│
 │_memory │ │compress│ │ation_ │ │_mem │ │_summary│ │_memory│ │ate_ │
 │ │ │ │ │compres-│ │ │ │_tiers │ │ │ │tokens│
 │ 230 LOC │ │ 170 LOC│ │sor │ │147LOC│ │ 292 LOC│ │216LOC │ │131LOC│
 │ │ │ │ │ 346 LOC│ │ │ │ │ │ │ │ │
 └────┬────┘ └───┬────┘ └───┬────┘ └──┬───┘ └───┬────┘ └──┬────┘ └──┬───┘
 │ │ │ │ │ │ │
 └──────────┴───────────┴────┬────┴─────────┴─────────┴─────────┘
 ▼
 ┌─────────────────┐
 │ lib/ │
 │ │
 │ tokens.py 68 │ Token estimation engine
 │ markdown.py 312 │ MD parsing & manipulation
 │ dedup.py 119 │ Shingle-hash dedup
 │ dictionary.py273│ Codebook compression
 │ rle.py 165 │ Run-length encoding
 │ tokenizer_ │
 │ optimizer 188 │ Format optimization
 │ config.py 81 │ JSON config loading
 │ exceptions 24 │ Custom exception types
 └─────────────────┘
 Total: 3,602 LOC

## Data Flow: Full Pipeline
┌──────────────────────┐ ┌──────────────────────┐
 │ memory/*.md │ │ .openclaw/sessions/ │
 │ MEMORY.md │ │ *.jsonl │
 │ TOOLS.md, etc. │ │ (raw transcripts) │
 └──────────┬───────────┘ └──────────┬────────────┘
 │ │
 ▼ ▼
 │ 1. estimate_tokens │ │ 2. observation_ │
 │ Baseline count │ │ compressor │
 │ (read-only) │ │ JSONL → XML → MD │
 └──────────┬───────────┘ │ 97% compression │
 │ └──────────┬────────────┘
 ▼ │
 ┌──────────────────────┐ │
 │ 3. compress_memory │ │
 │ Rule engine: │ ▼
 │ • dedup lines │ ┌──────────────────────┐
 │ • strip redundancy │ │ memory/observations/ │
 │ • merge sections │ │ (compressed output) │
 └──────────┬───────────┘ └────────────────────────┘
 │ 4. dictionary_ │
 │ compress │
 │ Build codebook → │
 │ Apply $XX codes │
 └──────────┬───────────┘
 │ 5. dedup_memory │ │ memory/.codebook.json│
 │ Cross-file scan │ │ (codebook artifact) │
 │ Shingle hashing │ └────────────────────────┘
 │ 6. generate_ │────▶│ memory/MEMORY-L0.md │
 │ summary_tiers │ │ memory/MEMORY-L1.md │
 │ L0/L1/L2 budgets │ │ (tier summaries) │
 └──────────────────────┘ └────────────────────────┘

## Module Responsibilities

### Entry Point
**`mem_compress.py`** (553 LOC)
The unified CLI. Parses arguments, routes to the appropriate command handler, and orchestrates the full pipeline. Handles progress reporting, JSON output mode, and error formatting.

### Compressor Modules
**`compress_memory.py`** (230 LOC)
Two-phase memory compression. Phase 1: deterministic rule engine (dedup lines, strip markdown filler, merge similar sections). Phase 2: optional LLM prompt generation for semantic compression. Operates on `.md` files in the workspace.

**`dictionary_compress.py`** (170 LOC)
CLI wrapper around `lib/dictionary.py`. Scans workspace markdown files, builds/loads codebook, applies/reverses compression. Manages the `.codebook.json` artifact.

**`observation_compressor.py`** (346 LOC)
Parses OpenClaw `.jsonl` session transcripts, extracts tool call interactions, classifies them by type (feature, bugfix, decision, etc.), and generates structured observation summaries. The single biggest source of savings (~97%). Tracks processed sessions in `.observed-sessions.json`.

**`dedup_memory.py`** (147 LOC)
Cross-file near-duplicate detection. Uses shingle hashing (n-gram fingerprinting) with Jaccard similarity. Reports duplicates or optionally auto-merges them.

**`generate_summary_tiers.py`** (292 LOC)
Creates L0/L1/L2 summaries from MEMORY.md. Classifies sections by priority (decision > action > config > log > archive), then fills each tier within its token budget, highest-priority sections first.

**`estimate_tokens.py`** (131 LOC)
Token counting and compression potential scoring. Scans all markdown files, reports per-file and total token usage. Identifies files with high compression potential.

**`audit_memory.py`** (216 LOC)
Health checker. Reports staleness (files not updated recently), bloat (high token/info ratio), and compression opportunities. Suggests specific actions.

**`compressed_context.py`** (280 LOC)
Compressed Context Protocol. Three compression levels (ultra/medium/light) for context passing between models. Generates decompression instructions for the receiving model's system prompt.

### Library Layer
**`lib/tokens.py`** (68 LOC)
Token estimation. Uses tiktoken's `cl100k_base` encoding when available, falls back to a CJK-aware heuristic (Chinese characters count as 1.5 tokens, others as chars÷4). Single function: `estimate_tokens(text) → int`.

**`lib/markdown.py`** (312 LOC)
Markdown parsing utilities. Section extraction by header level, section merging, content normalization, Chinese punctuation handling, header classification by priority keywords.

**`lib/dedup.py`** (119 LOC)
Shingle-hash deduplication engine. Generates n-gram (shingle) sets from text, computes Jaccard similarity between shingle sets, and groups entries by approximate length to reduce comparison space. O(n×k) instead of O(n²).

**`lib/dictionary.py`** (273 LOC)
The codebook engine. Scans text for n-gram frequencies (1-4 words), scores candidates by `freq × (len(phrase) - len(code)) - codebook_overhead`, builds a codebook of `$XX` codes, and provides `compress_text`/`decompress_text` as perfect inverses.

**`lib/rle.py`** (165 LOC)
Run-length encoding for structured patterns. Path compression (`$WS` shorthand), IP prefix extraction (`$IP` codes), and enumeration detection. All with roundtrip decompression.

**`lib/tokenizer_optimizer.py`** (188 LOC)
Encoding-aware format transformations. Converts markdown tables to key:value notation (60-70% savings), normalizes Chinese fullwidth punctuation, strips bold/italic/backtick markers, minimizes whitespace and indentation, compacts bullet lists.

**`lib/config.py`** (81 LOC)
Configuration loader. Reads `claw-compactor-config.json` from workspace root, merges with sensible defaults. All settings optional.

**`lib/exceptions.py`** (24 LOC)
Custom exception hierarchy: `MemCompressError` (base), `FileNotFoundError_`, etc.

## Layer 0: cacheRetention (Before Compression)
Before any compression runs, **prompt caching** (`cacheRetention: "long"`) provides a 90% discount on cached prompt tokens with a 1-hour TTL. This is orthogonal to compression — it reduces cost on whatever tokens remain.

```
Cost reduction stack:
  Layer 0: cacheRetention: "long"  → 90% cost discount on cached tokens
  Layer 1: observe (transcripts)   → ~97% token reduction
  Layer 2: compress (rule engine)  → 4-8% token reduction
  Layer 3: dict (codebook)         → 4-5% token reduction
  Layer 4: optimize (tokenizer)    → 1-3% token reduction
```

Layers 1-4 reduce token count. Layer 0 reduces cost-per-token. They multiply.

## Heartbeat Integration Flow
```
 ┌─────────────────────────┐
 │ Heartbeat fires │
 │ (every ~30 min) │
 └────────────┬────────────┘
              │
              ▼
 ┌─────────────────────────┐
 │ Read HEARTBEAT.md │
 │ → memory maintenance? │
 └────────────┬────────────┘
              │ yes
              ▼
 ┌─────────────────────────┐
 │ Run: benchmark │
 │ (non-destructive) │
 └────────────┬────────────┘
              │
         ┌────┴────┐
         │ >5% ? │
         └────┬────┘
        yes │    │ no
            ▼    │
 ┌──────────────┐│
 │ Run: full ││
 │ pipeline ││
 └──────────────┘│
              │◀──┘
              ▼
 ┌─────────────────────────┐
 │ New transcripts? │
 │ (unprocessed JSONL) │
 └────────────┬────────────┘
        yes │    │ no
            ▼    ▼
 ┌──────────────┐ HEARTBEAT_OK
 │ Run: observe │
 └──────────────┘
```

**Trigger logic:** The agent checks `HEARTBEAT.md` for a memory maintenance entry. If present, it runs `benchmark` first (cheap read-only). Only if savings exceed 5% does it commit to the full pipeline. New unprocessed transcripts always trigger `observe` regardless of benchmark results.

## Design Decisions

### Why shingle hashing for deduplication?
Naive pairwise comparison is O(n²) — unacceptable for workspaces with hundreds of sections. Shingle hashing (n-gram fingerprinting) gives us:
- O(n × k) complexity where k is the number of shingles per entry
- 3-word shingles with MD5 fingerprints provide good collision resistance
- Jaccard similarity on shingle sets is a well-studied near-duplicate metric
- Bucketing by approximate length further reduces comparisons

### Why tiktoken with heuristic fallback?
tiktoken gives exact token counts but requires compilation (Rust dependency). Many environments don't have it installed. The fallback heuristic (chars÷4, CJK-aware) is ~90% accurate — good enough for compression decisions. No hard dependency means the skill works out of the box everywhere.

### Why `$XX` codes instead of longer variable names?
Two-character codes minimize per-occurrence overhead. The codebook scoring function accounts for this: a phrase is only worth encoding if `freq × (len(phrase) - len(code)) > codebook_overhead`. Short codes win because the overhead term (the codebook entry itself) is amortized across many occurrences.

### Why section-level priority scoring for tiers?
Not all memory content is equal. A decision about architecture is worth more context tokens than a log of which files were edited. Priority classification (decision > action > config > log > archive) ensures L0 summaries contain the most important information, even at ~200 tokens.

### Why non-destructive by default?
Agents make mistakes. Every write operation is opt-in: `--dry-run` shows stats, `dedup` reports without modifying, `benchmark` never writes. This is critical for trust — users need to verify before committing to changes.

### Why XML format for observations (inspired by claude-mem)?
Structured XML (`<observation>`, `<type>`, `<title>`, `<facts>`) is:
1. Unambiguous to parse (unlike free-form markdown)
2. Token-efficient (tags are reusable tokens in cl100k_base)
3. Compatible with claude-mem's proven format
4. Easy to classify and search programmatically