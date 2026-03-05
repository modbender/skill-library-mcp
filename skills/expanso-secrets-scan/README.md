# secrets-scan

> Detect hardcoded secrets (API keys, tokens, passwords) in text or code.

Scan code, configs, and logs for accidentally committed credentials. Essential for:
- Pre-commit hooks
- CI/CD pipelines
- Code review automation
- Security audits

## Quick Start

### CLI Mode

```bash
export OPENAI_API_KEY=sk-...

# Scan a file
cat config.yaml | expanso-edge run pipeline-cli.yaml

# Scan before committing
git diff --cached | expanso-edge run pipeline-cli.yaml

# Scan entire codebase
find . -name "*.py" -exec cat {} \; | expanso-edge run pipeline-cli.yaml
```

### MCP Mode

```bash
PORT=8080 expanso-edge run pipeline-mcp.yaml &

curl -X POST http://localhost:8080/scan \
  -H "Content-Type: application/json" \
  -d '{
    "text": "const API_KEY = \"sk-abc123def456\";",
    "types": ["api_key", "token"]
  }'
```

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `SECRET_TYPES` | No | all | Comma-separated secret types |
| `PORT` | No | 8080 | HTTP port for MCP mode |

## Secret Types

| Type | Examples |
|------|----------|
| `api_key` | sk-xxx, AKIA..., api_key=... |
| `token` | ghp_xxx, Bearer xxx |
| `password` | password=xxx, pwd:xxx |
| `private_key` | -----BEGIN RSA PRIVATE KEY----- |
| `aws_key` | aws-xxx, aws_secret_access_key |
| `github_token` | ghp_xxx, gho_xxx |
| `slack_token` | slack-xxx |
| `openai_key` | sk-xxx |

## Example Output

### Input
```javascript
const config = {
  apiKey: "sk-proj-abc123def456ghi789",
  database: {
    password: "supersecret123!"
  },
  aws: {
    accessKeyId: "YOUR_AWS_ACCESS_KEY_ID",
    secretAccessKey: "YOUR_AWS_SECRET_KEY"
  }
};
```

### Output
```json
{
  "findings": [
    {
      "type": "openai_key",
      "value": "sk-p...789",
      "line": 2,
      "severity": "high",
      "context": "OpenAI API key in apiKey field"
    },
    {
      "type": "password",
      "value": "supe...123!",
      "line": 4,
      "severity": "high",
      "context": "Database password"
    },
    {
      "type": "aws_key",
      "value": "YOUR...ID",
      "line": 7,
      "severity": "high",
      "context": "AWS Access Key ID"
    },
    {
      "type": "aws_key",
      "value": "YOUR...KEY",
      "line": 8,
      "severity": "high",
      "context": "AWS Secret Access Key"
    }
  ],
  "has_secrets": true,
  "summary": "Found 4 high-severity secrets: 1 OpenAI key, 1 password, 2 AWS credentials"
}
```

## Pre-Commit Integration

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: secrets-scan
        name: Scan for secrets
        entry: bash -c 'git diff --cached | expanso-edge run skills/secrets-scan/pipeline-cli.yaml | jq -e ".has_secrets == false"'
        language: system
        pass_filenames: false
```

## False Positive Handling

The scanner automatically ignores:
- Placeholder values: `your-api-key-here`, `xxx`, `<token>`
- Environment references: `${API_KEY}`, `$SECRET`
- Example values from documentation
- Test fixtures with obvious fake data

## Related Skills

- [pii-detect](../pii-detect/) - Detect personally identifiable information
- [log-sanitize](../log-sanitize/) - Sanitize logs before storage
- [policy-check](../policy-check/) - Check configuration against policies

---

*Built with [Expanso Edge](https://expanso.io) - Your keys, your machine.*
