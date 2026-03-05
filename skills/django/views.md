# Views Traps

- `request.POST` empty for JSON — use `json.loads(request.body)`
- `request.body` consumed once — second read returns empty bytes
- Middleware order matters — auth before permission, response reverses
- `get_object_or_404` raises Http404 — not DoesNotExist, can't catch normally
- `redirect()` returns 302 — use `redirect(url, permanent=True)` for 301
- `context_processor` runs every request — expensive queries slow all views
- `@login_required` on class — use `LoginRequiredMixin` instead, decorator fails
- `self.request` in CBV — only available after dispatch, not in `__init__`
