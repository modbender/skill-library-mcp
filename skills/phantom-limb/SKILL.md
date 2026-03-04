---
name: phantom-limb
version: 1.0.0
description: >
  Detects phantom dependencies — references to things that no longer exist,
  ghost state that lives in the gaps between modules, and invisible wires
  that connect your code to assumptions nobody remembers making. The codebase
  equivalent of feeling a limb that's already been amputated.
author: J. DeVere Cooley
category: cognitive-diagnostics
tags:
  - dependency-analysis
  - ghost-detection
  - code-health
  - static-analysis
metadata:
  openclaw:
    emoji: "🦾"
    os: ["darwin", "linux", "win32"]
    cost: free
    requires_api: false
    tags:
      - zero-dependency
      - cognitive
      - diagnostics
---

# Phantom Limb

> "The most dangerous dependency is the one that used to exist."

## What It Does

Phantom Limb detects **ghost references** — code that reaches for things that aren't there anymore. Not broken imports (your linter catches those). The subtle kind: environment variables nobody sets, config keys that were renamed three sprints ago, API endpoints that were deprecated but never removed from the client, file paths that point to directories that exist only on the original developer's machine.

Every codebase accumulates phantoms. They don't cause errors — they cause *mystery*. They're the reason a feature "works everywhere except production." They're the reason onboarding takes two weeks instead of two days.

## Why This Exists

Static analysis catches what's **wrong**. Linters catch what's **ugly**. Phantom Limb catches what's **missing** — the negative space between your code and reality.

| Traditional Tools Find | Phantom Limb Finds |
|---|---|
| Broken imports | Imports that resolve but reference dead code paths |
| Syntax errors | Semantically valid references to deleted concepts |
| Unused variables | Used variables that reference phantom state |
| Missing files | Files that exist but contain assumptions from a previous architecture |
| Type mismatches | Types that match but describe something that no longer exists |

## The Six Classes of Phantoms

### 1. Environmental Phantoms
References to environment variables, config files, or system state that no process ever sets.

```
// This worked when we ran Redis locally
const cache = process.env.REDIS_URL || 'redis://localhost:6379';
// Redis was replaced with Memcached 8 months ago.
// Nobody removed this. The fallback silently runs. Against nothing.
```

**Detection method:** Cross-reference every `process.env`, `os.environ`, `ENV[]` read against actual `.env`, `.env.example`, CI/CD configs, and deployment manifests.

### 2. Referential Phantoms
Code that references functions, classes, or modules that were moved, renamed, or deleted — but the reference still "works" because a shim, re-export, or fallback catches it.

```python
# utils.py re-exports calculate_tax for "backwards compatibility"
# Nobody imports calculate_tax from the original location anymore
# But nobody removed the re-export either
# And the original calculate_tax was rewritten. The re-export points to the old version.
from legacy.tax import calculate_tax  # pragma: no cover
```

**Detection method:** Trace every import chain to its terminal definition. Flag chains longer than 2 hops. Flag anything with "legacy", "compat", "old", or "deprecated" in the path that has no deprecation deadline.

### 3. Temporal Phantoms
Code that depends on timing, ordering, or sequencing that was true under a previous architecture but is no longer guaranteed.

```javascript
// This worked when auth was synchronous middleware
// After the async rewrite, user might not be populated yet
app.get('/dashboard', (req, res) => {
  const name = req.user.displayName; // Sometimes undefined. Sometimes not.
});
```

**Detection method:** Map all implicit ordering assumptions. Flag any data access that assumes a prior middleware/hook/lifecycle event has already completed without explicit await/guard.

### 4. Contractual Phantoms
API contracts, database schemas, or wire formats that the code expects but the other side no longer honors.

```python
# The payments API v2 removed the 'discount_code' field
# Our code still sends it. The API silently ignores it.
# Nobody knows the discount feature has been broken for 3 months.
payload = {
    "amount": total,
    "discount_code": user.discount,  # Phantom. Silently ignored.
}
```

**Detection method:** Compare every outbound payload construction against the latest API schema/docs. Compare every database query against the current schema. Flag fields that are constructed but never consumed.

