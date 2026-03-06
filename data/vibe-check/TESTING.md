# TESTING.md — vibe-check Test Plan

Run all commands from `studio/skills/vibe-check/`.

## Prerequisites

```bash
bash --version
python3 --version
git --version
curl --version
```

## 1. Syntax Validation

```bash
bash -n scripts/common.sh
bash -n scripts/git-diff.sh
bash -n scripts/analyze.sh
bash -n scripts/report.sh
bash -n scripts/vibe-check.sh
```

Expected: no output and zero exit status for all commands.

## 2. Help Output

```bash
bash scripts/vibe-check.sh --help
```

Expected: usage/help text renders and exits 0.

## 3. Smoke Test (Heuristic Mode)

```bash
unset ANTHROPIC_API_KEY OPENAI_API_KEY
bash scripts/vibe-check.sh test_samples
```

Expected:
- Non-empty Markdown report
- Includes `# 🎭 Vibe Check Report`
- Includes a numeric score and grade

## 4. Fix Mode Smoke Test

```bash
unset ANTHROPIC_API_KEY OPENAI_API_KEY
bash scripts/vibe-check.sh --fix test_samples
```

Expected:
- Report contains `## 🔧 Suggested Fixes`
- If no patches are generated, report shows the fallback explanatory message

## 5. Output File Mode

```bash
rm -f /tmp/vibe-check-report.md
bash scripts/vibe-check.sh --output /tmp/vibe-check-report.md test_samples
test -s /tmp/vibe-check-report.md && echo "PASS: report file written"
```

Expected: `/tmp/vibe-check-report.md` exists and is non-empty.

## 6. Diff Mode (Temp Git Repo)

```bash
TMP_REPO="$(mktemp -d)"
cd "$TMP_REPO"
git init
git config user.email "test@example.com"
git config user.name "Vibe Check Test"
cat > app.py <<'PY'
print("hello")
PY
git add app.py
git commit -m "init"
cat >> app.py <<'PY'
eval("1+1")
PY
git add app.py
git commit -m "introduce risky pattern"
cd - >/dev/null
bash scripts/vibe-check.sh --diff HEAD~1 --output /tmp/vibe-check-diff.md "$TMP_REPO"
test -s /tmp/vibe-check-diff.md && echo "PASS: diff report written"
rm -rf "$TMP_REPO"
```

Expected: diff-mode report file is generated.

## 7. Flag Validation (Regression Guards)

```bash
bash scripts/vibe-check.sh --branch 2>&1 | grep -q "Missing value for --branch" && echo "PASS: --branch validation"
bash scripts/vibe-check.sh --output 2>&1 | grep -q "Missing value for --output" && echo "PASS: --output validation"
bash scripts/vibe-check.sh --max-files 2>&1 | grep -q "Missing value for --max-files" && echo "PASS: --max-files validation"
bash scripts/git-diff.sh --branch 2>&1 | grep -q "Missing value for --branch" && echo "PASS: git-diff --branch validation"
```

Expected: each command fails with a clear missing-value error.

## Cleanup

```bash
rm -f /tmp/vibe-check-report.md /tmp/vibe-check-diff.md
```
