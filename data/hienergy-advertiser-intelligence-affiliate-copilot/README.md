# Hi Energy AI

**Officially published by Hi Energy AI** for OpenClaw.

OpenClaw skill for **Hi Energy / HiEnergy advertiser intelligence and affiliate research** using the v1 API.

This skill supports:
- Advertisers
- Affiliate programs
- Deals
- Transactions
- Contacts

Useful links:
- HiEnergy website (homepage): https://www.hienergy.ai
- HiEnergy app (main app): https://www.hienergy.ai
- API docs index: https://app.hienergy.ai/api_documentation
- API key page: https://app.hienergy.ai/api_documentation/api_key
- Login: https://app.hienergy.ai/sign_in
- Source repository: https://github.com/HiEnergyAgency/open_claw_skill

---

## Security metadata (explicit)

- **Primary credential:** `HIENERGY_API_KEY` (API key)
- **Accepted alias:** `HI_ENERGY_API_KEY`
- **Required environment variables:** `HIENERGY_API_KEY` (or `HI_ENERGY_API_KEY`)
- **External API host used by runtime code:** `https://app.hienergy.ai` only
- **Skill homepage:** `https://www.hienergy.ai`
- **Skill source:** `https://github.com/HiEnergyAgency/open_claw_skill`

---

## Quick Start (2 minutes)

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Get your API key

1. Log in: https://app.hienergy.ai/sign_in
2. Open: https://app.hienergy.ai/api_documentation/api_key
3. Copy your API key

### 3) Set env var

```bash
export HIENERGY_API_KEY="your_api_key_here"
# optional alias supported by the skill
export HI_ENERGY_API_KEY="$HIENERGY_API_KEY"
```

### 4) Run example

```bash
python3 example_usage.py
```

Tip: copy `.env.example` to `.env` for local development and export `HIENERGY_API_KEY` from your shell.

---

## What this skill does

- Search advertisers by name
- Search advertisers by domain/URL (`/advertisers/search_by_domain`)
- Use advertiser **show endpoint** when detailed profile info is requested
- On advertiser index-style responses, prompt users to reply **yes** for deeper profile summary
- Include publisher context in advertiser responses (when available)
- Include advertiser deep links in responses:
  - `https://app.hienergy.ai/a/<advertiser_id>`
- Search affiliate programs (via advertiser index + domain search; no separate affiliate_programs endpoint)
- Research/rank affiliate programs (commission-focused)
- Find/filter deals with fallback search behavior
- Query transactions with documented filters (date/network/advertiser/currency/sort)
- Query contacts
- Answer natural-language affiliate questions

### Power prompts

- "Find top affiliate programs for [vertical] with commission >= 10%."
- "Show active affiliate deals for [brand/category] and rank by payout potential."
- "Find partner contacts for [advertiser] and summarize next outreach filters."

---

## API behavior

- Root URL: `https://app.hienergy.ai`
- API base path used by this client: `/api/v1` (requests resolve to `https://app.hienergy.ai/api/v1/...`)
- Auth header: `X-Api-Key: <HIENERGY_API_KEY>`
- Default method limit (safe mode): `20`
- Max page size clamp: `500`
- Supports cursor and page/per_page pagination where available
- Normalizes JSON:API payloads (`data[].attributes`) for easier downstream usage

---

## Common usage examples

### Python

```python
from scripts.hienergy_skill import HiEnergySkill

skill = HiEnergySkill()

# Advertisers
advertisers = skill.get_advertisers(search="qatar airways", limit=20)

# Programs
programs = skill.get_affiliate_programs(search="yoga", limit=20)

# Program research/ranking
report = skill.research_affiliate_programs(
    search="yoga",
    min_commission=5,
    top_n=5
)

# Deals
deals = skill.find_deals(search="wellness", limit=20)

# Transactions
transactions = skill.get_transactions(
    advertiser_id="qatar-airways",
    start_date="2026-01-01",
    end_date="2026-01-31",
    sort_by="commission_amount",
    sort_order="desc",
    limit=50,
)

# Natural language
answer = skill.answer_question("Show me more details about advertiser Qatar Airways")
print(answer)
```

---

## Missing API key behavior

If the API key is missing, the skill raises a clear error that tells users exactly where to get the key:
- API key page: https://app.hienergy.ai/api_documentation/api_key
- Login page: https://app.hienergy.ai/sign_in

---

## Security best practices

- Never commit real API keys to git
- Keep keys in shell env or local `.env` only
- `.env` is gitignored in this repo
- Rotate exposed keys immediately
- Use least-privilege account access when possible

---

## Testing

```bash
python3 -m unittest test_hienergy_skill.py -v
```

## Suggested ClawHub tags

`affiliate-marketing,affiliate-program-management,affiliate-program-discovery,affiliate-deal-discovery,deal-management,partner-marketing,commission-analysis,advertiser-intelligence,publisher-contacts,transactions,impact,rakuten,cj,hienergy,hi-energy-ai`

---

## Files

- `SKILL.md` — OpenClaw trigger metadata + usage guidance
- `scripts/hienergy_skill.py` — API client + routing/formatting logic
- `references/endpoints.md` — endpoint/auth reference
- `example_usage.py` — runnable examples
- `test_hienergy_skill.py` — unit and integration tests
