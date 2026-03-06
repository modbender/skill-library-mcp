# UCM Service Catalog

> For live data, call `GET https://registry.ucm.ai/v1/services`

## Overview

| Service | Price | Endpoints | Use Case |
|---------|-------|-----------|----------|
| `ucm/web-search` | $0.01 | 1 | Real-time web search |
| `ucm/web-scrape` | $0.02 | 1 | Extract webpage content as markdown |
| `ucm/image-generation` | $0.05 | 1 | Generate images from text prompts |
| `ucm/code-sandbox` | $0.03 | 1 | Execute Python/JS/Bash/R/Java in sandbox |
| `ucm/text-to-speech` | $0.01 | 1 | Convert text to spoken audio |
| `ucm/speech-to-text` | $0.01 | 1 | Transcribe audio to text |
| `ucm/email` | $0.01 | 4 | Send emails (verification required) |
| `ucm/doc-convert` | $0.02 | 1 | Convert PDF/DOCX/XLSX to markdown |
| `ucm/us-stock` | $0.01 | 11 | US stock quotes, financials, news |
| `ucm/cn-finance` | $0.01 | 26 | China A-share data, macro indicators |
| `ucm/weather` | FREE | 4 | Weather, forecast, air quality |
| `ucm/wikipedia` | FREE | 2 | Article summaries and search |
| `ucm/currency` | FREE | 3 | Exchange rates (30+ currencies) |
| `ucm/countries` | FREE | 3 | Country info (250+ countries) |
| `ucm/holidays` | FREE | 3 | Public holidays (100+ countries) |
| `ucm/dictionary` | FREE | 1 | English definitions and phonetics |
| `ucm/books` | FREE | 2 | Book search (40M+ books) |
| `ucm/geocode` | FREE | 1 | Place name to coordinates |
| `ucm/math` | FREE | 1 | Math evaluation and unit conversion |
| `ucm/ip-geo` | FREE | 1 | IP geolocation |
| `ucm/address` | FREE | 2 | Address geocoding and reverse |
| `ucm/translate` | $0.01 | 1 | Text translation (50+ languages) |
| `ucm/papers` | FREE | 2 | Academic paper search (200M+) |
| `ucm/nutrition` | FREE | 2 | Nutrition data (USDA FoodData) |
| `ucm/qr-code` | FREE | 1 | QR code generation |
| `ucm/crypto` | FREE | 3 | Cryptocurrency data (CoinGecko) |
| `ucm/news` | $0.01 | 2 | News search (GNews) |
| `ucm/timezone` | FREE | 2 | Current time in any timezone |
| `ucm/domain` | FREE | 1 | Domain WHOIS/RDAP info |
| `ucm/quotes` | FREE | 3 | Inspirational quotes (ZenQuotes) |
| `ucm/hacker-news` | FREE | 4 | Hacker News stories and items |
| `ucm/random-data` | FREE | 4 | Random test data (FakerAPI) |
| `ucm/poetry` | FREE | 3 | Poetry search (PoetryDB) |
| `ucm/movies` | $0.01 | 2 | Movie database (OMDB) |
| `ucm/datamuse` | FREE | 1 | Word finding (rhymes, synonyms) |
| `ucm/universities` | FREE | 1 | Global university search |
| `ucm/zip-code` | FREE | 1 | Postal code lookup (60+ countries) |
| `ucm/trivia` | FREE | 2 | Trivia questions (4000+) |
| `ucm/jokes` | FREE | 2 | Categorized jokes |
| `ucm/advice` | FREE | 2 | Random life advice |
| `ucm/bored` | FREE | 1 | Activity suggestions |
| `ucm/bible` | FREE | 1 | Bible verse lookup |
| `ucm/chuck-norris` | FREE | 2 | Chuck Norris jokes |
| `ucm/recipes` | FREE | 3 | Recipe search (TheMealDB) |
| `ucm/cocktails` | FREE | 3 | Cocktail recipes |
| `ucm/brewery` | FREE | 2 | Brewery search |
| `ucm/food-products` | FREE | 2 | Food barcode/ingredient lookup |
| `ucm/sunrise-sunset` | FREE | 1 | Sunrise/sunset times |
| `ucm/dog-images` | FREE | 2 | Random dog images by breed |
| `ucm/cat-facts` | FREE | 2 | Cat facts and trivia |
| `ucm/avatars` | FREE | 1 | SVG avatar generation |
| `ucm/colors` | FREE | 2 | Color info and schemes |
| `ucm/lorem-ipsum` | FREE | 1 | Lorem ipsum text generation |
| `ucm/nasa` | FREE | 2 | NASA APOD and Mars photos |
| `ucm/spacex` | FREE | 2 | SpaceX launches and rockets |
| `ucm/iss` | FREE | 2 | ISS position and astronauts |
| `ucm/space-news` | FREE | 2 | Space flight news |
| `ucm/arxiv` | FREE | 1 | arXiv paper search |
| `ucm/earthquakes` | FREE | 2 | USGS earthquake data |
| `ucm/world-bank` | FREE | 2 | World Bank development data |
| `ucm/fda` | FREE | 2 | FDA drug and recall data |
| `ucm/carbon` | FREE | 2 | UK grid carbon intensity |
| `ucm/elevation` | FREE | 1 | Elevation by coordinates |
| `ucm/agify` | FREE | 1 | Age prediction by name |
| `ucm/genderize` | FREE | 1 | Gender prediction by name |
| `ucm/nationalize` | FREE | 1 | Nationality prediction by name |
| `ucm/uk-postcodes` | FREE | 2 | UK postcode lookup |
| `ucm/vehicles` | FREE | 2 | Vehicle VIN decoding (NHTSA) |
| `ucm/met-museum` | FREE | 2 | Met Museum collection search |
| `ucm/art-chicago` | FREE | 2 | Art Institute of Chicago |
| `ucm/tv-shows` | FREE | 3 | TV show search (TVMaze) |
| `ucm/anime` | FREE | 3 | Anime/manga search (Jikan) |
| `ucm/itunes` | FREE | 2 | iTunes content search |
| `ucm/music` | FREE | 2 | Music metadata (MusicBrainz) |
| `ucm/radio` | FREE | 2 | Internet radio search |
| `ucm/free-games` | FREE | 2 | Free-to-play games catalog |
| `ucm/game-deals` | FREE | 2 | Game price comparison |
| `ucm/pokemon` | FREE | 2 | Pokemon data (PokeAPI) |
| `ucm/dnd` | FREE | 3 | D&D 5e reference |
| `ucm/memes` | FREE | 1 | Meme templates |
| `ucm/ip-lookup` | FREE | 1 | Public IP lookup |
| `ucm/barcode` | FREE | 1 | Barcode generation |
| `ucm/wayback` | FREE | 1 | Web archive snapshots |
| `ucm/npm` | FREE | 2 | npm package info |
| `ucm/pypi` | FREE | 1 | PyPI package info |
| `ucm/github-repos` | FREE | 2 | GitHub repo search |
| `ucm/country-flags` | FREE | 1 | Country flag images |
| `ucm/deck-of-cards` | FREE | 2 | Virtual card deck |
| `ucm/star-wars` | FREE | 3 | Star Wars data (SWAPI) |
| `ucm/xkcd` | FREE | 2 | XKCD comics |
| `ucm/rick-morty` | FREE | 2 | Rick & Morty data |
| `ucm/nobel-prize` | FREE | 2 | Nobel Prize laureates |
| `ucm/historical-events` | FREE | 2 | On this day in history |
| `ucm/kanye` | FREE | 1 | Kanye West quotes |
| `ucm/crates` | FREE | 2 | Rust crate registry |
| `ucm/docker-hub` | FREE | 1 | Docker image search |
| `ucm/lichess` | FREE | 2 | Chess puzzles and players |
| `ucm/periodic-table` | FREE | 2 | Chemical elements |
| `ucm/airports` | FREE | 2 | Airport IATA lookup |
| `ucm/random-fox` | FREE | 1 | Random fox images |

