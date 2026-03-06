# GTM API v2 — Quick Reference

Base URL: `https://tagmanager.googleapis.com/tagmanager/v2`

## Resource Hierarchy

```
Account
└── Container
    ├── Workspace (mutable draft)
    │   ├── Tags
    │   ├── Triggers
    │   ├── Variables
    │   ├── Built-in Variables
    │   ├── Folders
    │   ├── Templates
    │   ├── Clients (server-side)
    │   └── Zones
    ├── Versions (immutable snapshots)
    ├── Version Headers (lightweight list)
    ├── Environments (preview/staging)
    └── Destinations
```

## Path Format

All resources use path-based addressing:
- Account: `accounts/{accountId}`
- Container: `accounts/{accountId}/containers/{containerId}`
- Workspace: `accounts/{accountId}/containers/{containerId}/workspaces/{workspaceId}`
- Tag: `...workspaces/{workspaceId}/tags/{tagId}`

## Tag Resource

Key fields:
- `name` (string) — Display name
- `type` (string) — Tag type code (see below)
- `parameter[]` — Array of Parameter objects
- `firingTriggerId[]` — Trigger IDs that fire this tag
- `blockingTriggerId[]` — Trigger IDs that block this tag
- `paused` (boolean) — If true, tag won't fire
- `tagFiringOption` — `unlimited` | `oncePerEvent` | `oncePerLoad`
- `consentSettings` — Consent mode configuration

### Common Tag Types

| Type | Tag |
|------|-----|
| `awct` | Google Ads Conversion Tracking |
| `sp` | Google Ads Remarketing |
| `gclidw` | Conversion Linker |
| `gaawc` | GA4 Configuration |
| `gaawe` | GA4 Event |
| `html` | Custom HTML |
| `img` | Custom Image (pixel) |
| `flc` | Floodlight Counter |
| `fls` | Floodlight Sales |

## Trigger Resource

Key fields:
- `name` (string) — Display name
- `type` (EventType) — Trigger type
- `customEventFilter[]` — Conditions for custom events
- `filter[]` — General filter conditions
- `autoEventFilter[]` — Auto-event tracking conditions
- `eventName` — Timer event name

### Trigger Types (EventType)

| Type | Description |
|------|-------------|
| `pageview` | Page View |
| `domReady` | DOM Ready |
| `windowLoaded` | Window Loaded |
| `customEvent` | Custom Event (dataLayer) |
| `click` | All Element Clicks |
| `linkClick` | Just Links |
| `formSubmission` | Form Submission |
| `timer` | Timer |
| `scrollDepth` | Scroll Depth |
| `elementVisibility` | Element Visibility |
| `youTubeVideo` | YouTube Video |
| `historyChange` | History Change |
| `jsError` | JavaScript Error |
| `triggerGroup` | Trigger Group |

### Condition Operators

Used in `customEventFilter`, `filter`, `autoEventFilter`:

| Type | Meaning |
|------|---------|
| `equals` | Equals |
| `contains` | Contains |
| `startsWith` | Starts with |
| `endsWith` | Ends with |
| `matchRegex` | Matches regex |
| `greater` | Greater than |
| `greaterOrEquals` | Greater than or equals |
| `less` | Less than |
| `lessOrEquals` | Less than or equals |
| `cssSelector` | CSS selector match |

## Variable Resource

Key fields:
- `name` (string) — Display name
- `type` (string) — Variable type code
- `parameter[]` — Configuration parameters

### Common Variable Types

| Type | Variable |
|------|----------|
| `v` | Data Layer Variable |
| `jsm` | Custom JavaScript |
| `k` | 1st Party Cookie |
| `u` | URL |
| `c` | Constant |
| `r` | HTTP Referrer |
| `gas` | Google Analytics Settings |
| `remm` | Regex Table |
| `smm` | Lookup Table |

## Parameter Object

All tag/trigger/variable configuration uses Parameter objects:

```json
{
  "type": "TEMPLATE|INTEGER|BOOLEAN|LIST|MAP",
  "key": "parameterName",
  "value": "parameterValue",
  "list": [...],  // for LIST type
  "map": [...]    // for MAP type
}
```

## Version Workflow

1. Make changes in a **Workspace**
2. `create_version` — snapshots workspace into immutable Version, deletes workspace
3. `publish` — makes a Version the live version

## OAuth2 Scopes

| Scope | Access |
|-------|--------|
| `tagmanager.readonly` | Read-only access |
| `tagmanager.edit.containers` | Read + write tags/triggers/variables |
| `tagmanager.publish` | Publish versions |
| `tagmanager.manage.accounts` | Account management |
| `tagmanager.manage.users` | User permissions |
| `tagmanager.edit.containerversions` | Edit versions |

## Rate Limits

- 2000 requests per project per 100 seconds
- 100 requests per user per 100 seconds
