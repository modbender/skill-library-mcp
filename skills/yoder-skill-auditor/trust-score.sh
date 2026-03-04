#!/bin/bash
# Skill Auditor - Trust Score Calculator
# Generates a composite trust score (0-100) for a skill based on
# security audit, quality signals, and metadata analysis
# Usage: bash trust-score.sh /path/to/skill [--json]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AUDIT="$SCRIPT_DIR/audit.sh"
SKILL_DIR="${1:?Usage: trust-score.sh /path/to/skill [--json]}"
JSON_MODE=false
if [ "$2" = "--json" ]; then JSON_MODE=true; fi

export SCRIPT_DIR SKILL_DIR JSON_MODE

python3 << 'PYTHON'
import json, os, sys, subprocess, re
from datetime import datetime

skill_dir = os.environ.get("SKILL_DIR", "")
json_mode = os.environ.get("JSON_MODE", "false") == "true"
script_dir = os.environ.get("SCRIPT_DIR", ".")

skill_name = os.path.basename(os.path.abspath(skill_dir))

scores = {}
deductions = []
bonuses = []

# ─── SECURITY SCORE (max 40 points) ───
security_score = 40

# Run the audit
try:
    result = subprocess.run(
        ["bash", f"{script_dir}/audit.sh", skill_dir, "--json"],
        capture_output=True, text=True, timeout=30
    )
    audit = json.loads(result.stdout)
    
    criticals = audit.get("criticals", 0)
    warnings = audit.get("warnings", 0)
    
    # Criticals are devastating
    security_score -= criticals * 20
    if criticals > 0:
        deductions.append(f"Security: -{criticals * 20} ({criticals} critical finding(s))")
    
    # Warnings are moderate
    security_score -= warnings * 5
    if warnings > 0:
        deductions.append(f"Security: -{warnings * 5} ({warnings} warning(s))")
    
except Exception as e:
    security_score = 0
    deductions.append(f"Security: audit failed ({e})")

security_score = max(0, security_score)
scores["security"] = security_score

# ─── QUALITY SCORE (max 25 points) ───
quality_score = 0

# SKILL.md exists and has content
skill_md = os.path.join(skill_dir, "SKILL.md")
if os.path.exists(skill_md):
    content = open(skill_md).read()
    quality_score += 5  # exists
    
    # Has description
    if "description" in content.lower():
        quality_score += 3
        bonuses.append("Quality: +3 (has description)")
    
    # Has version
    if re.search(r'version.*\d+\.\d+', content, re.IGNORECASE):
        quality_score += 3
        bonuses.append("Quality: +3 (versioned)")
    
    # Has usage instructions
    if re.search(r'(usage|how to|getting started|quick start)', content, re.IGNORECASE):
        quality_score += 3
        bonuses.append("Quality: +3 (has usage docs)")
    
    # Has examples
    if "```" in content:
        quality_score += 2
        bonuses.append("Quality: +2 (has code examples)")
    
    # Substantial docs (>500 chars)
    if len(content) > 500:
        quality_score += 2
        bonuses.append("Quality: +2 (substantial documentation)")
    
    # Has metadata section
    if "metadata:" in content or "openclaw:" in content:
        quality_score += 2
        bonuses.append("Quality: +2 (has OpenClaw metadata)")
    
    # Declares requirements
    if "requires" in content.lower() or "dependencies" in content.lower() or "bins:" in content:
        quality_score += 2
        bonuses.append("Quality: +2 (declares requirements)")
    
    # Has changelog
    if re.search(r'(changelog|what.s new|version history)', content, re.IGNORECASE):
        quality_score += 3
        bonuses.append("Quality: +3 (has changelog)")
else:
    deductions.append("Quality: -25 (no SKILL.md)")

quality_score = min(25, quality_score)
scores["quality"] = quality_score

# ─── STRUCTURE SCORE (max 20 points) ───
structure_score = 0

# File organization
all_files = []
for root, dirs, files in os.walk(skill_dir):
    # Skip node_modules and .git
    dirs[:] = [d for d in dirs if d not in ('node_modules', '.git')]
    for f in files:
        all_files.append(os.path.join(root, f))

file_count = len(all_files)

# Has at least 2 files (SKILL.md + something)
if file_count >= 2:
    structure_score += 5
    bonuses.append("Structure: +5 (multiple files)")

