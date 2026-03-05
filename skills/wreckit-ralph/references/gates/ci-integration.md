# Gate: CI Integration

**Question:** Does this project have a CI pipeline that proves it works automatically?

## What to Check

- Presence of CI configuration files:
  - `.github/workflows/*.yml` (GitHub Actions)
  - `.gitlab-ci.yml` (GitLab CI)
  - `Jenkinsfile` (Jenkins)
  - `.circleci/config.yml` (CircleCI)
  - `Makefile` with `ci` or `test` targets
- Quality of existing CI config:
  - Tests are actually run (not just lint)
  - Type checking is included (for typed languages)
  - Coverage reporting is enabled
  - Security scanning (SAST/dependency audit) is included

## How to Run

```bash
scripts/ci-integration.sh [project-path]
```

The script:
1. Searches for CI config files in common locations
2. If found: parses and scores based on steps present
3. If not found: generates a starter `.github/workflows/wreckit-audit.yml`

Scoring (100 points total):
- Tests present: 40 pts
- Type check present: 30 pts
- Coverage reporting: 20 pts
- Security scan: 10 pts

## Pass / Fail Criteria

### PASS ✅
- CI config exists
- Score ≥ 70 (tests + type check at minimum)
- Pipeline runs on push AND pull requests

### WARN ⚠️
- CI config exists but score 40–69
- Missing type check or coverage steps
- Only runs on push, not PRs

### FAIL ❌
- No CI config found in project
- CI config exists but runs no tests (score < 40)

## Example Output

```json
{
  "ci_found": true,
  "ci_type": "github-actions",
  "score_100": 90,
  "missing_steps": ["security-scan"],
  "generated_config_path": null,
  "verdict": "PASS",
  "summary": "GitHub Actions found. Score 90/100. Missing: security scan."
}
```

## Generated Config (when none exists)

When no CI config is found, the script can generate a starter workflow:

```yaml
# .github/workflows/wreckit-audit.yml
name: wreckit audit
on: [push, pull_request]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm install
      - run: npx tsc --noEmit
      - run: npm test
```
