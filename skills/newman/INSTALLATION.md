# Newman Skill - Installation & Usage

## Installation

### Install the Skill

```bash
# Extract skill
tar -xzf newman.skill.tar.gz -C ~/.openclaw/workspace/skills/

# Or manually place in skills directory
mv newman ~/.openclaw/workspace/skills/
```

### Install Newman CLI

```bash
# Run the installation script
~/.openclaw/workspace/skills/newman/scripts/install-newman.sh --global

# Or install manually
npm install -g newman newman-reporter-htmlextra
```

## Quick Start

### 1. Export from Postman Desktop

**Collection:**
- Open Postman
- Collections → Click "..." → Export
- Choose "Collection v2.1"
- Save as `api-tests.json`

**Environment:**
- Environments → Click "..." → Export
- Save as `staging.json`

### 2. Run Tests

**Basic:**
```bash
newman run api-tests.json -e staging.json
```

**With reports:**
```bash
~/.openclaw/workspace/skills/newman/scripts/run-tests.sh \
  api-tests.json \
  staging.json \
  --output ./reports \
  --reporters cli,htmlextra \
  --bail
```

### 3. Security Audit

```bash
~/.openclaw/workspace/skills/newman/scripts/security-audit.sh \
  api-tests.json \
  staging.json
```

## Scripts Included

### install-newman.sh
Install Newman globally or locally.

```bash
# Global install (recommended)
./scripts/install-newman.sh --global

# Local install (project-specific)
./scripts/install-newman.sh --local
```

### run-tests.sh
Comprehensive test runner with security checks.

```bash
./scripts/run-tests.sh <collection> <environment> [options]

Options:
  -o, --output DIR        Output directory (default: ./test-results)
  -r, --reporters LIST    Reporters (default: cli,htmlextra)
  -b, --bail              Stop on first failure
  -v, --verbose           Verbose output
  -n, --iterations NUM    Iteration count
  -t, --timeout MS        Request timeout
```

**Example:**
```bash
./scripts/run-tests.sh \
  collections/api-tests.json \
  environments/staging.json \
  --bail \
  --output ./reports \
  --reporters cli,htmlextra,junit
```

### security-audit.sh
Scan collections for security issues.

```bash
./scripts/security-audit.sh <collection.json> [environment.json]
```

**Checks:**
- Hardcoded secrets/API keys
- Basic Auth credentials
- Insecure HTTP URLs
- SSL verification disabled
- PII exposure
- Variable usage best practices

## Environment Variables (Security)

**Never hardcode secrets!** Use environment variables:

```bash
# Export before running
export API_KEY="your-secret-key"
export DB_PASSWORD="your-password"

# Run Newman (auto-loads from env)
newman run collection.json -e environment.json

# Or pass directly
newman run collection.json --env-var "API_KEY=secret"
```

**In environment.json:**
```json
{
  "name": "Staging",
  "values": [
    {
      "key": "API_KEY",
      "value": "{{$processEnvironment.API_KEY}}",
      "enabled": true
    }
  ]
}
```

## CI/CD Examples

See `references/ci-cd-examples.md` for:
- GitHub Actions
- GitLab CI
- Jenkins
- CircleCI
- Bitbucket Pipelines
- Docker

## Advanced Patterns

See `references/advanced-patterns.md` for:
- Custom reporters
- Dynamic request chaining
- Data validation
- Performance testing
- Library integration
- Mock server integration

## Troubleshooting

**Collection not found:**
```bash
# Use absolute path
newman run /full/path/to/collection.json
```

**Environment variables not loading:**
```bash
# Check export
echo $API_KEY

# Use --env-var flag
newman run collection.json --env-var "API_KEY=value"
```

**SSL errors:**
```bash
# Development only!
newman run collection.json --insecure

# Production: add CA cert
newman run collection.json --ssl-extra-ca-certs ca.pem
```

## Best Practices

1. ✅ **Version Control**: Store collections in Git
2. ✅ **Security**: Use env vars, never commit secrets
3. ✅ **Separation**: dev/staging/prod environments
4. ✅ **Assertions**: Comprehensive test scripts
5. ✅ **CI Integration**: Run in every pipeline
6. ✅ **Reports**: Archive for historical analysis
7. ✅ **Timeouts**: Set reasonable values
8. ✅ **Modular**: Split collections by feature
9. ✅ **Documentation**: Use Postman descriptions
10. ✅ **Security Audit**: Run before deployment

## Support

- **Official Docs**: https://learning.postman.com/docs/running-collections/using-newman-cli/
- **Newman GitHub**: https://github.com/postmanlabs/newman
- **Skill Issues**: Report to skill maintainer

---

**Skill Version**: 1.0.0  
**Last Updated**: 2026-02-10
