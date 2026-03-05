# Rails/ActiveRecord Traps

- N+1 queries — use `includes(:association)` to eager load
- `update_all` skips callbacks — bypasses validations too
- `delete` vs `destroy` — delete skips callbacks, destroy runs them
- `where.not(nil)` — `where.not(field: nil)` not `where(field: !nil)`
- Transaction rollback — `raise ActiveRecord::Rollback` only works inside transaction block
- `find_each` for large datasets — loads in batches, avoids memory bloat
- Callback order — before callbacks can halt chain by returning false (Rails < 5) or throwing
- `pluck` vs `map` — pluck is SQL-only, more efficient for single columns
- `presence` vs `present?` — `presence` returns value or nil, `present?` returns boolean
- Memoization with nil — `@var ||= compute` recalculates if nil, use `defined?`
