# Research Library - Build Log

## [2026-02-07] Search & Ranking — PHASE 1

### Completed

- [x] FTS5 full-text search across research entries
- [x] FTS5 search across attachment extracted text
- [x] Material type weighting (Reference: 1.0, Research: 0.5)
- [x] Ranking formula implementation:
  - `score = (fts5 × mat_weight × 0.5) + (confidence × 0.3) + (recency × 0.2)`
- [x] Confidence validation (reference requires ≥0.8)
- [x] Confidence scoring heuristic
- [x] Project-scoped search (`search_project()`)
- [x] Cross-project search (`search_all_projects()`)
- [x] Linked research traversal (`get_linked_research()`)
- [x] Link type filtering (applies_to, contradicts, supersedes, related, references)
- [x] Bidirectional link discovery
- [x] File usage tracking (`get_file_usage()`)
- [x] Comprehensive test suite (50 tests)
- [x] Documentation (SEARCH-GUIDE.md)

### Files Created/Modified

| File | Lines | Description |
|------|-------|-------------|
| `reslib/__init__.py` | 89 | Package exports (updated) |
| `reslib/ranking.py` | 771 | Ranking formula, constants, validation |
| `reslib/search.py` | 1621 | ResearchSearch class, FTS5 queries |
| `tests/test_search.py` | 841 | 50 comprehensive tests |
| `docs/SEARCH-GUIDE.md` | 405 | Usage documentation |

### Performance (Actual)

Test environment: 20 documents, mixed reference/research, 5 attachments, 6 links

| Operation | Avg Latency | Max Latency | Target | Status |
|-----------|-------------|-------------|--------|--------|
| Basic FTS5 search ("servo") | **0.33ms** | 0.38ms | <100ms | ✅ |
| Project-scoped search | **0.21ms** | - | <100ms | ✅ |
| Link traversal | **0.05ms** | - | <100ms | ✅ |

**All queries >100x faster than target.**

### Test Results

```
50 passed, 0 failed
Test duration: 1.42s
```

Test categories:
- Ranking module: 8 tests ✅
- ResearchRanking class: 3 tests ✅
- Search utilities: 6 tests ✅
- Basic search: 4 tests ✅
- Material type weighting: 3 tests ✅
- Project scoping: 5 tests ✅
- Linked research: 5 tests ✅
- Confidence filtering: 3 tests ✅
- Attachment search: 3 tests ✅
- File usage: 2 tests ✅
- Performance: 3 tests ✅
- Edge cases: 5 tests ✅

### Ranking Formula Verification

Test case: Reference vs Research at same FTS5 relevance

| Document | Type | Confidence | Score |
|----------|------|------------|-------|
| Datasheet | reference | 0.95 | **0.827** |
| Blog Post | research | 0.95 | 0.652 |

**Reference correctly ranks first ✅**

### Issues Found

1. **FTS5 alias limitation**: Can't alias FTS5 virtual table when accessing `rank` column. Fixed by using full table name (`research_fts.rank`).

2. **Python 3.12 datetime warning**: SQLite datetime adapter deprecation warning (660 occurrences in tests). Non-blocking; will address in future update.

### Architecture Notes

- **FTS5 Porter tokenizer**: Enables stemming ("tuning" matches "tune")
- **Triggers maintain FTS5 sync**: INSERT/UPDATE/DELETE on research/attachments auto-updates FTS5 indexes
- **Indexes optimized for common queries**:
  - `idx_research_project_type` for project + material filtering
  - `idx_research_links_source_type` for link traversal
  - Partial index on high-relevance links

### Next Steps

- [ ] CLI ready for search commands
- [ ] Integration with MEDIA agent extraction pipeline
- [ ] Web UI for search results display
- [ ] Batch import CLI (`reslib batch-add`)
- [ ] Link suggestion engine (auto-detect related research)

---

## Version History

| Date | Phase | Status |
|------|-------|--------|
| 2026-02-07 | PHASE 1: Search & Ranking | ✅ Complete |
