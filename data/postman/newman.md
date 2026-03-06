# Newman — Postman CLI

## Installation

```bash
npm install -g newman
```

## Basic Commands

```bash
# Run collection
newman run collection.json

# With environment
newman run collection.json -e environment.json

# With globals
newman run collection.json -g globals.json

# Multiple environments
newman run collection.json -e dev.json -e secrets.json
```

## Filtering

```bash
# Run specific folder
newman run collection.json --folder "Users"

# Run specific request (by name)
newman run collection.json --folder "Auth" --folder "Login"
```

## Iterations & Data

```bash
# Run 10 times
newman run collection.json -n 10

# With data file (CSV or JSON)
newman run collection.json -d users.csv

# Delay between requests (ms)
newman run collection.json --delay-request 500
```

### Data File Format (CSV)
```csv
email,password
user1@test.com,pass1
user2@test.com,pass2
```

### Data File Format (JSON)
```json
[
  { "email": "user1@test.com", "password": "pass1" },
  { "email": "user2@test.com", "password": "pass2" }
]
```

## Reporters

```bash
# CLI only (default)
newman run collection.json -r cli

# Multiple reporters
newman run collection.json -r cli,json,htmlextra

# JSON output to file
newman run collection.json -r json --reporter-json-export results.json

# HTML report (install: npm i -g newman-reporter-htmlextra)
newman run collection.json -r htmlextra --reporter-htmlextra-export report.html
```

## CI/CD Integration

### Exit Codes
- `0` — All tests passed
- `1` — Tests failed or errors occurred

### GitHub Actions
```yaml
- name: Run API Tests
  run: |
    npm install -g newman
    newman run collection.json -e ${{ env.ENV }}.json --bail
```

### GitLab CI
```yaml
api_tests:
  script:
    - npm install -g newman
    - newman run collection.json -e ci.json --reporters cli,junit --reporter-junit-export results.xml
  artifacts:
    reports:
      junit: results.xml
```

## Useful Flags

| Flag | Purpose |
|------|---------|
| `--bail` | Stop on first error |
| `--ignore-redirects` | Don't follow 3xx |
| `--insecure` | Allow self-signed certs |
| `--timeout 10000` | Request timeout (ms) |
| `--timeout-request 5000` | Per-request timeout |
| `--timeout-script 5000` | Script timeout |
| `-k` | Disable SSL verification |
| `--verbose` | Detailed output |

## Environment Variables in CI

```bash
# Override env values from shell
newman run collection.json \
  --env-var "base_url=$API_URL" \
  --env-var "token=$API_TOKEN"
```

## Common Patterns

### Smoke Test (fail fast)
```bash
newman run collection.json --folder "Health" --bail
```

### Full Test Suite with Report
```bash
newman run collection.json \
  -e staging.json \
  -r htmlextra,cli \
  --reporter-htmlextra-export ./reports/$(date +%Y%m%d).html
```

### Load Test Simulation
```bash
# Run 100 iterations with data
newman run collection.json -d users.json -n 100 --delay-request 100
```
