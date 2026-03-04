---
name: newman
description: Automated API testing with Postman collections via Newman CLI. Use when user requests API testing, collection execution, automated testing, CI/CD integration, or mentions "Postman", "Newman", "API tests", "run collection", or "automated testing".
---

# Newman - Postman CLI Runner

Newman is the command-line Collection Runner for Postman. Run and test Postman collections directly from the command line with powerful reporting, environment management, and CI/CD integration.

## Quick Start

### Installation

```bash
# Global install (recommended)
npm install -g newman

# Project-specific
npm install --save-dev newman

# Verify
newman --version
```

### Basic Execution

```bash
# Run collection
newman run collection.json

# With environment
newman run collection.json -e environment.json

# With globals
newman run collection.json -g globals.json

# Combined
newman run collection.json -e env.json -g globals.json -d data.csv
```

## Core Workflows

### 1. Export from Postman Desktop

**In Postman:**
1. Collections → Click "..." → Export
2. Choose "Collection v2.1" (recommended)
3. Save as `collection.json`

**Environment:**
1. Environments → Click "..." → Export
2. Save as `environment.json`

### 2. Run Tests

```bash
# Basic run
newman run collection.json

# With detailed output
newman run collection.json --verbose

# Fail on errors
newman run collection.json --bail

# Custom timeout (30s)
newman run collection.json --timeout-request 30000
```

### 3. Data-Driven Testing

**CSV format:**
```csv
username,password
user1,pass1
user2,pass2
```

**Run:**
```bash
newman run collection.json -d test_data.csv --iteration-count 2
```

### 4. Reporters

```bash
# CLI only (default)
newman run collection.json

# HTML report
newman run collection.json --reporters cli,html --reporter-html-export report.html

# JSON export
newman run collection.json --reporters cli,json --reporter-json-export results.json

# JUnit (for CI)
newman run collection.json --reporters cli,junit --reporter-junit-export junit.xml

# Multiple reporters
newman run collection.json --reporters cli,html,json,junit \
  --reporter-html-export ./reports/newman.html \
  --reporter-json-export ./reports/newman.json \
  --reporter-junit-export ./reports/newman.xml
```

### 5. Security Best Practices

**❌ NEVER hardcode secrets in collections!**

Use environment variables:

```bash
# Export sensitive vars
export API_KEY="your-secret-key"
export DB_PASSWORD="your-db-pass"

# Newman auto-loads from env
newman run collection.json -e environment.json

# Or pass directly
newman run collection.json --env-var "API_KEY=secret" --env-var "DB_PASSWORD=pass"
```

**In Postman collection tests:**
```javascript
// Use {{API_KEY}} in requests
pm.request.headers.add({key: 'Authorization', value: `Bearer {{API_KEY}}`});

// Access in scripts
const apiKey = pm.environment.get("API_KEY");
```

**Environment file (environment.json):**
```json
{
  "name": "Production",
  "values": [
    {"key": "BASE_URL", "value": "https://api.example.com", "enabled": true},
    {"key": "API_KEY", "value": "{{$processEnvironment.API_KEY}}", "enabled": true}
  ]
}
```

Newman will replace `{{$processEnvironment.API_KEY}}` with the environment variable.

## Common Use Cases

### CI/CD Integration

See `references/ci-cd-examples.md` for GitHub Actions, GitLab CI, and Jenkins examples.

### Automated Regression Testing

```bash
#!/bin/bash
# scripts/run-api-tests.sh

set -e

echo "Running API tests..."

newman run collections/api-tests.json \
  -e environments/staging.json \
  --reporters cli,html,junit \
  --reporter-html-export ./test-results/newman.html \
  --reporter-junit-export ./test-results/newman.xml \
  --bail \
  --color on

echo "Tests completed. Report: ./test-results/newman.html"
```

### Load Testing

```bash
# Run with high iteration count
newman run collection.json \
  -n 100 \
  --delay-request 100 \
  --timeout-request 5000 \
  --reporters cli,json \
  --reporter-json-export load-test-results.json
```

### Parallel Execution

```bash
# Install parallel runner
npm install -g newman-parallel

# Run collections in parallel
newman-parallel -c collection1.json,collection2.json,collection3.json \
  -e environment.json \
  --reporters cli,html
```

## Advanced Features

### Custom Scripts

**Pre-request Script (in Postman):**
```javascript
// Generate dynamic values
pm.environment.set("timestamp", Date.now());
pm.environment.set("nonce", Math.random().toString(36).substring(7));
```

**Test Script (in Postman):**
```javascript
// Status code check
pm.test("Status is 200", function() {
    pm.response.to.have.status(200);
});

// Response body validation
pm.test("Response has user ID", function() {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('user_id');
});

// Response time check
pm.test("Response time < 500ms", function() {
    pm.expect(pm.response.responseTime).to.be.below(500);
});

// Set variable from response
pm.environment.set("user_token", pm.response.json().token);
```

### SSL/TLS Configuration

```bash
# Disable SSL verification (dev only!)
newman run collection.json --insecure

# Custom CA certificate
newman run collection.json --ssl-client-cert-list cert-list.json

# Client certificates
newman run collection.json \
  --ssl-client-cert client.pem \
  --ssl-client-key key.pem \
  --ssl-client-passphrase "secret"
```

### Error Handling

```bash
# Continue on errors
newman run collection.json --suppress-exit-code

# Fail fast
newman run collection.json --bail

# Custom error handling in wrapper
#!/bin/bash
newman run collection.json -e env.json
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "Tests failed! Exit code: $EXIT_CODE"
    # Send alert, rollback deployment, etc.
    exit 1
fi
```

## Troubleshooting

**Collection not found:**
- Use absolute paths: `newman run /full/path/to/collection.json`
- Check file permissions: `ls -la collection.json`

**Environment variables not loading:**
- Verify syntax: `{{$processEnvironment.VAR_NAME}}`
- Check export: `echo $VAR_NAME`
- Use `--env-var` flag as fallback

**Timeout errors:**
- Increase timeout: `--timeout-request 60000` (60s)
- Check network connectivity
- Verify API endpoint is reachable

**SSL errors:**
- Development: Use `--insecure` temporarily
- Production: Add CA cert with `--ssl-extra-ca-certs`

**Memory issues (large collections):**
- Reduce iteration count
- Split collection into smaller parts
- Increase Node heap: `NODE_OPTIONS=--max-old-space-size=4096 newman run ...`

## Best Practices

1. **Version Control**: Store collections and environments in Git
2. **Environment Separation**: Separate files for dev/staging/prod
3. **Secret Management**: Use environment variables, never commit secrets
4. **Meaningful Names**: Use descriptive collection and folder names
5. **Test Atomicity**: Each request should test one specific thing
6. **Assertions**: Add comprehensive test scripts to every request
7. **Documentation**: Use Postman descriptions for context
8. **CI Integration**: Run Newman in CI pipeline for every PR
9. **Reports**: Archive HTML reports for historical analysis
10. **Timeouts**: Set reasonable timeout values for production APIs

## References

- **CI/CD Examples**: See `references/ci-cd-examples.md`
- **Advanced Patterns**: See `references/advanced-patterns.md`
- **Official Docs**: https://learning.postman.com/docs/running-collections/using-newman-cli/command-line-integration-with-newman/
