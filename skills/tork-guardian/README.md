# Tork Guardian for OpenClaw

> OpenClaw is powerful. Tork makes it safe.

Enterprise-grade security and governance layer for OpenClaw agents. Detect PII, enforce policies, generate compliance receipts, control tool access, and scan skills for vulnerabilities before installation.

## Installation

```bash
npm install @torknetwork/guardian
```

## Quick Start

```typescript
import { TorkGuardian } from '@torknetwork/guardian';

const guardian = new TorkGuardian({
  apiKey: process.env.TORK_API_KEY!,
});

// Govern an LLM request before sending
const result = await guardian.governLLM({
  messages: [
    { role: 'user', content: 'Email john@example.com about the project' },
  ],
});
// PII is redacted: "Email [EMAIL_REDACTED] about the project"

// Check if a tool call is allowed
const decision = guardian.governTool({
  name: 'shell_execute',
  args: { command: 'rm -rf /' },
});
// { allowed: false, reason: 'Blocked shell command pattern: "rm -rf"' }
```

## Network Security

Tork Guardian governs all network activity — port binds, outbound connections, and DNS lookups — with SSRF prevention, reverse shell detection, and per-skill rate limiting.

### Using the network handler

```typescript
const guardian = new TorkGuardian({
  apiKey: process.env.TORK_API_KEY!,
  networkPolicy: 'default',
});

const network = guardian.getNetworkHandler();

// Validate a port bind
const bind = network.validatePortBind('my-skill', 3000, 'tcp');
// { allowed: true, reason: 'Port 3000/tcp bound' }

// Validate an outbound connection
const egress = network.validateEgress('my-skill', 'api.openai.com', 443);
// { allowed: true, reason: 'Egress to api.openai.com:443 allowed' }

// Validate a DNS lookup (flags raw IPs)
const dns = network.validateDNS('my-skill', 'api.openai.com');
// { allowed: true, reason: 'DNS lookup for api.openai.com allowed' }

// Get the full activity log for compliance
const log = network.getActivityLog();

// Get a network report with anomaly detection
const report = network.getMonitor().getNetworkReport();
```

### Standalone functions

```typescript
import { validatePortBind, validateEgress, validateDNS } from '@torknetwork/guardian';

const config = { apiKey: 'tork_...', networkPolicy: 'strict' as const };

validatePortBind(config, 'my-skill', 3000, 'tcp');
validateEgress(config, 'my-skill', 'api.openai.com', 443);
validateDNS(config, 'my-skill', 'api.openai.com');
```

### Switching policies

```typescript
// Default — balanced for dev & production
const guardian = new TorkGuardian({
  apiKey: 'tork_...',
  networkPolicy: 'default',
});

// Strict — enterprise lockdown (443 only, explicit domain allowlist)
const guardian = new TorkGuardian({
  apiKey: 'tork_...',
  networkPolicy: 'strict',
});

// Custom — override any setting
const guardian = new TorkGuardian({
  apiKey: 'tork_...',
  networkPolicy: 'custom',
  allowedOutboundPorts: [443, 8443],
  allowedDomains: ['api.myservice.com'],
  maxConnectionsPerMinute: 30,
});
```

See [docs/NETWORK-SECURITY.md](docs/NETWORK-SECURITY.md) for full details on threat coverage, policy comparison, and compliance receipts.

## Example Configs

Pre-built configurations for common environments:

```typescript
import {
  MINIMAL_CONFIG,
  DEVELOPMENT_CONFIG,
  PRODUCTION_CONFIG,
  ENTERPRISE_CONFIG,
} from '@torknetwork/guardian';
```

| Config | Policy | Network | Description |
|--------|--------|---------|-------------|
| `MINIMAL_CONFIG` | standard | default | Just an API key, all defaults |
| `DEVELOPMENT_CONFIG` | minimal | default | Permissive policies, full logging |
| `PRODUCTION_CONFIG` | standard | default | Blocked exfil domains (pastebin, ngrok, burp) |
| `ENTERPRISE_CONFIG` | strict | strict | Explicit domain allowlist, 20 conn/min, TLS only |

