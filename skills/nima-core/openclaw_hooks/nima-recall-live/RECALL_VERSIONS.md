# NIMA Recall Version History

## Current Version: `lazy_recall.py` (Canonical)

**Consolidated:** 2026-02-15 (from v1/v2/v3)

**Features:**
- ✅ Pre-computed embedding index (instant semantic search)
- ✅ Query cache (zero latency for repeated queries)
- ✅ Deferred summary loading (only loads after final scoring)
- ✅ Affect-weighted reranking (emotional resonance scoring)
- ✅ FTS + semantic hybrid search
- ✅ Time decay and recency boost
- ✅ Configurable via environment variables

**Performance:**
- Cold query: ~100-200ms
- Cached query: <5ms
- FTS-only query: ~30ms

## Legacy Versions (Archived)

### `lazy_recall_legacy_v1.py`
- Original implementation
- FTS-only, no semantic search
- No caching
- **Deprecated:** 2026-02-14

### `lazy_recall_legacy_v2.py`
- Added Voyage AI embeddings
- On-demand embedding computation (slow)
- No pre-computed index
- **Deprecated:** 2026-02-14

### `lazy_recall_v3.py` → `lazy_recall.py`
- Added pre-computed embedding index
- Added query cache
- Deferred summary loading
- **Promoted to canonical:** 2026-02-15

## Migration Notes

If you were using `lazy_recall_v3.py` directly, update your imports:

```python
# Old
from lazy_recall_v3 import lazy_recall

# New
from lazy_recall import lazy_recall
```

The `index.js` hook has been updated automatically.

## Why Consolidate?

**Before:**
- 3 versions (v1, v2, v3)
- Unclear which to use
- Tech debt and confusion
- Duplicate code

**After:**
- 1 canonical version
- Clear upgrade path
- Legacy versions archived (not deleted) for reference
- Clean codebase

## Performance Comparison

| Version | FTS | Semantic | Cache | Avg Latency |
|---------|-----|----------|-------|-------------|
| v1 | ✅ | ❌ | ❌ | 30ms |
| v2 | ✅ | ✅ (slow) | ❌ | 500ms |
| v3/canonical | ✅ | ✅ (fast) | ✅ | 100ms (cold), 5ms (cached) |

## Future Work

- [ ] Add configurable MAX_RESULTS via plugin config
- [ ] Support custom embedding models (not just Voyage)
- [ ] Add telemetry for query performance tracking
- [ ] Implement automatic index rebuilding when stale
