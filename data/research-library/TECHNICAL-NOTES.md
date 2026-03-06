# Technical Notes for Phase 2

## What Worked Well (Keep This Pattern)

### 1. SQLite + FTS5 Combination
- **Zero-config deployment** — No database server to manage
- **FTS5 performance** — Sub-100ms searches even with 200+ documents
- **WAL mode** — Enables concurrent reads while writing
- **Portable** — Single file backup/restore

**Keep:** SQLite is perfect for personal research libraries up to ~50K documents.

### 2. Click CLI Framework
- **Built-in testing** — `CliRunner` makes testing trivial
- **Automatic help** — `--help` generated from docstrings
- **Context passing** — Database connections flow through context
- **JSON output mode** — `--json-output` flag for programmatic use

**Keep:** Click is mature and well-documented.

### 3. Dataclass Models
- **Validation in `__post_init__`** — Catches errors early
- **Type hints** — IDE support and documentation
- **Immutable-friendly** — Easy to reason about

**Keep:** Dataclasses are the right abstraction level.

### 4. Material Type Weighting
- **Simple ranking formula** — Easy to explain and adjust
- **Reference > Research** — Intuitive priority
- **Confidence factor** — Higher confidence documents rank higher

**Keep:** The formula `score = (fts5 × material_weight) + (confidence × 0.3) + (recency × 0.2)` is effective.

### 5. Project-Scoped Organization
- **Required project_id** — Forces organization from the start
- **Cross-project search** — Available when needed
- **Isolation by default** — Prevents accidental data mixing

**Keep:** Project-first organization scales well.

---

## What Was Hard (Need to Improve)

### 1. FTS5 Query Syntax Edge Cases
**Problem:** FTS5 has special syntax (`AND`, `OR`, `NEAR`, quotes, asterisks) that can cause query errors if user input isn't sanitized.

**Current State:** Basic sanitization in `sanitize_fts5_query()`, but edge cases like `&`, `|`, unbalanced quotes still problematic.

**Phase 2 Fix:**
- Implement robust query parser
- Add query builder DSL for complex searches
- Consider Tantivy or Meilisearch for production

### 2. PDF/Image Extraction Quality
**Problem:** Text extraction from PDFs varies wildly in quality. Scanned PDFs need OCR.

**Current State:** Falls back to low confidence for problematic PDFs.

**Phase 2 Fix:**
- Integrate Tesseract OCR for images/scanned PDFs
- Add extraction quality metrics
- Queue failed extractions for manual review

### 3. Attachment Storage Path Management
**Problem:** Attachments are copied to `attachments/project/YYYY-MM/` which works but makes reorganization hard.

**Phase 2 Fix:**
- Store by content hash for deduplication
- Add symlinks for human-readable structure
- Consider blob storage abstraction

### 4. Concurrent Write Handling
**Problem:** SQLite locks on writes. Multiple rapid CLI commands can hit "database is locked".

**Current State:** Exponential backoff retry works but adds latency.

**Phase 2 Fix:**
- Consider write queue/journal pattern
- Or migrate heavy-write scenarios to PostgreSQL

### 5. Test Runtime for Stress Tests
**Problem:** Full stress tests (100+ documents) take 3+ seconds each.

**Phase 2 Fix:**
- Add `pytest.mark.slow` configuration
- Create separate CI job for stress tests
- Add `--quick` flag to skip stress tests

---

## Known Limitations (Deferred to Phase 2)

### 1. No Vector Search / Semantic Search
- Currently FTS5 only (keyword matching)
- Phase 2: Add embedding storage + similarity search
- Consider: pgvector (PostgreSQL) or Qdrant

### 2. No Multi-User Support
- Single SQLite database
- No authentication/authorization
- Phase 2: Add user_id column if needed, or stay single-user

### 3. No Web UI
- CLI only
- Phase 2: Add FastAPI backend + simple React frontend

### 4. No Version Control for Documents
- Can update but no history
- Phase 2: Add document versioning (like Git for docs)

### 5. Limited Attachment Types
- PDF, images, text, code files
- No: Word docs, Excel, PowerPoint
- Phase 2: Add more extractors (python-docx, openpyxl)

### 6. No Tagging Hierarchy
- Flat tag list only
- No: tag categories, parent-child tags
- Phase 2: Add tag_parent_id for hierarchical tags

### 7. No Full-Text Preview
- Search returns snippets only
- No: inline document viewer
- Phase 2: Add `reslib view <id>` with pager

---

## Performance Ceiling (When to Upgrade)

### SQLite Limits
| Metric | SQLite OK | Consider PostgreSQL |
|--------|-----------|---------------------|
| Documents | <50,000 | >50,000 |
| Attachments | <100,000 | >100,000 |
| Concurrent users | 1 | >1 |
| Write throughput | <100/s | >100/s |
| Database size | <10 GB | >10 GB |

### Migration Path
1. Keep schema identical
2. Use SQLAlchemy as ORM layer
3. Swap connection string
4. Re-index FTS (PostgreSQL uses tsvector)

### When to Consider Meilisearch/Elasticsearch
- Need typo tolerance
- Need faceted search
- Need instant search-as-you-type
- >100K documents

---

## Architecture Decisions That Held Up

### ✅ Single-Table Documents
Originally considered separate tables for notes, sources, references. Single `documents` table with `material_type` column is simpler and works.

### ✅ FTS5 Triggers
Auto-sync of FTS virtual table via triggers means no manual index management. Zero operational burden.

### ✅ Project Isolation
Making project_id required was the right call. Prevents the "everything in one folder" antipattern.

### ✅ Confidence as First-Class Citizen
Having confidence score on every document enables smart ranking and filtering.

### ⚠️ Link Types as Enum
Works but may need expansion. Consider moving to a `link_types` table for user-defined types.

### ⚠️ Extraction Queue as Table
Works for single worker. May need Redis/RabbitMQ for distributed workers.

---

## Recommendations for Phase 2 Developer

1. **Read the existing tests first** — 214 tests document expected behavior.

2. **Use the CLI as reference** — `reslib/cli.py` is the canonical interface.

3. **Don't break existing behavior** — Add features additively.

4. **Test performance changes** — Run `test_integration.py` stress tests.

5. **Keep it simple** — This is a personal tool, not enterprise software.

6. **Document decisions** — Update this file when making architectural changes.

---

## Files to Review

| File | Purpose |
|------|---------|
| `reslib/cli.py` | Main interface, start here |
| `reslib/search.py` | FTS5 search + ranking logic |
| `reslib/worker.py` | Async extraction worker |
| `tests/test_integration.py` | Full workflow examples |
| `war-room/BUILD_LOG.md` | Build history |
| `PHASE1-FINAL-METRICS.md` | Final stats |
