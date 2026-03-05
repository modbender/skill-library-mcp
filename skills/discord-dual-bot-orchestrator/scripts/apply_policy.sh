#!/usr/bin/env bash
set -euo pipefail

BOTB_CONFIG="${BOTB_CONFIG:-$HOME/.openclaw-bot-b/openclaw.json}"
GUILD_ID="${GUILD_ID:-GUILD_ID}"
CHANNEL_ID_LIST="${CHANNEL_ID_LIST:-CHANNEL_ID_LIST}"

python3 - << PY
import json
from pathlib import Path
cfg=Path("$BOTB_CONFIG")
d=json.loads(cfg.read_text())
channels={}
for cid in "$CHANNEL_ID_LIST".split(','):
    cid=cid.strip()
    if cid and cid!='CHANNEL_ID_LIST':
        channels[cid]={'allow':True,'requireMention':True}
if not channels:
    raise SystemExit('No CHANNEL_ID_LIST provided')

d.setdefault('channels',{}).setdefault('discord',{}).setdefault('guilds',{})["$GUILD_ID"]={'channels':channels}
cfg.write_text(json.dumps(d,ensure_ascii=False,indent=2))
print('Applied bot-b mention-gated allowlist:', list(channels.keys()))
PY

echo "Restart bot-b gateway after applying policy."
