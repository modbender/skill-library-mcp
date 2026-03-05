# Service Catalog Template

Use this model to keep service ownership and risk visible.

## Required Fields

- Service name and business purpose
- Runtime (container, VM, host process)
- Data location and backup owner
- Exposure level: LAN-only, VPN-only, or internet-facing
- Authentication boundary and admin URL policy
- Health check source and alert destination

## Lightweight Table

| Service | Runtime | Data Path | Exposure | Backup | Health Check |
|---------|---------|-----------|----------|--------|--------------|
| Example: nextcloud | docker | /srv/nextcloud | VPN-only | nightly snapshot | uptime probe |

## Ownership Rules

- Every service has a primary owner and fallback owner.
- Every internet-facing service has a documented reverse proxy route.
- Every stateful service has restore instructions linked in incident notes.

## Review Cadence

- Weekly: health and disk trend review
- Monthly: patch level and certificate expiry review
- Quarterly: restore drill and dependency refresh
