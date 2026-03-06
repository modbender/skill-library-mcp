# Query Cookbook (hardcore EFT usage)

## 1) Service health

```bash
python3 skills/tarkov-api/scripts/tarkov_api.py status
```

Use before raids/tournaments to avoid queueing into outages.

---

## 2) Item economy scan

```bash
python3 skills/tarkov-api/scripts/tarkov_api.py item-search --name "ledx" --limit 10
python3 skills/tarkov-api/scripts/tarkov_api.py item-price --name "ledx"
```

Use to decide hold/sell and route (trader vs market reference values).

---

## 3) Ammo stack ranking

```bash
python3 skills/tarkov-api/scripts/tarkov_api.py ammo-compare \
  --names "7.62x39mm BP gzh" "7.62x39mm PS gzh" "7.62x39mm PP gzh"
```

Use for pen/dmg/price tradeoffs.

---

## 4) Quest chain unblock

```bash
python3 skills/tarkov-api/scripts/tarkov_api.py task-lookup --name "gunsmith"
python3 skills/tarkov-api/scripts/tarkov_api.py task-lookup --name "setup"
```

Use to quickly identify prerequisites and map context.

---

## 5) Boss route scouting

```bash
python3 skills/tarkov-api/scripts/tarkov_api.py map-bosses --map-name "Customs"
python3 skills/tarkov-api/scripts/tarkov_api.py map-bosses --map-name "Interchange"
```

Use when planning risk-heavy boss farming raids.

---

## 6) JSON mode for automation or dashboards

```bash
python3 skills/tarkov-api/scripts/tarkov_api.py item-price --name "bitcoin" --json
python3 skills/tarkov-api/scripts/tarkov_api.py ammo-compare --names "M855A1" "M995" --json
```

Use as machine-readable output for local scripts.

---

## 7) Stash value snapshot

`stash.json`:

```json
[
  {"name": "LEDX Skin Transilluminator", "count": 1},
  {"name": "Graphics Card", "count": 3},
  {"name": "Moonshine", "count": 2}
]
```

Run:

```bash
python3 skills/tarkov-api/scripts/tarkov_api.py stash-value --items-file ./stash.json
```

---

## 8) Trader flip detector

```bash
python3 skills/tarkov-api/scripts/tarkov_api.py trader-flip \
  --name "ammo" \
  --min-spread 15000 \
  --top 20
```

Use gross spread as a shortlist only; verify in-game fees/limits before committing capital.

---

## 9) Composite map risk score

```bash
python3 skills/tarkov-api/scripts/tarkov_api.py map-risk \
  --map-name "Customs" \
  --task-focus "setup" "bullshit"
```

Use score to tune kit risk, route aggression, and party composition.

---

## 10) Raid-kit recommendation

```bash
python3 skills/tarkov-api/scripts/tarkov_api.py raid-kit \
  --map-name "Customs" \
  --ammo-names "5.56x45mm M855A1" "5.56x45mm M856A1" "5.56x45mm M995" \
  --task-focus "setup"
```

Use this as a fast pre-raid decision helper; then adjust for your actual bankroll and confidence.

---

## 11) Wiki search for task/item pages

```bash
python3 skills/tarkov-api/scripts/tarkov_api.py wiki-search --query "Gunsmith Part 1" --limit 5
```

---

## 12) Wiki intro + revision context

```bash
python3 skills/tarkov-api/scripts/tarkov_api.py wiki-intro --title "LEDX Skin Transilluminator"
```

---

## 13) Wiki recent changes monitor

```bash
python3 skills/tarkov-api/scripts/tarkov_api.py wiki-recent --limit 20
```

Use to spot community-updated pages after patches/events.

---

## 14) Raw query (expert)

`query.graphql`:

```graphql
query($name: String!, $gm: GameMode) {
  items(name: $name, gameMode: $gm, limit: 5) {
    name
    avg24hPrice
    low24hPrice
    high24hPrice
  }
}
```

Run:

```bash
python3 skills/tarkov-api/scripts/tarkov_api.py raw \
  --query-file ./query.graphql \
  --variables '{"name":"sugar","gm":"regular"}'
```
