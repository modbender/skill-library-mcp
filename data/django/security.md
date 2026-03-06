# Security Traps

- `|safe` filter disables escaping — XSS if content is user input
- `mark_safe()` trusts content — never use on user data
- `@csrf_exempt` removes protection — use only with other auth (API keys)
- `.extra()` / `.raw()` — SQL injection if interpolating user input
- `DEBUG=True` in production — exposes settings, paths, SQL queries
- `SECRET_KEY` in repo — session hijacking, must be env var
- `ALLOWED_HOSTS` empty in production — 400 on all requests
- `request.user.is_authenticated` — is property now, not method (no `()`)
- `login()` doesn't check password — only creates session, must validate first
- `@permission_required` without login check — anonymous gets redirect loop
