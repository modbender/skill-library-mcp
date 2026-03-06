#!/usr/bin/env python3
"""
Skill Auditor v2.0.0 - Trust Score Calculator
Generates a composite trust score (0-100) across 5 dimensions.
Usage:
  python3 trust_score.py /path/to/skill [--json]
  python3 trust_score.py /path/to/skill1 --compare /path/to/skill2
  python3 trust_score.py /path/to/skill --trend
"""

import json, os, sys, subprocess, re, time
from datetime import datetime

TREND_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trust_trends.json")

def calculate_trust_score(skill_dir, json_mode=False):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_name = os.path.basename(os.path.abspath(skill_dir))
    
    scores = {}
    deductions = []
    bonuses = []

    # ─── SECURITY SCORE (max 35 points) ───
    security_score = 35
    audit_data = None
    try:
        result = subprocess.run(
            ["bash", os.path.join(script_dir, "audit.sh"), skill_dir, "--json"],
            capture_output=True, text=True, timeout=30
        )
        audit_data = json.loads(result.stdout)
        criticals = audit_data.get("criticals", 0)
        warnings = audit_data.get("warnings", 0)
        
        security_score -= criticals * 18
        if criticals > 0:
            deductions.append(f"Security: -{criticals * 18} ({criticals} critical finding(s))")
        security_score -= warnings * 4
        if warnings > 0:
            deductions.append(f"Security: -{warnings * 4} ({warnings} warning(s))")
    except Exception as e:
        security_score = 0
        deductions.append(f"Security: audit failed ({e})")

    scores["security"] = max(0, security_score)

    # ─── QUALITY SCORE (max 22 points) ───
    quality_score = 0
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if os.path.exists(skill_md):
        content = open(skill_md).read()
        quality_score += 4  # has SKILL.md
        
        if "description" in content.lower():
            quality_score += 3
            bonuses.append("Quality: +3 (has description)")
        if re.search(r'version.*\d+\.\d+', content, re.IGNORECASE):
            quality_score += 2
            bonuses.append("Quality: +2 (versioned)")
        if re.search(r'(usage|how to|getting started|quick start)', content, re.IGNORECASE):
            quality_score += 3
            bonuses.append("Quality: +3 (has usage docs)")
        if "```" in content:
            quality_score += 2
            bonuses.append("Quality: +2 (has code examples)")
        if len(content) > 500:
            quality_score += 2
            bonuses.append("Quality: +2 (substantial documentation)")
        if "metadata:" in content or "openclaw:" in content:
            quality_score += 2
            bonuses.append("Quality: +2 (has OpenClaw metadata)")
        if "requires" in content.lower() or "dependencies" in content.lower() or "bins:" in content:
            quality_score += 2
            bonuses.append("Quality: +2 (declares requirements)")
        if re.search(r'(changelog|what.s new|version history)', content, re.IGNORECASE):
            quality_score += 2
            bonuses.append("Quality: +2 (has changelog)")
    else:
        deductions.append("Quality: -22 (no SKILL.md)")

    scores["quality"] = min(22, quality_score)

    # ─── STRUCTURE SCORE (max 18 points) ───
    structure_score = 0
    all_files = []
    for root, dirs, files in os.walk(skill_dir):
        dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', 'test-skills')]
        for f in files:
            all_files.append(os.path.join(root, f))

    file_count = len(all_files)
    script_exts = {'.sh', '.py', '.js', '.ts', '.rb', '.go'}
    
    if file_count >= 2:
        structure_score += 4
        bonuses.append("Structure: +4 (multiple files)")
    
    has_scripts = any(os.path.splitext(f)[1] in script_exts for f in all_files)
    if has_scripts:
        structure_score += 2
        bonuses.append("Structure: +2 (has executable scripts)")
    
    oversized = [f for f in all_files if os.path.getsize(f) > 500000]
    if not oversized:
        structure_score += 3
        bonuses.append("Structure: +3 (no oversized files)")
    
    if 2 <= file_count <= 20:
        structure_score += 3
        bonuses.append(f"Structure: +3 ({file_count} files, reasonable scope)")
    elif file_count > 20:
        structure_score += 1
    
    has_tests = any('test' in os.path.basename(f).lower() for f in all_files)
    if has_tests:
        structure_score += 3
        bonuses.append("Structure: +3 (has tests)")
    
    has_readme = any(os.path.basename(f).lower() in ('readme.md', 'readme') for f in all_files)
    if has_readme:
        structure_score += 3
        bonuses.append("Structure: +3 (has README)")

    scores["structure"] = min(18, structure_score)

    # ─── TRANSPARENCY SCORE (max 15 points) ───
    transparency_score = 0
    
    has_license = any(os.path.basename(f).lower().startswith('license') for f in all_files)
    if has_license:
        transparency_score += 5
        bonuses.append("Transparency: +5 (has license)")
    
    script_files = [f for f in all_files if os.path.splitext(f)[1] in script_exts]
    has_minified = False
    for f in script_files:
        try:
            lines = open(f).read().split('\n')
            if any(len(l) > 500 for l in lines):
                has_minified = True
                break
        except:
            pass
    
    if not has_minified:
        transparency_score += 5
        bonuses.append("Transparency: +5 (no minified code)")
    else:
        deductions.append("Transparency: minified/obfuscated code detected")
    
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

    scores["transparency"] = min(15, transparency_score)

    # ─── BEHAVIORAL SCORE (max 10 points) ───
    behavioral_score = 0
    
    for f in script_files:
        try:
            content = open(f).read()
            
            # Rate limiting checks
            if re.search(r'(rate.?limit|throttl|sleep|delay|backoff|retry)', content, re.IGNORECASE):
                behavioral_score += 3
                bonuses.append("Behavioral: +3 (has rate limiting/backoff)")
                break
        except:
            pass
    
    # Error handling
    for f in script_files:
        try:
            content = open(f).read()
            ext = os.path.splitext(f)[1]
            if ext in ('.py',):
                if 'try:' in content and 'except' in content:
                    behavioral_score += 4
                    bonuses.append("Behavioral: +4 (has error handling)")
                    break
            elif ext in ('.js', '.ts'):
                if 'try {' in content or 'catch' in content or '.catch(' in content:
                    behavioral_score += 4
                    bonuses.append("Behavioral: +4 (has error handling)")
                    break
            elif ext in ('.sh', '.bash'):
                if 'set -e' in content or 'trap ' in content or '|| ' in content or 'if [' in content:
                    behavioral_score += 4
                    bonuses.append("Behavioral: +4 (has error handling)")
                    break
        except:
            pass
    
    # Input validation
    for f in script_files:
        try:
            content = open(f).read()
            if re.search(r'(\$\{1:\?|if \[ -z|if \[ !|\.strip\(\)|\.trim\(\)|validate|sanitize|assert |isinstance\()', content, re.IGNORECASE):
                behavioral_score += 3
                bonuses.append("Behavioral: +3 (has input validation)")
                break
        except:
            pass

    scores["behavioral"] = min(10, behavioral_score)

    # ─── TOTAL ───
    total = max(0, min(100, sum(scores.values())))
    
    if total >= 90: grade, label = "A", "Excellent - High trust"
    elif total >= 75: grade, label = "B", "Good - Generally trustworthy"
    elif total >= 60: grade, label = "C", "Fair - Review recommended"
    elif total >= 40: grade, label = "D", "Poor - Use with caution"
    else: grade, label = "F", "Fail - Do not install"

    result = {
        "skill": skill_name, "trust_score": total, "grade": grade,
        "label": label, "breakdown": scores,
        "bonuses": bonuses, "deductions": deductions,
        "timestamp": datetime.now().isoformat()
    }

    if json_mode:
        print(json.dumps(result, indent=2))
    else:
        print(f"{'='*45}")
        print(f"  Trust Score: {skill_name}")
        print(f"{'='*45}")
        print()
        filled = int(total / 2)
        bar = '█' * filled + '░' * (50 - filled)
        print(f"  [{bar}] {total}/100")
        print(f"  Grade: {grade} - {label}")
        print()
        print(f"  Breakdown:")
        print(f"    Security:      {scores['security']}/35")
        print(f"    Quality:       {scores['quality']}/22")
        print(f"    Structure:     {scores['structure']}/18")
        print(f"    Transparency:  {scores['transparency']}/15")
        print(f"    Behavioral:    {scores['behavioral']}/10")
        print()
        if bonuses:
            print(f"  Bonuses:")
            for b in bonuses: print(f"    + {b}")
            print()
        if deductions:
            print(f"  Deductions:")
            for d in deductions: print(f"    - {d}")
            print()

    return result


