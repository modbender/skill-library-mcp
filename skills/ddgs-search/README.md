# ddgs-search

Free multi-engine web search skill for [OpenClaw](https://github.com/camopel/openclaw) agents. No API keys required.

Supports: **Google, Bing, DuckDuckGo, Brave, Yandex, Yahoo, Wikipedia** + **arXiv API** for academic papers.

## Install

```bash
python3 scripts/install.py
```

Installs the `ddgs` Python package and verifies the CLI is accessible.

## Scripts

### `scripts/search.py` — Web search

```bash
python3 scripts/search.py -q "your query" -m 5
python3 scripts/search.py -q "AI news" -m 10 -b bing
python3 scripts/search.py -q "python tutorial" -m 5 -b google
```

**Options:**
| Flag | Description | Default |
|------|-------------|---------|
| `-q` | Search query | (required) |
| `-m` | Max results | 5 |
| `-b` | Backend: `duckduckgo`, `google`, `bing`, `brave`, `yandex`, `yahoo` | `duckduckgo` |

**Output:** JSON with `results` array of `{title, url, snippet}`.

### `scripts/arxiv_search.py` — arXiv paper search

```bash
python3 scripts/arxiv_search.py -q "transformer architecture" -m 10
python3 scripts/arxiv_search.py -q "diffusion models" -m 5 --sort-by relevance
```

**Options:**
| Flag | Description | Default |
|------|-------------|---------|
| `-q` | Search query | (required) |
| `-m` | Max results | 10 |
| `--sort-by` | `relevance` or `date` | `relevance` |

**Output:** JSON with `results` array including `arxiv_id`, `title`, `abstract`, `authors`, `published`, `pdf_url`.

## Usage in OpenClaw

The skill is registered with OpenClaw and provides two tools:

- **`web_search`** — Search the web across multiple engines
- **`arxiv_search`** — Search academic papers on arXiv

## Requirements

- Python 3.8+
- `ddgs` package (installed automatically)
- macOS or Linux (Windows: partial support)

## License

MIT
