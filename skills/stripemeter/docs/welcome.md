# Welcome to StripeMeter

StripeMeter helps you **prove and enforce pre-invoice parity** for Stripe usage billing.

---

## 1) Ingest (send usage events, exactly once)
- Endpoint: `/v1/events/ingest`  
- Send usage with an **Idempotency-Key** so duplicates are counted once.  
- Try it: see the 30-sec demo in the README.

**Read next:** [Ingest API](./api/ingest.md)

---

## 2) Replay (fix late events within a watermark window)
- Endpoint: `POST /v1/replay`  
- Run **dry-run** to see the delta, or **apply** to update counters.  
- Deterministic **parity report** via the Reconciliation Summary.

**Read next:** [Reconciliation Summary API](./api/reconciliation-summary.md)

---

## 3) Reconcile (prove drift → 0 before finalization)
- Endpoint: `GET /v1/reconciliation/summary`  
- View **drift** and **counters before/after**.  
- Use the **Parity Visualizer** to see the time-series change after replay.

**Read next:** [Reconciliation Summary API](./api/reconciliation-summary.md)

---

## 4) Usage History (visualize counters over time)
- Endpoint: `GET /v1/usage/history`  
- Returns **time-series** and **totals** for dashboards before/after replay.

**Read next:** [Usage History API](./api/usage-history.md)
