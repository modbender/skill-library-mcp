# governance-guard

Structural authority separation for autonomous agent actions. An [OpenClaw](https://openclaw.dev) skill that interposes a three-phase governance pipeline between agent intent and execution.

**Core principle**: PROPOSE ≠ DECIDE ≠ PROMOTE. The agent proposes actions. A separate, deterministic policy engine decides admissibility. Only approved actions are promoted to execution. Every transition is witnessed.

## Quick start

```bash
# Install
npm install

# Run the governance pipeline
npx tsx scripts/governance.ts pipeline \
  '{"skill":"browser","tool":"fetch","model":"claude","actionType":"network","target":"https://api.example.com","parameters":{},"dataScope":[],"conversationId":"c1","messageId":"m1","userInstruction":"fetch the API"}' \
  --policy policies/standard.yaml
```

## Architecture

```
Agent Intent  →  PROPOSE  →  DECIDE  →  PROMOTE  →  Execution
                   │            │           │
              Serialize    Evaluate     Gate on
              + hash       policy       approval
                           (no LLM)    + freshness
```

| Phase | Authority | Implementation |
|-------|-----------|---------------|
| PROPOSE | Agent (LLM) | Structured intent capture with SHA-256 hash binding |
| DECIDE | Policy Engine (deterministic) | Pure function: policy + intent → verdict. No LLM. |
| PROMOTE | Execution Gate | Approve verdict + hash match + freshness check |

## Policy presets

| Preset | Default | Use case |
|--------|---------|----------|
| `minimal` | approve | Low friction. Blocks only credentials and destructive commands. |
| `standard` | deny | Recommended. Allows common ops, escalates network/delete. |
| `strict` | deny | Maximum safety. Reads only, everything else escalates. |

See [references/policy-schema.md](references/policy-schema.md) for the full policy file specification.

## Witness chain

Every governance decision is recorded as a hash-chained witness record in `~/.openclaw/governance/witness.jsonl`. The chain is tamper-evident: any modification to a historical record invalidates all subsequent hashes.

```bash
# Verify chain integrity
npx tsx scripts/governance.ts verify

# Audit recent decisions
npx tsx scripts/governance.ts audit --last 10
```

## Security properties

| Property | Guarantee |
|----------|-----------|
| Authority separation | DECIDE is a pure function with no LLM invocation |
| Fail-closed | System failures → deny. Missing policy → deny. Errors → deny. |
| Tamper evidence | Hash-chained witness log detects any historical modification |
| Verdict freshness | 30-second expiry prevents stale approval replay |
| Policy atomicity | Failed validation retains previous valid policy |

## Development

```bash
npm install
npm test                    # Run test suite
npm run typecheck           # TypeScript type checking
```

## License

MIT — MetaCortex Dynamics LLC
