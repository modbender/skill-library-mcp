---
name: DynamoDB
description: Design DynamoDB tables and write efficient queries avoiding common NoSQL pitfalls.
metadata: {"clawdbot":{"emoji":"⚡","requires":{"anyBins":["aws"]},"os":["linux","darwin","win32"]}}
---

## Key Design

- Partition key determines data distribution—high-cardinality keys spread load evenly
- Hot partition = one key gets all traffic—use composite keys or add random suffix
- Sort key enables range queries within partition—design for access patterns
- Can't change keys after creation—model all access patterns before creating table

## Query vs Scan

- Query uses partition key + optional sort key—O(items in partition), always prefer
- Scan reads entire table—expensive, slow, avoids indexes; almost never correct
- "I need to filter by X" usually means missing GSI—add index, don't scan
- FilterExpression applies AFTER read—still consumes full read capacity

## Global Secondary Indexes

- GSI = different partition/sort key—enables alternate access patterns
- GSI is eventually consistent—writes propagate with slight delay
- GSI consumes separate capacity—provision or pay for each GSI independently
- Sparse index trick: only items with attribute appear in GSI

## Single-Table Design

- One table for multiple entity types—prefix partition key: `USER#123`, `ORDER#456`
- Overloaded sort key: `METADATA`, `ORDER#2024-01-15`, `ITEM#abc`
- Query returns mixed types—filter client-side or use begins_with
- Not always right—start with access patterns, not doctrine

## Pagination

- Results capped at 1MB per request—must handle pagination
- `LastEvaluatedKey` in response means more pages—pass as `ExclusiveStartKey`
- Loop until `LastEvaluatedKey` is absent—common mistake: assume one call gets all
- `Limit` limits evaluated items, not returned—still need pagination logic

## Consistency

- Reads are eventually consistent by default—may return stale data
- `ConsistentRead: true` for strong consistency—costs 2x read capacity
- GSI reads always eventually consistent—no strong consistency option
- Write-then-read needs consistent read or retry—eventual consistency bites here

## Conditional Writes

- `ConditionExpression` for optimistic locking—fails if condition false
- Prevent overwrites: `attribute_not_exists(pk)`
- Version check: `version = :expected` then increment
- ConditionCheckFailedException = retry with fresh data, don't just fail

## Batch Operations

- `BatchWriteItem` is NOT atomic—partial success possible, check UnprocessedItems
- Retry unprocessed with exponential backoff—built into AWS SDK
- Max 25 items per batch, 16MB total—split larger batches
- No conditional writes in batch—use TransactWriteItems for atomicity

## Transactions

- `TransactWriteItems` for atomic multi-item writes—all or nothing
- Max 100 items per transaction, 4MB total
- TransactGetItems for consistent multi-read—snapshot isolation
- 2x cost of normal operations—use only when atomicity required

## TTL

- Enable TTL on timestamp attribute—DynamoDB deletes expired items automatically
- Deletion is background process—items may persist hours after expiration
- TTL value is Unix epoch seconds—milliseconds silently fails
- Filter `attribute_exists(ttl) AND ttl > :now` for queries if needed

## Capacity

- On-demand: pay per request, auto-scales—good for unpredictable traffic
- Provisioned: set RCU/WCU, cheaper at scale—needs capacity planning
- Provisioned with auto-scaling for predictable patterns—set min/max/target
- ProvisionedThroughputExceededException = throttled—back off and retry

## Limits

- Item size max 400KB—store large objects in S3, reference in DynamoDB
- Partition throughput: 3000 RCU, 1000 WCU—spread across partitions
- Query/Scan returns max 1MB—pagination required for more
- Attribute name max 64KB total per item—don't use long attribute names
