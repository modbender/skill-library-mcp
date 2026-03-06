# Controller Traps

- Validation `required` allows empty string — use `required|filled` for content
- `$request->all()` includes unexpected fields — use `$request->validated()`
- DI in constructor vs method — constructor runs before middleware
- Middleware order in Kernel — earlier wraps later, auth before rate-limit fails open
- Route middleware params `role:admin,editor` — comma splits into multiple args
- `abort(404)` after DB query — use `findOrFail()`, don't fetch then check
- Form request `authorize()` returns false — silent 403, no error message
- `$request->input('key')` returns null — `$request->input('key', 'default')` for default
