# Locations & Users API Reference

## Locations — `/locations/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/locations/{locationId}` | Get location details |
| PUT | `/locations/{locationId}` | Update location |
| GET | `/locations/search?companyId={id}` | Search locations (Agency) |
| POST | `/locations/` | Create sub-account (Agency) |
| DELETE | `/locations/{locationId}` | Delete sub-account (Agency) |
| GET | `/locations/timeZones` | List all time zones |

### Custom Fields CRUD
| Method | Path | Description |
|--------|------|-------------|
| GET | `/locations/{id}/customFields` | List custom fields |
| POST | `/locations/{id}/customFields` | Create custom field |
| PUT | `/locations/{id}/customFields/{fieldId}` | Update custom field |
| DELETE | `/locations/{id}/customFields/{fieldId}` | Delete custom field |

### Custom Values CRUD
| Method | Path | Description |
|--------|------|-------------|
| GET | `/locations/{id}/customValues` | List custom values |
| POST | `/locations/{id}/customValues` | Create custom value |
| PUT | `/locations/{id}/customValues/{valueId}` | Update custom value |
| DELETE | `/locations/{id}/customValues/{valueId}` | Delete custom value |

### Tags CRUD
| Method | Path | Description |
|--------|------|-------------|
| GET | `/locations/{id}/tags` | List tags |
| POST | `/locations/{id}/tags` | Create tag |
| PUT | `/locations/{id}/tags/{tagId}` | Update tag |
| DELETE | `/locations/{id}/tags/{tagId}` | Delete tag |

| GET | `/locations/{id}/templates` | List templates |
| GET | `/locations/{id}/tasks/search` | Search location tasks |

**Scopes**: `locations.readonly`, `locations.write` (Agency), `locations/customValues.*`, `locations/customFields.*`, `locations/tags.*`, `locations/templates.readonly`, `locations/tasks.readonly`

## Users — `/users/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/users/?locationId={id}` | List users |
| GET | `/users/{userId}` | Get user |
| POST | `/users/` | Create user |
| PUT | `/users/{userId}` | Update user |
| DELETE | `/users/{userId}` | Delete user |

**Filters**: companyId, email, status
**Note**: Agency users cannot be created via API

**Scopes**: `users.readonly`, `users.write`
