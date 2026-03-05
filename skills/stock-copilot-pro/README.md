# Stock Copilot Pro

Global multi-source stock analysis skill for ClawHub/OpenClaw style agents.

## SEO Keywords

OpenClaw stock skill, AI stock analysis, stock copilot, A股分析工具, 港股分析工具, 美股分析工具, 量化选股, 基本面分析, 技术分析 RSI MACD, 新闻情绪分析, X/Twitter sentiment, 行业雷达, 早报晚报, watchlist 管理, QVeris API, THS iFinD, Caidazi, Alpha Vantage, Finnhub

## Supported Capabilities

- `analyze`: 单票深度分析（估值、财务质量、技术面、新闻情绪、时序风险）
- `compare`: 多标的对比与风险收益排序
- `watch`: 持仓/关注池管理（list/add/remove）
- `brief`: 持仓导向的早报/晚报（可执行建议）
- `radar`: 行业热点雷达（多源主题聚合 + 投资线索）
- OpenClaw 场景优化：技能负责结构化数据，LLM 负责专业报告生成

## Data Sources (What powers this skill)

- **QVeris MCP/API**: unified tool discovery and execution (`qveris.ai`)
- **THS iFinD (CN/HK market data)**:
  - real-time quote: `ths_ifind.real_time_quotation`
  - financial statements: `ths_ifind.financial_statements`
  - company profile: `ths_ifind.company_basics`
  - historical prices: `ths_ifind.history_quotation`
- **Caidazi (CN news/research/public account)**:
  - `caidazi.news.query`
  - `caidazi.report.query`
  - `caidazi.search.hybrid.list`
  - `caidazi.search.hybrid_v2.query`
- **Global market/news sentiment**:
  - `alpha_news_sentiment`
  - `finnhub.news`
- **X/Twitter domain sentiment**:
  - `qveris_social.x_domain_hot_topics`
  - `qveris_social.x_domain_hot_events`
  - `qveris_social.x_domain_new_posts`
  - `x_developer.2.tweets.search.recent`

## Highlights

- Full-stack market intelligence: quote, fundamentals, technicals, news sentiment, and X sentiment
- Deterministic routing with `references/tool-chains.json` (stable tool priority by market/capability)
- Evolution v2: parameter-template memory from successful calls (reduces parameter mismatch errors)
- Cross-market support for US/HK/CN with market-aware symbol normalization
- Company-name friendly flow: auto resolves common company names to ticker + market (e.g. `特变电工` -> `600089.SH`)
- CN/HK sentiment enhanced with `caidazi` channels (research reports, news, WeChat/public accounts)
- CN/HK fundamentals enhanced with THS financial statements (income/balance sheet/cash flow)
- Data quality guardrails: completeness, freshness, and cross-source consistency checks
- LLM-ready structured outputs: skill code focuses on data, OpenClaw focuses on final narrative
- Structured thesis output: drivers, risks, bull/base/bear scenarios, tracking KPIs
- Event radar from latest news + X, with timeline/theme view and cross-source topic evidence
- Structured outputs for both human workflows (`markdown`) and downstream systems (`json`)

## Why It Stands Out

- **Reliable in noisy API environments**: auto-fallback when a provider degrades or rejects symbols.
- **Stable but adaptive**: hardcoded tool-chain for predictability + evolution parameter templates for robustness.
- **Signal fusion, not single-source bias**: combines market data and sentiment channels.
- **Security-minded by default**: avoids key leakage and keeps evolution state metadata-only.
- **Readable by default, evidence on demand**: standard report is concise; add `--evidence` for full parsed/raw trace.

## Requirements

- Node.js 18+
- `QVERIS_API_KEY`

```bash
export QVERIS_API_KEY="your-api-key"
```

## Install as an Independent Skill

```bash
npx skills add <repo-url> --skill stock-copilot-pro
```

Or copy this folder directly into your agent skill directory.

## What You Get

- One-symbol analysis with confidence and risk notes
- Multi-symbol comparison for portfolio-level decisions
- Watchlist management for holdings and watch symbols (`watch list/add/remove`)
- Scheduled daily briefs (`brief --type morning|evening`) for OpenClaw cron jobs
- Industry hot-topic radar (`radar`) with candidate idea mapping
- Unified OpenClaw flow:
  - Skill commands return structured data (`analyze`/`brief`/`radar`)
  - `SKILL.md` provides professional analysis guides for each module
  - OpenClaw LLM generates concise, actionable final reports

