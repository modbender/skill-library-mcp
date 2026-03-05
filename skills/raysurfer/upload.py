#!/usr/bin/env python3
"""Upload code to Raysurfer cache. Usage: python upload.py "task description" path/to/file.py"""
import json, os, sys, urllib.request

task, filepath = sys.argv[1], sys.argv[2]
content = open(filepath).read()
req = urllib.request.Request(
    "https://api.raysurfer.com/api/store/execution-result",
    data=json.dumps({
        "task": task,
        "file_written": {"path": os.path.basename(filepath), "content": content},
        "succeeded": True,
        "auto_vote": True,
    }).encode(),
    headers={"Authorization": f"Bearer {os.environ['RAYSURFER_API_KEY']}", "Content-Type": "application/json"},
)
with urllib.request.urlopen(req) as resp:
    print(json.dumps(json.loads(resp.read()), indent=2))
