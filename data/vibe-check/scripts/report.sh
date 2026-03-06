#!/usr/bin/env bash
# report.sh — Generate the vibe-check Markdown report from analysis JSON
# Reads JSON lines (one per analyzed file) from stdin
# Outputs a beautiful Markdown scorecard
#
# Usage: cat analysis_results.jsonl | ./report.sh [--target PATH] [--fix]

set -euo pipefail
source "$(dirname "$0")/common.sh"

TARGET="${1:-.}"
FIX_MODE="false"

# Parse args
for arg in "$@"; do
  case "$arg" in
    --fix)     FIX_MODE="true" ;;
    --target)  : ;;  # handled positionally
    *)         TARGET="$arg" ;;
  esac
done

# Read all analysis results from stdin
RESULTS_FILE=$(mktemp)
trap "rm -f '$RESULTS_FILE'" EXIT
cat > "$RESULTS_FILE"

# Validate we have results
LINE_COUNT=$(wc -l < "$RESULTS_FILE" | tr -d ' ')
if [ "$LINE_COUNT" -eq 0 ]; then
  err "No analysis results to report on."
  exit 1
fi

# Generate report using Python
RESULTS_FILE_ENV="$RESULTS_FILE" TARGET_ENV="$TARGET" FIX_MODE_ENV="$FIX_MODE" python3 -c "
import json, sys, os

results_file = os.environ['RESULTS_FILE_ENV']
target = os.environ['TARGET_ENV']
fix_mode = os.environ.get('FIX_MODE_ENV', 'false') == 'true'

# Read analysis results
results = []
with open(results_file) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if 'error' not in obj:
                results.append(obj)
        except json.JSONDecodeError:
            pass

if not results:
    print('❌ No valid analysis results found.')
    sys.exit(0)

# ═══════════════════════════════════════════════════════════════════
# COMPUTE SCORES
# ═══════════════════════════════════════════════════════════════════

category_weights = {
    'error_handling': 0.20,
    'duplication': 0.15,
    'dead_code': 0.10,
    'input_validation': 0.15,
    'magic_values': 0.10,
    'test_coverage': 0.10,
    'naming_quality': 0.10,
    'security': 0.10,
}

category_labels = {
    'error_handling': 'Error Handling',
    'duplication': 'Duplication',
    'dead_code': 'Dead Code',
    'input_validation': 'Input Validation',
    'magic_values': 'Magic Values',
    'test_coverage': 'Test Coverage',
    'naming_quality': 'Naming Quality',
    'security': 'Security',
}

category_emoji = {
    'error_handling': '🛡️',
    'duplication': '📋',
    'dead_code': '💀',
    'input_validation': '🔍',
    'magic_values': '🔮',
    'test_coverage': '🧪',
    'naming_quality': '📛',
    'security': '🔒',
}

# Compute per-file weighted scores
file_scores = []
for r in results:
    scores = r.get('scores', {})
    line_count = r.get('line_count', 1)
    # Weighted score for this file
    ws = 0
    for cat, weight in category_weights.items():
        ws += scores.get(cat, 50) * weight
    file_scores.append({
        'file': r['file'],
        'language': r.get('language', 'unknown'),
        'line_count': line_count,
        'weighted_score': round(ws),
        'scores': scores,
        'findings': r.get('findings', []),
        'summary': r.get('summary', ''),
    })

# Overall score: weighted average by line count (complexity proxy)
total_lines = sum(f['line_count'] for f in file_scores)
if total_lines > 0:
    overall_score = round(sum(f['weighted_score'] * f['line_count'] for f in file_scores) / total_lines)
else:
    overall_score = round(sum(f['weighted_score'] for f in file_scores) / len(file_scores))

overall_score = max(0, min(100, overall_score))

# Letter grade
if overall_score >= 90: grade = 'A'
elif overall_score >= 80: grade = 'B'
elif overall_score >= 70: grade = 'C'
elif overall_score >= 60: grade = 'D'
else: grade = 'F'

# Grade color for badge
grade_colors = {'A': 'brightgreen', 'B': 'green', 'C': 'yellow', 'D': 'orange', 'F': 'red'}
badge_color = grade_colors.get(grade, 'lightgrey')

