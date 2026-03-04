#!/bin/bash
# Bounty Hunter — Triage Slither findings with local LLM
# Usage: bash scripts/triage.sh <slither-output.json>
set -e

JSON_FILE="$1"
if [ -z "$JSON_FILE" ] || [ ! -f "$JSON_FILE" ]; then
  echo "Usage: bash scripts/triage.sh <slither-output.json>"
  exit 1
fi

# Extract HIGH/MEDIUM findings
python3 << PYEOF
import json, sys

with open("$JSON_FILE") as f:
    data = json.load(f)

detectors = data.get("results", {}).get("detectors", [])
findings = [d for d in detectors if d.get("impact") in ("High", "Medium")]

if not findings:
    print("No HIGH/MEDIUM findings.")
    sys.exit(0)

print(f"Found {len(findings)} HIGH/MEDIUM findings:\n")

for i, f in enumerate(findings, 1):
    check = f.get("check", "unknown")
    impact = f.get("impact", "?")
    confidence = f.get("confidence", "?")
    desc = f.get("description", "No description")[:200]
    
    # Get affected contract/function
    elements = f.get("elements", [])
    location = "unknown"
    if elements:
        e = elements[0]
        loc_type = e.get("type", "")
        loc_name = e.get("name", "")
        source = e.get("source_mapping", {}).get("filename_relative", "")
        location = f"{source}::{loc_name} ({loc_type})"
    
    print(f"#{i} [{impact}/{confidence}] {check}")
    print(f"   Location: {location}")
    print(f"   {desc}")
    print()
PYEOF

# If Ollama is available, ask it to rate exploitability
if curl -s http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  echo "--- Local LLM Triage ---"
  FINDINGS_TEXT=$(python3 -c "
import json
with open('$JSON_FILE') as f:
    data = json.load(f)
findings = [d for d in data.get('results',{}).get('detectors',[]) if d.get('impact') in ('High','Medium')]
for f in findings[:5]:
    print(f'{f.get(\"check\")}: {f.get(\"description\",\"\")[:150]}')
")
  
  PROMPT="You are a smart contract security expert. Rate each finding as EXPLOITABLE, MAYBE, or FALSE_POSITIVE. Be brief, one line each:\n\n$FINDINGS_TEXT"
  
  curl -s http://127.0.0.1:11434/api/generate \
    -d "{\"model\":\"deepseek-coder-v2:16b-lite-instruct-q5_K_M\",\"prompt\":\"$PROMPT\",\"stream\":false}" \
    2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('response','No response'))" 2>/dev/null || echo "(Local LLM unavailable)"
fi
