# Publishing to ClawHub

Skill folder: `./skills/xmind`

Suggested slug: `ben/xmind`

## 1) Login
```bash
cd /Users/ben/clawd
npx -y clawhub login
npx -y clawhub whoami
```

## 2) Publish
```bash
cd /Users/ben/clawd
npx -y clawhub publish ./skills/xmind \
  --slug ben/xmind \
  --name "xmind" \
  --version 0.1.0 \
  --changelog "Initial release: generate/read XMind via xmind-generator-mcp MCP server" \
  --tags latest
```

## 3) Update
Bump version and publish again.