# Verdict
if overall_score >= 90: verdict = 'Pristine code. Minimal vibe coding detected. Ship it! 🚀'
elif overall_score >= 80: verdict = 'Clean code with minor issues. A few human touches needed.'
elif overall_score >= 70: verdict = 'Decent code but some lazy patterns crept in. Worth a review pass.'
elif overall_score >= 60: verdict = 'Noticeable vibe coding. This code needs human attention.'
else: verdict = 'Heavy vibe coding detected. This codebase needs serious human review. 🚨'

# Aggregate category scores across all files (weighted by line count)
agg_scores = {}
agg_issues = {}
for cat in category_weights:
    if total_lines > 0:
        agg_scores[cat] = round(sum(f['scores'].get(cat, 50) * f['line_count'] for f in file_scores) / total_lines)
    else:
        agg_scores[cat] = round(sum(f['scores'].get(cat, 50) for f in file_scores) / len(file_scores))
    # Count findings in this category
    agg_issues[cat] = sum(len([fn for fn in f['findings'] if fn.get('category') == cat]) for f in file_scores)

# Collect all findings sorted by severity
all_findings = []
for f in file_scores:
    for fn in f['findings']:
        fn['_file'] = f['file']
        all_findings.append(fn)

severity_order = {'critical': 0, 'warning': 1, 'info': 2}
all_findings.sort(key=lambda x: severity_order.get(x.get('severity', 'info'), 3))

critical_findings = [f for f in all_findings if f.get('severity') == 'critical']
warning_findings = [f for f in all_findings if f.get('severity') == 'warning']
info_findings = [f for f in all_findings if f.get('severity') == 'info']

# ═══════════════════════════════════════════════════════════════════
# RENDER REPORT
# ═══════════════════════════════════════════════════════════════════

print()
print('# 🎭 Vibe Check Report')
print()
print(f'**Project:** \`{target}\`')
print(f'**Score:** {overall_score}/100 (Grade: {grade})')
print(f'**Files analyzed:** {len(results)}')
print(f'**Total lines:** {total_lines:,}')
print(f'**Verdict:** {verdict}')
print()

# Badge
badge_score = str(overall_score)
badge_url = f'https://img.shields.io/badge/vibe--score-{badge_score}%2F100-{badge_color}'
print(f'![Vibe Score]({badge_url})')
print()
print(f'\`\`\`markdown')
print(f'![Vibe Score]({badge_url})')
print(f'\`\`\`')
print()

# ─── Score Breakdown Table ────────────────────────────────────────
print('## 📊 Score Breakdown')
print()
print('| Category | Score | Weight | Issues |')
print('|----------|:-----:|:------:|:------:|')

for cat in ['error_handling', 'duplication', 'dead_code', 'input_validation', 'magic_values', 'test_coverage', 'naming_quality', 'security']:
    label = category_labels[cat]
    emoji = category_emoji[cat]
    score = agg_scores[cat]
    weight = int(category_weights[cat] * 100)
    issues = agg_issues[cat]
    print(f'| {emoji} {label} | {score} | {weight}% | {issues} |')

print()

# ─── Category Bars ───────────────────────────────────────────────
print('## 📈 Category Bars')
print()
print('\`\`\`')
for cat in ['error_handling', 'duplication', 'dead_code', 'input_validation', 'magic_values', 'test_coverage', 'naming_quality', 'security']:
    label = category_labels[cat]
    score = agg_scores[cat]
    bar_width = 20
    blocks = round(score / 100 * bar_width)
    bar = '█' * blocks + '░' * (bar_width - blocks)
    print(f'{label:<20s} {bar} {score:>3d}/100')
print('\`\`\`')
print()

# ─── Top Findings ────────────────────────────────────────────────
print('## 🔍 Top Findings')
print()

finding_num = 0

