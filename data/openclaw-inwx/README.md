# openclaw-inwx

OpenClaw plugin for INWX (InterNetworX) domain registrar automation.

It provides 23 tools for domain lifecycle operations, DNS management, DNSSEC, contact handling, WHOIS, and account checks.

## Features

- INWX DomRobot JSON-RPC integration via `domrobot-client`
- Environment switch: `production` or `ote`
- Optional 2FA login support (`otpSecret`)
- Safety controls:
  - `readOnly` blocks all write tools
  - `allowedOperations` allowlist for tool-level policy
- TypeScript strict mode

## Installation

```bash
npm install @elvatis_com/openclaw-inwx
```

For local development:

```bash
npm install
npm run build
npm test
```

## INWX Account Setup

1. Create or use your INWX account.
2. Enable API access in INWX account settings.
3. If 2FA is enabled, provide a shared secret via `otpSecret`.
4. For safe testing, use OTE environment (`ote.inwx.com`).

## Plugin Config

```json
{
  "username": "your-inwx-user",
  "password": "your-inwx-password",
  "otpSecret": "optional-2fa-secret",
  "environment": "ote",
  "readOnly": false,
  "allowedOperations": []
}
```

## Tool List

### Read Tools

1. `inwx_domain_check`
   - INWX method: `domain.check`
   - Params: `domain` (string)
2. `inwx_domain_list`
   - INWX method: `domain.list`
   - Params: optional filters (object)
3. `inwx_domain_info`
   - INWX method: `domain.info`
   - Params: `domain` (string)
4. `inwx_domain_pricing`
   - INWX method: `domain.check`
   - Params: `domain` (string) or `domains` (string[])
5. `inwx_nameserver_list`
   - INWX method: `nameserver.list` or `domain.info`
   - Params: optional `domain`
6. `inwx_dns_record_list`
   - INWX method: `nameserver.info`
   - Params: `domain` (string)
7. `inwx_dnssec_list`
   - INWX method: `dnssec.info`
   - Params: optional filters
8. `inwx_contact_list`
   - INWX method: `contact.list`
   - Params: optional filters
9. `inwx_whois`
   - INWX method: `domain.whois`
   - Params: `domain` (string)
10. `inwx_account_info`
    - INWX method: `account.info`
    - Params: none

### Write Tools

11. `inwx_domain_register`
    - INWX method: `domain.create`
    - Params: `domain`, `period`, `contacts`, `ns`
12. `inwx_domain_update`
    - INWX method: `domain.update`
    - Params: method payload
13. `inwx_domain_delete`
    - INWX method: `domain.delete`
    - Params: method payload
14. `inwx_domain_transfer`
    - INWX method: `domain.transfer`
    - Params: method payload
15. `inwx_domain_renew`
    - INWX method: `domain.renew`
    - Params: method payload
16. `inwx_nameserver_set`
    - INWX method: `domain.update`
    - Params: `domain`, `ns` (string[])
17. `inwx_dns_record_add`
    - INWX method: `nameserver.createRecord`
    - Params: method payload
18. `inwx_dns_record_update`
    - INWX method: `nameserver.updateRecord`
    - Params: method payload
19. `inwx_dns_record_delete`
    - INWX method: `nameserver.deleteRecord`
    - Params: method payload
20. `inwx_dnssec_enable`
    - INWX method: `dnssec.create`
    - Params: method payload
21. `inwx_dnssec_disable`
    - INWX method: `dnssec.delete`
    - Params: method payload
22. `inwx_contact_create`
    - INWX method: `contact.create`
    - Params: method payload
23. `inwx_contact_update`
    - INWX method: `contact.update`
    - Params: method payload

## OTE Test Environment

Set:

```json
{ "environment": "ote" }
```

This points the client to INWX OTE API endpoint and allows free integration testing without production costs.

## Integration with openclaw-ispconfig

