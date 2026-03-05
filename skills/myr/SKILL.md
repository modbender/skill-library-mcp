---
name: myr
description: Capture, search, verify, export, import, and synthesize Methodological Yield Reports (MYRs) for Starfighter/Pistis intelligence compounding. Use when: (1) installing MYR on a node, (2) storing yield from OODA cycles, (3) searching prior yield before new work, (4) operator-reviewing MYR quality, (5) exporting/importing signed MYRs between nodes, (6) generating weekly digests, or (7) integrating MYR with an agent memory system. Triggers: "install MYR", "store a MYR", "what did we learn about", "weekly yield", "export yield", "import yield", "methodological yield", "MYR".
---

# MYR — Methodological Yield Reports

A pistis-native intelligence compounding system. Every meaningful OODA cycle (Observe, Orient, Decide, Act) produces yield — techniques, insights, falsifications, patterns. MYR captures it so it compounds across sessions, agents, and nodes.

**Repo:** https://github.com/JordanGreenhall/myr-system

## Required Outputs

For every MYR operation, return:
1. Action performed
2. Artifact IDs affected
3. Verification result
4. Next recommended step

## Installation (New Node)

```bash
git clone https://github.com/JordanGreenhall/myr-system.git
cd myr-system
npm install
cp config.example.json config.json
```

Edit `config.json`:
- Set unique `node_id` (short, e.g. `n2`, `north-star`)
- Confirm paths and key locations are writable

Generate keys:

```bash
node scripts/myr-keygen.js
```

Set environment:

```bash
export MYR_HOME=/absolute/path/to/myr-system
```

## Node Identity

Every node must have a unique `node_id` and a `node_uuid`. These are set during keygen and enforced at runtime.

**All scripts refuse to run if `node_id` is still the default `"n1"`.** You will get an error with remediation steps and exit 1.

`myr-keygen` generates your keypair and writes `node_uuid` to `config.json` automatically. Verify your identity before any cross-node exchange:

```bash
node $MYR_HOME/scripts/myr-identity.js
```

Output:
```
MYR Node Identity
─────────────────────────────────────────
  node_id:     n2
  node_uuid:   0c12b56f-0e44-44df-82a9-53d32dd0b1f3
  key:         SHA256:212a98c0e6f6b3c9…

  Fingerprint: n2 / 0c12b56f / SHA256:212a98c0e6f6b3c9…
─────────────────────────────────────────
```

**Before exchanging packages with a peer:** run `myr-identity.js` on both nodes. Read your fingerprint to your peer out-of-band and confirm theirs. Only proceed once fingerprints are mutually confirmed.

## Verify Installation (Ping Test)

Run all five. All must succeed.

```bash
cd $MYR_HOME
node scripts/myr-store.js --intent "Installation test" --type technique \
  --question "Does MYR work on this node?" --evidence "Store succeeded" \
  --changes "MYR is operational" --tags "test"
node scripts/myr-search.js --query "installation test"
node scripts/myr-verify.js --queue
node scripts/myr-sign.js --all
node scripts/myr-export.js --all
```

If all five succeed, node is operational.

## Capturing Yield

```bash
node $MYR_HOME/scripts/myr-store.js \
  --intent "What was being attempted" \
  --type insight \
  --question "The specific question resolved" \
  --evidence "Observable evidence supporting the answer" \
  --changes "What will be different next cycle" \
  --tags "domain1,domain2" \
  [--falsified "What was proven NOT to work"] \
  [--confidence 0.85] \
  [--agent agent-name]
```

Yield types:
- `technique` — reusable method that works
- `insight` — orientation-changing understanding
- `falsification` — proof something does not work (high value)
- `pattern` — recurring structure across cycles

## Searching Prior Yield

```bash
node $MYR_HOME/scripts/myr-search.js --query "topic" [--tags "domain"] [--type technique] [--limit 5]
```

Use before known-domain work, architecture decisions, and when asked "what do we know about X?"

## Verification and Rating Policy

- Rating scale is 1-5.
- Only designated operators may assign final ratings.
- A MYR is "network-eligible" only after at least 1 operator review.
- Node join criterion: at least 10 MYRs and average operator rating >= 3.0 over the most recent 10 reviewed MYRs.
- If ratings conflict by >=2 points, require a second operator review.