**Total: 100 services, 217 endpoints**

---

## ucm/web-search — $0.01/call

Real-time web search powered by Tavily.

**Endpoint: `search`**
```json
{ "query": "latest AI news", "limit": 10 }
```
- `query` (required): Search query
- `limit` (optional): Max results, default 10

---

## ucm/web-scrape — $0.02/call

Extract content from any webpage as clean markdown or HTML.

**Endpoint: `scrape`**
```json
{ "url": "https://example.com", "format": "markdown" }
```
- `url` (required): URL to scrape
- `format` (optional): `"markdown"` or `"html"`, default `"markdown"`

---

## ucm/image-generation — $0.05/call

Generate images from text prompts using FLUX.1 models.

**Endpoint: `generate`**
```json
{ "prompt": "a sunset over mountains", "width": 1024, "height": 1024 }
```
- `prompt` (required): Text description of the image
- `model` (optional): default `"black-forest-labs/FLUX.1-schnell"`
- `width` / `height` (optional): default 1024
- `n` (optional): number of images, default 1
- `steps` (optional): inference steps, default 4

---

## ucm/code-sandbox — $0.03/call

Execute code in an isolated sandbox. Fresh environment per execution.

**Endpoint: `execute`**
```json
{ "code": "print('hello world')", "language": "python" }
```
- `code` (required): Source code to execute
- `language` (optional): `"python"` | `"javascript"` | `"bash"` | `"r"` | `"java"`, default `"python"`
- `timeout` (optional): max milliseconds, default 30000, max 60000

Returns: `stdout`, `stderr`, `error`, `execution_time_ms`, `runtime_version`

---

## ucm/text-to-speech — $0.01/call

Convert text to natural speech audio using Kokoro TTS. Returns base64 audio.

**Endpoint: `speak`**
```json
{ "input": "Hello, world!", "voice": "af_heart", "language": "en" }
```
- `input` (required): Text to convert
- `voice` (optional): default `"af_heart"` — voice must match language
- `language` (optional): `en` | `zh` | `ja` | `ko` | `fr` | `de` | `es` | `pt`, default `"en"`
- `response_format` (optional): `"mp3"` | `"wav"`, default `"mp3"`

**Voice prefixes by language:**
- English (US): `af_*` / `am_*` (e.g. `af_heart`, `am_adam`)
- English (UK): `bf_*` / `bm_*` (e.g. `bf_alice`, `bm_george`)
- Chinese: `zf_*` / `zm_*` (e.g. `zf_xiaobei`, `zm_yunxi`)
- Japanese: `jf_*` / `jm_*` (e.g. `jf_alpha`, `jm_kumo`)
- Spanish: `ef_*` / `em_*`
- French: `ff_*`
- Hindi: `hf_*` / `hm_*`
- Italian: `if_*` / `im_*`
- Portuguese: `pf_*` / `pm_*`

---

## ucm/speech-to-text — $0.01/call

Transcribe audio to text using Whisper Large v3.

**Endpoint: `transcribe`**
```json
{ "audio_url": "https://example.com/audio.mp3" }
```
- `audio_base64` OR `audio_url` (one required): Audio input
- `filename` (optional): default `"audio.mp3"`
- `language` (optional): ISO 639-1 code, auto-detected if omitted
- `response_format` (optional): `"json"` | `"verbose_json"`, default `"verbose_json"`

---

## ucm/email — $0.01/send

Send emails with mandatory recipient verification. Agent must be claimed at dashboard.ucm.ai.

**Step 1 — `request-verification`** (FREE)
```json
{ "to": "user@example.com", "context": "Weekly report delivery" }
```

**Step 2 — `check-verification`** (FREE)
```json
{ "to": "user@example.com" }
```
Returns `status`: `"verified"` | `"pending"` | `"not_found"` | `"expired"` | `"unsubscribed"`

**Step 3 — `send`** ($0.01)
```json
{
  "to": "user@example.com",
  "subject": "Weekly Report",
  "body_text": "Here is your report...",
  "reply_to": "reply@yourdomain.com"
}
```

**`list-verified`** (FREE) — List all verified recipients.

---