## Usage

### Analyze one symbol

```bash
node scripts/stock_copilot_pro.mjs analyze --symbol AAPL --market US --mode comprehensive
```

### Public-audience preference flow

Without preference flags, the script returns a questionnaire by default.

```bash
node scripts/stock_copilot_pro.mjs analyze --symbol AAPL
```

Skip questionnaire and run directly:

```bash
node scripts/stock_copilot_pro.mjs analyze --symbol AAPL --skip-questionnaire --style balanced --risk mid --horizon mid
```

### Analyze HK/CN symbols

```bash
node scripts/stock_copilot_pro.mjs analyze --symbol 0700 --market HK --mode technical
node scripts/stock_copilot_pro.mjs analyze --symbol 600519 --market CN --mode comprehensive
node scripts/stock_copilot_pro.mjs analyze --symbol "特变电工" --mode comprehensive
```

### Compare multiple symbols

```bash
node scripts/stock_copilot_pro.mjs compare --symbols AAPL,MSFT,NVDA --market GLOBAL --mode comprehensive
```

### Watchlist management

```bash
node scripts/stock_copilot_pro.mjs watch --action list
node scripts/stock_copilot_pro.mjs watch --action add --bucket holdings --symbol AAPL --market US
node scripts/stock_copilot_pro.mjs watch --action add --bucket watchlist --symbol 0700.HK --market HK
node scripts/stock_copilot_pro.mjs watch --action remove --bucket watchlist --symbol 0700.HK --market HK
```

### Morning/Evening brief

```bash
node scripts/stock_copilot_pro.mjs brief --type morning --format markdown
node scripts/stock_copilot_pro.mjs brief --type evening --format chat
```

### Industry radar

```bash
node scripts/stock_copilot_pro.mjs radar --market GLOBAL --limit 10
```

### JSON output

```bash
node scripts/stock_copilot_pro.mjs analyze --symbol AAPL --format json --skip-questionnaire
```

### Chat output

```bash
node scripts/stock_copilot_pro.mjs analyze --symbol AAPL --format chat --skip-questionnaire
```

### Event radar options

```bash
node scripts/stock_copilot_pro.mjs analyze --symbol NVDA --skip-questionnaire --event-view theme --event-window-days 14 --event-universe global
```

### Routing and evolution behavior

- Tool selection priority comes from `references/tool-chains.json`
- If preferred tools fail, script falls back to generic capability search
- Evolution state file: `.evolution/tool-evolution.json` (v2 schema)
- Evolution stores successful parameter templates (`param_templates`) and examples (`sample_successful_params`)
- Evolution does **not** control tool priority ranking
- No API key/auth header/raw payload are persisted
- You can disable persistence per run with `--no-evolution`

## Prompt Examples

- `Give me a comprehensive report for AAPL`
- `Analyze 0700.HK with technical focus`
- `Compare AAPL, MSFT, NVDA and rank by risk-reward`
- `Analyze 600519 with fundamentals and sentiment`
- `Give me AAPL analysis with X sentiment included`
- `Compare 0700.HK and 600519 across fundamentals and sentiment`

## Options

- `--market`: `US|HK|CN|GLOBAL` (default: `GLOBAL`)
- `--mode`: `basic|fundamental|technical|comprehensive` (default: `comprehensive`)
- `--format`: `markdown|json|chat` (default: `markdown`)
- `--action`: `list|add|remove` (for `watch` command)
- `--bucket`: `holdings|watchlist` (for `watch add/remove`)
- `--type`: `morning|evening` (for `brief` command)
- `--max-items`: max symbols included in brief (default: `8`)
- `--limit`: search result count per capability (default: `10`)
- `--max-size`: max response bytes per execution (default: `30000`)
- `--timeout`: timeout in seconds (default: `25`)
- `--include-source-urls`: include provider `full_content_file_url` in output (off by default)
- `--evidence`: include full parsed/raw evidence sections (off by default)
- `--no-evolution`: disable reading/writing `.evolution/tool-evolution.json` for this run
- `--horizon`: `short|mid|long`
- `--risk`: `low|mid|high`
- `--style`: `value|balanced|growth|trading`
- `--actionable`: include execution-oriented strategy rules
- `--skip-questionnaire`: skip default preference questionnaire
- `--summary-only`: compact summary-first markdown output
- `--event-window-days`: event window size (7/14/30)
- `--event-universe`: `global|same_market`
- `--event-view`: `timeline|theme`