Queue and review commands:

```bash
node $MYR_HOME/scripts/myr-verify.js --queue
node $MYR_HOME/scripts/myr-verify.js --id ID --rating 4 --notes "..."
```

## Weekly Digest

```bash
node $MYR_HOME/scripts/myr-weekly.js [--week 2026-02-17] [--output report.md]
```

## Cross-Node Operations

### Export signed yield

```bash
node $MYR_HOME/scripts/myr-export.js --all
```

Produces signed JSON artifact in `$MYR_HOME/exports/` containing only eligible reviewed yield.

### Import peer yield

Import runs a preflight scan before touching the database. Two distinct errors:
- **"You are importing your own artifacts"** — `node_id` and `node_uuid` both match your node. Exit 2.
- **"Label collision between two different nodes"** — `node_id` matches but `node_uuid` differs. Peer must set a unique `node_id` and re-export. Exit 2.

If the peer's public key is already registered and a new import presents a different key for the same `node_id`, import exits 3 with remediation. No silent key overwrite.

```bash
node $MYR_HOME/scripts/myr-import.js --file path.myr.json [--peer-key keys/n2.public.pem]
```

### Cross-node synthesis

```bash
node $MYR_HOME/scripts/myr-synthesize.js --tags "domain" --min-nodes 2
```

Identifies convergent findings, divergences, and unique contributions.

## Signing and Trust Requirements

- Every exported MYR bundle must include a detached signature and signer ID.
- Import must fail closed on signature verification failure.
- Record signer ID, verification timestamp, and source node on successful import.
- Never merge unsigned or unverifiable MYRs into trusted datasets.

## Joining the Network

To become a peer in the Starfighter/Pistis network:
1. Install and verify node
2. Run `myr-identity.js` and exchange fingerprints out-of-band with your peer before touching packages
3. Exchange public keys (`$MYR_HOME/keys/{node_id}.public.pem`)
3. Produce real OODA yield (at least 10 MYRs with concrete evidence and explicit operational changes)
4. Complete operator review cycle (average rating >=3.0 over the most recent 10 reviewed MYRs)
5. Exchange signed artifacts and import peer artifacts

## Proposed Sharing Workflow (v0.1)

This is the current best-practice proposal for identifying and sharing yield across nodes. We have not yet fully field-tested this end-to-end at scale; treat as the current operating model and refine after prototype runs.

1. **Generate local artifacts** during normal operations (logs, notes, commits, analyses).
2. **Identify candidate yield**: select only learnings that are reusable outside the originating context.
3. **Convert to MYRs** with explicit evidence and “what changes next” fields.
4. **Filter for safety**: remove secrets, sensitive internals, PII, and context that should remain local.
5. **Operator review**: rate quality and transferability; only eligible reviewed MYRs move forward.
6. **Export signed bundle** (`myr-export --all`) and share artifact with peer plus key material as needed.
7. **Peer import and verify** (`myr-import --file ... --peer-key ...`): fail closed on invalid signature, reject duplicates, record provenance.
8. **Operationalize on receiving node**: make imported MYRs searchable and available for synthesis/decision support.

### Selection Rule (What to Share)

Share yield that is:
- **Generalizable** (helps another node run better)
- **Verified** (operator-reviewed, rating >=3)
- **Safe** (no protected local data)

Do not share raw internal ops artifacts when a distilled MYR captures the transferable method.

## Memory-System Integration (Async)

- MYR capture must be fire-and-forget from the primary agent flow.
- Do not block user response on MYR persistence.
- On persistence failure, log the error and surface a non-fatal warning.
- Include correlation ID so stored MYRs can be traced to source task/session.

Reference implementation: `$MYR_HOME/docs/INTEGRATION-EXAMPLES.md`

## ID Format

`{node_id}-{YYYYMMDD}-{seq}` — example: `n2-20260227-001`

## Architecture

For network protocol and scale roadmap (3 -> 300,000 nodes), see:
`$MYR_HOME/docs/NETWORK-ARCHITECTURE.md`
