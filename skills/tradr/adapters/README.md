# Signal Adapters

A signal adapter connects any signal source to tradr's execution engine.

## The Interface

tradr's entry contract is one command:

```bash
python3 tradr-enter.py <ca> --score <N> [--chain <chain>] [--token <name>]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `ca` | Yes | Contract address |
| `--score` | Yes | Confidence score (0-10). Maps to position sizing via config. |
| `--chain` | No | `solana`, `base`, `ethereum`, `polygon`, `unichain`. Auto-detected from CA format if omitted. |
| `--token` | No | Human-readable name/ticker for logs and notifications. |

tradr handles everything after the signal: sizing, entry guards, buy execution, position tracking, exit management, and notifications.

## Score → Size Mapping

Scores map to position sizes via `score_to_size` in `config.json`:

```json
"score_to_size": {
  "8": 200.0,    // score >= 8 → $200
  "5": 150.0,    // score >= 5 → $150
  "3": 100.0,    // score >= 3 → $100
  "0": 50.0      // score >= 0 → $50
}
```

Higher score = higher conviction = bigger position. Customize the thresholds and sizes in your config.

## Score → Mode Mapping

Scores can also auto-select exit modes via `score_to_mode`:

```json
"score_to_mode": {
  "8": "swing",    // high conviction → longer hold
  "5": "snipe",    // medium → quick in/out
  "0": "snipe"     // low → quick in/out
}
```

## Building an Adapter

An adapter is any script or service that:

1. **Watches** a signal source
2. **Detects** trade signals
3. **Scores** them (your logic — what makes a signal strong vs weak?)
4. **Calls** `tradr-enter.py` with the CA + score

### Example Signal Sources

| Source | How It Works | Scoring Ideas |
|--------|-------------|---------------|
| **Twitter/X** | Monitor KOL accounts for token mentions | More KOLs mentioning = higher score |
| **On-chain whale tracking** | Watch large wallets for new buys | Multiple whales = higher score |
| **Telegram alpha groups** | Parse messages for contract addresses | Multiple groups = higher score |
| **DEX volume spikes** | Monitor unusual volume on DexScreener | Volume magnitude = higher score |
| **Copy-trading apps** | Parse notifications from Fomo, Cielo, etc. | Trader ranking + confluence = score |
| **Custom aggregator** | Combine multiple sources | Weighted multi-source scoring |

### Adapter Patterns

**Polling adapter** — check your source every N seconds:
```python
while True:
    signals = check_source()
    for s in signals:
        feed_to_tradr(s["ca"], s["score"], s["chain"])
    time.sleep(30)
```

**Webhook adapter** — receive signals via HTTP:
```python
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        feed_to_tradr(data["ca"], data["score"], data.get("chain"))
        self.send_response(200)
        self.end_headers()

HTTPServer(("", 8080), Handler).serve_forever()
```

**File watcher adapter** — watch a signals file:
```python
import time

last_pos = 0
while True:
    with open("signals.jsonl") as f:
        f.seek(last_pos)
        for line in f:
            signal = json.loads(line)
            feed_to_tradr(signal["ca"], signal["score"])
        last_pos = f.tell()
    time.sleep(5)
```

## Entry Guards

tradr rejects entries that fail any of these checks (you don't need to implement these in your adapter):

- Market cap exceeds ceiling
- Cooldown active for same token
- Daily trade limit reached
- Max concurrent positions reached
- Position size exceeds cap
- Already in position for this CA

## Files

- `example-adapter.py` — Complete working template. Replace `get_signals()` with your source.