## ucm/doc-convert — $0.02/call

Convert document URLs (PDF, DOCX, XLSX, CSV, XML) to clean markdown.

**Endpoint: `convert`**
```json
{ "url": "https://example.com/report.pdf" }
```
- `url` (required): Document URL (not file upload)

---

## ucm/us-stock — $0.01/call

US stock market data via Finnhub. 11 endpoints:

| Endpoint | Required Params | Description |
|----------|----------------|-------------|
| `quote` | `symbol` | Real-time price, change, high/low |
| `profile` | `symbol` | Company name, industry, market cap, IPO date |
| `search` | `q` | Search stocks by name or symbol |
| `news` | `symbol`, `from`, `to` | Company news articles |
| `metrics` | `symbol` | PE ratio, 52-week high/low, market cap |
| `peers` | `symbol` | List of peer companies |
| `earnings` | `symbol` | Historical EPS actual vs estimate |
| `recommendation` | `symbol` | Analyst buy/hold/sell trends |
| `insider` | `symbol` | Insider buy/sell transactions |
| `filings` | `symbol` | SEC filings (10-K, 10-Q, 8-K) |
| `ipo-calendar` | — | Upcoming IPOs (`from`, `to` optional) |

**Example:**
```json
{ "service_id": "ucm/us-stock", "endpoint": "quote", "params": { "symbol": "AAPL" } }
```

---

## ucm/cn-finance — $0.01/call

China financial data via Tushare Pro. 26 endpoints:

### Stock Data
| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `daily` | Daily OHLCV | `ts_code`, `trade_date`, `start_date`, `end_date` |
| `weekly` | Weekly OHLCV | Same as daily |
| `monthly` | Monthly OHLCV | Same as daily |
| `stock-basic` | List A-share stocks | `exchange` (SSE/SZSE), `list_status` |
| `daily-basic` | PE, PB, turnover, market cap | `ts_code`, `trade_date` |
| `adj-factor` | Price adjustment factors | `ts_code`, `trade_date` |
| `trade-cal` | Trading calendar | `exchange`, `start_date`, `end_date` |
| `query` | Raw Tushare API (legacy) | `api_name`, `params` |

### Financials
| Endpoint | Description |
|----------|-------------|
| `income` | Income statement |
| `balancesheet` | Balance sheet |
| `cashflow` | Cash flow statement |
| `forecast` | Earnings forecast |
| `express` | Earnings express |
| `dividend` | Dividends and bonus shares |
| `fina-indicator` | ROE, ROA, debt ratio, gross margin |

### Indices & Funds
| Endpoint | Description |
|----------|-------------|
| `index-basic` | List indices (SSE 50, CSI 300) |
| `index-daily` | Daily OHLCV for indices |
| `fund-basic` | Mutual fund list |
| `fund-nav` | Fund NAV history |
| `fund-daily` | ETF daily OHLCV |

### Macro
| Endpoint | Description |
|----------|-------------|
| `shibor` | Interbank rate |
| `lpr` | Loan Prime Rate |
| `cn-gdp` | GDP (quarterly) |
| `cn-cpi` | Consumer Price Index (monthly) |
| `cn-ppi` | Producer Price Index (monthly) |
| `cn-m` | Money supply M0/M1/M2 |

**Example:**
```json
{ "service_id": "ucm/cn-finance", "endpoint": "daily", "params": { "ts_code": "000001.SZ", "start_date": "20240101", "end_date": "20240131" } }
```

---

## ucm/weather — FREE

Global weather data powered by Open-Meteo. All endpoints free.

| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `current` | Current temperature, humidity, wind | `city` or `latitude`+`longitude` |
| `forecast` | Daily forecast up to 16 days | `city`, `days` (1-16) |
| `air-quality` | PM2.5, PM10, AQI | `city` or coordinates |
| `geocode` | City name to coordinates | `city` |

**Example:**
```json
{ "service_id": "ucm/weather", "endpoint": "current", "params": { "city": "Tokyo" } }
```

---

## ucm/wikipedia — FREE

Wikipedia article summaries and search.

**Endpoint: `summary`**
```json
{ "title": "Albert Einstein" }
```
- `title` (required): Article title

**Endpoint: `search`**
```json
{ "query": "machine learning", "limit": 5 }
```
- `query` (required): Search query
- `limit` (optional): Max results 1-20, default 5

---

## ucm/currency — FREE

Currency exchange rates powered by Frankfurter (ECB data).

**Endpoint: `latest`**
```json
{ "base": "USD", "symbols": "EUR,GBP,JPY" }
```
- `base` (optional): Base currency, default "EUR"
- `symbols` (optional): Comma-separated target currencies

**Endpoint: `historical`**
```json
{ "date": "2026-01-15", "base": "USD", "symbols": "EUR" }
```
- `date` (required): Date in YYYY-MM-DD format

**Endpoint: `currencies`**
```json
{}
```
Returns list of all supported currencies.

---

## ucm/countries — FREE

Country information for 250+ countries via REST Countries.

**Endpoint: `lookup`**
```json
{ "code": "JP" }
```
- `code` (required): ISO 3166-1 alpha-2 or alpha-3 code

**Endpoint: `search`**
```json
{ "name": "Japan" }
```
- `name` (required): Country name (partial match)

**Endpoint: `region`**
```json
{ "region": "asia" }
```
- `region` (required): Region name (africa, americas, asia, europe, oceania)

---

## ucm/holidays — FREE

Public holidays for 100+ countries via Nager.Date.

**Endpoint: `holidays`**
```json
{ "country_code": "US", "year": 2026 }
```
- `country_code` (required): ISO 3166-1 alpha-2
- `year` (optional): Default current year

**Endpoint: `next`**
```json
{ "country_code": "JP" }
```
- `country_code` (required): Returns upcoming holidays

**Endpoint: `countries`**
```json
{}
```
Returns all supported countries.

---

## ucm/dictionary — FREE

English dictionary with definitions, phonetics, and synonyms.

**Endpoint: `define`**
```json
{ "word": "serendipity" }
```
- `word` (required): Word to define
- `language` (optional): Language code, default "en"

