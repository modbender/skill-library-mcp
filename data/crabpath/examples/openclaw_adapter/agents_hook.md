# CrabPath Memory Graph (auto-installed)

**Query** (before answering questions about prior work, context, decisions, corrections, lessons):
```bash
python3 ~/crabpath/examples/openclaw_adapter/query_brain.py ~/.crabpath/AGENT/state.json '<summary of user message>' --chat-id '<chat_id from inbound metadata>' --json
```
Always pass `--chat-id` so fired nodes are logged for later corrections.

**Learn** (after each response, using fired node IDs from query output):
- Good: `crabpath learn --state ~/.crabpath/AGENT/state.json --outcome 1.0 --fired-ids <ids>`
- Bad: `crabpath learn --state ~/.crabpath/AGENT/state.json --outcome -1.0 --fired-ids <ids>`

**Inject correction** (when corrected — same turn, don't wait for harvester):
```bash
python3 ~/crabpath/examples/openclaw_adapter/learn_correction.py \
  --state ~/.crabpath/AGENT/state.json \
  --chat-id '<chat_id>' --outcome -1.0 \
  --content "The correction text here"
```
This penalizes the last query's fired nodes AND injects a CORRECTION node with inhibitory edges.

**Inject new knowledge** (when you learn something not in any workspace file):
```bash
crabpath inject --state ~/.crabpath/AGENT/state.json \
  --id "teaching::<short-id>" --content "The new fact" --type TEACHING
```

**Health:** `crabpath health --state ~/.crabpath/AGENT/state.json`

**Maintenance** (structural ops — runs automatically via harvester cron, but can also run manually):
```bash
crabpath maintain --state ~/.crabpath/AGENT/state.json --tasks health,decay,prune,merge
```
Dry-run first: add `--dry-run` to preview changes without applying.

**Sync workspace** (after editing files):
```
crabpath sync --state ~/.crabpath/AGENT/state.json --workspace /path/to/workspace
```

**Compact old notes** (weekly or via cron):
```
crabpath compact --state ~/.crabpath/AGENT/state.json --memory-dir /path/to/memory
```
