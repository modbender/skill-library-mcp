#!/usr/bin/env python3
"""Quick test for scholar-research skill"""

import subprocess
import sys
import os

# Change to correct directory
os.chdir("/home/bigclaw/.openclaw/workspace/skills/scholar-research/src/scholar_research")

topics = [
    "sodium ion battery",
    "zinc ion battery", 
    "lithium battery",
    "solid state battery",
    "quantum computing",
    "neural network",
    "machine learning",
    "solar cell",
    "fuel cell",
    "cancer immunotherapy",
]

passed = 0
failed = 0

for topic in topics:
    print(f"\n{'='*50}")
    print(f"Testing: {topic}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(
            ["python3", "scholar_research.py", topic, "--top=3"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        output = result.stdout + result.stderr
        
        if "Error" in output and "Traceback" in output:
            print(f"❌ FAILED")
            print(output[:300])
            failed += 1
        elif "TOP PAPERS" in output:
            print(f"✅ PASSED")
            passed += 1
        else:
            print(f"⚠️ UNCLEAR")
            print(output[:200])
            failed += 1
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        failed += 1

print(f"\n{'='*50}")
print(f"RESULTS: {passed}/{passed+failed} passed")
print(f"{'='*50}")
