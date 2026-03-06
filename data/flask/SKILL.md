---
name: Flask
description: Avoid common Flask mistakes — context errors, circular imports, session configuration, and production gotchas.
metadata: {"clawdbot":{"emoji":"🍶","requires":{"bins":["python3"]},"os":["linux","darwin","win32"]}}
---

## Application Context
- `current_app` only works inside request or with `app.app_context()` — "working outside application context" error
- `g` is per-request storage — lost after request ends, use for db connections
- Background tasks need context — `with app.app_context():` or pass data, not proxies
- `create_app()` factory pattern avoids circular imports — import `current_app` not `app`

## Request Context
- `request`, `session` only inside request — "working outside request context" error
- `url_for` needs context — `url_for('static', filename='x', _external=True)` for absolute URLs
- Test client provides context automatically — but manual context for non-request code

## Circular Imports
- `from app import app` in models causes circular — use factory pattern
- Import inside function for late binding — or use `current_app`
- Blueprints help organize — register at factory time, not import time
- Extensions init with `init_app(app)` pattern — create without app, bind later

## Sessions and Security
- `SECRET_KEY` required for sessions — random bytes, not weak string
- No SECRET_KEY = unsigned cookies — anyone can forge session data
- `SESSION_COOKIE_SECURE=True` in production — only send over HTTPS
- `SESSION_COOKIE_HTTPONLY=True` — JavaScript can't access

## Debug Mode
- `debug=True` in production = remote code execution — attacker can run Python
- Use `FLASK_DEBUG` env var — not hardcoded
- Debug PIN in logs if debug enabled — extra layer, but still dangerous

## Blueprints
- `url_prefix` set at registration — `app.register_blueprint(bp, url_prefix='/api')`
- Blueprint routes relative to prefix — `@bp.route('/users')` becomes `/api/users`
- `blueprint.before_request` only for that blueprint — `app.before_request` for all

## SQLAlchemy Integration
- `db.session.commit()` explicitly — autocommit not default
- Session scoped to request by Flask-SQLAlchemy — but background tasks need own session
- Detached object error — object from different session, refetch or merge
- `db.session.rollback()` on error — or session stays in bad state

## Production
- `flask run` is dev server — use Gunicorn/uWSGI in production
- `threaded=True` for dev server concurrency — but still not production-ready
- Static files through nginx — Flask serving static is slow
- `PROPAGATE_EXCEPTIONS=True` for proper error handling with Sentry etc.

## Common Mistakes
- `return redirect('/login')` vs `return redirect(url_for('login'))` — url_for is refactor-safe
- JSON response: `return jsonify(data)` — not `return json.dumps(data)`
- Form data in `request.form` — JSON body in `request.json` or `request.get_json()`
- `request.args` for query params — `request.args.get('page', default=1, type=int)`
