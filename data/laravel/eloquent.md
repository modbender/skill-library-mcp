# Eloquent Traps

- Loop without `with()` — N+1 query per iteration, use `User::with('posts')->get()`
- Nested relations need dot — `with('posts.comments')` not separate calls
- `$fillable` AND `$guarded` both set — Laravel ignores one, unpredictable
- Accessor `get{Attr}Attribute` hides DB column — can't access raw value
- Observer `saved` fires on create AND update — check `wasRecentlyCreated` to distinguish
- `withCount()` returns string — cast to int if doing math
- Soft deleted excluded by default — `withTrashed()` or relations return null
- `push()` saves model AND relations — silent writes you didn't expect
- `refresh()` reloads from DB — clears unsaved changes, data loss
- `clone $model` shares relations — use `replicate()` for true copy
