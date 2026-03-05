---
name: Rails
slug: rails
version: 1.0.1
description: Build reliable Rails apps avoiding ActiveRecord traps, N+1 queries, and callback pitfalls.
metadata: {"clawdbot":{"emoji":"🛤️","requires":{"bins":["rails"]},"os":["linux","darwin","win32"]}}
---

## Quick Reference

| Topic | File |
|-------|------|
| N+1, callbacks, validations, scopes | `activerecord.md` |
| Strong params, filters, render | `controllers.md` |
| Route conflicts, constraints | `routing.md` |
| Partials, helpers, caching, XSS | `views.md` |
| ActiveJob, Sidekiq, retries | `jobs.md` |
| Mass assignment, CSRF, SQL injection | `security.md` |

## Critical Rules

- `save` returns false on failure — `save!` raises, check return or use bang
- `update_all`/`delete_all` skip callbacks and validations — data corruption if unaware
- `find_each` for batches — `Model.all.each` loads entire table into memory
- `redirect_to` doesn't halt execution — code after it runs, use `and return`
- `dependent: :destroy` missing — orphan records accumulate forever
- `default_scope` pollutes all queries including joins — almost always wrong
- Callbacks chain silently — `throw :abort` stops save but returns false, not exception
- `includes` without `references` in `where` string — N+1 still happens
- `||=` memoization caches nil/false — use `defined?(@var) ? @var : @var = compute`
- `has_many through:` vs `has_and_belongs_to_many` — latter has no join model for attrs
- Nested `before_action` — multiple inheritance makes flow unreadable
- `render` doesn't stop action — code continues, duplicate render crashes
