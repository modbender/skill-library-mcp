#!/usr/bin/env python3
"""Search Raysurfer cache. Usage: python search.py "task description" """
import json, os, sys, urllib.request

task = sys.argv[1] if len(sys.argv) > 1 else "Parse a CSV file and generate a bar chart"
req = urllib.request.Request(
    "https://api.raysurfer.com/api/retrieve/search",
    data=json.dumps({"task": task, "top_k": 5, "min_verdict_score": 0.3}).encode(),
    headers={"Authorization": f"Bearer {os.environ['RAYSURFER_API_KEY']}", "Content-Type": "application/json"},
)
with urllib.request.urlopen(req) as resp:
    print(json.dumps(json.loads(resp.read()), indent=2))
