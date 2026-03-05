# grupo-venus

Agentic skill that acts as a conversational frontend for [grupovenus.com](https://grupovenus.com) — natal charts, transit forecasts, and compatibility reports, all from the free tier.

> **Unofficial.** Not affiliated with or endorsed by Grupo Venus.

---

## What it does

- Fetches and displays **natal chart images**
- Parses **1-year slow-planet transit graphs** (Saturn, Uranus, Neptune, Pluto) and identifies the most active transits by intensity and timing
- Retrieves **interpretation texts** in three styles: colloquial, technical, and potentials
- Generates **compatibility reports** between two people (synastry, friendship, composite chart)
- Stores people across sessions in a local memory file
- Adapts its reading style per person: `casual`, `deep`, or `practical`

No API key required. Uses the public free tier of grupovenus.com as-is.

---

## Requirements

- `curl`
- `python3` (for URL-decoding the registration response)

---

## People storage

Person data is stored locally at:

```
~/.openclaw/workspace/memory/grupo-venus.json
```

---

## Free tier coverage

| Feature | Available |
|---------|-----------|
| Natal chart image | ✅ |
| 1-year outer planet transits (Sat–Plu) | ✅ |
| 3-day / 1-week short forecasts | ✅ |
| Transit interpretation texts | ✅ |
| Compatibility reports (partial) | ✅ |
| Full natal report text | Ticket required |
| 2-year forecast | Ticket required |

---

## License

MIT
