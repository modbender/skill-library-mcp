# Quick Start

Get up and running with Tork Guardian in 2 minutes.

## Install

```bash
npm install @tork/guardian
```

## Initialize

```typescript
import { TorkGuardian } from '@tork/guardian';

const guardian = new TorkGuardian({
  apiKey: process.env.TORK_API_KEY!,
});
```

Sign up at [tork.network](https://tork.network) to get your API key.

## Govern an LLM Request

Scan messages for PII before sending to an LLM:

```typescript
const result = await guardian.governLLM({
  messages: [{ role: 'user', content: 'Email john@example.com about the project' }],
});
// PII is redacted: "Email [EMAIL_REDACTED] about the project"
```

See [README.md](../README.md#quick-start) for full LLM governance docs.

## Govern a Tool Call

Check if a tool call is safe before executing:

```typescript
const decision = guardian.governTool({
  name: 'shell_execute',
  args: { command: 'rm -rf /' },
});
// { allowed: false, reason: 'Blocked shell command pattern: "rm -rf"' }
```

See [README.md](../README.md#policies) for policy configuration.

## Scan a Skill for Vulnerabilities

Scan any OpenClaw skill before installing it:

```typescript
import { SkillScanner } from '@tork/guardian';

const scanner = new SkillScanner();
const report = await scanner.scanSkill('./some-skill');
console.log(`Risk: ${report.riskScore}/100, Verdict: ${report.verdict}`);
```

Or use the CLI:

```bash
npx tork-scan ./some-skill --verbose
```

See [SCANNER.md](SCANNER.md) for the full rule reference and badge system.

## Enable Network Security

Govern port binds, outbound connections, and DNS lookups:

```typescript
const guardian = new TorkGuardian({
  apiKey: process.env.TORK_API_KEY!,
  networkPolicy: 'strict',
});
const network = guardian.getNetworkHandler();
```

See [NETWORK-SECURITY.md](NETWORK-SECURITY.md) for threat coverage, policies, and compliance receipts.

## What's Next

| Feature | Docs |
|---------|------|
| PII redaction & compliance | [README.md](../README.md) |
| Network governance | [NETWORK-SECURITY.md](NETWORK-SECURITY.md) |
| Security scanner & CLI | [SCANNER.md](SCANNER.md) |
| Example configurations | [README.md](../README.md#example-configs) |
