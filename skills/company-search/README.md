# Company Research — Multi-LLM Adaptive Skill

Multi-source company research tool that generates structured reports comparable to Tianyancha / Qichacha.
Works across Kimi / OpenAI GPT / Claude / Gemini / MiniMax / Cursor and generic Agent environments.

基于多源搜索的公司调研工具，生成对标天眼查/企查查信息颗粒度的结构化报告。

---

## Files

| File | Description |
|------|-------------|
| `SKILL.md` | Main skill definition — AI reads this to execute research |
| `search_fetch.py` | Local fallback script for environments without built-in web tools |
| `package.json` | Metadata and setup script |

---

## Setup (optional — only needed for local fallback)

Requires Python 3.8+.

```bash
pip install ddgs requests beautifulsoup4 lxml trafilatura
```

Or via the package script:

```bash
npm run setup
```

---

## Usage

### As a Cursor / Codex Skill

Point your AI agent to `SKILL.md`. The skill handles tool detection automatically — no manual configuration needed.

### Local fallback (`search_fetch.py`)

For environments without built-in search/fetch tools:

```bash
# Search
python search_fetch.py search "字节跳动 注册资本 法定代表人" --num 10

# Fetch a URL
python search_fetch.py fetch "https://example.com/page.html" --max-chars 12000
```

Fetch strategies (tried in order by default):
- `direct` — browser-like headers, works on most open pages
- `jina` — r.jina.ai reader proxy, bypasses common bot-checks (free, no API key)
- `archive` — Wayback Machine snapshot, fallback for pages that no longer exist

---

## Supported Tool Environments

| Priority | SEARCH tool | FETCH tool |
|----------|-------------|------------|
| 1 | `kimi_search` | `kimi_fetch` |
| 2 | `web_search_preview` | `fetch` |
| 3 | `web_search` | `url_context` |
| 4 | `brave_web_search` | `browser_navigate` + `browser_snapshot` |
| 5 | `google_search` | `bash` / local script |
| 6 | `tavily_search` | — |
| 7 | `bash` / local script | — |

The skill auto-detects available tools and falls back gracefully down the priority list.
