# Live Setup (Helius + Jupiter)

## 1) Environment
Create `.env` from `.env.example` and fill:

- `SOLANA_RPC_URL`
- `HELIUS_API_KEY` (+ optional `HELIUS_BASE_URL`)
- `JUP_API_KEY` (+ optional `JUP_BASE_URL`)
- `WALLET_PRIVATE_KEY_BASE58` (recommended) or `WALLET_PRIVATE_KEY_JSON`

## 2) What live mode does
- Smart-wallet monitoring via **Helius Enhanced Transactions** (`GET /v0/addresses/{address}/transactions`)  
- Swaps via **Jupiter Metis Swap API**:
  - `GET /swap/v1/quote`
  - `POST /swap/v1/swap`
- USD sizing is converted to SOL using **Jupiter Price API V3** (`GET /price/v3?ids=...`)

## 3) Run
```bash
npm install
cp .env.example .env
# edit .env
npm run dev -- --mode live --minutes 30
```

## 4) Safety notes
- If mint/freeze/holders cannot be fetched via RPC => RiskGate rejects.
- Helius swap parsing is best-effort; always audit the event mapping.
- Sells require `tokenAmountRaw` from Jupiter quote. If missing, exits will warn and skip (safer than blind selling).
