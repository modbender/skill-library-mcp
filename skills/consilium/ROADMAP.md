# Council Roadmap

## v2.1 (current) ✅
- Unique lenses per panelist
- Opus as panelist + orchestrator with dual-role bias mitigation
- Profiles (thorough/balanced/fast) with min response thresholds
- Soft-timeout with quorum
- Optional Round 2 (debate)
- Mandatory "Dissenting opinions" block
- Agreement level indicator (🟢🟡🔴)
- Explicit language detection

## Considered and rejected

### Nested orchestrator (v4 proposal)
**Rejected** after council deliberation (2026-02-24). The problem it solves (user pings after 60s) doesn't justify the complexity (extra depth, error handling, token cost). Current "spawn → ping → synthesize" flow works fine.

### Auto-debate (auto Round 2 on disagreement)
**Deferred.** Models rarely change positions in Round 2, and auto-triggering doubles cost. Manual `--rounds 2` is sufficient.

### Blind mode (anonymize models during synthesis)
**Deferred.** Interesting idea but unproven benefit. Sonnet called it "a solution looking for a problem."

### Domain lenses (auto-detect question domain)
**Deferred.** Risk of narrowing thinking vs expanding it. Manual `--lenses` override is enough for now.

## Future ideas (if demand arises)
- State persistence (save panelist responses, --resume on synthesis failure)
- Observability (council-log.jsonl, stats command)
- Follow-up context (--follow-up previous council)
- User feedback loop (👍/👎 after synthesis)
- Weighted expertise per domain
