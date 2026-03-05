#!/usr/bin/env bash
set -euo pipefail

ACCOUNT="${GOG_ACCOUNT:-alan.alwakeel@gmail.com}"
export GOG_KEYRING_PASSWORD="${GOG_KEYRING_PASSWORD:-openclaw}"

VOICE_REF="/home/delta/.openclaw/workspace/skills/gmail-secretary/references/voice.md"
OUT_TRIAGE="/home/delta/.openclaw/workspace/cache/gmail-triage.md"
OUT_DRAFTS="/home/delta/.openclaw/workspace/cache/gmail-drafts.md"
INBOX_CACHE="/home/delta/.openclaw/workspace/cache/gmail-inbox-raw.json"
mkdir -p "$(dirname "$OUT_TRIAGE")"

# Step 1: Fetch inbox
/home/linuxbrew/.linuxbrew/bin/gog gmail messages search \
  'in:inbox (is:unread OR newer_than:2d)' \
  --max 20 \
  --account "$ACCOUNT" \
  --json > "$INBOX_CACHE"

# Step 2: Extract summaries for LLM classification
node -e "
const fs=require('fs');
const raw=JSON.parse(fs.readFileSync('$INBOX_CACHE','utf8'));
const msgs=Array.isArray(raw)?raw:(raw?.messages||raw?.items||[]);
const out=msgs.slice(0,12).map((m,i)=>{
  function pick(o,ks){for(const k of ks){if(o&&o[k]!=null)return o[k]}return null}
  function hdr(o,n){const hs=o?.payload?.headers||o?.headers;if(Array.isArray(hs)){const h=hs.find(x=>(x?.name||'').toLowerCase()===n.toLowerCase());return h?.value||null}return null}
  const subj=hdr(m,'Subject')||pick(m,['subject'])||'(no subject)';
  const from=hdr(m,'From')||pick(m,['from'])||'(unknown)';
  const snip=(pick(m,['snippet','text','preview'])||'').replace(/\s+/g,' ').trim().slice(0,200);
  const id=pick(m,['id','messageId'])||'';
  const threadId=pick(m,['threadId'])||id;
  const date=hdr(m,'Date')||pick(m,['date','internalDate'])||'';
  return {i,id,threadId,subj,from,snip,date};
});
fs.writeFileSync('/home/delta/.openclaw/workspace/cache/gmail-inbox-summaries.json',JSON.stringify(out,null,2));
console.log('Extracted '+out.length+' email summaries');
"

echo "Inbox fetched. Ready for agent classification."