def compare_skills(dir1, dir2, json_mode=False):
    """Compare two skills side by side."""
    # Suppress individual output by capturing
    import io
    old_stdout = sys.stdout
    
    sys.stdout = io.StringIO()
    r1 = calculate_trust_score(dir1, json_mode=True)
    out1 = sys.stdout.getvalue()
    
    sys.stdout = io.StringIO()
    r2 = calculate_trust_score(dir2, json_mode=True)
    out2 = sys.stdout.getvalue()
    
    sys.stdout = old_stdout
    
    r1 = json.loads(out1)
    r2 = json.loads(out2)

    if json_mode:
        print(json.dumps({"comparison": [r1, r2], "delta": r1["trust_score"] - r2["trust_score"]}, indent=2))
    else:
        print(f"{'='*60}")
        print(f"  Comparative Trust Score")
        print(f"{'='*60}")
        print(f"  {'Dimension':<16} {r1['skill']:>15} {r2['skill']:>15}  {'Delta':>8}")
        print(f"  {'-'*56}")
        for dim in ("security", "quality", "structure", "transparency", "behavioral"):
            v1 = r1["breakdown"][dim]
            v2 = r2["breakdown"][dim]
            delta = v1 - v2
            sign = "+" if delta > 0 else ""
            print(f"  {dim.capitalize():<16} {v1:>15} {v2:>15}  {sign}{delta:>7}")
        print(f"  {'-'*56}")
        t1, t2 = r1["trust_score"], r2["trust_score"]
        delta = t1 - t2
        sign = "+" if delta > 0 else ""
        print(f"  {'TOTAL':<16} {t1:>15} {t2:>15}  {sign}{delta:>7}")
        print(f"  {'Grade':<16} {r1['grade']:>15} {r2['grade']:>15}")
        print()


