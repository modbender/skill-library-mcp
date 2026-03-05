# Schema Design Patterns

## Embedding vs Referencing Decision

- Embed for 1:1 and 1:few relationships—data always accessed together
- Reference for 1:many and many:many—data accessed independently
- Embed when child doesn't exist without parent—natural containment
- Reference when entity is shared across multiple parents—avoid duplication

## Embedding Advantages

- Single read gets all data—no additional queries
- Atomic updates on single document—no transactions needed
- Data locality—related data physically together on disk
- Simpler application code—no manual joining

## Embedding Dangers

- Document growth causes relocation—performance hit on updates
- 16MB limit approached gradually then suddenly—plan ahead
- Duplicated embedded data becomes stale—update complexity
- Can't query embedded documents independently

## Referencing Patterns

- Store `_id` of related document—manual lookup required
- Use `$lookup` for server-side join—but has performance cost
- Denormalize frequently accessed fields—store name WITH reference
- Accept eventual consistency of denormalized copies

## Bucketing Pattern

- Instead of array per document, create fixed-size buckets
- Example: `{sensor_id, date, readings: [...], count: 50}`
- When count reaches limit, create new bucket document
- Great for time-series, IoT, logs—predictable document size

## Attribute Pattern

- Many similar optional fields → hard to index all separately
- Convert to array of key-value pairs: `attrs: [{k: "color", v: "red"}]`
- Single index covers all attributes: `{attrs.k: 1, attrs.v: 1}`
- Query: `{attrs: {$elemMatch: {k: "color", v: "red"}}}`

## Polymorphic Pattern

- Different document structures in same collection—flexible schema
- Use `type` or `kind` field to discriminate
- Partial indexes per type: `{age: 1}, {partialFilterExpression: {type: "person"}}`
- Application code must handle all shapes

## Computed Pattern

- Store pre-computed values to avoid repeated aggregation
- Update computed fields on write—single source of truth
- `$inc` for counters: `{$inc: {viewCount: 1}}`—atomic, no read needed
- Trade write complexity for read performance

## Anti-Patterns to Avoid

- Massive arrays that grow unbounded—time bomb
- Deep nesting > 3 levels—hard to query and index
- Storing large blobs inline—use GridFS
- One collection per user/tenant—operational nightmare
