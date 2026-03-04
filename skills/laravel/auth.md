# Auth Traps

- `auth()->user()` returns null — no guard = guest, always null-check
- Policy method not found — returns false silently, access denied without error
- Gate `before()` returning null — continues to check, return false to deny
- Sanctum token abilities — `tokenCan('x')` not `can('x')`, different systems
- Multiple guards in `auth` middleware — `auth:sanctum,web` tries in order, confusing
- `Auth::onceUsingId()` — doesn't persist, next request is guest again
- Password reset token — single use, expired link returns no error by default