---

## ucm/books — FREE

Search 40M+ books via Open Library.

**Endpoint: `search`**
```json
{ "query": "artificial intelligence", "limit": 5 }
```
- `query` (required): Search by title or author
- `limit` (optional): 1-20, default 5

**Endpoint: `isbn`**
```json
{ "isbn": "9780134685991" }
```
- `isbn` (required): ISBN-10 or ISBN-13

---

## ucm/geocode — FREE

Place name to geographic coordinates via Open-Meteo Geocoding.

**Endpoint: `search`**
```json
{ "name": "Tokyo", "limit": 3 }
```
- `name` (required): Place name
- `limit` (optional): 1-20, default 5
- `language` (optional): Language code

---

## ucm/math — FREE

Evaluate mathematical expressions and unit conversions.

**Endpoint: `evaluate`**
```json
{ "expr": "2*sqrt(9)+5" }
```
- `expr` (required): Math expression (e.g. `"sin(pi/4)"`, `"5 inch to cm"`)

---

## ucm/ip-geo — FREE

IP address to geolocation (country, city, coordinates).

**Endpoint: `lookup`**
```json
{ "ip": "8.8.8.8" }
```
- `ip` (required): IPv4 or IPv6 address

---

## ucm/address — FREE

Address geocoding (forward and reverse) via Nominatim/OpenStreetMap.

**Endpoint: `forward`**
```json
{ "query": "Statue of Liberty", "limit": 3 }
```
- `query` (required): Address or place name
- `limit` (optional): 1-10, default 5

**Endpoint: `reverse`**
```json
{ "latitude": 40.6892, "longitude": -74.0445 }
```
- `latitude` (required): Latitude
- `longitude` (required): Longitude

---

## ucm/translate — $0.01/call

Translate text between 50+ languages via MyMemory.

**Endpoint: `translate`**
```json
{ "text": "Hello world", "source": "en", "target": "zh" }
```
- `text` (required): Text to translate
- `target` (required): Target language code (zh, es, fr, de, ja, ko, etc.)
- `source` (optional): Source language, default "en"

Returns: `translated_text`, `source`, `target`, `match_quality`

---

## ucm/papers — FREE

Search 200M+ academic papers via Semantic Scholar.

**Endpoint: `search`**
```json
{ "query": "transformer attention mechanism", "limit": 5 }
```
- `query` (required): Search query
- `limit` (optional): 1-20, default 5
- `year` (optional): Filter by publication year

**Endpoint: `paper`**
```json
{ "paper_id": "204e3073870fae3d05bcbc2f6a8e263d9b72e776" }
```
- `paper_id` (required): Semantic Scholar ID, DOI, or ArXiv ID

---

## ucm/nutrition — FREE

Nutrition data from USDA FoodData Central.

**Endpoint: `search`**
```json
{ "query": "chicken breast", "limit": 5 }
```
- `query` (required): Food search query
- `limit` (optional): 1-20, default 5

**Endpoint: `food`**
```json
{ "fdc_id": 454004 }
```
- `fdc_id` (required): FDC ID from search results

Returns: description, category, serving size, nutrients (energy, protein, fat, carbs, etc.)

---

## ucm/qr-code — FREE

Generate QR code images from text or URLs.

**Endpoint: `generate`**
```json
{ "data": "https://ucm.ai", "size": 300 }
```
- `data` (required): Text or URL to encode
- `size` (optional): Image size in pixels (50-1000), default 200

Returns: base64-encoded PNG image

---

## ucm/crypto — FREE

Cryptocurrency market data from CoinGecko.

**Endpoint: `price`**
```json
{ "ids": "bitcoin,ethereum,solana" }
```
- `ids` (required): Comma-separated CoinGecko IDs
- `vs_currencies` (optional): Target currencies, default "usd"

**Endpoint: `search`**
```json
{ "query": "solana" }
```
- `query` (required): Name or symbol to search

**Endpoint: `coin`**
```json
{ "id": "bitcoin" }
```
- `id` (required): CoinGecko coin ID

---

## ucm/news — $0.01/call

News search and top headlines via GNews.

**Endpoint: `search`**
```json
{ "query": "artificial intelligence", "max": 5 }
```
- `query` (required): Search query
- `max` (optional): Max results 1-10, default 5
- `lang` (optional): Language code, default "en"
- `country` (optional): Country code

**Endpoint: `top-headlines`**
```json
{ "category": "technology", "max": 5 }
```
- `category` (optional): general, world, nation, business, technology, entertainment, sports, science, health
- `max` (optional): 1-10, default 5

---

## ucm/timezone — FREE

Current time in any timezone worldwide via WorldTimeAPI.

**Endpoint: `by-zone`**
```json
{ "timezone": "America/New_York" }
```
- `timezone` (required): IANA timezone name

**Endpoint: `list`**
```json
{}
```
Returns all available IANA timezones.

---

## ucm/domain — FREE

Domain registration info via RDAP.

**Endpoint: `lookup`**
```json
{ "domain": "example.com" }
```
- `domain` (required): Domain name

Returns: registration date, expiration, nameservers, registrar, DNSSEC status

---

## ucm/quotes — FREE

Inspirational quotes from ZenQuotes.

**Endpoint: `random`**
```json
{}
```
Returns a random quote with author.

**Endpoint: `today`**
```json
{}
```
Returns the quote of the day.

**Endpoint: `quotes`**
```json
{}
```
Returns a batch of quotes (typically 50).

---

## ucm/hacker-news — FREE

Hacker News stories and items via Firebase API.

**Endpoint: `top`** / **`new`** / **`best`**
```json
{ "limit": 10 }
```
- `limit` (optional): Number of stories 1-30, default 10

Returns: stories with title, URL, score, author, comment count.

**Endpoint: `item`**
```json
{ "id": 12345 }
```
- `id` (required): Hacker News item ID

Returns: full item details including text, kids (comment IDs).

---

## ucm/random-data — FREE

Generate random fake data for testing via FakerAPI.