# Has script files
script_exts = {'.sh', '.py', '.js', '.ts', '.rb', '.go'}
has_scripts = any(os.path.splitext(f)[1] in script_exts for f in all_files)
if has_scripts:
    structure_score += 3
    bonuses.append("Structure: +3 (has executable scripts)")

# No oversized files (>500KB)
oversized = [f for f in all_files if os.path.getsize(f) > 500000]
if not oversized:
    structure_score += 3
    bonuses.append("Structure: +3 (no oversized files)")
else:
    deductions.append(f"Structure: {len(oversized)} oversized file(s)")

# Reasonable file count (not too many, not too few)
if 2 <= file_count <= 20:
    structure_score += 3
    bonuses.append(f"Structure: +3 ({file_count} files, reasonable scope)")
elif file_count > 20:
    structure_score += 1
    bonuses.append(f"Structure: +1 ({file_count} files, large skill)")

# Has test files
has_tests = any('test' in f.lower() for f in all_files)
if has_tests:
    structure_score += 3
    bonuses.append("Structure: +3 (has tests)")

# Has a README or README.md (separate from SKILL.md)
has_readme = any(os.path.basename(f).lower() in ('readme.md', 'readme') for f in all_files)
if has_readme:
    structure_score += 3
    bonuses.append("Structure: +3 (has README)")

structure_score = min(20, structure_score)
scores["structure"] = structure_score

# ─── TRANSPARENCY SCORE (max 15 points) ───
transparency_score = 0

# Check for license
has_license = any(os.path.basename(f).lower().startswith('license') for f in all_files)
if has_license:
    transparency_score += 5
    bonuses.append("Transparency: +5 (has license)")

# No minified/obfuscated code
script_files = [f for f in all_files if os.path.splitext(f)[1] in script_exts]
has_minified = False
for f in script_files:
    try:
        content = open(f).read()
        # Minified = very long lines with no whitespace
        lines = content.split('\n')
        long_lines = [l for l in lines if len(l) > 500]
        if long_lines:
            has_minified = True
            break
    except:
        pass

if not has_minified:
    transparency_score += 5
    bonuses.append("Transparency: +5 (no minified code)")
else:
    deductions.append("Transparency: minified/obfuscated code detected")

# Comments in scripts
has_comments = False
for f in script_files:
    try:
        content = open(f).read()
        if '#' in content or '//' in content or '/*' in content:
            has_comments = True
            break
    except:
        pass

if has_comments:
    transparency_score += 5
    bonuses.append("Transparency: +5 (code has comments)")

transparency_score = min(15, transparency_score)
scores["transparency"] = transparency_score

# ─── TOTAL ───
total = sum(scores.values())
total = max(0, min(100, total))

# Grade
if total >= 90:
    grade = "A"
    label = "Excellent - High trust"
elif total >= 75:
    grade = "B"
    label = "Good - Generally trustworthy"
elif total >= 60:
    grade = "C"
    label = "Fair - Review recommended"
elif total >= 40:
    grade = "D"
    label = "Poor - Use with caution"
else:
    grade = "F"
    label = "Fail - Do not install"

if json_mode:
    output = {
        "skill": skill_name,
        "trust_score": total,
        "grade": grade,
        "label": label,
        "breakdown": scores,
        "bonuses": bonuses,
        "deductions": deductions
    }
    print(json.dumps(output, indent=2))
else:
    print(f"{'='*45}")
    print(f"  Trust Score: {skill_name}")
    print(f"{'='*45}")
    print()
    
    # Score bar
    filled = int(total / 2)
    bar = '█' * filled + '░' * (50 - filled)
    print(f"  [{bar}] {total}/100")
    print(f"  Grade: {grade} - {label}")
    print()
    
    print(f"  Breakdown:")
    print(f"    Security:      {scores['security']}/40")
    print(f"    Quality:       {scores['quality']}/25")
    print(f"    Structure:     {scores['structure']}/20")
    print(f"    Transparency:  {scores['transparency']}/15")
    print()
    
    if bonuses:
        print(f"  Bonuses:")
        for b in bonuses:
            print(f"    + {b}")
        print()
    
    if deductions:
        print(f"  Deductions:")
        for d in deductions:
            print(f"    - {d}")
        print()

PYTHON
