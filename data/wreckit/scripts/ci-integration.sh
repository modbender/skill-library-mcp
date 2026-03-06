#!/usr/bin/env bash
# wreckit — CI config detection, scoring, and generation
# Usage: ./ci-integration.sh [project-path] [--generate]
# Output: JSON to stdout, human summary to stderr
# --generate: write starter GitHub Actions workflow if no CI found
# Exit 0 = results produced, check JSON verdict for pass/fail

set -euo pipefail
PROJECT="${1:-.}"
GENERATE=false
if [ "${2:-}" = "--generate" ]; then
  GENERATE=true
fi
PROJECT="$(cd "$PROJECT" && pwd)"
cd "$PROJECT"

echo "=== CI Integration Check ===" >&2
echo "Project: $(pwd)" >&2

# ─── Detect CI configs ────────────────────────────────────────────────────────

CI_FOUND=false
CI_TYPE=""
CI_FILE=""

# GitHub Actions
if ls .github/workflows/*.yml >/dev/null 2>&1 || ls .github/workflows/*.yaml >/dev/null 2>&1; then
  CI_FOUND=true
  CI_TYPE="github-actions"
  CI_FILE=$(ls .github/workflows/*.yml .github/workflows/*.yaml 2>/dev/null | head -1 || true)
  echo "Found GitHub Actions: $CI_FILE" >&2
fi

# GitLab CI
if [ "$CI_FOUND" = false ] && [ -f ".gitlab-ci.yml" ]; then
  CI_FOUND=true
  CI_TYPE="gitlab-ci"
  CI_FILE=".gitlab-ci.yml"
  echo "Found GitLab CI: $CI_FILE" >&2
fi

# CircleCI
if [ "$CI_FOUND" = false ] && [ -f ".circleci/config.yml" ]; then
  CI_FOUND=true
  CI_TYPE="circleci"
  CI_FILE=".circleci/config.yml"
  echo "Found CircleCI: $CI_FILE" >&2
fi

# Jenkins
if [ "$CI_FOUND" = false ] && [ -f "Jenkinsfile" ]; then
  CI_FOUND=true
  CI_TYPE="jenkins"
  CI_FILE="Jenkinsfile"
  echo "Found Jenkinsfile" >&2
fi

# Azure Pipelines
if [ "$CI_FOUND" = false ] && [ -f "azure-pipelines.yml" ]; then
  CI_FOUND=true
  CI_TYPE="azure-pipelines"
  CI_FILE="azure-pipelines.yml"
  echo "Found Azure Pipelines: $CI_FILE" >&2
fi

# Travis CI
if [ "$CI_FOUND" = false ] && [ -f ".travis.yml" ]; then
  CI_FOUND=true
  CI_TYPE="travis"
  CI_FILE=".travis.yml"
  echo "Found Travis CI: $CI_FILE" >&2
fi

# ─── Score existing CI config ─────────────────────────────────────────────────

SCORE=0
MISSING_STEPS="[]"
GENERATED_CONFIG_PATH=""

if [ "$CI_FOUND" = true ] && [ -n "$CI_FILE" ] && [ -f "$CI_FILE" ]; then
  echo "Scoring $CI_FILE..." >&2
  missing=""

  if [ "$CI_TYPE" = "github-actions" ]; then
    WORKFLOW_FILES=$(ls .github/workflows/*.yml .github/workflows/*.yaml 2>/dev/null || true)
    if [ -z "$WORKFLOW_FILES" ]; then
      WORKFLOW_COUNT=0
    else
      WORKFLOW_COUNT=$(echo "$WORKFLOW_FILES" | wc -l | tr -d ' ')
    fi

    if [ "$WORKFLOW_COUNT" -gt 0 ]; then
      SCORE=$((SCORE + 30))
      echo "  ✓ Workflows present: +30pts" >&2
    else
      missing="${missing}\"workflows\","
      echo "  ✗ Workflows present: 0pts" >&2
    fi

    JOB_WORKFLOW_COUNT=0
    ON_FOUND=false
    STEP_FOUND=false
    MATRIX_FOUND=false
    OS_UBUNTU=false
    OS_WINDOWS=false
    OS_MACOS=false

    while IFS= read -r wf; do
      [ -z "$wf" ] && continue
      if grep -qiE "^[[:space:]]*jobs:" "$wf" 2>/dev/null; then
        JOB_WORKFLOW_COUNT=$((JOB_WORKFLOW_COUNT + 1))
      fi
      if grep -qiE "(^|[^a-z])(push|pull_request)([^a-z]|$)" "$wf" 2>/dev/null; then
        ON_FOUND=true
      fi
      if grep -qiE "run:.*(test|lint|build)|npm test|npm run test|pytest|go test|cargo test|vitest|jest|mocha|yarn test" "$wf" 2>/dev/null; then
        STEP_FOUND=true
      fi
      if grep -qiE "matrix:" "$wf" 2>/dev/null; then
        MATRIX_FOUND=true
      fi
      if grep -qiE "runs-on:.*ubuntu" "$wf" 2>/dev/null; then
        OS_UBUNTU=true
      fi
      if grep -qiE "runs-on:.*windows" "$wf" 2>/dev/null; then
        OS_WINDOWS=true
      fi
      if grep -qiE "runs-on:.*macos" "$wf" 2>/dev/null; then
        OS_MACOS=true
      fi
    done <<< "$WORKFLOW_FILES"

    if [ "$JOB_WORKFLOW_COUNT" -gt 0 ]; then
      SCORE=$((SCORE + 15 * JOB_WORKFLOW_COUNT))
      echo "  ✓ Workflows with jobs: +$((15 * JOB_WORKFLOW_COUNT))pts" >&2
    else
      missing="${missing}\"jobs\","
      echo "  ✗ Workflows with jobs: 0pts" >&2
    fi

    if [ "$ON_FOUND" = true ]; then
      SCORE=$((SCORE + 20))
      echo "  ✓ Runs on push/PR: +20pts" >&2
    else
      missing="${missing}\"on-push-pr\","
      echo "  ✗ Runs on push/PR: 0pts" >&2
    fi

    if [ "$STEP_FOUND" = true ]; then
      SCORE=$((SCORE + 15))
      echo "  ✓ Test/lint/build step: +15pts" >&2
    else
      missing="${missing}\"test-lint-build\","
      echo "  ✗ Test/lint/build step: 0pts" >&2
    fi

    OS_COUNT=0
    [ "$OS_UBUNTU" = true ] && OS_COUNT=$((OS_COUNT + 1))
    [ "$OS_WINDOWS" = true ] && OS_COUNT=$((OS_COUNT + 1))
    [ "$OS_MACOS" = true ] && OS_COUNT=$((OS_COUNT + 1))
    if [ "$MATRIX_FOUND" = true ] || [ "$OS_COUNT" -ge 2 ]; then
      SCORE=$((SCORE + 20))
      echo "  ✓ Matrix or multi-OS: +20pts" >&2
    else
      missing="${missing}\"matrix-or-multi-os\","
      echo "  ✗ Matrix or multi-OS: 0pts" >&2
    fi
  else
    SCORE=$((SCORE + 30))
    echo "  ✓ CI config present: +30pts" >&2

    if [ -s "$CI_FILE" ]; then
      SCORE=$((SCORE + 15))
      echo "  ✓ CI config non-empty: +15pts" >&2
    else
      missing="${missing}\"empty-config\","
      echo "  ✗ CI config non-empty: 0pts" >&2
    fi

    if grep -qiE "(test|lint|build)" "$CI_FILE" 2>/dev/null; then
      SCORE=$((SCORE + 15))
      echo "  ✓ Test/lint/build step: +15pts" >&2
    else
      missing="${missing}\"test-lint-build\","
      echo "  ✗ Test/lint/build step: 0pts" >&2
    fi

    if grep -qiE "(push|pull_request|merge_request)" "$CI_FILE" 2>/dev/null; then
      SCORE=$((SCORE + 20))
      echo "  ✓ Triggers present: +20pts" >&2
    else
      missing="${missing}\"triggers\","
      echo "  ✗ Triggers present: 0pts" >&2
    fi
  fi

  if [ "$SCORE" -gt 100 ]; then
    SCORE=100
  fi

  if [ -n "$missing" ]; then
    MISSING_STEPS="[${missing%,}]"
  fi

  echo "  Total score: $SCORE/100" >&2

fi

# ─── Generate CI config if not found ─────────────────────────────────────────

if [ "$CI_FOUND" = false ]; then
  echo "" >&2
  echo "No CI configuration found." >&2

  # Detect project type for config generation
  SETUP_STEP="- uses: actions/setup-node@v4\n        with: { node-version: '20' }"
  INSTALL_CMD="npm install"
  TYPECHECK_CMD="npx tsc --noEmit"
  TEST_CMD="npm test"

  if [ -f "go.mod" ]; then
    SETUP_STEP="- uses: actions/setup-go@v5\n        with: { go-version: '1.22' }"
    INSTALL_CMD="go mod download"
    TYPECHECK_CMD="go vet ./..."
    TEST_CMD="go test ./..."
  elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    SETUP_STEP="- uses: actions/setup-python@v5\n        with: { python-version: '3.12' }"
    INSTALL_CMD="pip install -r requirements.txt"
    TYPECHECK_CMD="python -m mypy . || true"
    TEST_CMD="python -m pytest"
  fi

  GENERATED_CONFIG_PATH=".github/workflows/wreckit-audit.yml"

  if [ "$GENERATE" = true ]; then
    mkdir -p ".github/workflows"
    cat > "$GENERATED_CONFIG_PATH" <<YAMLEOF
# Generated by wreckit ci-integration.sh
name: wreckit audit
on: [push, pull_request]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - ${SETUP_STEP}
      - run: ${INSTALL_CMD}
      - run: ${TYPECHECK_CMD}
      - run: ${TEST_CMD}
YAMLEOF
    echo "Generated: $GENERATED_CONFIG_PATH" >&2
  else
    echo "Run with --generate flag to create $GENERATED_CONFIG_PATH" >&2
    GENERATED_CONFIG_PATH=""
  fi
fi

# ─── Determine verdict ────────────────────────────────────────────────────────

VERDICT="FAIL"
SUMMARY=""
CONFIDENCE="0.0"

if [ "$CI_FOUND" = false ]; then
  VERDICT="FAIL"
  SUMMARY="FAIL: No CI configuration found in project."
  CONFIDENCE="1.0"
elif [ "$SCORE" -ge 70 ]; then
  VERDICT="PASS"
  SUMMARY="PASS: CI found (${CI_TYPE}), score ${SCORE}/100."
elif [ "$SCORE" -ge 40 ]; then
  VERDICT="WARN"
  SUMMARY="WARN: CI found (${CI_TYPE}) but incomplete, score ${SCORE}/100."
  CONFIDENCE="0.5"
else
  VERDICT="FAIL"
  SUMMARY="FAIL: CI found (${CI_TYPE}) but critically incomplete, score ${SCORE}/100."
  CONFIDENCE="0.5"
fi

# ─── Output ───────────────────────────────────────────────────────────────────

echo "" >&2
echo "CI found: $CI_FOUND" >&2
echo "CI type: ${CI_TYPE:-none}" >&2
echo "Score: $SCORE/100" >&2
echo "Verdict: $VERDICT" >&2
echo "Summary: $SUMMARY" >&2

CI_FILE_JSON="null"
if [ -n "$CI_FILE" ]; then
  CI_FILE_JSON="\"$CI_FILE\""
fi

GENERATED_JSON="null"
if [ -n "$GENERATED_CONFIG_PATH" ]; then
  GENERATED_JSON="\"$GENERATED_CONFIG_PATH\""
fi

cat <<EOF
{
  "ci_found": $CI_FOUND,
  "ci_type": "${CI_TYPE:-none}",
  "ci_file": $CI_FILE_JSON,
  "score_100": $SCORE,
  "missing_steps": $MISSING_STEPS,
  "generated_config_path": $GENERATED_JSON,
  "status": "$VERDICT",
  "verdict": "$VERDICT",
  "summary": "$SUMMARY",
  "confidence": $CONFIDENCE
}
EOF
