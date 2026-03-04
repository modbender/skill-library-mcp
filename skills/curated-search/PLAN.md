# Curated Search Skill - Build Plan

**Purpose:** Domain-restricted search system that indexes only trusted technical sources, providing clean, authoritative results for OpenClaw agents and human users.

**Core Philosophy:** The whitelist curation is the product. Keep implementation simple, ship fast, iterate based on usage.

---

## Phase 1: Foundation & Configuration

**Goal:** Lock in the domain whitelist and crawl parameters that define what we search.

1. **Curate Domain Whitelist**
   - Define authoritative sources (docs, repos, wikis, Q&A sites)
   - Categorize by topic (programming, sysadmin, web dev, etc.)
   - Document rationale for each domain

2. **Design Config Schema**
   - YAML structure for domains, crawl settings, index paths
   - Environment-specific overrides (dev vs prod)
   - Validation rules (required fields, value ranges)

3. **Seed URL Strategy**
   - Identify entry points for each domain (not just homepages)
   - Prioritize high-value paths (/docs, /api, /wiki)
   - Plan for domains that block crawlers (fallback strategies)

---

## Phase 2: Core Indexer (The Library)

**Goal:** Build the searchable document store with zero external dependencies.

1. **Implement Document Model**
   - Fields: url, title, content, excerpt, domain, crawled_at, depth
   - Compute excerpt (first 200 chars + ellipsis)
   - Validate URLs and normalize

2. **Integrate MiniSearch**
   - Configure index fields (title, content, domain)
   - Set up stored fields (url, domain, excerpt, crawled_at)
   - Design serialization format (JSON persistence)

3. **Build CRUD Operations**
   - `addDocument(doc)` - index new content
   - `removeByUrl(url)` - purge outdated entries
   - `search(query, opts)` - BM25 ranked results
   - `getStats()` - document count, domains, last crawl

4. **Persistence Layer**
   - Save index to JSON on changes
   - Load index on startup
   - Handle corruption gracefully (rebuild if needed)

---

## Phase 3: Domain-Restricted Crawler

**Goal:** Polite, focused crawler that respects boundaries and stays on whitelist.

1. **URL Discovery**
   - Extract links from HTML using JSDOM
   - Normalize URLs (resolve relative, strip fragments)
   - Filter: whitelist domains only, respect max depth

2. **Content Extraction**
   - Parse HTML to extract title and main text
   - Strip boilerplate (nav, footers, ads where possible)
   - Handle different content types (docs, READMEs, wikis)

3. **Politeness Controls**
   - robots.txt parsing and respect
   - Rate limiting per host (configurable delay)
   - User agent identification
   - Request timeout handling

4. **Orchestration**
   - Breadth-first crawling with depth tracking
   - Resume capability (save crawl state)
   - Incremental updates (only crawl changed content)
   - Graceful shutdown (finish current batch, save state)

---

## Phase 4: Search Tool Interface

**Goal:** Simple CLI tool that OpenClaw can invoke directly.

1. **Argument Parsing**
   - `--query="search terms"` (required)
   - `--limit=N` (default 5)
   - `--domain=example.com` (optional filter)

2. **Query Execution**
   - Load index from disk
   - Execute search with filters
   - Format results as JSON array

3. **Error Handling**
   - Empty index → return empty array (not error)
   - Missing config → clear error message
   - Malformed query → sanitize and attempt

4. **Performance**
   - Target: <500ms for index load + search
   - Optimize: cache index in memory for multiple calls? (future)

---

## Phase 5: OpenClaw Integration

**Goal:** Register as a native skill with proper metadata.

1. **Skill Manifest (skill.yaml)**
   - Tool definition with parameters
   - Command mapping to search script
   - Timeout and return type specifications

2. **Wrapper Scripts**
   - Ensure Node.js executable permissions
   - Handle path resolution relative to skill directory
   - Set working directory correctly

3. **Registration**
   - Copy/link skill to OpenClaw skills directory
   - Verify tool appears in `openclaw tools list`
   - Test invocation from agent

