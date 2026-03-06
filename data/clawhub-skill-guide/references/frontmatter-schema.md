# Frontmatter Schema Reference

Complete documentation of every YAML frontmatter field supported by ClawHub.

> **Important:** The built-in `skill-creator` skill says "Do not include any
> other fields in YAML frontmatter." This is outdated. ClawHub supports all
> fields documented here, and the scanner checks several of them.

---

## Required Fields

### `name`

- **Type:** string
- **Required:** Yes
- **Rules:** Lowercase letters, digits, hyphens only. Under 64 characters.
- **Scanner check:** Must be present and valid.

```yaml
# Good
name: my-api-skill

# Bad — uppercase, spaces
name: My API Skill
```

### `description`

- **Type:** string (multi-line recommended)
- **Required:** Yes
- **Scanner check:** Must be present and substantive. Short or vague descriptions
  may trigger ℹ on PURPOSE & CAPABILITY.

The description serves as the primary trigger mechanism. Include:
- Concrete actions the skill performs
- Keywords users would use when they need this skill
- "Use when:" clause listing activation scenarios

```yaml
# Good
description: >
  Query and manage EVE Online market data, character skills, and
  corporation assets via the ESI API. Supports real-time price lookups,
  skill queue management, and asset inventory. Use when: checking EVE
  market prices, managing character skills, querying corporation data,
  working with EVE ESI endpoints.

# Bad — too vague, no trigger keywords
description: "Helps with EVE stuff."
```

---

## Environment Variable Fields

Three formats exist. All are recognized by the ClawHub registry scanner.

**Compatibility note:** The local packager (`package_skill.py`) only allows
these top-level keys: `name`, `description`, `license`, `metadata`, `allowed-tools`.
The direct `env:` key works when publishing directly with `npx clawhub publish`
but fails local `package_skill.py` validation. Use Format 2 or 3 (under `metadata`)
for full compatibility with both the local packager and the registry scanner.

### Format 1: `env` (Recommended)

- **Type:** array of objects
- **Required:** When the skill uses any credentials or configurable values
- **Scanner check:** PURPOSE & CAPABILITY and CREDENTIALS categories both verify
  that referenced env vars are declared here.

Each object supports:

| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `name` | string | — | Env var name (UPPER_SNAKE_CASE) |
| `description` | string | — | What this variable is for |
| `required` | boolean | false | Whether the skill fails without it |
| `sensitive` | boolean | false | Whether this is a secret/credential |

```yaml
# Real example: eve-esi skill pattern
env:
  - name: EVE_CLIENT_ID
    description: "EVE Developer Application Client ID"
    required: false
    sensitive: false
  - name: EVE_CLIENT_SECRET
    description: "EVE Developer Application Client Secret"
    required: false
    sensitive: true
  - name: EVE_TOKEN_MAIN
    description: "ESI OAuth2 access token for main character"
    required: false
    sensitive: true
```

**Tradeoffs:**
- Gives the scanner the `sensitive` flag (Format 2 and 3 lack this)
- Most explicit and readable
- **BUT** fails `package_skill.py` local validation (top-level `env:` not allowed)
- Works fine when publishing directly with `npx clawhub publish` (bypasses local packager)

### Format 2: `metadata.openclaw.env`

- **Type:** nested object → array
- **Scanner check:** Recognized as env declaration.

```yaml
# Real example: raon-os skill pattern
metadata:
  openclaw:
    env:
      - name: GEMINI_API_KEY
        description: "Google Gemini API key"
        required: false
```

Missing the `sensitive` field compared to Format 1. Use when you need to group
env declarations with other openclaw metadata.

### Format 3: `metadata.openclaw.requires`

- **Type:** nested object with `env` (string array), `bins` (string array), `primaryEnv` (string)
- **Scanner check:** Recognized, but provides least detail.

```yaml
# Real example: zen-founder-agent skill pattern
metadata:
  openclaw:
    requires:
      env:
        - ZEN_FOUNDER_AGENT_API_KEY
      bins:
        - curl
    primaryEnv: ZEN_FOUNDER_AGENT_API_KEY
```

