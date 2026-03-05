# Pi-hole Database Schema (pihole-FTL.db)

## Tables
- **queries**: Main log table.
  - `timestamp`: Unix timestamp
  - `domain`: Domain requested
  - `status`: 1=Blocked, 2=Allowed, 3=Allowed (Cache)
  - `client`: IP/Name of requestor

- **network**: Device discovery.
  - `hwaddr`: MAC Address
  - `name`: Hostname
  - `firstSeen`, `lastQuery`

## CLI Tools (`pihole`)
- `pihole -g`: Update Gravity (blocklists).
- `pihole -w <domain>`: Whitelist domain.
- `pihole -b <domain>`: Blacklist domain.
- `pihole status`: Check FTL service.
