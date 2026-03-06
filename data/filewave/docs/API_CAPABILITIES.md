# API Capabilities & Endpoints

This document maps documented CLI features to their corresponding FileWave API endpoints.

## Core API Endpoints

- `GET /api/inv/api/v1/query_result/{query_id}` — Inventory Query (Main data source for large fleet lists)
- `GET /filewave/api/devices/v1/devices/{id}` — Device details (Original records)
- `PATCH /filewave/api/devices/v1/devices/{id}` — Update device metadata (Name, Auth Username)
- `GET /filewave/api/devices/internal/devices` — Hierarchical listing and recursive search
- `GET /filewave/api/devices/internal/devices/{id}/groups` — Group membership lookup
- `GET /filewave/api/devices/internal/devices/{id}/details/hardware/fields` — Hardware-level identification
- `POST /filewave/api/fwserver/update_model` — Refresh model

## Discovery & Discovery Logic

The skill uses the internal Discovery API (same as Web Admin) for comprehensive fleet searches and "type-aware" counting.

### Authoritative Hardware Identification

When querying for specific types (e.g., "Find all iPads"), the skill does not rely solely on name matches. It queries the internal devices endpoint with specific `search_fields` to retrieve:

`invf_Client_device_product_name`

**Example mappings:**
- Returns "iPad" → Classified as **iPad**
- Returns "iPhone" → Classified as **iPhone**
- Returns "MacBookPro18,3" → Classified as **Mac**

### Recursive Traversal

For servers where "Smart Groups" (like "All iOS") have not yet been created, the skill performs a depth-limited recursive traversal:

1. List root-level groups via `/filewave/api/devices/internal/devices`
2. Iterate through groups with `has_children: true`
3. Identify devices vs. sub-groups
4. Flatten the hierarchy into a unified list of unique device records

## Bulk Operations

### Model Refresh
After any `PATCH` operation to device metadata, a `POST` to `/filewave/api/fwserver/update_model` is required for the changes to take effect in the FileWave database and push to clients.

## Fleet Analytics

### Module: `lib/device_analytics.py`

Provides fleet-wide analytics by processing Inventory Query results. All operations are read-only.

| Class | Purpose |
|-------|---------|
| `PlatformBreakdown` | Aggregates devices by OS platform and version. Classifies using `OperatingSystem_name` and extracts macOS codenames (Sonoma, Sequoia, Tahoe, etc.) |
| `StaleDeviceReport` | Identifies devices not seen in N days via `Client_last_connected_to_fwxserver`. Handles ISO 8601 timestamps with timezone awareness. Configurable threshold (default: 30 days) |
| `DeviceInsights` | High-level runner. Accepts raw API response or pre-parsed dicts. Methods: `.platform_breakdown()`, `.stale_report(threshold_days)`, `.field_summary(field)` |

### Helper Functions

- `classify_platform(os_name)` — Maps OS name string to canonical platform
- `parse_os_version(os_name, os_version)` — Extracts human-friendly version label
- `rows_to_dicts(fields, values)` — Converts FileWave column-oriented response to list of dicts

## Performance & Caching

The skill implements a multi-layer caching and optimization strategy:

- **7-Day TTL Cache:** Stores `Device ID`, `Serial Number`, `Device UID`, and `Group` mappings.
- **Dual-Index Caching:** Caches are keyed by both `Device Name` and `Numeric ID` for instant lookups regardless of source.
- **Parallel Fetching:** Search operations use `ThreadPoolExecutor` to fetch device details concurrently, reducing the N+1 query penalty by up to 2x.
- **Proactive Cache Warming:** The `warm-cache` command leverages platform smart groups to index the entire fleet in parallel typically in < 5 seconds.
- **Self-Healing:** Cache automatically clears on API errors to prevent stale data.