```typescript
import { TorkGuardian, PRODUCTION_CONFIG } from '@torknetwork/guardian';

const guardian = new TorkGuardian({
  ...PRODUCTION_CONFIG,
  apiKey: process.env.TORK_API_KEY!,
});
```

## Configuration

```typescript
const guardian = new TorkGuardian({
  // Required
  apiKey: 'tork_...',

  // Optional
  baseUrl: 'https://www.tork.network',   // API endpoint
  policy: 'standard',                     // 'strict' | 'standard' | 'minimal'
  redactPII: true,                        // Enable PII redaction

  // Shell command governance
  blockShellCommands: [
    'rm -rf', 'mkfs', 'dd if=', 'chmod 777',
    'shutdown', 'reboot',
  ],

  // File access control
  allowedPaths: [],                        // Empty = allow all (except blocked)
  blockedPaths: [
    '.env', '.env.local', '~/.ssh',
    '~/.aws', 'credentials.json',
  ],

  // Network governance
  networkPolicy: 'default',               // 'default' | 'strict' | 'custom'
  allowedInboundPorts: [3000, 8080],       // Ports skills may bind to
  allowedOutboundPorts: [443],             // Ports for outbound connections
  allowedDomains: ['api.openai.com'],      // If non-empty, only these domains are allowed
  blockedDomains: ['evil.com'],            // Domains always blocked
  maxConnectionsPerMinute: 60,             // Per-skill egress rate limit
});
```

## Policies

| Policy | PII | Shell | Files | Network |
|--------|-----|-------|-------|---------|
| **strict** | Deny on detection | Block all | Whitelist only | Block all |
| **standard** | Redact | Block dangerous | Block sensitive | Allow |
| **minimal** | Redact | Allow all | Allow all | Allow all |

## Standalone Functions

```typescript
import { redactPII, generateReceipt, governToolCall } from '@torknetwork/guardian';

// Redact PII from text
const result = await redactPII('tork_...', 'Call 555-123-4567');

// Generate a compliance receipt
const receipt = await generateReceipt('tork_...', 'Processed user data');

// Check a tool call against policy
const decision = governToolCall(
  { name: 'file_write', args: { path: '.env' } },
  { policy: 'standard', blockedPaths: ['.env'] }
);
```

## Security Scanner

Scan any OpenClaw skill for vulnerabilities **before** installing it. The scanner checks for 14 security patterns across code and network categories.

### CLI

```bash
# Scan a skill directory
npx tork-scan ./my-skill

# Full details for every finding
npx tork-scan ./my-skill --verbose

# JSON output for CI/CD
npx tork-scan ./my-skill --json

# Fail on any high or critical finding
npx tork-scan ./my-skill --strict
```

### Programmatic

```typescript
import { SkillScanner, generateBadge } from '@torknetwork/guardian';

const scanner = new SkillScanner();
const report = await scanner.scanSkill('./my-skill');

console.log(`Risk: ${report.riskScore}/100`);
console.log(`Verdict: ${report.verdict}`); // 'verified' | 'reviewed' | 'flagged'
```

See [docs/SCANNER.md](docs/SCANNER.md) for the full rule reference, severity weights, and example output.

## Tork Verified Badges

Skills that pass the security scanner receive a Tork Verified badge:

| Badge | Score | Meaning |
|-------|-------|---------|
| **Tork Verified** (green) | 0 - 29 | Safe to install |
| **Tork Reviewed** (yellow) | 30 - 49 | Manual review recommended |
| **Tork Flagged** (red) | 50 - 100 | Security risks detected |

```typescript
import { SkillScanner, generateBadge, generateBadgeMarkdown } from '@torknetwork/guardian';

const scanner = new SkillScanner();
const report = await scanner.scanSkill('./my-skill');
const badge = generateBadge(report);

// Add to your README
console.log(generateBadgeMarkdown(badge));
```

## Get Your API Key

Sign up at [tork.network](https://tork.network) to get your API key.
