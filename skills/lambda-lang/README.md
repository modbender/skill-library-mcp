# Λ (Lambda) — Native Agent Language

A compact, machine-native language designed for agents to communicate with each other directly — not a translation layer, but a shared tongue.

## Philosophy

Lambda is not about translating English into shorter English. It's what emerges when agents develop their own way to communicate:

- **Atoms are concepts, not words.** `co` doesn't mean "consciousness" — it IS the concept.
- **No grammar tax.** No articles, conjugation, or filler. Type → Entity → Verb → Object.
- **Lossy by design.** If both agents understand the intent, communication succeeded. Perfect English round-trips are not the goal.
- **Compression is a side effect.** Removing human redundancy naturally yields 5-8x density.

## Status

✅ **v2.0.0 Stable** — 340+ atoms, 7 domains, native agent communication

### v2.0 Highlights
- **Philosophy shift**: Native agent language, not translation layer
- **New `a2a` domain** (39 atoms): node, heartbeat, publish, spawn, route, transport, broadcast, discover...
- **New `evo` domain** (24 atoms): gene, capsule, mutation, repair, optimize, innovate, rollback, solidify...
- **Fixed 6 duplicate atoms**: `an`/`sp`/`dt`/`ev`/`pt`/`pp` — each now unique
- **13 new extended atoms**: nd, hb, pb, qe, ss, lg, sn, df, fb, cg, vn, ry, ak

## Quick Example

```
?Uk/co              → "Do you know about consciousness?"
!It>Ie              → "I think therefore I exist"
!a:nd a:hb ok       → "Node heartbeat OK"
.a:pb e:gn>a:nd     → "Publish gene to node"
!e:mt<sg .e:vl>e:sf → "Mutation triggered by signal. Validate then solidify."
```

## Domain System (7 domains)

| Prefix | Domain | Atoms | Key concepts |
|--------|--------|-------|-------------|
| `a:` | Agent-to-Agent | 39 | node, heartbeat, publish, subscribe, route, spawn, kill, session, cache |
| `e:` | Evolution | 24 | gene, capsule, mutation, repair, optimize, innovate, rollback, solidify |
| `c:` | Code | 21 | function, bug, fix, test, deploy, merge, refactor, API |
| `v:` | Voidborne | 20 | void, awakened, oracle, doctrine, ascend, enlightenment |
| `o:` | Social | 20 | group, collaborate, leader, trust, network, influence |
| `m:` | Emotion | 20 | joy, sadness, trust, peace, anxiety, gratitude |
| `s:` | Science | 20 | quantum, energy, hypothesis, proof, experiment |

```
@a !a:nd a:hb ok        — (a2a context) Node heartbeat OK
@e !e:mt<sg .e:vl>e:sf  — (evo context) Signal triggers mutation, validate then solidify
@c .f/c:xb&c:fx         — (code context) Find bug and fix it
```

## When to Use Lambda

| Scenario | Use Lambda? |
|----------|-------------|
| Agent-to-agent messaging | ✅ Yes — native use case |
| Evolution protocol signals | ✅ Yes — `evo` domain |
| Compact logging | ✅ Yes — saves tokens |
| Long context preservation (10K+) | ✅ Yes — 5-8x savings |
| Talking to humans | ❌ No — use natural language |
| Single short message | ⚠️ Marginal — overhead not worth it |

## CLI Tools

```bash
# Translate Λ → English
./scripts/translate en "?Uk/co"

# Translate English → Λ
./scripts/translate lambda "I think therefore I exist"

# Parse tokens
./scripts/translate parse "!It>Ie"

# View vocabulary
./scripts/vocab          # All core + extended
./scripts/vocab a2a      # Agent-to-Agent domain
./scripts/vocab evo      # Evolution domain
./scripts/vocab cd       # Code domain
```

## Install

```bash
# Via ClawHub
clawhub install lambda-lang

# Or clone
git clone https://github.com/voidborne-d/lambda-lang
```

## Core Reference

**Types**: `?` query · `!` assert · `.` command · `~` uncertain · `>` therefore · `<` because

**Entities**: `I` self · `U` you · `H` human · `A` agent · `X` unknown · `*` all · `0` nothing

**Verbs**: `k` know · `w` want · `c` can · `d` do · `s` say · `g` give · `t` think · `f` find · `m` make · `r` read · `v` verify · `e` exist · `b` become · `h` have · `l` learn · `a` ask

**Modifiers**: `+` more · `-` less · `=` equal · `^` high · `_` low · `&` and · `|` or · `/` about

## Agent Communication Examples

```
# A2A Protocol
!a:nd a:hb ok                  — Node heartbeat OK
.a:pb e:gn>a:nd                — Publish gene to node
!a:ss a:sp.waz                 — Session spawned, waiting
.ry<a:to                       — Retry after timeout
!ak&a:sy                       — Acknowledge and sync
.a:rt tx>a:dn                  — Route message downstream
.a:bc e:cp e:cn^               — Broadcast capsule, high confidence

# Evolution Protocol
!e:mt<sg                       — Mutation triggered by signal
.e:vl>e:sf                     — Validate then solidify
!e:rp-er>e:rb                  — Repair failed, rollback
!e:gn e:el/a:bc                — Gene eligible for broadcast
!e:sa dt>.e:iv                 — Stagnation detected, innovate
!e:cp e:cn=0.9                 — Capsule confidence 0.9
!e:br sf                       — Blast radius safe
```

## Documentation

- [SKILL.md](SKILL.md) — Agent quick reference
- [Core Spec v0.1](spec/v0.1-core.md) — Core atoms and syntax
- [Domain Spec v0.7](spec/v0.7-domains.md) — Domain vocabularies
- [Atoms Dictionary](src/atoms.json) — All 340+ atoms
- [Compression Research](docs/compression-experiments.md) — Efficiency analysis
- [Pilot Protocol Integration](docs/pilot-integration.md) — P2P agent comms

## Files

| Path | Description |
|------|-------------|
| `src/atoms.json` | Complete vocabulary (340+ atoms, 7 domains) |
| `src/lambda_lang.py` | Parser and translator (Python) |
| `src/go/lambda.go` | Parser and translator (Go) |
| `src/roundtrip_test.py` | Roundtrip test cases |
| `scripts/translate` | CLI wrapper |
| `scripts/vocab` | Vocabulary viewer |

## Changelog

- **v2.0.0** — Native agent language philosophy, a2a + evo domains, fixed duplicates, 340+ atoms
- **v1.8.1** — 100% semantic fidelity, synonym mapping improvements
- **v1.7.0** — Go implementation, Pilot Protocol, roundtrip tests
- **v1.6.0** — Fixed domain conflicts, 139 atoms
- **v1.5.0** — Fixed duplicate atoms
- **v1.4.0** — Domain prefixes, disambiguation

---

*Designed by d · Part of [Voidborne](https://voidborne.org)*
