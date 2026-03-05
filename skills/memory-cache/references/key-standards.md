# Redis Key Naming Standards

## Core Namespace: `mema:`

### 1. Ephemeral Context (Short-Term Memory)
- **Prefix**: `mema:context:`
- **Purpose**: Store conversation state, recent tool outputs, or temporary reasoning buffers.
- **TTL**: 1-24 hours.
- **Examples**:
  - `mema:context:summary` (Current active context summary)
  - `mema:context:last_search` (Last search results)

### 2. Task Queues
- **Prefix**: `mema:queue:`
- **Purpose**: Managing background tasks or agent handoffs.
- **Structure**: Lists or Streams.
- **Examples**:
  - `mema:queue:pending_reports`
  - `mema:queue:notifications`

### 3. Application State (Persistent)
- **Prefix**: `mema:state:`
- **Purpose**: Long-term configuration or state flags.
- **TTL**: None (Persistent).
- **Examples**:
  - `mema:state:maintenance_mode` (1/0)
  - `mema:state:last_backup_ts`

### 4. Cache (External Data)
- **Prefix**: `mema:cache:`
- **Purpose**: Cached API responses (Google, Wiki, etc.).
- **TTL**: 24h - 7 days.
- **Examples**:
  - `mema:cache:search:<hash>`
  - `mema:cache:rss:<feed_id>`

## Best Practices
1.  **Colon Separators**: Always use `:` to separate hierarchy.
2.  **Snake Case**: Use `snake_case` for segments.
3.  **Deterministic**: Key names should be predictable (e.g., using hashes of inputs).