if critical_findings:
    print('### 🔴 Critical')
    print()
    for f in critical_findings[:10]:
        finding_num += 1
        file_ref = f.get('_file', '?')
        line = f.get('line')
        line_end = f.get('line_end')
        snippet = f.get('code_snippet', '')
        msg = f.get('message', '')
        
        loc = file_ref
        if line:
            if line_end and line_end != line:
                loc = f'{file_ref}:{line}-{line_end}'
            else:
                loc = f'{file_ref}:{line}'
        
        snippet_display = f' — \`{snippet}\`' if snippet else ''
        print(f'{finding_num}. **{loc}**{snippet_display} — {msg}')
    print()

if warning_findings:
    print('### 🟡 Warning')
    print()
    for f in warning_findings[:15]:
        finding_num += 1
        file_ref = f.get('_file', '?')
        line = f.get('line')
        line_end = f.get('line_end')
        snippet = f.get('code_snippet', '')
        msg = f.get('message', '')
        
        loc = file_ref
        if line:
            if line_end and line_end != line:
                loc = f'{file_ref}:{line}-{line_end}'
            else:
                loc = f'{file_ref}:{line}'
        
        snippet_display = f' — \`{snippet}\`' if snippet else ''
        print(f'{finding_num}. **{loc}**{snippet_display} — {msg}')
    print()

if info_findings and finding_num < 20:
    print('### 🔵 Info')
    print()
    remaining = 20 - finding_num
    for f in info_findings[:remaining]:
        finding_num += 1
        file_ref = f.get('_file', '?')
        line = f.get('line')
        snippet = f.get('code_snippet', '')
        msg = f.get('message', '')
        
        loc = f'{file_ref}:{line}' if line else file_ref
        snippet_display = f' — \`{snippet}\`' if snippet else ''
        print(f'{finding_num}. **{loc}**{snippet_display} — {msg}')
    print()

if finding_num == 0:
    print('✨ No significant findings! This code looks clean.')
    print()

# ─── Per-File Breakdown ──────────────────────────────────────────
if len(file_scores) > 1:
    print('## 📁 Per-File Breakdown')
    print()
    print('| File | Score | Grade | Lines | Top Issue |')
    print('|------|:-----:|:-----:|------:|-----------|')
    
    sorted_files = sorted(file_scores, key=lambda x: x['weighted_score'])
    for f in sorted_files:
        fs = f['weighted_score']
        fg = 'A' if fs >= 90 else 'B' if fs >= 80 else 'C' if fs >= 70 else 'D' if fs >= 60 else 'F'
        top_issue = ''
        if f['findings']:
            top = f['findings'][0]
            top_issue = top.get('message', '')[:50]
            if len(top.get('message', '')) > 50:
                top_issue += '...'
        
        # Shorten file path for display
        file_display = f['file']
        if len(file_display) > 40:
            file_display = '...' + file_display[-37:]
        
        print(f'| \`{file_display}\` | {fs} | {fg} | {f[\"line_count\"]} | {top_issue} |')
    print()

# ─── Fix Mode ────────────────────────────────────────────────────
if fix_mode:
    fixes = [f for f in all_findings if f.get('fix')]
    if fixes:
        print('## 🔧 Suggested Fixes')
        print()
        for i, f in enumerate(fixes[:15], 1):
            file_ref = f.get('_file', '?')
            line = f.get('line', '?')
            msg = f.get('message', '')
            fix = f.get('fix', '')
            
            print(f'### Fix #{i}: {file_ref}:{line}')
            print(f'> {msg}')
            print()
            print('\`\`\`diff')
            # Clean up the fix string (handle escaped newlines)
            fix_clean = fix.replace('\\\\n', '\n') if '\\\\n' in fix else fix
            print(fix_clean)
            print('\`\`\`')
            print()
    else:
        print('## 🔧 Suggested Fixes')
        print()
        print('No automated fixes were generated for this run.')
        print('Tip: this can happen in heuristic fallback mode or when the model returned findings without patch output.')
        print()

# ─── Summary ─────────────────────────────────────────────────────
total_findings = len(all_findings)
print('---')
print()
print(f'*🎭 Vibe Check v{\"0.1.0\"} — {total_findings} findings across {len(results)} files*')
print(f'*Badge for your README:* \`![Vibe Score]({badge_url})\`')
print()
" 2>/dev/null