This format only lists env var **names** — no descriptions or sensitivity flags.
Use when you also need to declare binary dependencies (`bins`).

### Combining Formats

You can use `env:` for detailed declarations and `metadata.openclaw.requires.bins`
for binary dependencies:

```yaml
env:
  - name: MY_API_KEY
    description: "API key for the service"
    required: true
    sensitive: true
metadata:
  openclaw:
    requires:
      bins:
        - curl
        - jq
    primaryEnv: MY_API_KEY
```

---

## Optional Fields

### `requires`

- **Type:** array of strings
- **Purpose:** Human-readable list of requirements, displayed to users.
- **Scanner check:** Checked against actual skill content for consistency.

```yaml
requires:
  - "Active account on Example service with API access"
  - "curl CLI tool installed"
  - "Node.js 18+ for script execution"
```

### `homepage`

- **Type:** string (URL)
- **Purpose:** Link to source code or documentation.

```yaml
homepage: "https://github.com/user/my-skill"
```

### `category`

- **Type:** string
- **Purpose:** Categorize the skill in ClawHub listings.

```yaml
category: "developer-tools"
```

### `emoji`

- **Type:** string (single emoji)
- **Purpose:** Display icon in ClawHub listings.

```yaml
emoji: "🔧"
```

### `version`

- **Type:** string (semver)
- **Purpose:** Version in frontmatter. Can also be set via `--version` flag on publish.
- **Note:** The CLI `--version` flag takes precedence if both are set.

```yaml
version: "1.2.0"
```

---

## Scanner Impact by Field

| Field | Scanner Category | Impact |
|-------|-----------------|--------|
| `name` | All | Must be present |
| `description` | PURPOSE & CAPABILITY | Must match actual functionality |
| `env` | CREDENTIALS, PURPOSE | All used credentials must be declared |
| `env[].sensitive` | CREDENTIALS | Secrets must be flagged |
| `metadata.openclaw.requires.bins` | INSTALL MECHANISM | Declared tools validated |
| `requires` | PURPOSE & CAPABILITY | Checked against skill content |

---

## Complete Example

A well-structured frontmatter covering all common fields:

```yaml
---
name: example-api-manager
description: >
  Manage Example API resources including users, projects, and billing.
  Query data, generate reports, and monitor usage with full CRUD support.
  Use when: querying Example API, generating usage reports, managing
  API projects, checking billing, creating API resources, monitoring
  service health.
env:
  - name: EXAMPLE_API_KEY
    description: "API key from Example dashboard (Settings → API Keys)"
    required: true
    sensitive: true
  - name: EXAMPLE_ORG_ID
    description: "Organization ID (visible in account settings)"
    required: false
    sensitive: false
requires:
  - "Example API account with admin access"
  - "curl CLI tool"
homepage: "https://github.com/example/example-api-manager"
category: "api-integrations"
emoji: "🔌"
---
```

---

## Anti-Patterns

### Missing env declarations

```yaml
# BAD — skill body references OPENAI_API_KEY but frontmatter doesn't declare it
---
name: my-skill
description: "Uses AI to analyze text."
---
# Result: ! on CREDENTIALS
```

### Overly broad description

```yaml
# BAD — description doesn't match actual narrow functionality
---
name: pdf-rotate
description: >
  Complete PDF suite for all document operations including editing,
  signing, encrypting, converting, and managing PDFs.
---
# Result: ℹ on PURPOSE & CAPABILITY (description overpromises)
```

### Inline JSON metadata

```yaml
# WORKS but hard to read and maintain
metadata: {"openclaw":{"requires":{"env":["MY_KEY"],"bins":["curl"]},"primaryEnv":"MY_KEY"}}
```

Prefer expanded YAML:

```yaml
metadata:
  openclaw:
    requires:
      env:
        - MY_KEY
      bins:
        - curl
    primaryEnv: MY_KEY
```