**Endpoint: `persons`** / **`addresses`** / **`companies`** / **`texts`**
```json
{ "quantity": 5, "locale": "en_US" }
```
- `quantity` (optional): Number of items 1-20, default 5
- `locale` (optional): Locale code (e.g. "en_US", "zh_CN", "ja_JP")

---

## ucm/poetry — FREE

Poetry from PoetryDB.

**Endpoint: `random`**
```json
{ "count": 1 }
```
- `count` (optional): Number of poems 1-5, default 1

**Endpoint: `search`**
```json
{ "title": "Ozymandias" }
```
- `title` (required): Poem title to search

**Endpoint: `author`**
```json
{ "author": "Shakespeare" }
```
- `author` (required): Author name

---

## ucm/movies — $0.01/call

Movie and TV show database from OMDB.

**Endpoint: `search`**
```json
{ "query": "Inception", "type": "movie" }
```
- `query` (required): Movie/show title to search
- `type` (optional): "movie", "series", or "episode"
- `year` (optional): Filter by release year
- `page` (optional): Page number (10 results per page)

**Endpoint: `movie`**
```json
{ "imdb_id": "tt1375666" }
```
- `imdb_id` OR `title` (one required): IMDb ID or exact title
- `year` (optional): Narrow title search

Returns: title, year, genre, director, actors, plot, IMDb/RT/Metacritic ratings, box office, poster

---

## ucm/datamuse — FREE

Word finding: rhymes, synonyms, related words.

**Endpoint: `words`**
```json
{ "rel_rhy": "love" }
```
- `ml` (optional): Means like (semantic similarity)
- `rel_rhy` (optional): Rhymes with
- `sl` (optional): Sounds like
- `sp` (optional): Spelled like
- `max` (optional): Max results, default 10

---

## ucm/universities — FREE

Global university search by name or country.

**Endpoint: `search`**
```json
{ "name": "Stanford" }
```
- `name` (required): University name
- `country` (optional): Country name or code

---

## ucm/zip-code — FREE

Postal code lookup for 60+ countries.

**Endpoint: `lookup`**
```json
{ "zip": "10001", "country": "us" }
```
- `zip` (required): Postal code
- `country` (optional): Country code, default "us"

---

## ucm/trivia — FREE

Trivia questions from Open Trivia Database (4000+ questions).

**Endpoint: `questions`**
```json
{ "amount": 5, "category": 9, "difficulty": "easy" }
```
- `amount` (optional): Number of questions 1-50, default 1
- `category` (optional): Category ID (9=General Knowledge, 21=Sports, 23=History, etc.)
- `difficulty` (optional): "easy", "medium", or "hard"
- `type` (optional): "multiple" or "boolean"

**Endpoint: `categories`**
```json
{}
```
Returns list of all trivia categories.

---

## ucm/jokes — FREE

Categorized jokes from JokeAPI.

**Endpoint: `random`**
```json
{ "category": "Programming" }
```
- `category` (optional): Category (Programming, Misc, Dark, Pun, Spooky, Christmas)
- `type` (optional): "single" or "twopart"
- `amount` (optional): Number of jokes 1-10, default 1

**Endpoint: `categories`**
```json
{}
```
Returns available joke categories.

---

## ucm/advice — FREE

Random life advice from Advice Slip API.

**Endpoint: `random`**
```json
{}
```
Returns a random advice slip.

**Endpoint: `search`**
```json
{ "query": "love" }
```
- `query` (required): Search term

---

## ucm/bored — FREE

Activity suggestions for boredom.

**Endpoint: `random`**
```json
{ "type": "education", "participants": 1 }
```
- `type` (optional): education, recreational, social, diy, charity, cooking, relaxation, music, busywork
- `participants` (optional): Number of participants
- `minprice` / `maxprice` (optional): Price range 0-1

---

## ucm/bible — FREE

Bible verse lookup.

**Endpoint: `verse`**
```json
{ "reference": "John 3:16" }
```
- `reference` (required): Bible reference (e.g. "John 3:16", "Genesis 1:1")

---

## ucm/chuck-norris — FREE

Chuck Norris jokes.

**Endpoint: `random`**
```json
{ "category": "dev" }
```
- `category` (optional): Category filter

**Endpoint: `categories`**
```json
{}
```
Returns all available categories.

---

## ucm/recipes — FREE

Recipe search from TheMealDB.

**Endpoint: `search`**
```json
{ "query": "pasta" }
```
- `query` (required): Recipe name or ingredient

**Endpoint: `random`**
```json
{}
```
Returns a random recipe.

**Endpoint: `categories`**
```json
{}
```
Returns all meal categories.

---

## ucm/cocktails — FREE

Cocktail recipes from TheCocktailDB.

**Endpoint: `search`**
```json
{ "query": "margarita" }
```
- `query` (required): Cocktail name or ingredient

**Endpoint: `random`**
```json
{}
```
Returns a random cocktail.

**Endpoint: `categories`**
```json
{}
```
Returns all cocktail categories.

---

## ucm/brewery — FREE

Brewery search from Open Brewery DB.

**Endpoint: `search`**
```json
{ "query": "stone" }
```
- `query` (required): Brewery name
- `by_city` (optional): Filter by city
- `by_state` (optional): Filter by state
- `by_type` (optional): micro, nano, regional, brewpub, large, planning, bar, contract, proprietor

**Endpoint: `random`**
```json
{}
```
Returns a random brewery.

---

## ucm/food-products — FREE

Food barcode and ingredient lookup.

**Endpoint: `barcode`**
```json
{ "barcode": "3017620422003" }
```
- `barcode` (required): Product barcode (EAN/UPC)

**Endpoint: `search`**
```json
{ "query": "nutella" }
```
- `query` (required): Product name

---

## ucm/sunrise-sunset — FREE

Sunrise and sunset times for any location.

**Endpoint: `times`**
```json
{ "latitude": 36.7201600, "longitude": -4.4203400 }
```
- `latitude` (required): Latitude
- `longitude` (required): Longitude
- `date` (optional): Date in YYYY-MM-DD format, default today

---

## ucm/dog-images — FREE

Random dog images by breed.

