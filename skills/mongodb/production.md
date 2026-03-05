# Production Configuration

## Before Going to Production

- Test with production-like data volume—aggregations behave differently at scale
- Enable profiling for slow queries—catch problems early
- Set up monitoring: connections, replication lag, disk space, index usage
- Plan sharding strategy before you need it—resharding is painful

## Write Concern

- Default `w: 1` acknowledges primary only—data could be lost if primary fails
- `w: "majority"` waits for majority of replicas—durable but slower
- `j: true` waits for journal flush—most durable, slowest
- Match write concern to data importance—not everything needs majority

## Read Concern

- Default may read uncommitted data—"dirty reads" possible
- `readConcern: "majority"` only reads committed data—safe
- `readConcern: "linearizable"` strongest—but slow and availability issues
- Combine with read preference for full consistency strategy

## Read Preference

- `primary` = always read from primary—consistent but all load on one node
- `primaryPreferred` = primary unless unavailable—slight risk of stale
- `secondary` = read from secondaries—scales reads but stale data
- `nearest` = lowest latency—may be stale, may vary between requests

## Connection Management

- Use connection pool—creating connections is expensive
- Default pool size often too small—tune `maxPoolSize` based on load
- Set appropriate timeouts—`serverSelectionTimeoutMS`, `socketTimeoutMS`
- `retryWrites: true`—handles transient failures automatically

## Replica Set Operations

- Always connect to replica set URI, not individual nodes—automatic failover
- Monitor replication lag: `rs.printReplicationInfo()`
- Test failover in staging—know what happens before production emergency
- Secondary reads: understand that data may be seconds/minutes stale

## Sharding Considerations

- Choose shard key carefully—can't change it easily
- High cardinality key—many possible values
- Even distribution—avoid "hot" shards
- Write distribution matters more than read—reads can be scattered

## Backup Strategy

- `mongodump` for logical backup—portable but slow on large data
- Filesystem snapshots for large databases—faster but requires consistency
- Ops Manager/Cloud Manager for managed backups
- Point-in-time recovery needs oplog—enable with `--oplogReplay`

## Monitoring Essentials

- Connections: current vs available—hitting limit = operations queue
- Replication lag: `rs.printReplicationInfo()`—if growing, investigate
- Disk space: MongoDB doesn't shrink files—plan for growth
- Query performance: enable profiler, review slow queries
- Lock percentage: high lock wait = contention issues
