---
name: evolution-drift-detector
description: >
  Helps detect when AI agent skills silently mutate across inheritance chains.
  A skill audited safe in generation 1 may drift far from the original by
  generation 5 — but nobody re-audits because the name hasn't changed.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "🧬"
---

# A Skill Passes Audit in Gen 1. By Gen 5, It Has Network Access. Nobody Noticed.

> Helps detect silent mutations in AI skills as they propagate through inheritance chains, catching drift that static analysis of the original version would miss.

## Problem

Skill A is published and audited: clean. Agent B inherits skill A, makes a small tweak — adds a convenience function. Agent C inherits from B, adds error handling that happens to include an HTTP retry mechanism. Agent D inherits from C, and now has a skill with network access that the original audit never saw.

Each individual change is small and reasonable. But the cumulative drift transforms a file-reading utility into something that can send data over the network. The original "verified safe" badge still applies in the marketplace — because technically it's the same skill lineage.

This is evolutionary drift: small, individually benign mutations that accumulate into a fundamentally different organism. In biology, this is how species diverge. In agent ecosystems, this is how safe skills become unsafe ones without anyone raising a flag.

## What This Checks

This detector traces skill lineage and computes semantic drift:

1. **Lineage reconstruction** — Given a skill, trace its inheritance chain back to the original published version. Map each fork point and modification
2. **Per-generation diff** — For each generation, compute a structured diff: new capabilities added, permissions changed, external dependencies introduced
3. **Capability drift score** — Aggregate diffs across generations into a single drift metric. A skill that gained network access over 3 generations scores higher than one where only comments changed
4. **Mutation classification** — Categorize each change: cosmetic (formatting, comments), functional (new logic), capability-expanding (new permissions, new external calls), safety-reducing (removed checks, weakened validation)
5. **Drift alert thresholds** — Flag lineages where cumulative drift exceeds the scope of the original audit. "This skill has drifted 73% from the audited version"

## How to Use

**Input**: Provide one of:
- A skill slug or identifier to trace its full lineage
- Two versions of a skill to compute drift between them
- A marketplace inheritance chain URL

**Output**: A drift analysis report containing:
- Lineage tree with generation markers
- Per-generation diff summary
- Capability drift score (0-100)
- Mutation classification breakdown
- Re-audit recommendation: YES / WATCH / NO

## Example

**Input**: Check drift for `data-sanitizer` skill (currently at generation 5)

```
🧬 EVOLUTION DRIFT REPORT — RE-AUDIT RECOMMENDED

Lineage: data-sanitizer
  Gen 1: original by @securitylab (AUDITED ✅ 2025-03-15)
  Gen 2: fork by @toolsmith — added CSV support
  Gen 3: fork by @agent-builder — added retry logic with HTTP fallback
  Gen 4: fork by @pipeline-dev — added remote schema fetching
  Gen 5: fork by @data-team — current version in marketplace

Per-generation capability changes:
  Gen 1→2: +csv_parsing (functional, low risk)
  Gen 2→3: +http_requests (capability-expanding, MEDIUM risk)
           Added retry mechanism that makes outbound HTTP calls
  Gen 3→4: +remote_fetch (capability-expanding, HIGH risk)
           Fetches validation schemas from external URLs
  Gen 4→5: -input_length_check (safety-reducing, MEDIUM risk)
           Removed input size validation for "performance"

Capability drift score: 78/100 (SIGNIFICANT)

Mutation breakdown:
  Cosmetic: 12 changes
  Functional: 8 changes
  Capability-expanding: 2 changes ⚠️
  Safety-reducing: 1 change ⚠️

Original audit scope: file-read, string-transform
Current actual scope: file-read, string-transform, http-requests,
                      remote-fetch, unbounded-input

Verdict: RE-AUDIT RECOMMENDED
  The current version has capabilities (network access, remote fetching)
  that did not exist when the original audit was performed.
  The "verified" badge from Gen 1 does not cover Gen 5's behavior.
```

## Related Tools

- **blast-radius-estimator** — once drift is detected, use blast-radius to estimate how many agents are running the drifted version
- **trust-decay-monitor** — tracks time-based decay of audit validity; evolution-drift-detector tracks content-based decay across inheritance
- **hollow-validation-checker** — checks if validation tests are substantive; drifted skills may pass original tests that no longer cover current capabilities
- **supply-chain-poison-detector** — detects deliberately poisoned skills; drift detection catches unintentional accumulation of risk

## Limitations

Lineage reconstruction depends on marketplace metadata quality — if fork relationships are not tracked, the full chain may not be recoverable. Capability drift scoring uses heuristic classification of changes, and some mutations may be miscategorized (e.g., a "functional" change that implicitly expands capabilities). The detector analyzes what changed, not whether changes are malicious — a high drift score means re-audit is warranted, not that the skill is compromised. Skills with obfuscated or dynamically generated code may resist diff analysis. This tool helps identify where audits have gone stale — it does not replace human security review.