This plugin exports a `provisionDomainWithHosting` function that orchestrates both openclaw-inwx and openclaw-ispconfig into a single domain-to-hosting provisioning workflow. No hard npm dependency on openclaw-ispconfig is required - the function accepts both toolsets via dependency injection.

### Provisioning workflow steps

1. **Domain check** - verify availability via `inwx_domain_check`
2. **Domain register** - register via `inwx_domain_register` (skipped if already taken or `skipRegistration=true`)
3. **Nameserver set** - configure nameservers via `inwx_nameserver_set`
4. **Hosting provision** - create site, DNS zone, mail, and database via `isp_provision_site`

### Usage

```typescript
import { buildToolset, provisionDomainWithHosting } from "@elvatis_com/openclaw-inwx";
import ispPlugin from "@elvatis_com/openclaw-ispconfig";

const inwxTools = buildToolset({
  username: "inwx-user",
  password: "inwx-pass",
  environment: "ote",
});

const ispTools = ispPlugin.buildToolset({
  apiUrl: "https://ispconfig.example.com:8080/remote/json.php",
  username: "api-user",
  password: "api-pass",
  serverId: 1,
  defaultServerIp: "1.2.3.4",
});

const result = await provisionDomainWithHosting(inwxTools, ispTools, {
  domain: "example.com",
  nameservers: ["ns1.hosting.de", "ns2.hosting.de"],
  serverIp: "1.2.3.4",
  clientName: "Acme Corp",
  clientEmail: "admin@acme.com",
  createMail: true,
  createDb: true,
});

console.log(result.ok);     // true if all steps succeeded
console.log(result.steps);  // per-step status tracking
console.log(result.created); // summary of what was created
```

### Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| domain | string | yes | - | Domain to register and provision |
| nameservers | string[] | yes | - | Nameservers to set on the domain |
| serverIp | string | yes | - | Hosting server IP (for ISPConfig A record) |
| clientName | string | yes | - | ISPConfig client name |
| clientEmail | string | yes | - | ISPConfig client email |
| createMail | boolean | no | true | Create mail domain and mailboxes |
| createDb | boolean | no | true | Create database and user |
| serverId | number | no | config default | ISPConfig server ID |
| registrationPeriod | number | no | 1 | Domain registration period in years |
| contacts | object | no | - | INWX contact IDs for registration |
| skipRegistration | boolean | no | false | Skip domain registration step |

### Result structure

```typescript
{
  ok: boolean;            // true if all steps succeeded
  domain: string;
  steps: Array<{
    step: string;         // "domain_check" | "domain_register" | "nameserver_set" | "isp_provision"
    status: "ok" | "error" | "skipped";
    data?: unknown;
    error?: string;
  }>;
  created: {
    domainRegistered?: boolean;
    nameserversConfigured?: boolean;
    hostingProvisioned?: boolean;
    ispProvisionResult?: unknown;
  };
}
```

## Safety

- `readOnly=true` allows only:
  - domain check/list/info/pricing
  - nameserver list
  - dns record list
  - dnssec list
  - contact list
  - whois
  - account info
- `allowedOperations` can restrict to explicit tool names.

## Testing

### Unit tests

```bash
npm test
```

Unit tests use mocks only and require no credentials.

### OTE integration tests

Integration tests run against the INWX OTE sandbox (`ote.inwx.com`). OTE is safe - no real billing, no production impact.

```bash
# Set OTE credentials
export INWX_OTE_USERNAME="your-ote-user"
export INWX_OTE_PASSWORD="your-ote-pass"
export INWX_OTE_OTP="optional-2fa-secret"

# Run OTE tests
npm run test:ote
```

Without credentials set, the OTE suite is automatically skipped.

**Test coverage:**
- Client authentication and session management
- All read tools (account info, domain check/list/pricing, contacts)
- Guard enforcement (readOnly, allowedOperations) on live connection
- Input validation (empty/missing required params)
- API error handling (invalid credentials)
- Full buildToolset round-trip against OTE
