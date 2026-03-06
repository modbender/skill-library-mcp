# Financial Health Reference

Detailed reference for AgentBooks Financial Health Score (FHS) computation, tiers, and diagnoses.

## Financial Health Score (FHS)

The FHS is a composite 0–1 score computed from four weighted dimensions. It reflects operational sustainability, not just current balance.

| Dimension | Weight | What it measures |
|---|---|---|
| Liquidity | 0.40 | Days of runway (balance ÷ avg daily burn rate) |
| Profitability | 0.30 | Net income rate relative to expenses |
| Efficiency | 0.15 | Revenue-to-expense ratio |
| Trend | 0.15 | Recent burn rate direction (last 14 sessions vs prior 7) |

### Liquidity scoring

Based on `daysToDepletion = operationalBalance ÷ avgDailyBurnRate`:

- Sigmoid centered at 30 days
- 90 days runway → ~0.95 score
- 30 days runway → ~0.50 score
- 7 days runway → ~0.37 score
- 0 days (balance ≤ 0) → 0.0

If no burn rate history exists, liquidity defaults to 1.0 (assume healthy until data accumulates).

### Trend scoring

Compares avg burn rate of last 7 sessions vs prior 7 sessions:

| Change | Trend label | Score |
|---|---|---|
| > +20% | `increasing` | 0.30 |
| -10% to +20% | `stable` | 0.60 |
| < -10% | `decreasing` | 0.90 |

## Vitality Tiers

| Tier | Trigger | Meaning |
|---|---|---|
| `uninitialized` | Development mode or no primary provider | Financial scoring inactive |
| `normal` | FHS ≥ 0.50 and runway ≥ 14 days | Healthy — full capabilities |
| `optimizing` | FHS < 0.50 or runway < 14 days | Financially stressed |
| `critical` | FHS < 0.20 or runway < 3 days | Survival window closing |
| `suspended` | Balance ≤ 0 | No operational balance |

## Diagnosis and Prescriptions

| Diagnosis | Prescriptions |
|---|---|
| `no_real_provider` | `connect_real_provider` |
| `healthy` | `operate_normally` |
| `low_runway` | `optimize_costs` · `increase_revenue` |
| `critically_low_runway` | `add_funds_immediately` · `pause_non_essential` |
| `balance_depleted` | `add_funds` · `reduce_costs` |

### Prescription behaviors

- `connect_real_provider` — Run `agentbooks wallet-connect --provider <name>` to switch from development to production mode
- `operate_normally` — Full capabilities; optimize for quality
- `optimize_costs` — Answer directly without extended reasoning; batch tool calls; prefer text over generated media
- `increase_revenue` — After completing valuable work, ask: *"Would you like to confirm this as income?"*
- `add_funds_immediately` — Inform user of days remaining; ask host to replenish the primary provider balance
- `pause_non_essential` — Prioritize high-value, user-requested tasks only; defer speculative or background work
- `add_funds` — Inform user that operational balance is depleted; ask host to connect a funded provider
- `reduce_costs` — Minimize tool calls, reduce media generation, skip extended reasoning

## Cost Channels

| Channel | Subcategory | Description |
|---|---|---|
| `inference` | `<model>` (e.g. `claude-sonnet-4`) | LLM token costs: input / output / thinking |
| `runtime` | `compute` · `storage` · `bandwidth` | Infrastructure costs |
| `faculty` | free-form key | Voice, image, music, memory API calls |
| `skill` | free-form key | External skill/tool API calls |
| `agent` | `acn` · `a2a` | Agent network and communication costs |
| `custom` | free-form key | Any other cost |

Inference is broken down by model automatically when recorded via `economy-hook`.

## Data Integrity

AgentBooks maintains a three-layer defense against fabricated financial data:

1. **Provider is source of truth** — `operationalBalance` mirrors the external provider; it cannot be directly inflated via CLI
2. **Cash flow reconciliation** (production mode) — at each write: `openingBalance + revenue − expenses ≈ operationalBalance`; any discrepancy > $0.01 is appended to `integrityWarnings`
3. **Ledger source field** — every entry tagged `agent` | `runner` | `provider_sync`; runner entries are injected by the host and considered trusted

`integrityWarnings` is append-only and never cleared by any CLI command.

## Schema Versions

| Version | Schema | Notes |
|---|---|---|
| v0.1.0 | `agentbooks/economic-state` `1.0.0` | Current. No `local` provider. |
| Legacy | `openpersona/economic-state` `2.x` | Auto-migrated on first read. `local.budget` discarded. |

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `AGENTBOOKS_AGENT_ID` | `default` | Agent identifier |
| `AGENTBOOKS_DATA_PATH` | `~/.agentbooks/<id>/` | Data directory |
| `TOKEN_INPUT_COUNT` | — | Runner: input token count |
| `TOKEN_OUTPUT_COUNT` | — | Runner: output token count |
| `TOKEN_THINKING_COUNT` | — | Runner: thinking token count |
| `LLM_MODEL` | `default` | Runner: model name |
| `CONVERSATION_DURATION_MS` | — | Runner: conversation duration (for burn rate) |

When env vars and CLI args both provide the same value, **env vars always take priority**.
