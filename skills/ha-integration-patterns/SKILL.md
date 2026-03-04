---
name: ha-integration-patterns
description: Home Assistant custom integration patterns and architectural decisions. Use when building HACS integrations, custom components, or API bridges for Home Assistant. Covers service response data, HTTP views, storage APIs, and integration architecture.
---

# Home Assistant Integration Patterns

## Service Response Data Pattern

### The Problem
By default, HA services are "fire-and-forget" and return empty arrays `[]`.

### The Solution (HA 2023.7+)
Register service with `supports_response`:

```python
from homeassistant.helpers.service import SupportsResponse

hass.services.async_register(
    domain, 
    "get_full_config", 
    handle_get_full_config,
    schema=GET_CONFIG_SCHEMA,
    supports_response=SupportsResponse.ONLY,  # ← KEY PARAMETER
)
```

Call with `?return_response` flag:
```bash
curl -X POST "$HA_URL/api/services/your_domain/get_full_config?return_response"
```

### Response Handler
```python
async def handle_get_full_config(hass: HomeAssistant, call: ServiceCall):
    """Handle the service call and return data."""
    # ... your logic ...
    return {"entities": entity_data, "automations": automation_data}
```

---

## HTTP View vs Service: When to Use Each

| Use Case | Use | Don't Use |
|----------|-----|-----------|
| Return complex data | HTTP View | Service (without response support) |
| Fire-and-forget actions | Service | HTTP View |
| Trigger automations | Service | HTTP View |
| Query state/config | HTTP View | Internal storage APIs |

### HTTP View Pattern
For data retrieval APIs:

```python
from homeassistant.components.http import HomeAssistantView

class OpenClawConfigView(HomeAssistantView):
    """HTTP view for retrieving config."""
    url = "/api/openclaw/config"
    name = "api:openclaw:config"
    requires_auth = True

    async def get(self, request):
        hass = request.app["hass"]
        config = await get_config_data(hass)
        return json_response(config)

# Register in async_setup:
hass.http.register_view(OpenClawConfigView())
```

---

## Critical: Avoid Internal APIs

**Never use underscore-prefixed APIs** — they're private and change between versions.

❌ **Wrong:**
```python
storage_collection = hass.data["_storage_collection"]
```

✅ **Right:**
```python
# Use public APIs only
from homeassistant.helpers.storage import Store
store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
```

---

## Storage Patterns

### For Small Data (Settings, Cache)
```python
from homeassistant.helpers.storage import Store

STORAGE_KEY = "your_domain.storage"
STORAGE_VERSION = 1

store = Store(hass, STORAGE_VERSION, STORAGE_KEY)

# Save
data = {"entities": modified_entities}
await store.async_save(data)

# Load
data = await store.async_load()
```

### For Large Data (History, Logs)
Use external database or file storage, not HA storage helpers.

---

## Breaking Changes to Watch

| Change | Version | Migration |
|--------|---------|-----------|
| Conversation agents | 2025.x+ | Use `async_process` directly |
| Service response data | 2023.7+ | Add `supports_response` param |
| Config entry migration | 2022.x+ | Use `async_migrate_entry` |

**Always check:** https://www.home-assistant.io/blog/ for your target version range.

---

## HACS Integration Structure

```
custom_components/your_domain/
├── __init__.py          # async_setup_entry
├── config_flow.py       # UI configuration
├── manifest.json        # Dependencies, version
├── services.yaml        # Service definitions
└── storage_services.py  # Your storage logic
```

### Minimal manifest.json
```json
{
  "domain": "your_domain",
  "name": "Your Integration",
  "codeowners": ["@yourusername"],
  "config_flow": true,
  "dependencies": [],
  "requirements": [],
  "version": "1.0.0"
}
```

---

## Testing Checklist

- [ ] Service calls return expected data (with `?return_response`)
- [ ] HTTP views accessible with auth token
- [ ] No underscore-prefixed API usage
- [ ] Storage persists across restarts
- [ ] Config flow creates config entry
- [ ] Error handling returns meaningful messages

---

## Documentation Resources

- Integration basics: `developers.home-assistant.io/docs/creating_integration_index`
- Service calls: `developers.home-assistant.io/docs/dev_101_services`
- HTTP views: `developers.home-assistant.io/docs/api/webserver`
- Breaking changes: `home-assistant.io/blog/` (filter by version)
- HACS guidelines: `hacs.xyz/docs/publish/start`

---

## Lesson Learned

From HA-OpenClaw Bridge attempt:

> *"80% of our issues were discoverable with 30-60 minutes of upfront docs reading. We jumped straight to coding based on assumptions rather than reading how HA actually works."*

Use `skills/pre-coding-research/` methodology before starting.
