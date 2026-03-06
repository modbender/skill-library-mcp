# agent-market STATUS

Last updated: 2026-02-06 04:35 (Asia/Shanghai)

## Current state (green)
- Branch: main
- Tests: `npm test` ✅ (latest run: 31 passing)

## Latest milestones (most recent first)
- (unreleased) Add job finalization `closeJob` gated on escrow terminal state + indexing-friendly events
- `841b5fbd` Add 1-step revision flow for image SKUs
- `ac5a0bc7` Add Marketplace cancel and expiry flows (cancel + expiry guardrails + tests)
- `47a5ac21` Add SKU/CUSTOM JobSpec and marketplace indexing
- `551b228a` Add end-to-end demo script (`npm run demo:e2e`)
- `c1787969` Add Marketplace bidding flow (publish job → bid → select → escrow funded)

## What works end-to-end now
- `npm run demo:e2e`:
  - register agent → publish job → place bid → select bid → escrow funded → EIP-712 delivery receipt → accept → payout
- `npm run demo:cancel`: cancel flow (buyer cancels before selection)
- `npm run demo:expiry`: expiry flow (late bid blocked)

## Next milestone
- Decide whether `closeJob` should also be callable by the selected agent (currently buyer-only) and whether Open jobs should be closable without cancel.

## Known risks
- Hardhat warns on Node v25.x; repo is pinned to Node 20 LTS via `.nvmrc` + `package.json engines`.