## Notes

- Data availability can vary by symbol and provider.
- The script will attempt fallback tools and clearly report missing sections.
- External source URLs are hidden by default in report output.
- `full_content_file_url` is supported for complete payload retrieval, but runtime restricts fetch host to `qveris.ai` (HTTPS only).
- X sentiment may use direct ticker search first and fall back to finance-domain hot posts when needed.
- Report includes system-time data cutoff and transparent routing/template-hit metadata.
- Watchlist local file path: `config/watchlist.json` (example: `config/watchlist.example.json`).
- OpenClaw scheduler example: `config/openclaw-cron.example.json`.

## Containerized local development

Development and OpenClaw integration files are managed at repository root under
`dev-infra/` to keep this skill folder publish-clean for ClawHub.

- Start dev container: `make up`
- Check runtime: `make check`
- Run regression smoke: `make smoke`
- Stop containers: `make down`

OpenClaw session prompt fixtures are in
`dev-infra/stock-copilot-pro/prompts/` (not in skill package).

## Troubleshooting

- `QVERIS_API_KEY environment variable is required`
  - Export the key first, then rerun.
- Some symbols return sparse/empty fields
  - Retry with market-specific code format (`0700.HK`, `600519.SH`).
  - For CN/HK fundamentals, the script prioritizes THS financial statements and always calls `company_basics` to补齐公司画像字段。
  - For some HK symbols, income/cash-flow fields may still be empty due to upstream coverage; report will explicitly标注数据源空缺。
  - Use `--mode basic` to get a quick quote/fundamentals baseline.
- Sentiment endpoint rejects ticker format
  - Script falls back to general market news and adds warnings in `risks`.
- X query result quality is noisy
  - Use stricter queries or combine with `fundamental` mode for better filtering.
- Rate-limited providers
  - Wait 30-60 seconds and retry, or reduce request burst.

## Live Validation Snapshot

Validated via QVeris MCP tool executions:

- `US (AAPL)`:
  - Quote: success
  - Fundamentals: success
  - Technicals: success
  - Sentiment: success
  - X sentiment: success
- `HK (0700.HK)`:
  - Quote: success (THS real-time quotation)
  - Fundamentals: success (THS financial statements / company basics fallback)
  - Technical trend: success (THS history quotation)
  - Sentiment: fallback when ticker format is rejected
  - X sentiment: success (cached and direct query path verified)
- `CN (600519.SH/600519.SS)`:
  - Quote: success (THS real-time quotation)
  - Fundamentals: success (THS financial statements / company basics fallback)
  - Technical trend: success (THS history quotation / RSI where available)
  - Sentiment: fallback when ticker format is rejected
  - X sentiment: success (direct or fallback path verified)
- `CN company-name input (特变电工)`:
  - Input resolution: success (`特变电工` -> `600089.SH`)
  - News: success (`caidazi.news.query`)
  - Research reports: success (`caidazi.report.query`)
  - Fundamentals: success (`ths_ifind.financial_statements`, income statement fields verified)

## Security

- Never hardcode `QVERIS_API_KEY` in committed files.
- `.env.local` is supported for local testing but should not be uploaded.
- Runtime evolution state stores tool metadata and parameter templates only.
- API keys and authorization headers are not persisted in evolution files.
- Evolution state is pruned with bounded size to avoid unbounded local persistence.
- Script calls only QVeris APIs (`qveris.ai`) and does not install packages or run arbitrary commands.
- Even when provider payload includes `full_content_file_url`, fetch is host-restricted to `qveris.ai` to prevent arbitrary outbound requests.

## Disclaimer

This skill is for research and educational purposes only.
It does not constitute financial or investment advice.

