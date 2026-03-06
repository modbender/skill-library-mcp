# Publish To ClawHub

Reference: https://docs.openclaw.ai/tools/clawhub

## 1. Install and log in

```bash
npm i -g clawhub
clawhub login
clawhub whoami
```

## 2. Dry run (optional)

```bash
clawhub publish ./skills/blankfiles \
  --slug filearchitect-blankfiles \
  --name "Blank Files Gateway" \
  --version 1.0.0 \
  --changelog "Initial release" \
  --tags latest \
  --no-input
```

## 3. Publish

```bash
clawhub publish ./skills/blankfiles \
  --slug filearchitect-blankfiles \
  --name "Blank Files Gateway" \
  --version 1.0.0 \
  --changelog "Initial release" \
  --tags latest
```

## 4. Update release

```bash
clawhub publish ./skills/blankfiles \
  --slug filearchitect-blankfiles \
  --name "Blank Files Gateway" \
  --version 1.0.1 \
  --changelog "Add new binary formats and API guidance" \
  --tags latest
```

## 5. Verify discoverability

```bash
clawhub search "blank files"
clawhub search "binary upload testing"
```

Tip: keep the skill description focused on "binary upload testing" and "direct download URLs" for better search ranking.
