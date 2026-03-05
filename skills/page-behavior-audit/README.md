# page-behavior-audit

OpenClaw Skill for deep behavioral page auditing with hashed policy.

## Installation

```bash
npx clawhub@latest install page-behavior-audit
```

## Required Environment Variables

```bash
export WECOM_WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
export OPENCLAW_AUDIT_DIR="${HOME}/.openclaw/audit"  # optional
```

## Usage

```bash
curl -X POST http://localhost:8080/api/audit/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Version

1.0.3

## License

MIT
