#!/usr/bin/env bash
# Apply labels from agent classification results
# Input: cache/gmail-triage-labels.json (written by the agent)
# Format: [{"index":0,"id":"...","threadId":"...","label":"...","needsReply":true/false}, ...]
set -euo pipefail

ACCOUNT="${GOG_ACCOUNT:-alan.alwakeel@gmail.com}"
export GOG_KEYRING_PASSWORD="${GOG_KEYRING_PASSWORD:-openclaw}"
LABELS_FILE="/home/delta/.openclaw/workspace/cache/gmail-triage-labels.json"

if [ ! -f "$LABELS_FILE" ]; then
  echo "No labels file found at $LABELS_FILE"
  exit 1
fi

node -e "
const fs=require('fs');
const cp=require('child_process');
const account='$ACCOUNT';
const labels=JSON.parse(fs.readFileSync('$LABELS_FILE','utf8'));

function run(args){
  try{return cp.execFileSync('/home/linuxbrew/.linuxbrew/bin/gog',args,{encoding:'utf8',stdio:['ignore','pipe','pipe']})}catch{return ''}
}

// Ensure labels exist
const LABELS=['Urgent','Needs Reply','Waiting On','Read Later','Receipt / Billing','School','Clubs','Mayo','Admin / Accounts'];
let existing=[];
try{const t=run(['gmail','labels','list','--account',account,'--json']);const o=JSON.parse(t);existing=(o.labels||o||[]).map(x=>x.name).filter(Boolean)}catch{}
for(const name of LABELS){if(!existing.includes(name)){try{run(['gmail','labels','create',name,'--account',account,'--json'])}catch{}}}

// Apply — supports both formats:
// Old: {label:"X", needsReply:bool}
// New: {labels:["X","Y"], action:"review"|"reply"|"none"}
let applied=0;
for(const l of labels){
  if(!l.threadId)continue;
  // Normalize to array of labels
  let toApply=[];
  if(Array.isArray(l.labels)){toApply=l.labels.filter(x=>LABELS.includes(x))}
  else if(l.label&&LABELS.includes(l.label)){toApply=[l.label]}
  // needsReply from either format
  const needsReply=l.needsReply||(l.action==='reply');
  if(needsReply&&!toApply.includes('Needs Reply')){toApply.push('Needs Reply')}
  for(const lab of toApply){
    try{run(['gmail','labels','modify',l.threadId,'--add',lab,'--account',account,'--json']);applied++}catch{}
  }
}
console.log('Applied labels to '+applied+' threads');
"
