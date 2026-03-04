#!/usr/bin/env python3
# OpenClaw Cost Auditor
import glob
import re
import sys

log_dir = sys.argv[1] if len(sys.argv)>1 else '/var/log/openclaw'
total_tokens = 0
for log in glob.glob(f"{log_dir}/*.log"):
    with open(log) as f:
        for line in f:
            tokens = re.findall(r'tokens: (\d+)', line)
            total_tokens += sum(int(t) for t in tokens)
print(f"Total tokens: {total_tokens}")
print(f"Est. cost: ${total_tokens * 0.00001:.2f} (at $10/M)")
