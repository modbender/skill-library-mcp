# Contributing to Curated Search

Thank you for your interest in improving Curated Search! This document provides guidelines and instructions for contributing.

## Areas of Contribution

### 1. Adding New Domains

The curated whitelist is the core product. When adding a new domain:

**a. Evaluate Quality & Authority**
- Prefer official documentation (e.g., `docs.python.org`, `developer.mozilla.org`)
- Avoid marketing-heavy homepages; target specific `/docs/`, `/api/` sections
- Consider maintenance burden: stable sites are better than ones that change structure frequently

**b. Update `config.yaml`**
- Add the domain to the `domains:` list
- Add one or more seed URLs under `seeds:` that point directly to content-rich pages

**c. Add Site-Specific Content Extraction (if needed)**
If the domain requires custom selectors or cleanup:
- Open `src/content-extractor.js`
- Add the domain to `detectContentType` mapping
- Implement extraction in the appropriate method (`extractMDN`, `extractGeneric`, or new dedicated method)
- Add corresponding test fixtures in `test/fixtures/`

**d. Document Rationale**
Update `DOMAIN_GUIDE.md` with a new entry explaining:
- What the domain provides
- Why it's valuable
- Any special crawl considerations (rate limits, blocking, depth)

**e. Test**
```bash
# Create a small config with just the new domain and shallow depth
npm run crawl
# Verify index contains documents and search works
node scripts/search.js --query="test" --pretty
```

### 2. Code Style & Testing

**Style:**
- Use consistent indentation (2 spaces)
- Prefer explicit variable names
- Add JSDoc comments for public functions
- Keep functions small and focused

**Testing:**
- All new functionality must include unit tests
- Update existing tests when modifying behavior
- Aim to maintain or increase coverage
- Use fixtures in `test/fixtures/` for HTML content extraction tests

Run tests frequently:
```bash
npm test
```

### 3. Pull Request Process

1. Fork the repository and create a feature branch
2. Make your changes with clear, concise commit messages
3. Ensure all tests pass (`npm test`)
4. Update documentation (README, SKILL.md, DOMAIN_GUIDE.md) as needed
5. Submit a pull request with a description of the changes and rationale
6. Address any review feedback

### 4. Reporting Issues

When filing issues, include:
- A clear description of the problem
- Steps to reproduce (including config snippets, sample URLs)
- Expected vs actual behavior
- Relevant logs or error output
- Environment details (OS, Node version)

## Development Setup

```bash
# Clone and install dependencies
npm ci

# Run tests
npm test

# Run a small crawl for manual testing (edit config.yaml first)
npm run crawl

# Search the index
node scripts/search.js --query="your query"
```

## Key Files

- `src/crawler.js` — main crawler orchestration
- `src/content-extractor.js` — HTML → text pipeline
- `src/indexer.js` — MiniSearch wrapper
- `src/url-normalizer.js` — canonicalization and SSRF prevention
- `src/rate-limiter.js` — per-host politeness
- `scripts/search.js` — CLI tool
- `config.yaml` — default configuration

## Philosophy

- The whitelist is a feature, not a limitation. Quality over quantity.
- Respect target sites: obey robots.txt, use reasonable delays, and don't hammer servers.
- Keep the implementation simple and maintainable.
- Document decisions and assumptions.

Questions? Open an issue or reach out.
