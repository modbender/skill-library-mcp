# Routing Traps

- Route order matters — `/posts/new` after `/posts/:id` makes `new` an id
- `resources :posts` adds 7 routes — `only:` or `except:` to limit
- `namespace` vs `scope` — namespace expects controller in module, scope doesn't
- `member` vs `collection` — member has `:id`, collection doesn't
- `get '*path'` catchall — must be last or eats all routes below
- Constraints regex without anchors — `constraints: { id: /\d+/ }` still matches `123abc`
- Duplicate route names — silently uses last one, `rake routes` shows both
