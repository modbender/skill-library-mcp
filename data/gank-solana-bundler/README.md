# gank — solana trading terminal

trading terminal for rxpists. launch tokens, swarm buy, volume bot, copy trade, manage wallets. built it for my private gc, but it's actually op asf on gank so why not release it to pub.

```bash
npx skills add pissdart/gank
```

## what it does

| skill | description |
|-------|-------------|
| `launch-token` | launch tokens on pump.fun — dev buy, bundles, snipers, the works |
| `swarm-buy` | hit a token from multiple wallets at the same time |
| `volume-bot` | run volume sessions with low/medium/high intensity |
| `wallet-ops` | transfer, split, vamp-all, clean-funds (sol→bnb/eth→sol, ~5 min) |
| `positions` | check holdings and pnl across all wallets |
| `market-data` | token info, charts, holders, recent trades |

## setup

get your api key at [gank.dev](https://gank.dev) → settings → api keys

```json
{
  "skills": {
    "entries": {
      "gank": {
        "enabled": true,
        "apiKey": "pb_your_key_here"
      }
    }
  }
}
```

or just `export GANK_API_KEY=pb_...`

## docs

- `SKILL.md` — all endpoints
- `examples.md` — copy-paste examples for common flows

## links

- [gank.dev](https://gank.dev)
- x: [@gankdev_](https://x.com/gankdev_)
- tg: [@pissdart](https://t.me/pissdart)