---

## Phase 6: Testing & Validation

**Goal:** Prove it works end-to-end before relying on it.

1. **Unit Tests**
   - Indexer: add, search, remove, persist
   - Crawler: URL filtering, robots.txt parsing
   - Config: validation, loading

2. **Smoke Tests**
   - Crawl single domain, shallow depth (depth=1)
   - Verify documents appear in index
   - Search returns expected results

3. **Integration Tests**
   - Full crawl of 2-3 domains
   - Query across different domains
   - Filter by domain works correctly
   - Empty queries handled gracefully

4. **Load Tests** (optional)
   - Index 10k documents, measure search latency
   - Verify memory usage stays bounded

---

## Phase 7: Documentation

**Goal:** Clear docs for setup, usage, and contribution.

1. **README.md** (public)
   - What this is and why it exists
   - Quick start (install, configure, run)
   - Architecture overview
   - Troubleshooting common issues

2. **SKILL.md** (OpenClaw reference)
   - Tool specification for agent
   - Example queries
   - Response format reference

3. **CONTRIBUTING.md** (future)
   - How to add new domains
   - Code style and testing
   - Submitting PRs

---

## Phase 8: Deployment & Operations

**Goal:** Run continuously without manual intervention.

1. **Initial Index Build**
   - Run full crawl of all whitelisted domains
   - Monitor for failures or blocks
   - Verify index size and search quality

2. **Update Strategy**
   - Schedule: Weekly re-crawls? Triggered updates?
   - Incremental vs full rebuild
   - Backup/snapshot index before updates

3. **Monitoring**
   - Log crawl success/failure rates
   - Track index size growth over time
   - Alert on crawl failures or search errors

4. **Maintenance**
   - Remove dead domains from whitelist
   - Add new authoritative sources
   - Prune old/outdated documents

---

## Future Enhancements (Post-MVP)

**Only after core system is stable and in daily use:**

1. **Semantic Search**
   - Vector embeddings (sentence-transformers)
   - Hybrid keyword + semantic ranking
   - Requires: embedding model, vector DB

2. **Web UI**
   - Simple search interface for humans
   - Results with previews and snippets

3. **Federation**
   - Share curated indexes between trusted OpenClaw instances
   - Index exchange format
   - Distributed crawling (avoid hammering same sites)

4. **Advanced Crawling**
   - Sitemap.xml parsing
   - RSS/Atom feed monitoring for updates
   - API-based content (GitHub API, etc.)

5. **Performance Optimization**
   - Persistent API server (if load demands it)
   - In-memory index caching
   - Connection pooling for crawls

---

## Success Criteria

**MVP is complete when:**

- [ ] All whitelisted domains crawled successfully (depth=2)
- [ ] Index contains >1000 documents from >5 domains
- [ ] Search tool returns relevant results in <1 second
- [ ] OpenClaw agent can invoke tool and get useful answers
- [ ] Documentation is clear enough for another human to set up

**Quality metrics:**
- Search result relevance (subjective: "did I find what I needed?")
- Crawl completion rate (% of domains successfully indexed)
- System uptime (no crashes during normal operation)
- Maintenance burden (hours per week to keep running)

---

## File Locations

This plan: `skills/curated-search/PLAN.md`

Implementation will reside in: `skills/curated-search/`
- `config.yaml` - Domain whitelist and settings
- `src/indexer.js` - Search index library
- `src/crawler.js` - Domain-restricted crawler
- `scripts/search.js` - CLI tool for OpenClaw
- `skill.yaml` - OpenClaw skill manifest
- `README.md` - Public documentation
- `SKILL.md` - Agent reference

---

**Philosophy Check:**

- Complexity should match the problem. Don't build a search engine, build a curated index.
- The whitelist is a feature, not a limitation. Embrace it.
- Working beats perfect. Ship the MVP, improve incrementally.
- Document assumptions. The next person (or future you) needs context.
