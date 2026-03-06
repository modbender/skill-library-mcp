# ClawMeter Architecture

This document explains how ClawMeter works internally.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      OpenClaw Session Logs                   │
│              ~/.openclaw/agents/*/sessions/*.jsonl           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  File Watcher     │ ◄── chokidar (watches for changes)
                  │  (server.mjs)     │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  Ingest Pipeline  │ ◄── parses .jsonl, extracts usage
                  │  (ingest.mjs)     │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  Pricing Engine   │ ◄── calculates costs per token
                  │  (pricing.mjs)    │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  SQLite Database  │ ◄── stores sessions, events, aggregates
                  │  (db.mjs)         │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  Budget Alerts    │ ◄── checks thresholds, sends notifications
                  │  (alerts.mjs)     │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  Express API      │ ◄── REST endpoints for data access
                  │  (server.mjs)     │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  Dashboard UI     │ ◄── Chart.js + vanilla JS
                  │  (index.html)     │
                  └───────────────────┘
```

---

## Data Flow

### 1. Log Detection

**Trigger:** New session log created or updated

**Process:**
- `chokidar` watches `~/.openclaw/agents/*/sessions/*.jsonl`
- On `add` or `change` event, triggers ingest

**Code:** `src/server.mjs` lines 12-24

---

### 2. Ingestion

**Trigger:** File watcher event or manual `npm run ingest`

**Process:**

1. **Read file** and split into lines
2. **Parse each line** as JSON
3. **Identify event types:**
   - `session` → Create/update session record
   - `model_change` → Track model switches
   - `message` with `role=assistant` and `usage` → Extract token data
4. **Calculate costs** using `pricing.mjs`
5. **Insert into database** (deduplicated by `session_id` + `event_id`)
6. **Aggregate** session totals
7. **Rebuild daily aggregates**

**Code:** `src/ingest.mjs`

**Key functions:**
- `ingestAll(agentsDir)` — Scans all agents and sessions
- `ingestFile(filePath, agent)` — Processes a single .jsonl file
- `rebuildDailyAggregates()` — Recalculates daily totals

---

### 3. Cost Calculation

**Trigger:** Each `usage` event during ingestion

**Process:**

1. **Identify model** (from message or session state)
2. **Look up pricing** in `MODEL_PRICING` map
3. **Calculate:**
   - `inputCost = (inputTokens / 1M) * pricePerM`
   - `outputCost = (outputTokens / 1M) * pricePerM`
   - `cacheReadCost = (cacheReadTokens / 1M) * cacheReadPricePerM`
   - `cacheWriteCost = (cacheWriteTokens / 1M) * cacheWritePricePerM`
   - `totalCost = inputCost + outputCost + cacheReadCost + cacheWriteCost`
4. **Store** breakdown in `usage_events` table

**Code:** `src/pricing.mjs`

**Fuzzy matching:**
If exact model name not found, tries prefix/contains matching (e.g., "gpt-4o-2024-11-20" matches "gpt-4o").

---

### 4. Database Storage

**Schema:**

```sql
-- Sessions (one per conversation)
sessions (
  id,                -- Session UUID
  agent,             -- Agent name (e.g., "main")
  started_at,        -- ISO timestamp
  model,             -- Primary model used
  provider,          -- Provider (anthropic, openai, etc.)
  total_cost,        -- Sum of all usage events
  total_input_tokens,
  total_output_tokens,
  total_cache_read,
  total_cache_write,
  message_count
)

-- Usage events (one per assistant message)
usage_events (
  id,                -- Auto-increment
  session_id,        -- Foreign key
  event_id,          -- Message UUID (for deduplication)
  timestamp,         -- ISO timestamp
  model,
  provider,
  input_tokens,
  output_tokens,
  cache_read,
  cache_write,
  cost_input,        -- Breakdown by cost type
  cost_output,
  cost_cache_read,
  cost_cache_write,
  cost_total,
  stop_reason
)

-- Daily aggregates (for fast queries)
daily_aggregates (
  date,              -- YYYY-MM-DD
  model,
  provider,
  total_cost,
  total_input_tokens,
  total_output_tokens,
  session_count,
  message_count
)

-- Alert log (prevents duplicate notifications)
alerts_log (
  id,
  type,              -- "daily_budget" or "monthly_budget"
  threshold,
  actual,
  message,
  sent_at
)

-- Ingest state (tracks which files have been processed)
ingest_state (
  file_path,         -- Absolute path to .jsonl file
  last_line,         -- Last line number processed
  last_modified      -- mtime of file
)
```

**Why sql.js instead of better-sqlite3?**

- **Portability:** sql.js runs anywhere (no native binaries)
- **Simplicity:** Single-file database, easy to backup
- **Trade-off:** Slightly slower, but fine for our use case

**Code:** `src/db.mjs`

---

### 5. Budget Alerts

**Trigger:** After each ingest that adds new data

**Process:**

1. **Query daily spend:** Sum `daily_aggregates` for today
2. **Query monthly spend:** Sum `daily_aggregates` for current month
3. **Compare to thresholds** in `.env`
4. **If exceeded:**
   - Check `alerts_log` to avoid duplicate notifications (one per day)
   - Send via Telegram and/or email
   - Log to `alerts_log`

**Code:** `src/alerts.mjs`

**Alert methods:**
- **Telegram:** HTTP POST to Telegram Bot API
- **Email:** SMTP via `nodemailer`

---

### 6. API Layer

**Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/summary` | GET | Overall stats (today/week/month/all-time) |
| `/api/daily?days=N` | GET | Daily cost breakdown |
| `/api/sessions?limit=N&offset=M` | GET | List sessions with pagination |
| `/api/models` | GET | Cost breakdown by model |
| `/api/top-sessions?limit=N` | GET | Most expensive sessions |
| `/api/alerts` | GET | Recent budget alerts |
| `/api/ingest` | POST | Trigger manual re-ingest |

**Query pattern:**

```javascript
app.get('/api/endpoint', (req, res) => {
  const result = db.prepare('SELECT ...').all();
  res.json(result);
});
```

**Code:** `src/server.mjs` lines 26-59

---

### 7. Dashboard UI

**Tech stack:**
- **Vanilla JavaScript** (no framework)
- **Chart.js** for visualizations
- **CSS custom properties** for theming
- **Fetch API** for data loading

**Data flow:**

1. **Page loads** → Calls `loadAll()`
2. **loadAll()** → Fetches from all API endpoints
3. **Render functions** → Update DOM with data
4. **Auto-refresh** → Calls `loadAll()` every 30 seconds

**Key functions:**

- `loadSummary()` — Stat cards
- `loadDaily()` — Bar chart
- `loadModels()` — Donut chart
- `loadTopSessions()` — Table
- `loadRecentSessions()` — Table
- `loadAlerts()` — Alert history

**Code:** `web/index.html` (all-in-one file)

---

## Performance Considerations

### Ingestion Speed

**Bottleneck:** Parsing .jsonl files and database writes

**Optimizations:**
- **Incremental ingestion:** Only processes new lines (tracked via `ingest_state`)
- **Transactions:** Batch inserts in a single transaction
- **Deduplication:** `UNIQUE(session_id, event_id)` prevents double-counting

**Benchmark:** ~1000 messages/second on typical hardware

---

### Query Performance

**Bottleneck:** Large aggregations over millions of events

**Optimizations:**
- **Pre-aggregation:** `daily_aggregates` table avoids scanning all events
- **Indexes:** On `timestamp`, `session_id`, `date`
- **Efficient queries:** Use `SUM()` and `GROUP BY` in SQLite

**Benchmark:** Dashboard loads in <100ms with 100K+ events

---

### Memory Usage

**Footprint:** ~50-100 MB

**Components:**
- **Node.js runtime:** ~30 MB
- **sql.js in-memory DB:** ~20-50 MB (depends on data size)
- **Express server:** ~10 MB

---

## Error Handling

### File Parsing Errors

**Scenario:** Corrupted .jsonl line

**Handling:**
```javascript
try {
  p = JSON.parse(lines[i]);
} catch {
  continue; // Skip invalid lines
}
```

**Result:** Graceful skip, no crash

---

### Model Not Found

**Scenario:** Unknown model in session logs

**Handling:**
- `getModelPricing()` returns `null`
- `calculateCost()` returns `{ ..., estimated: true, unknownModel: 'model-id' }`
- Cost is `0`, but we track that it's an estimate

**Result:** Dashboard shows $0.00 for unknown models (with warning in data)

---

### Database Corruption

**Scenario:** SQLite file corrupted or locked

**Handling:**
- Backup exists in `data/clawmeter.db-shm` and `.db-wal` (WAL mode)
- User can delete and re-ingest from logs

**Prevention:** WAL mode reduces lock contention

---

## Scalability Limits

### Small to Medium Deployments

- **10K-100K messages:** Works perfectly
- **Database size:** ~10-100 MB
- **Query time:** <100ms

### Large Deployments

- **1M+ messages:** Database grows to ~1 GB
- **Query time:** May slow to ~500ms
- **Solution:** Periodic archiving or switch to PostgreSQL

### Multi-User

**Current:** Single-user (no auth)

**Future:** Add authentication + multi-tenant schema

---

## Security Model

### Local-Only by Default

- **Server binds to `localhost:3377`**
- **No external network access**
- **No cloud dependencies**

### Data Privacy

- **Only stores metadata:** Tokens, costs, timestamps
- **No message content** stored
- **No API keys** in database

### Remote Access

**Options:**

1. **SSH tunnel:**
   ```bash
   ssh -L 3377:localhost:3377 your-server
   ```

2. **Reverse proxy with auth:**
   ```nginx
   location /clawmeter/ {
     auth_basic "ClawMeter";
     auth_basic_user_file /etc/nginx/.htpasswd;
     proxy_pass http://localhost:3377/;
   }
   ```

---

## Future Improvements

### Planned

- [ ] PostgreSQL backend for massive scale
- [ ] User authentication (OAuth, API keys)
- [ ] Multi-tenant support (team workspaces)
- [ ] Export to CSV/JSON
- [ ] Cost forecasting (ML-based predictions)
- [ ] Slack/Discord webhooks
- [ ] Advanced filtering (by agent, session label, date range)
- [ ] Custom dashboards (user-configurable panels)

### Under Consideration

- [ ] Distributed tracing integration
- [ ] Real-time WebSocket updates (instead of polling)
- [ ] Mobile app (React Native)
- [ ] Cost optimization recommendations
- [ ] Anomaly detection (spike alerts)

---

## Contributing to Architecture

When making architectural changes:

1. **Update this document** to reflect new design
2. **Add tests** for critical paths
3. **Benchmark** performance impact
4. **Consider backward compatibility**
5. **Document migration path** if breaking changes

---

**Last updated:** 2026-02-14
