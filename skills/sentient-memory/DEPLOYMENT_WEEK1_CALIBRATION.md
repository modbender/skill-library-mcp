# Deployment Week 1 Calibration Playbook

Purpose: tune thresholds safely using real workload signal without increasing exposure risk.

## Day 0 (Before live traffic)
- Run all mandatory test vectors in Pragmatic and Strict modes.
- Record baseline metrics:
  - false Harm Spike rate
  - revocation propagation time
  - legibility gate rejection rate
  - metadata budget burn rate
  - stale-frame drift rate

## Day 1-2 (Conservative launch)
- Keep Strict auto-step enabled.
- Start with default thresholds from Annex A.
- Allow only low-risk memory promotion (Invariant/Pattern).
- Hold Exception/Move promotion for manual review.

## Day 3-4 (Measured tuning)
Adjust only one family of parameters per cycle:
1) detection sensitivity (Harm Spike window/count)
2) distribution safety (plurality/entropy floors)
3) privacy surface (metadata budget, epsilon)

Rules:
- one change set per 24h
- compare against Day 0 baseline
- rollback immediately if drift or exposure worsens

## Day 5-6 (Stress and edge cases)
- Run replay, sybil, and metadata-inference pressure tests.
- Simulate cross-jurisdiction conflict protocol.
- Verify protective pause rights are operational.

## Day 7 (Lock and document)
- Freeze tuned values for one full week.
- Publish a plain-language change note:
  - what changed
  - why it changed
  - what improved
  - what remains risky

## Red-line rollback triggers
Rollback to prior stable config if any occur:
- revocation SLA misses > 2 in 24h
- metadata budget exhaustion before 50% of day
- plurality or entropy floor breach without controlled response
- increase in stale-frame drift over baseline by >20%
