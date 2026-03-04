---
name: Storage
description: Choose and architect storage systems for applications with the right tradeoffs.
metadata: {"clawdbot":{"emoji":"💾","os":["linux","darwin","win32"]}}
---

## Object vs Block vs File

- Object storage (S3, R2, GCS) for immutable blobs: images, videos, backups, logs — cheap, scales infinitely, but no partial updates
- Block storage (EBS, Persistent Disks) for databases and apps needing filesystem semantics — faster, but tied to single instance
- Network file systems (NFS, EFS) when multiple instances need shared filesystem access — convenient but latency and cost add up
- Default to object storage for user uploads — block storage for database files only

## When SQL vs NoSQL

- SQL when you need joins, transactions, or complex queries — fighting against NoSQL for relational data wastes months
- Document stores (MongoDB, Firestore) for nested/variable schemas where you always fetch the whole document
- Key-value (Redis, DynamoDB) for simple lookups by ID at massive scale — not for complex queries
- Time-series databases (InfluxDB, TimescaleDB) for metrics with timestamp-based queries — regular SQL struggles with retention policies
- Start with PostgreSQL unless you have a specific reason not to — it handles JSON, full-text search, and scales further than most assume

## Local vs Cloud Storage

- Local disk for ephemeral data: temp files, build artifacts, caches — assume it disappears on restart
- Cloud storage for anything that must survive instance termination — never store user data only on local disk
- Local SSD for databases in production — network-attached storage adds latency to every query
- Hybrid: local cache in front of cloud storage for frequently accessed files

## CDN Patterns

- Put CDN in front of static assets always — origin requests are slower and more expensive
- Set long cache TTLs with versioned URLs (`style.abc123.css`) — cache invalidation is slow and unreliable
- CDN for dynamic content only if latency matters more than freshness — adds complexity for marginal gains
- Edge caching for API responses works but cache keys get tricky — start simple, add only when needed

## Upload Handling

- Never accept uploads directly to app server disk in production — use presigned URLs to cloud storage
- Set file size limits at load balancer level, not just application — prevents memory exhaustion attacks
- Generate unique keys for uploads (UUIDs) — user-provided filenames cause collisions and path traversal risks
- Validate file types by content (magic bytes), not extension — extensions are trivially spoofed

## Data Locality

- Keep compute and storage in same region — cross-region data transfer adds latency and cost
- Replicate data to regions where users are, not where developers are
- Multi-region storage adds complexity — single region with backups elsewhere usually sufficient
- Database read replicas in user regions for read-heavy workloads

## Retention and Lifecycle

- Define retention policy before storing data — "keep everything" becomes expensive and legally risky
- Automate deletion of temporary data — manual cleanup never happens consistently
- Tiered storage for aging data: hot → warm → cold → archive — but check retrieval costs before archiving
- Separate storage for logs vs business data — different retention, different compliance requirements

## Cost Traps

- Egress fees dominate cloud storage costs — calculate before choosing provider
- Many small files cost more than few large files — batch small writes when possible
- Minimum storage duration on cold tiers — early deletion still charges full period
- API request costs matter at scale — millions of LIST operations add up

## Backup Strategy

- 3-2-1 rule: 3 copies, 2 different media types, 1 offsite — cloud counts as one location
- Test restores regularly — untested backups are not backups
- Point-in-time recovery for databases — daily snapshots lose a day of data
- Version important files — deletion or corruption often discovered late
