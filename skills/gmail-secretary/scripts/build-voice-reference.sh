#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="/home/delta/.openclaw/workspace/skills/gmail-secretary/references"
OUT="$OUT_DIR/voice.md"
mkdir -p "$OUT_DIR"

ACCOUNT="${GOG_ACCOUNT:-alan.alwakeel@gmail.com}"
export GOG_KEYRING_PASSWORD="${GOG_KEYRING_PASSWORD:-openclaw}"

TMP_IDS=$(mktemp)
trap 'rm -f "$TMP_IDS"' EXIT

# Get 50 recent sent message IDs.
/home/linuxbrew/.linuxbrew/bin/gog gmail messages search \
  'in:sent newer_than:180d' \
  --max 50 \
  --account "$ACCOUNT" \
  --json > "$TMP_IDS"

TMP_IDS_JSON="$TMP_IDS" OUT="$OUT" ACCOUNT="$ACCOUNT" node - <<'NODE'
const fs=require('fs');
const cp=require('child_process');

const account=process.env.ACCOUNT;
const raw=JSON.parse(fs.readFileSync(process.env.TMP_IDS_JSON,'utf8'));
const msgs=Array.isArray(raw)?raw:(raw?.messages||raw?.items||[]);
const ids=msgs.map(m=>m.id).filter(Boolean).slice(0,50);

function run(args){
  return cp.execFileSync('/home/linuxbrew/.linuxbrew/bin/gog', args, {encoding:'utf8', stdio:['ignore','pipe','pipe']});
}

function parseHeaders(m){
  const hs=m?.payload?.headers||[];
  const get=(n)=>{
    const h=hs.find(x=>(x.name||'').toLowerCase()===n.toLowerCase());
    return (h?.value||'').trim();
  };
  return {to:get('To'), subject:get('Subject'), date:get('Date')};
}

const samples=[];
for (const id of ids){
  try{
    const txt=run(['gmail','get',id,'--format=full','--account',account,'--json']);
    const m=JSON.parse(txt);
    const {to,subject,date}=parseHeaders(m);
    const body=String(m?.body||'').replace(/\r/g,'');
    // Strip quoted email chains (very rough)
    const cleaned=body
      .split('\n')
      .filter(line => !/^>/.test(line))
      .filter(line => !/^On .* wrote:/.test(line))
      .join('\n')
      .replace(/\n{3,}/g,'\n\n')
      .trim();
    let sn=cleaned.replace(/\s+/g,' ').trim();
    // Redact common personal identifiers
    sn = sn
      .replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/ig,'[email]')
      .replace(/\b\+?1?[-. (]*\d{3}[-. )]*\d{3}[-. ]*\d{4}\b/g,'[phone]')
      .replace(/\bLinkedIn\b/ig,'[link]');
    if (!sn) continue;
    samples.push({subject,to,date,snippet:sn.slice(0,600)});
  } catch (e){
    // ignore individual failures
  }
}

// Basic style heuristics (best-effort)
const greetings=['hi','hello','hey','good morning','good afternoon','good evening'];
let greetingCount=0, thanksCount=0, shortCount=0;
for (const s of samples){
  const t=s.snippet.toLowerCase();
  if (greetings.some(g=>t.startsWith(g+' ')||t.startsWith(g+','))) greetingCount++;
  if (/\bthank(s| you)\b/i.test(t)) thanksCount++;
  if (s.snippet.length<=180) shortCount++;
}

const lines=[];
lines.push('# Alan voice reference (auto)');
lines.push('');
lines.push(`Generated: ${new Date().toISOString()}`);
lines.push(`Sample size (sent snippets): ${samples.length}`);
lines.push('');
lines.push('## High-level style (heuristics)');
lines.push(`- Concise snippets (<=180 chars): ${Math.round(100*shortCount/Math.max(1,samples.length))}%`);
lines.push(`- Greeting present: ${Math.round(100*greetingCount/Math.max(1,samples.length))}%`);
lines.push(`- Gratitude language: ${Math.round(100*thanksCount/Math.max(1,samples.length))}%`);
lines.push('');
lines.push('## Drafting rules');
lines.push('- Clear, direct, polite.');
lines.push('- Keep it short by default (2–6 sentences).');
lines.push('- If you need something: context → ask → deadline/timeframe.');
lines.push('- Avoid filler.');
lines.push('');
lines.push('## Representative micro-snippets (snippets only)');
for (const s of samples.slice(0,15)){
  lines.push(`- “${s.snippet.slice(0,220)}${s.snippet.length>220?'…':''}”`);
}

fs.writeFileSync(process.env.OUT, lines.join('\n')+'\n');
NODE