### 5. Intentional Phantoms
Comments, TODOs, and documentation that describe behavior the code no longer exhibits. The specification has become a ghost story.

```java
/**
 * Retries up to 3 times with exponential backoff.
 * Falls back to cache on failure.
 */
// Retry logic was removed in PR #847. Cache fallback was never implemented.
public Response fetchData() {
    return client.get(url); // One shot. No retry. No fallback.
}
```

**Detection method:** Parse doc comments and compare claimed behavior against actual implementation. Flag docstrings that mention patterns (retry, cache, fallback, queue, batch) that don't appear in the method body.

### 6. Identity Phantoms
Variables, functions, or modules whose names describe something they no longer do. The name is a phantom of their original purpose.

```go
// This was a temporary cache. Three years ago.
func getTempCache() *PermanentStore {
    return &PermanentStore{ttl: 0} // TTL of zero = lives forever
}
```

**Detection method:** Semantic analysis of identifier names vs. their actual behavior. Flag contradictions between name semantics and implementation semantics (e.g., `temp` + no expiry, `async` + synchronous execution, `safe` + no error handling).

## How It Works

```
Phase 1: EXCAVATION
├── Scan all source files for external references
├── Build a reference graph (what reaches for what)
├── Map all environment reads, config lookups, API calls
└── Catalog all import chains and their terminal definitions

Phase 2: REALITY CHECK
├── Cross-reference against actual environment state
├── Compare API contracts against current schemas
├── Trace import chains to detect phantom re-exports
└── Compare documentation claims against implementation

Phase 3: PHANTOM CLASSIFICATION
├── Classify each phantom by type (1-6 above)
├── Score severity (silent failure vs. loud failure vs. latent)
├── Estimate blast radius (how many codepaths are affected)
└── Calculate haunting duration (how long has this been phantom)

Phase 4: EXORCISM REPORT
├── Prioritized list of phantoms by severity × blast radius
├── For each phantom: what it references, what's actually there, and what to do
├── Quick-fix suggestions for each class
└── Dependency reality map (what your code thinks exists vs. what does)
```

## Severity Scoring

| Severity | Description | Example |
|---|---|---|
| **Critical** | Phantom causes silent data loss or corruption | API field silently ignored, data never saved |
| **High** | Phantom causes intermittent failures | Temporal phantom, race condition with ghost state |
| **Medium** | Phantom causes confusion but no runtime errors | Identity phantom, misleading names |
| **Low** | Phantom is inert but adds cognitive load | Dead re-exports, orphaned configs |
| **Vestigial** | Phantom is harmless but indicates architectural rot | TODO comments from 2+ years ago |

## Output Format

```
╔══════════════════════════════════════════════════════════════╗
║                    PHANTOM LIMB SCAN                        ║
║                    12 phantoms detected                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  CRITICAL (2)                                                ║
║  ├── [Contractual] POST /api/payments sends 'discount_code'  ║
║  │   → Field removed in API v2 (2024-11-03)                 ║
║  │   → 3 months of silent discount failures                  ║
║  │   → Fix: Remove field from payload builder                ║
║  │                                                           ║
║  ├── [Environmental] REDIS_URL referenced in 4 files         ║
║  │   → No process sets this variable                         ║
║  │   → Fallback to localhost:6379 connects to nothing        ║
║  │   → Fix: Remove Redis references, use Memcached client    ║
║  │                                                           ║
║  HIGH (3)                                                    ║
║  ├── [Temporal] req.user accessed before auth middleware      ║
║  │   ...                                                     ║
╚══════════════════════════════════════════════════════════════╝
```

## Integration

Invoke when:
- Onboarding a new developer (show them where the ghosts live)
- After a major refactor (find what the refactor left behind)
- Before a production deploy (catch phantoms before users do)
- During architecture review (map the gap between intent and reality)

## Why It Matters

Every codebase has a **phantom architecture** — the system it *thinks* it is, layered on top of the system it *actually* is. The gap between these two architectures is where bugs hide, onboarding stalls, and technical debt compounds silently.

Phantom Limb doesn't find bugs. It finds the *conditions* that make bugs inevitable.

Zero external dependencies. Zero API calls. Pure structural analysis.