def save_trend(skill_dir):
    """Save current score to trend file."""
    import io
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    calculate_trust_score(skill_dir, json_mode=True)
    out = sys.stdout.getvalue()
    sys.stdout = old_stdout
    
    result = json.loads(out)
    
    trends = {}
    if os.path.exists(TREND_FILE):
        try:
            trends = json.load(open(TREND_FILE))
        except:
            pass
    
    skill_name = result["skill"]
    if skill_name not in trends:
        trends[skill_name] = []
    
    trends[skill_name].append({
        "timestamp": result["timestamp"],
        "score": result["trust_score"],
        "grade": result["grade"],
        "breakdown": result["breakdown"]
    })
    
    # Keep last 50 entries per skill
    trends[skill_name] = trends[skill_name][-50:]
    
    with open(TREND_FILE, "w") as f:
        json.dump(trends, f, indent=2)
    
    print(f"Saved trend data for {skill_name} (score: {result['trust_score']}, grade: {result['grade']})")
    
    entries = trends[skill_name]
    if len(entries) >= 2:
        prev = entries[-2]["score"]
        curr = entries[-1]["score"]
        delta = curr - prev
        sign = "+" if delta > 0 else ""
        direction = "📈" if delta > 0 else ("📉" if delta < 0 else "➡️")
        print(f"Trend: {direction} {sign}{delta} since last measurement ({prev} → {curr})")
    
    return result


def show_trend(skill_dir):
    """Show trend history for a skill."""
    skill_name = os.path.basename(os.path.abspath(skill_dir))
    
    if not os.path.exists(TREND_FILE):
        print(f"No trend data found. Run with --save-trend first.")
        return
    
    trends = json.load(open(TREND_FILE))
    if skill_name not in trends:
        print(f"No trend data for {skill_name}. Run with --save-trend first.")
        return
    
    entries = trends[skill_name]
    print(f"{'='*45}")
    print(f"  Trend History: {skill_name}")
    print(f"{'='*45}")
    print(f"  {'Date':<22} {'Score':>6} {'Grade':>6}")
    print(f"  {'-'*36}")
    for e in entries:
        ts = e["timestamp"][:19]
        print(f"  {ts:<22} {e['score']:>6} {e['grade']:>6}")
    print()


if __name__ == "__main__":
    args = sys.argv[1:]
    
    if not args:
        print("Usage: python3 trust_score.py /path/to/skill [--json] [--compare /path/to/skill2] [--trend] [--save-trend]")
        sys.exit(1)
    
    skill_dir = args[0]
    json_mode = "--json" in args
    
    if "--compare" in args:
        idx = args.index("--compare")
        if idx + 1 < len(args):
            compare_skills(skill_dir, args[idx + 1], json_mode)
        else:
            print("Error: --compare requires a second skill path")
            sys.exit(1)
    elif "--save-trend" in args:
        save_trend(skill_dir)
    elif "--trend" in args:
        show_trend(skill_dir)
    else:
        calculate_trust_score(skill_dir, json_mode)
