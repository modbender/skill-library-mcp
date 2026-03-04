# Curated Search - Domain Guide

**Purpose:** Documenting why each domain is whitelisted, what content it provides, and how to crawl it effectively.

**Last Updated:** 2026-02-12

---

## Domain Categories

### Programming Languages & Runtimes

#### Python (python.org)
**What:** Official Python documentation and resources
**Why:** Definitive source for Python standard library, language reference, tutorials
**Priority:** Critical
**Crawl Strategy:**
- Seed: `/doc/` paths
- Depth: 3 (extensive docs hierarchy)
- Note: Well-structured, crawler-friendly

#### Node.js (nodejs.org)
**What:** Node.js runtime documentation
**Why:** JavaScript server-side runtime docs, API reference
**Priority:** High
**Crawl Strategy:**
- Seed: `/docs/` paths
- Depth: 2
- Note: Modern site structure, responsive

---

### Web Development

#### MDN Web Docs (developer.mozilla.org)
**What:** Mozilla Developer Network - HTML, CSS, JavaScript, Web APIs
**Why:** The gold standard for web platform documentation
**Priority:** Critical
**Crawl Strategy:**
- Seed: `/en-US/docs/Web/` (language-agnostic paths)
- Depth: 3
- Note: Massive site, focus on Web/API section
- Caution: Respect robots.txt, very popular site

---

### System Administration & Linux

#### Linux man pages (man7.org)
**What:** Linux man pages, system calls, library functions
**Why:** Authoritative Linux C API and system documentation
**Priority:** High
**Crawl Strategy:**
- Seed: `/linux/man-pages/` paths
- Depth: 2
- Note: Text-heavy, technical content

#### Linux.die.net
**What:** Alternative Linux man pages with search
**Why:** Backup/alternative for Linux docs
**Priority:** Medium
**Crawl Strategy:**
- Seed: `/man/` paths
- Depth: 2
- Note: May overlap with man7.org, dedupe by URL

---

### Q&A and Community Knowledge

#### Stack Overflow (stackoverflow.com)
**What:** Programming Q&A community
**Why:** Millions of practical solutions, code examples
**Priority:** High (but tricky)
**Crawl Strategy:**
- Seed: `/questions/tagged/` specific tags
- Depth: 1 (question pages have related links)
- Note: Aggressive anti-scraping, may require careful throttling
- Alternative: Consider StackPrinter links for better crawling
**Caution:** High load site, very sensitive to crawling

---

### Reference & Encyclopedia

#### Wikipedia (en.wikipedia.org)
**What:** Collaborative encyclopedia, technical topics
**Why:** Broad technical overview, theory, concepts
**Priority:** Medium
**Crawl Strategy:**
- Seed: `/wiki/` pages for specific tech topics
- Depth: 2
- Note: Focus on Computing/Technology categories
- Caution: Very large, use depth limits strictly

---

### Platforms & Code Repositories

#### GitHub (github.com)
**What:** Code repositories, READMEs, documentation
**Why:** Actual code, real-world examples, library docs
**Priority:** Medium-High
**Crawl Strategy:**
- Seed: Specific repo paths, not root
- Depth: 1 (follow links within repos)
- Note: Most content is dynamic, focus on README.md files
- Alternative: Use raw.githubusercontent.com for markdown files
**Caution:** Rate limits apply, respect API guidelines

---

### Self-Documented

#### OpenClaw Docs (docs.openclaw.ai)
**What:** OpenClaw documentation
**Why:** Self-documenting the system
**Priority:** Low (dogfooding)
**Crawl Strategy:**
- Seed: Root and navigation pages
- Depth: 2
**Note:** Validate during testing

---

### Commercial (Optional/Experimental)

#### Amazon (amazon.com, amzn.to)
**What:** Product pages, reviews
**Why:** Hardware specs, technology product info
**Priority:** Low
**Crawl Strategy:**
- Seed: `/s?k=technology+keywords` search results
- Depth: 1
- Note: Heavy anti-scraping, may not be feasible
**Caution:** Consider removing if blocked consistently

---

## Domain Risk Assessment

| Domain | Blocking Risk | Content Quality | Maintenance Burden |
|--------|---------------|-----------------|-------------------|
| python.org | Low | High | Low |
| nodejs.org | Low | High | Low |
| developer.mozilla.org | Medium | Critical | Low |
| man7.org | Low | High | Low |
| stackoverflow.com | High | High | Medium |
| github.com | Medium | High | Medium |
| wikipedia.org | Low | Medium | Low |
| amazon.com | High | Low | High |

**Recommendation:** Start with Low/Medium risk domains for MVP. Add high-risk ones later with fallback strategies.

---

## Seed URL Strategy

**Don't crawl homepages.** They're usually:
- Marketing content (not searchable docs)
- Navigation-heavy (lots of links, little text)
- Rate-limited or monitored for abuse

**Instead, target:**

| Domain Type | Good Seed URL Pattern | Example |
|-------------|----------------------|---------|
| Documentation | `/docs/`, `/doc/`, `/guide/` | `https://docs.python.org/3/` |
| API Reference | `/api/`, `/reference/` | `https://nodejs.org/api/` |
| Wiki-style | `/wiki/` prefix | `https://en.wikipedia.org/wiki/Python_(programming_language)` |
| Knowledge Base | `/kb/`, `/help/` | `https://help.github.com/` |
| Questions | `/questions/`, `/q/` | `https://stackoverflow.com/questions/tagged/python` |

---

## Fallback Strategies

**When a domain blocks crawling:**

1. **Try alternative paths:**
   - `docs.example.com` instead of `example.com/docs`
   - `developer.example.com` for API docs
   - `support.example.com` for KB articles

2. **Use mirror sites:**
   - MDN: Multiple language mirrors available
   - Man pages: Multiple hosting sites

3. **Stack Overflow alternatives:**
   - Use StackPrinter URLs (text-only version)
   - Example: `http://stackprinter.appspot.com/export?question=123&service=stackoverflow&language=en&hideAnswers=false&width=640`

4. **GitHub alternatives:**
   - Raw content: `raw.githubusercontent.com`
   - GitHub Pages: `username.github.io/repo`

5. **Accept defeat:**
   - If a site consistently blocks with 403/429
   - Document in DOMAIN_GUIDE.md
   - Consider removing from whitelist

---

## Content Deduplication

**Challenge:** Same content appears on multiple domains

**Examples:**
- Man pages: man7.org vs linux.die.net
- Python docs: docs.python.org vs multiple mirrors
- Wikipedia: Language-specific vs mobile versions

**Strategy:**
- Normalize URLs (strip mobile prefixes)
- Hash content and skip duplicates
- Prefer canonical URLs (rel="canonical")
- Index only one authoritative source

---

## Updating This Guide

**When adding a new domain:**
1. Add to appropriate category section
2. Document rationale (what, why, priority)
3. Add crawl strategy notes
4. Update risk assessment table
5. Test seed URLs before enabling in production

**When a domain stops working:**
1. Document failure mode (403, 429, timeout)
2. Try fallback strategies
3. If consistently failing, consider removal
4. Update risk assessment

---

**Rule:** When in doubt, prefer quality over quantity. Ten well-indexed domains beat a hundred poorly scraped ones.
