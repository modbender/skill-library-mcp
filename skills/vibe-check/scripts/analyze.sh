#!/usr/bin/env bash
# analyze.sh — LLM-powered code analysis for vibe coding sins
# Reads source files and produces JSON findings via LLM
#
# Usage: ./analyze.sh FILE [FILE...] [--fix]
#   Outputs JSON lines: one object per file with findings
#
# Environment:
#   ANTHROPIC_API_KEY or OPENAI_API_KEY — required for analysis

set -euo pipefail
source "$(dirname "$0")/common.sh"

FIX_MODE="false"
FILES=()

# Parse args
for arg in "$@"; do
  case "$arg" in
    --fix) FIX_MODE="true" ;;
    *)     FILES+=("$arg") ;;
  esac
done

if [ ${#FILES[@]} -eq 0 ]; then
  err "No files provided to analyze."
  exit 1
fi

# ─── Build the analysis prompt ────────────────────────────────────────
build_prompt() {
  local file_path="$1"
  local file_content="$2"
  local language="$3"
  local fix_flag="$4"

  local fix_instruction=""
  local fix_field=""
  if [ "$fix_flag" = "true" ]; then
    fix_instruction='
For each finding, also include a "fix" field with a unified diff patch that fixes the issue.
The diff should be minimal and applicable. Format:
"fix": "--- a/FILE\n+++ b/FILE\n@@ -LINE,COUNT +LINE,COUNT @@\n context\n-old line\n+new line\n context"'
    fix_field=',
      "fix": "<unified diff patch or null>"'
  fi

  cat <<PROMPT_EOF
You are a code auditor specializing in detecting "vibe coding" — patterns that indicate AI-generated code accepted without proper human review.

Analyze this ${language} file for the following sin categories:

1. **error_handling** (weight 20%): Missing try/catch, no edge case handling, bare except/catch clauses, no error propagation
2. **duplication** (weight 15%): Copy-pasted logic, repeated patterns that should be abstracted, DRY violations
3. **dead_code** (weight 10%): Unused imports, unreachable code, commented-out blocks, unused variables
4. **input_validation** (weight 15%): No type checks, no bounds checks, trusting all input, missing null/undefined checks
5. **magic_values** (weight 10%): Hardcoded strings/numbers/URLs without named constants, magic numbers
6. **test_coverage** (weight 10%): No test patterns, no assertions, no test files referenced
7. **naming_quality** (weight 10%): Vague names like data/result/temp/x/foo, single-letter vars in non-trivial contexts, misleading names
8. **security** (weight 10%): eval(), exec(), hardcoded secrets/passwords, SQL string concat, unsafe deserialization, path traversal

**File:** \`${file_path}\`
**Language:** ${language}

\`\`\`${language}
${file_content}
\`\`\`

Respond with ONLY a JSON object (no markdown fences, no explanation) in this exact format:
{
  "file": "${file_path}",
  "language": "${language}",
  "line_count": <number of lines>,
  "scores": {
    "error_handling": <0-100>,
    "duplication": <0-100>,
    "dead_code": <0-100>,
    "input_validation": <0-100>,
    "magic_values": <0-100>,
    "test_coverage": <0-100>,
    "naming_quality": <0-100>,
    "security": <0-100>
  },
  "findings": [
    {
      "severity": "critical|warning|info",
      "category": "<sin_category_slug>",
      "line": <line_number_or_null>,
      "line_end": <end_line_or_null>,
      "code_snippet": "<the offending code, max 120 chars>",
      "message": "<human-readable explanation>"${fix_field}
    }
  ],
  "summary": "<one-sentence assessment of this file>"
}

Scoring guide:
- 100 = no issues found in this category
- 80-99 = minor issues only
- 50-79 = moderate issues, needs attention
- 20-49 = significant problems
- 0-19 = severe/pervasive issues

Be specific. Reference exact line numbers. The code snippet should be the actual offending code.
For test_coverage: score 0 if there are no test patterns in the file AND it's not a test file itself. Score 50 if it has some defensive patterns. Score 100 only for actual test files.
For files that are genuinely well-written, give high scores — don't manufacture issues.${fix_instruction}
PROMPT_EOF
}

# ─── Call LLM ─────────────────────────────────────────────────────────
call_llm() {
  local prompt="$1"
  local result=""

  # Escape prompt for JSON
  local escaped_prompt
  escaped_prompt=$(python3 -c "
import json, sys
prompt = sys.stdin.read()
print(json.dumps(prompt))
" <<< "$prompt" 2>/dev/null)

  # Method 1: Anthropic API
  if [ -z "$result" ] && [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    result=$(curl -sf --max-time 60 \
      -H "x-api-key: ${ANTHROPIC_API_KEY}" \
      -H "anthropic-version: 2023-06-01" \
      -H "content-type: application/json" \
      -d "{\"model\":\"claude-sonnet-4-20250514\",\"max_tokens\":4096,\"messages\":[{\"role\":\"user\",\"content\":${escaped_prompt}}]}" \
      https://api.anthropic.com/v1/messages 2>/dev/null | python3 -c "
import json, sys
resp = json.load(sys.stdin)
print(resp['content'][0]['text'])
" 2>/dev/null) || result=""
  fi

  # Method 2: OpenAI API
  if [ -z "$result" ] && [ -n "${OPENAI_API_KEY:-}" ]; then
    result=$(curl -sf --max-time 60 \
      -H "Authorization: Bearer ${OPENAI_API_KEY}" \
      -H "content-type: application/json" \
      -d "{\"model\":\"gpt-4o\",\"messages\":[{\"role\":\"user\",\"content\":${escaped_prompt}}],\"max_tokens\":4096}" \
      https://api.openai.com/v1/chat/completions 2>/dev/null | python3 -c "
import json, sys
resp = json.load(sys.stdin)
print(resp['choices'][0]['message']['content'])
" 2>/dev/null) || result=""
  fi

  # Method 3: openclaw llm
  if [ -z "$result" ] && command -v openclaw &>/dev/null; then
    result=$(echo "$prompt" | openclaw llm --raw 2>/dev/null) || result=""
  fi

  if [ -z "$result" ]; then
    err "No LLM available. Set ANTHROPIC_API_KEY or OPENAI_API_KEY."
    return 1
  fi

  echo "$result"
}

# ─── Parse LLM response to clean JSON ────────────────────────────────
parse_response() {
  local response="$1"
  python3 -c "
import json, sys, re

text = sys.stdin.read().strip()

# Strip markdown code fences if present
if text.startswith('\`\`\`'):
    # Remove first line (```json or ```)
    text = text.split('\n', 1)[1] if '\n' in text else text[3:]
if text.endswith('\`\`\`'):
    text = text[:text.rfind('\`\`\`')]
text = text.strip()

# Try direct parse
try:
    obj = json.loads(text)
    print(json.dumps(obj))
    sys.exit(0)
except json.JSONDecodeError:
    pass

# Try to find JSON object in text
match = re.search(r'\{[\s\S]*\}', text)
if match:
    try:
        obj = json.loads(match.group())
        print(json.dumps(obj))
        sys.exit(0)
    except json.JSONDecodeError:
        pass

# Failed — output error marker
print(json.dumps({'error': 'Failed to parse LLM response', 'raw': text[:500]}))
sys.exit(1)
" <<< "$response" 2>/dev/null
}

# ─── Fallback analysis (no LLM available) ────────────────────────────
fallback_analyze() {
  local file_path="$1"
  local language="$2"

  FILE_PATH_ENV="$file_path" LANGUAGE_ENV="$language" python3 -c "
import json, sys, re, os

file_path = os.environ['FILE_PATH_ENV']
language = os.environ['LANGUAGE_ENV']

with open(file_path, 'r', errors='replace') as f:
    content = f.read()
    lines = content.split('\n')

line_count = len(lines)
findings = []

# Simple heuristic analysis
scores = {
    'error_handling': 70,
    'duplication': 80,
    'dead_code': 80,
    'input_validation': 70,
    'magic_values': 80,
    'test_coverage': 0,
    'naming_quality': 70,
    'security': 90
}

# Check for try/except or try/catch
has_try = bool(re.search(r'\btry\s*[:{]', content))
if not has_try and line_count > 20:
    scores['error_handling'] = 30
    findings.append({
        'severity': 'warning',
        'category': 'error_handling',
        'line': None,
        'line_end': None,
        'code_snippet': '',
        'message': f'No try/catch blocks found in {line_count}-line file'
    })

# Check for bare except
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if language == 'python' and stripped in ('except:', 'except Exception:'):
        scores['error_handling'] = max(scores['error_handling'] - 20, 0)
        findings.append({
            'severity': 'warning',
            'category': 'error_handling',
            'line': i,
            'line_end': i,
            'code_snippet': stripped,
            'message': 'Bare except clause — catches all exceptions indiscriminately'
        })

# Check for eval/exec
for i, line in enumerate(lines, 1):
    if re.search(r'\beval\s*\(', line):
        scores['security'] = max(scores['security'] - 40, 0)
        findings.append({
            'severity': 'critical',
            'category': 'security',
            'line': i,
            'line_end': i,
            'code_snippet': line.strip()[:120],
            'message': 'Use of eval() — potential code injection vulnerability'
        })
    if re.search(r'\bexec\s*\(', line) and language == 'python':
        scores['security'] = max(scores['security'] - 30, 0)
        findings.append({
            'severity': 'critical',
            'category': 'security',
            'line': i,
            'line_end': i,
            'code_snippet': line.strip()[:120],
            'message': 'Use of exec() — potential code injection vulnerability'
        })

# Check for magic numbers (not 0, 1, 2, common ports)
common_numbers = {0, 1, 2, -1, 100, 1000, 10, 80, 443, 8080, 3000, 5000}
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped.startswith('#') or stripped.startswith('//'):
        continue
    nums = re.findall(r'\b(\d{2,})\b', stripped)
    for n in nums:
        if int(n) not in common_numbers and 'import' not in stripped:
            scores['magic_values'] = max(scores['magic_values'] - 5, 0)
            findings.append({
                'severity': 'info',
                'category': 'magic_values',
                'line': i,
                'line_end': i,
                'code_snippet': stripped[:120],
                'message': f'Magic number {n} — consider using a named constant'
            })
            break  # One per line is enough

# Check for test patterns (match against basename only, not directory path)
basename = os.path.basename(file_path)
is_test_file = bool(re.search(r'(test_|_test\.|\.test\.|\.spec\.)', basename)) or '/tests/' in file_path
has_assert = bool(re.search(r'\b(assert|expect|should|test|describe|it\(|pytest)', content))
if is_test_file or has_assert:
    scores['test_coverage'] = 80
elif line_count > 10:
    scores['test_coverage'] = 0
    findings.append({
        'severity': 'info',
        'category': 'test_coverage',
        'line': None,
        'line_end': None,
        'code_snippet': '',
        'message': 'No test patterns found in this file'
    })

# Check for vague names
vague_names = {'data', 'result', 'temp', 'tmp', 'foo', 'bar', 'baz', 'x', 'y', 'val', 'obj', 'item', 'stuff', 'thing'}
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('*'):
        continue
    # Look for variable assignments
    if language == 'python':
        m = re.match(r'(\w+)\s*=', stripped)
    else:
        m = re.match(r'(?:let|const|var)\s+(\w+)', stripped)
    if m:
        name = m.group(1)
        if name.lower() in vague_names and len(stripped) > 10:
            scores['naming_quality'] = max(scores['naming_quality'] - 10, 0)
            findings.append({
                'severity': 'info',
                'category': 'naming_quality',
                'line': i,
                'line_end': i,
                'code_snippet': stripped[:120],
                'message': f'Vague variable name \"{name}\" — consider a more descriptive name'
            })

# Check for commented-out code blocks
comment_block_count = 0
in_comment_block = False
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    is_comment = stripped.startswith('#') or stripped.startswith('//')
    if is_comment and len(stripped) > 5:
        # Looks like commented-out code (has code-like patterns)
        if re.search(r'[=\(\)\[\]{};]', stripped):
            if not in_comment_block:
                comment_block_count += 1
                in_comment_block = True
        else:
            in_comment_block = False
    else:
        in_comment_block = False

if comment_block_count > 2:
    scores['dead_code'] = max(scores['dead_code'] - 15 * comment_block_count, 0)
    findings.append({
        'severity': 'info',
        'category': 'dead_code',
        'line': None,
        'line_end': None,
        'code_snippet': '',
        'message': f'{comment_block_count} commented-out code blocks found'
    })

summary = f'Heuristic analysis of {file_path} ({line_count} lines, {language})'

result = {
    'file': file_path,
    'language': language,
    'line_count': line_count,
    'scores': scores,
    'findings': findings[:30],  # Cap findings
    'summary': summary
}

print(json.dumps(result))
" 2>/dev/null
}

# ─── Main analysis loop ──────────────────────────────────────────────
TOTAL=${#FILES[@]}
ANALYZED=0
HAS_LLM="false"

# Check if LLM is available
if [ -n "${ANTHROPIC_API_KEY:-}" ] || [ -n "${OPENAI_API_KEY:-}" ] || command -v openclaw &>/dev/null; then
  HAS_LLM="true"
fi

for file_path in "${FILES[@]}"; do
  ANALYZED=$((ANALYZED + 1))

  # Validate file exists and is readable
  if [ ! -f "$file_path" ]; then
    warn "File not found: $file_path"
    continue
  fi

  if [ ! -r "$file_path" ]; then
    warn "File not readable: $file_path"
    continue
  fi

  # Check file size
  FILE_SIZE=$(wc -c < "$file_path" 2>/dev/null || echo "0")
  if [ "$FILE_SIZE" -gt "$MAX_FILE_SIZE" ]; then
    warn "Skipping $file_path (${FILE_SIZE} bytes > ${MAX_FILE_SIZE} max)"
    continue
  fi

  # Skip empty files
  if [ "$FILE_SIZE" -eq 0 ]; then
    warn "Skipping empty file: $file_path"
    continue
  fi

  LANGUAGE=$(detect_language "$file_path")
  FILE_CONTENT=$(cat "$file_path" 2>/dev/null || echo "")

  if [ "$HAS_LLM" = "true" ]; then
    # Build prompt and call LLM
    PROMPT=$(build_prompt "$file_path" "$FILE_CONTENT" "$LANGUAGE" "$FIX_MODE")
    
    LLM_RESPONSE=$(call_llm "$PROMPT" 2>/dev/null) || {
      warn "LLM call failed for $file_path, falling back to heuristics"
      fallback_analyze "$file_path" "$LANGUAGE"
      continue
    }

    # Parse and validate
    PARSED=$(parse_response "$LLM_RESPONSE" 2>/dev/null) || {
      warn "Failed to parse LLM response for $file_path, falling back to heuristics"
      fallback_analyze "$file_path" "$LANGUAGE"
      continue
    }

    # Validate it has the required fields
    VALID=$(echo "$PARSED" | python3 -c "
import json, sys
try:
    obj = json.load(sys.stdin)
    assert 'scores' in obj
    assert 'findings' in obj
    print('ok')
except:
    print('fail')
" 2>/dev/null)

    if [ "$VALID" = "ok" ]; then
      echo "$PARSED"
    else
      warn "Invalid LLM response structure for $file_path, falling back"
      fallback_analyze "$file_path" "$LANGUAGE"
    fi
  else
    # No LLM — use fallback heuristics
    if [ "$ANALYZED" -eq 1 ]; then
      warn "No LLM available. Using heuristic analysis (set ANTHROPIC_API_KEY or OPENAI_API_KEY for better results)."
    fi
    fallback_analyze "$file_path" "$LANGUAGE"
  fi

  progress "$ANALYZED" "$TOTAL" "files" >&2
done

progress_done >&2
info "Analyzed ${ANALYZED}/${TOTAL} files" >&2
