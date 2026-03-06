# ActiveRecord Traps

- `includes(:assoc).where("assocs.x = ?", v)` needs `references(:assoc)` — silent N+1 otherwise
- `update_all`/`delete_all` skip callbacks — validation/audit logic bypassed silently
- `pluck` returns arrays not models — `pluck(:id).first.name` crashes with NoMethodError
- `find_each` ignores `order` — silently reorders by primary key
- `where.not(status: nil)` vs `where.not(status: [nil, ""])` — empty string isn't nil
- `after_save` runs before transaction commits — external service calls may see stale data
- `dependent: :destroy` on large assocs — N+1 deletes, use `dependent: :delete_all`
- `scope` returning nil breaks chaining — always return relation, use `all` fallback
- `inverse_of` missing with `has_many through:` — duplicate objects in memory
- `touch: true` in callbacks — infinite loop if both models touch each other
