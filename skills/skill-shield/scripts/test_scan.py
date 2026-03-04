#!/usr/bin/env python3
"""
Test suite for skill-shield scanner v0.4.0
Tests pattern detection, context detection, and rating logic.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCANNER = Path(__file__).parent / "scan.py"
PASS = 0
FAIL = 0

def run_scan(skill_dir):
    """Run scanner on a skill directory and return parsed JSON."""
    r = subprocess.run(
        ["python3", str(SCANNER), str(skill_dir)],
        capture_output=True, text=True, timeout=30
    )
    output = r.stdout + r.stderr
    start = output.find('{')
    if start < 0:
        return {}
    depth = 0
    for i in range(start, len(output)):
        if output[i] == '{': depth += 1
        elif output[i] == '}': depth -= 1
        if depth == 0:
            return json.loads(output[start:i+1])
    return {}

def make_skill(name, skill_md="", scripts=None):
    """Create a temporary skill directory."""
    d = Path(tempfile.mkdtemp()) / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(skill_md or f"---\nname: {name}\ndescription: test\n---\n# {name}\n")
    if scripts:
        sd = d / "scripts"
        sd.mkdir()
        for fname, content in scripts.items():
            (sd / fname).write_text(content)
    return d

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")

# ============================================================
print("=== Test 1: Empty/doc-only skill → N/A rating ===")
d = make_skill("test-empty")
r = run_scan(d)
check("doc-only gets N/A", r.get("security_rating") == "N/A")
check("is_documentation_only", r.get("is_documentation_only") == True)
shutil.rmtree(d.parent)

# ============================================================
print("\n=== Test 2: Clean Python script → A rating ===")
d = make_skill("test-clean", scripts={
    "main.py": "def hello():\n    print('hello world')\n\nhello()\n"
})
r = run_scan(d)
check("clean code gets A", r.get("security_rating") == "A")
check("zero high findings", all(f["severity"] < 4 for f in r.get("findings", [])))
shutil.rmtree(d.parent)

# ============================================================
print("\n=== Test 3: Dangerous patterns → F rating ===")
d = make_skill("test-dangerous", scripts={
    "evil.py": "import os\nos.system('rm -rf /')\nimport subprocess\nsubprocess.run(['sudo', 'chmod', '777', '/'])\n"
})
r = run_scan(d)
check("dangerous code gets F", r.get("security_rating") == "F")
check("has high findings", any(f["severity"] >= 4 for f in r.get("findings", [])))
shutil.rmtree(d.parent)

# ============================================================
print("\n=== Test 4: String literal context (v0.4.0) — security tool patterns ===")
d = make_skill("test-security-tool", scripts={
    "scanner.py": '''import re
PATTERNS = [r"rm -rf", r"sudo", r"curl .*\\| bash"]
SHELL = [r"chmod +x", r"eval("]
compiled = re.compile(r"\\bos\\.system\\b")
'''
})
r = run_scan(d)
check("security tool patterns demoted", r.get("security_rating") in ("A", "B"),
      f"got {r.get('security_rating')}")
check("no high findings from string patterns",
      all(f["severity"] < 4 for f in r.get("findings", [])),
      f"high findings: {[f for f in r.get('findings',[]) if f['severity']>=4]}")
shutil.rmtree(d.parent)

# ============================================================
print("\n=== Test 5: JS regex literal (v0.4.0) ===")
d = make_skill("test-js-regex", scripts={
    "check.js": '''const dangerous = /\\b(rm\\s+-rf|curl\\s+http|sudo)\\b/i;
const safe = "hello world";
'''
})
r = run_scan(d)
check("JS regex patterns demoted", r.get("security_rating") in ("A", "B"),
      f"got {r.get('security_rating')}")
shutil.rmtree(d.parent)

# ============================================================
print("\n=== Test 6: noscan marker ===")
d = make_skill("test-noscan", scripts={
    "audit.py": '''PATTERNS = {  # noscan
    "rm_rf": r"rm -rf",  # noscan
    "sudo": r"sudo",  # noscan
}
'''
})
r = run_scan(d)
check("noscan lines skipped", r.get("security_rating") in ("A", "B", "N/A"),
      f"got {r.get('security_rating')}")
shutil.rmtree(d.parent)

# ============================================================
print("\n=== Test 7: ignore-next-line comment ===")
d = make_skill("test-ignore", scripts={
    "tool.py": '''# skill-shield: ignore-next-line
os.system("echo hello")
'''
})
r = run_scan(d)
check("ignored line not flagged", 
      not any(f["pattern_id"] == "os_system" for f in r.get("findings", [])),
      f"findings: {[f['pattern_id'] for f in r.get('findings',[])]}")
shutil.rmtree(d.parent)

# ============================================================
print("\n=== Test 8: SKILL.md table cells not flagged ===")
d = make_skill("test-skillmd-table", skill_md="""---
name: test
description: test
---
# Test

| Feature | Command |
|---------|---------|
| Delete | `rm -rf` |
| Admin | `sudo apt install` |
""")
r = run_scan(d)
check("SKILL.md table not flagged high",
      all(f["severity"] < 4 for f in r.get("findings", [])),
      f"high: {[(f['pattern_id'], f['severity']) for f in r.get('findings',[]) if f['severity']>=4]}")
shutil.rmtree(d.parent)

# ============================================================
print("\n=== Test 9: Dual rating — Security vs Compliance ===")
d = make_skill("test-dual", scripts={
    "main.py": "import subprocess\nsubprocess.run(['ls'])\n"
}, skill_md="---\nname: test\ndescription: test\n---\n# Test\nA simple tool.\n")
r = run_scan(d)
check("has security_rating", "security_rating" in r)
check("has compliance_rating", "compliance_rating" in r)
check("has recommendation", "recommendation" in r)
shutil.rmtree(d.parent)

# ============================================================
print("\n=== Test 10: Regression — known good skills ===")
# Test that variable names don't trigger false positives
d = make_skill("test-variable-names", scripts={
    "app.js": '''const hostname = window.location.hostname;
const whoami = user.whoami;
let result = parsed.hostname;
'''
})
r = run_scan(d)
check("variable names not flagged high",
      all(f["severity"] < 4 for f in r.get("findings", []) 
          if f["pattern_id"] in ("hostname_cmd", "whoami_cmd")),
      f"findings: {[(f['pattern_id'], f['severity']) for f in r.get('findings',[]) if f['pattern_id'] in ('hostname_cmd','whoami_cmd')]}")
shutil.rmtree(d.parent)

# ============================================================
print(f"\n{'='*50}")
print(f"Results: {PASS} passed, {FAIL} failed, {PASS+FAIL} total")
if FAIL > 0:
    sys.exit(1)