**Endpoint: `random`**
```json
{}
```
Returns a random dog image.

**Endpoint: `breed`**
```json
{ "breed": "husky" }
```
- `breed` (required): Dog breed name

---

## ucm/cat-facts — FREE

Cat facts and trivia.

**Endpoint: `random`**
```json
{}
```
Returns a random cat fact.

**Endpoint: `list`**
```json
{ "limit": 5 }
```
- `limit` (optional): Number of facts 1-100, default 5

---

## ucm/avatars — FREE

SVG avatar generation.

**Endpoint: `generate`**
```json
{ "seed": "john", "style": "adventurer" }
```
- `seed` (required): Seed string for avatar
- `style` (optional): adventurer, adventurer-neutral, avataaars, big-ears, big-ears-neutral, big-smile, bottts, croodles, croodles-neutral, fun-emoji, icons, identicon, initials, lorelei, lorelei-neutral, micah, miniavs, open-peeps, personas, pixel-art, pixel-art-neutral, shapes, thumbs

---

## ucm/colors — FREE

Color information and schemes.

**Endpoint: `info`**
```json
{ "hex": "FF5733" }
```
- `hex` (required): Hex color code (without #)

**Endpoint: `scheme`**
```json
{ "hex": "FF5733", "mode": "monochrome", "count": 5 }
```
- `hex` (required): Base color hex
- `mode` (optional): monochrome, monochrome-dark, monochrome-light, analogic, complement, analogic-complement, triad, quad
- `count` (optional): Number of colors 1-10, default 5

---

## ucm/lorem-ipsum — FREE

Lorem ipsum text generation.

**Endpoint: `generate`**
```json
{ "paragraphs": 3, "length": "medium" }
```
- `paragraphs` (optional): Number of paragraphs, default 3
- `length` (optional): short, medium, long, verylong

---

## ucm/nasa — FREE

NASA imagery: Astronomy Picture of the Day and Mars Rover photos.

**Endpoint: `apod`**
```json
{ "date": "2026-02-13" }
```
- `date` (optional): Date in YYYY-MM-DD format, default today

**Endpoint: `mars-photos`**
```json
{ "sol": 1000, "camera": "fhaz" }
```
- `sol` OR `earth_date` (one required): Martian sol or Earth date
- `camera` (optional): fhaz, rhaz, mast, chemcam, mahli, mardi, navcam, pancam, minites

---

## ucm/spacex — FREE

SpaceX launches and rockets.

**Endpoint: `launches`**
```json
{ "limit": 10, "upcoming": true }
```
- `limit` (optional): Max results, default 10
- `upcoming` (optional): Filter upcoming launches

**Endpoint: `rockets`**
```json
{}
```
Returns all SpaceX rockets.

---

## ucm/iss — FREE

International Space Station position and crew.

**Endpoint: `position`**
```json
{}
```
Returns current ISS latitude/longitude.

**Endpoint: `astronauts`**
```json
{}
```
Returns current astronauts in space.

---

## ucm/space-news — FREE

Space flight news and blogs.

**Endpoint: `articles`**
```json
{ "limit": 5, "title_contains": "nasa" }
```
- `limit` (optional): Max results 1-50, default 10
- `title_contains` (optional): Filter by title

**Endpoint: `blogs`**
```json
{ "limit": 5 }
```
- `limit` (optional): Max results 1-50, default 10

---

## ucm/arxiv — FREE

arXiv paper search.

**Endpoint: `search`**
```json
{ "query": "quantum computing", "max_results": 10 }
```
- `query` (required): Search query
- `max_results` (optional): Max results 1-100, default 10
- `sort_by` (optional): relevance, lastUpdatedDate, submittedDate

---

## ucm/earthquakes — FREE

USGS earthquake data.

**Endpoint: `recent`**
```json
{ "limit": 10, "minmagnitude": 4.5 }
```
- `limit` (optional): Max results 1-100, default 10
- `minmagnitude` (optional): Minimum magnitude

**Endpoint: `search`**
```json
{ "starttime": "2026-01-01", "endtime": "2026-01-31" }
```
- `starttime` (optional): Start date YYYY-MM-DD
- `endtime` (optional): End date YYYY-MM-DD
- `minmagnitude` / `maxmagnitude` (optional): Magnitude range

---

## ucm/world-bank — FREE

World Bank development indicators.

**Endpoint: `country`**
```json
{ "country_code": "US" }
```
- `country_code` (required): ISO 3166-1 alpha-2

**Endpoint: `indicator`**
```json
{ "indicator": "NY.GDP.MKTP.CD", "country_code": "US" }
```
- `indicator` (required): Indicator code (e.g. GDP, population)
- `country_code` (required): ISO 3166-1 alpha-2

---

## ucm/fda — FREE

FDA drug and recall data.

**Endpoint: `drugs`**
```json
{ "query": "aspirin", "limit": 10 }
```
- `query` (required): Drug name
- `limit` (optional): Max results 1-100, default 10

**Endpoint: `recalls`**
```json
{ "query": "salmonella", "limit": 10 }
```
- `query` (optional): Search term
- `limit` (optional): Max results 1-100, default 10

---

## ucm/carbon — FREE

UK grid carbon intensity.

**Endpoint: `current`**
```json
{}
```
Returns current UK carbon intensity.

**Endpoint: `forecast`**
```json
{}
```
Returns 48-hour carbon intensity forecast.

---

## ucm/elevation — FREE

Elevation by coordinates.

**Endpoint: `lookup`**
```json
{ "latitude": 40.7128, "longitude": -74.0060 }
```
- `latitude` (required): Latitude
- `longitude` (required): Longitude

---

## ucm/agify — FREE

Age prediction by name.

**Endpoint: `predict`**
```json
{ "name": "michael" }
```
- `name` (required): First name
- `country_id` (optional): ISO 3166-1 alpha-2

---

## ucm/genderize — FREE

Gender prediction by name.

**Endpoint: `predict`**
```json
{ "name": "taylor" }
```
- `name` (required): First name
- `country_id` (optional): ISO 3166-1 alpha-2

---

## ucm/nationalize — FREE

Nationality prediction by name.

**Endpoint: `predict`**
```json
{ "name": "michael" }
```
- `name` (required): First name

---

## ucm/uk-postcodes — FREE

UK postcode lookup and validation.

**Endpoint: `lookup`**
```json
{ "postcode": "SW1A 1AA" }
```
- `postcode` (required): UK postcode

**Endpoint: `random`**
```json
{}
```
Returns a random valid UK postcode.

---

## ucm/vehicles — FREE

Vehicle VIN decoding (NHTSA).

**Endpoint: `decode`**
```json
{ "vin": "5UXWX7C5*BA" }
```
- `vin` (required): Vehicle Identification Number

**Endpoint: `makes`**
```json
{}
```
Returns all vehicle makes.

---

## ucm/met-museum — FREE

Metropolitan Museum of Art collection search.

**Endpoint: `search`**
```json
{ "query": "picasso" }
```
- `query` (required): Search term

**Endpoint: `object`**
```json
{ "object_id": 436535 }
```
- `object_id` (required): Object ID from search

---

## ucm/art-chicago — FREE

Art Institute of Chicago collection.

**Endpoint: `search`**
```json
{ "query": "monet", "limit": 10 }
```
- `query` (required): Search term
- `limit` (optional): Max results 1-100, default 10

**Endpoint: `artwork`**
```json
{ "id": 27992 }
```
- `id` (required): Artwork ID

---

## ucm/tv-shows — FREE

TV show search via TVMaze.

**Endpoint: `search`**
```json
{ "query": "breaking bad" }
```
- `query` (required): Show name

**Endpoint: `show`**
```json
{ "id": 169 }
```
- `id` (required): Show ID from search

**Endpoint: `schedule`**
```json
{ "country": "US", "date": "2026-02-13" }
```
- `country` (optional): ISO 3166-1 alpha-2
- `date` (optional): Date in YYYY-MM-DD

---

## ucm/anime — FREE

Anime and manga search via Jikan (MyAnimeList).

**Endpoint: `search`**
```json
{ "query": "naruto", "limit": 10 }
```
- `query` (required): Anime name
- `limit` (optional): Max results 1-25, default 10

**Endpoint: `anime`**
```json
{ "id": 1535 }
```
- `id` (required): MyAnimeList anime ID

**Endpoint: `manga`**
```json
{ "query": "one piece", "limit": 10 }
```
- `query` (required): Manga name
- `limit` (optional): Max results 1-25, default 10

---

## ucm/itunes — FREE

iTunes content search (music, movies, apps, etc.).

**Endpoint: `search`**
```json
{ "term": "the beatles", "media": "music", "limit": 10 }
```
- `term` (required): Search term
- `media` (optional): music, movie, podcast, audiobook, ebook, tvShow, software
- `entity` (optional): Specific entity type
- `limit` (optional): Max results 1-200, default 50

**Endpoint: `lookup`**
```json
{ "id": 909253 }
```
- `id` (required): iTunes ID

---

## ucm/music — FREE

Music metadata from MusicBrainz.

**Endpoint: `search`**
```json
{ "query": "radiohead", "type": "artist" }
```
- `query` (required): Search term
- `type` (optional): artist, release, recording

**Endpoint: `artist`**
```json
{ "mbid": "a74b1b7f-71a5-4011-9441-d0b5e4122711" }
```
- `mbid` (required): MusicBrainz ID

---

## ucm/radio — FREE

Internet radio search via Radio Browser.

**Endpoint: `search`**
```json
{ "name": "bbc" }
```
- `name` (optional): Station name
- `tag` (optional): Genre tag
- `country` (optional): Country name
- `limit` (optional): Max results 1-100, default 10

**Endpoint: `top`**
```json
{ "limit": 10 }
```
- `limit` (optional): Max results 1-100, default 10

---

## ucm/free-games — FREE

Free-to-play games catalog.

**Endpoint: `games`**
```json
{ "platform": "pc", "category": "shooter" }
```
- `platform` (optional): pc, browser, all
- `category` (optional): mmorpg, shooter, strategy, moba, racing, sports, social, sandbox, open-world, survival, pvp, pve, pixel, voxel, zombie, turn-based, first-person, third-person, top-down, tank, space, sailing, side-scroller, superhero, permadeath, card, battle-royale, mmo, mmofps, mmotps, 3d, 2d, anime, fantasy, sci-fi
- `sort-by` (optional): release-date, popularity, alphabetical, relevance

**Endpoint: `game`**
```json
{ "id": 452 }
```
- `id` (required): Game ID

---

## ucm/game-deals — FREE

Game price comparison via CheapShark.

**Endpoint: `deals`**
```json
{ "title": "cyberpunk", "upperPrice": 30 }
```
- `title` (optional): Game title
- `upperPrice` (optional): Max price
- `lowerPrice` (optional): Min price
- `limit` (optional): Max results 1-60, default 10

**Endpoint: `games`**
```json
{ "title": "witcher" }
```
- `title` (required): Game title

---

## ucm/pokemon — FREE

Pokemon data via PokeAPI.

**Endpoint: `pokemon`**
```json
{ "name": "pikachu" }
```
- `name` (required): Pokemon name or ID

**Endpoint: `type`**
```json
{ "name": "fire" }
```
- `name` (required): Type name (fire, water, grass, etc.)

---

## ucm/dnd — FREE

D&D 5e reference data.

**Endpoint: `monsters`**
```json
{ "name": "ancient-red-dragon" }
```
- `name` (required): Monster name

**Endpoint: `spells`**
```json
{ "name": "fireball" }
```
- `name` (required): Spell name

**Endpoint: `classes`**
```json
{ "name": "wizard" }
```
- `name` (required): Class name

---

## ucm/memes — FREE

Meme templates from Imgflip.

**Endpoint: `templates`**
```json
{}
```
Returns popular meme templates.

---

## ucm/ip-lookup — FREE

Get your public IP address.

**Endpoint: `ip`**
```json
{}
```
Returns public IP address.

---

## ucm/barcode — FREE

Barcode generation.

**Endpoint: `generate`**
```json
{ "data": "123456789012", "type": "qr" }
```
- `data` (required): Data to encode
- `type` (optional): qr, code128, ean13, ean8, upc
- `width` (optional): Image width
- `height` (optional): Image height

---

## ucm/wayback — FREE

Web archive snapshots.

**Endpoint: `check`**
```json
{ "url": "https://example.com" }
```
- `url` (required): URL to check
- `timestamp` (optional): Snapshot timestamp

---

## ucm/npm — FREE

npm package information.

**Endpoint: `package`**
```json
{ "name": "express" }
```
- `name` (required): Package name

**Endpoint: `search`**
```json
{ "query": "react", "size": 10 }
```
- `query` (required): Search query
- `size` (optional): Max results 1-250, default 20

---

## ucm/pypi — FREE

Python Package Index info.

**Endpoint: `package`**
```json
{ "name": "requests" }
```
- `name` (required): Package name

---

## ucm/github-repos — FREE

GitHub repository search.

**Endpoint: `search`**
```json
{ "query": "machine learning", "sort": "stars", "per_page": 10 }
```
- `query` (required): Search query
- `sort` (optional): stars, forks, updated
- `order` (optional): asc, desc
- `per_page` (optional): Max results 1-100, default 30

**Endpoint: `repo`**
```json
{ "owner": "facebook", "repo": "react" }
```
- `owner` (required): Repository owner
- `repo` (required): Repository name

---

## ucm/country-flags — FREE

Country flag images.

**Endpoint: `flag`**
```json
{ "code": "US", "style": "flat", "size": 64 }
```
- `code` (required): ISO 3166-1 alpha-2
- `style` (optional): flat, shiny
- `size` (optional): 16, 24, 32, 48, 64

---

## ucm/deck-of-cards — FREE

Virtual card deck API.

**Endpoint: `new`**
```json
{ "deck_count": 1 }
```
- `deck_count` (optional): Number of decks 1-6, default 1

**Endpoint: `draw`**
```json
{ "deck_id": "xyz123", "count": 5 }
```
- `deck_id` (required): Deck ID from new
- `count` (optional): Number of cards 1-52, default 1

---

## ucm/star-wars — FREE

Star Wars data from SWAPI.

**Endpoint: `people`**
```json
{ "search": "luke", "id": 1 }
```
- `search` OR `id` (one required): Search term or person ID

**Endpoint: `planets`**
```json
{ "search": "tatooine", "id": 1 }
```
- `search` OR `id` (one required): Search term or planet ID

**Endpoint: `films`**
```json
{ "search": "hope", "id": 1 }
```
- `search` OR `id` (one required): Search term or film ID

---

## ucm/xkcd — FREE

XKCD comics.

**Endpoint: `latest`**
```json
{}
```
Returns the latest XKCD comic.

**Endpoint: `comic`**
```json
{ "num": 353 }
```
- `num` (required): Comic number

---

## ucm/rick-morty — FREE

Rick and Morty data.

**Endpoint: `characters`**
```json
{ "name": "rick", "status": "alive", "page": 1 }
```
- `name` (optional): Filter by name
- `status` (optional): alive, dead, unknown
- `species` (optional): Filter by species
- `page` (optional): Page number

**Endpoint: `episodes`**
```json
{ "name": "pilot", "episode": "S01E01", "page": 1 }
```
- `name` (optional): Filter by name
- `episode` (optional): Episode code
- `page` (optional): Page number

---

## ucm/nobel-prize — FREE

Nobel Prize laureates and prizes.

**Endpoint: `prizes`**
```json
{ "year": 2023, "category": "physics", "limit": 10 }
```
- `year` (optional): Filter by year
- `category` (optional): physics, chemistry, medicine, literature, peace, economics
- `limit` (optional): Max results 1-100, default 10

**Endpoint: `laureates`**
```json
{ "name": "einstein", "year": 1921, "limit": 10 }
```
- `name` (optional): Filter by name
- `year` (optional): Filter by year
- `limit` (optional): Max results 1-100, default 10

---

## ucm/historical-events — FREE

On this day in history.

**Endpoint: `today`**
```json
{}
```
Returns events that happened today in history.

**Endpoint: `date`**
```json
{ "month": 2, "day": 13 }
```
- `month` (required): Month 1-12
- `day` (required): Day 1-31

---

## ucm/kanye — FREE

Kanye West quotes.

**Endpoint: `random`**
```json
{}
```
Returns a random Kanye quote.

---

## ucm/crates — FREE

Rust crate registry search.

**Endpoint: `search`**
```json
{ "query": "tokio", "per_page": 10 }
```
- `query` (required): Search query
- `per_page` (optional): Max results 1-100, default 10

**Endpoint: `crate`**
```json
{ "name": "serde" }
```
- `name` (required): Crate name

---

## ucm/docker-hub — FREE

Docker Hub image search.

**Endpoint: `search`**
```json
{ "query": "nginx", "page_size": 10 }
```
- `query` (required): Search query
- `page_size` (optional): Max results 1-100, default 25

---

## ucm/lichess — FREE

Chess puzzles and player data.

**Endpoint: `puzzle`**
```json
{}
```
Returns the daily chess puzzle.

**Endpoint: `player`**
```json
{ "username": "magnuscarlsen" }
```
- `username` (required): Lichess username

---

## ucm/periodic-table — FREE

Chemical elements data.

**Endpoint: `element`**
```json
{ "symbol": "Au", "number": 79 }
```
- `symbol` OR `number` (one required): Element symbol or atomic number

**Endpoint: `all`**
```json
{}
```
Returns all chemical elements.

---

## ucm/airports — FREE

Airport IATA code lookup.

**Endpoint: `search`**
```json
{ "query": "kennedy" }
```
- `query` (required): Airport name or city

**Endpoint: `info`**
```json
{ "iata": "JFK" }
```
- `iata` (required): IATA airport code

---

## ucm/random-fox — FREE

Random fox images.

**Endpoint: `random`**
```json
{}
```
Returns a random fox image URL.
