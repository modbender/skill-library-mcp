"""Private App — Personal PWA App Marketplace server.

FastAPI backend that:
- Serves the React PWA frontend (from static/dist/ after `npm run build`)
- Auto-discovers and mounts built-in app plugins from apps/

- Manages app enable/disable state in a local SQLite DB
- Provides core API: app list, push notifications
- Serves all static files (no separate web server needed)

Usage:
    python3 scripts/server.py
    python3 scripts/server.py --config /path/to/config.json
    python3 scripts/server.py --host 0.0.0.0 --port 8800

Development (with Vite hot-reload):
    # Terminal 1: python3 scripts/server.py   (FastAPI on :8800)
    # Terminal 2: cd frontend && npm run dev   (Vite on :5173, proxies /api → :8800)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import os
import platform
import socket
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware

# ── Paths ─────────────────────────────────────────────────────────────
SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPTS_DIR.parent
APPS_DIR = REPO_DIR / "apps"
REGISTRY_DIR = REPO_DIR / "registry"  # unused, kept for load_apps compat
# React build output: `npm run build` in frontend/ → static/dist/
# (configured in vite.config.ts as outDir: '../static/dist')
DIST_DIR = REPO_DIR / "static" / "dist"

# ── Logging ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("privateapp")

# ── Config ────────────────────────────────────────────────────────────

def load_config(path: Path) -> dict:
    default: dict = {
        "host": "0.0.0.0",
        "port": 8800,
        "data_dir": "~/.local/share/privateapp",
        "file_browser": {
            "root": "~",
        },
        "push": {
            "vapid_email": "admin@localhost",
        },
    }
    if path.exists():
        try:
            loaded = json.loads(path.read_text())
            for k, v in loaded.items():
                if isinstance(v, dict) and isinstance(default.get(k), dict):
                    default[k].update(v)
                else:
                    default[k] = v
        except Exception as e:
            log.warning(f"Config parse error ({path}): {e} — using defaults")
    return default


def find_config() -> Path:
    for c in [
        SCRIPTS_DIR / "config.json",
        Path("~/.local/share/privateapp/config.json").expanduser(),
        Path("~/.config/privateapp/config.json").expanduser(),
    ]:
        if c.exists():
            return c
    return SCRIPTS_DIR / "config.json"


# ── Arg parsing (before app creation) ────────────────────────────────
_parser = argparse.ArgumentParser(description="privateapp server", add_help=False)
_parser.add_argument("--config", default=None)
_parser.add_argument("--host", default=None)
_parser.add_argument("--port", type=int, default=None)
_parser.add_argument("--help", action="store_true")
_args, _ = _parser.parse_known_args()

if _args.help:
    print(__doc__)
    sys.exit(0)

_config_path = Path(_args.config).expanduser() if _args.config else find_config()
CONFIG = load_config(_config_path)
DATA_DIR = Path(CONFIG["data_dir"]).expanduser()
DATA_DIR.mkdir(parents=True, exist_ok=True)
if _args.host:
    CONFIG["host"] = _args.host
if _args.port:
    CONFIG["port"] = _args.port

# ── Expose LLM config as env vars for apps ────────────────────────────
_llm = CONFIG.get("llm", {})
if _llm.get("endpoint") and "LLM_ENDPOINT" not in os.environ:
    os.environ["LLM_ENDPOINT"] = _llm["endpoint"]
if _llm.get("model") and "LLM_MODEL" not in os.environ:
    os.environ["LLM_MODEL"] = _llm["model"]
if _llm.get("api_key") and "LLM_API_KEY" not in os.environ:
    os.environ["LLM_API_KEY"] = _llm["api_key"]

# ── Push notification setup ───────────────────────────────────────────
sys.path.insert(0, str(SCRIPTS_DIR))

# Legacy push_notify module (kept for compatibility)
from push_notify import (  # noqa: E402
    set_config as push_set_config,
    get_all_subscriptions,
    save_subscription,
    remove_subscription,
    send_push_notification,
)
push_set_config(str(DATA_DIR), CONFIG["push"]["vapid_email"])

# New PushManager from commons
from commons.push import PushManager  # noqa: E402
_push_manager = PushManager(str(DATA_DIR), CONFIG["push"]["vapid_email"])

# ── App loader ────────────────────────────────────────────────────────
from app_loader import (  # noqa: E402
    load_apps,
    discover_app_dirs,
    AppInfo,
    init_settings_db,
    is_app_enabled as _is_app_enabled,
    set_app_enabled as _set_app_enabled,
    get_discovery_paths,
    add_discovery_path,
    remove_discovery_path,
    toggle_discovery_path,
    get_preference,
    set_preference,
)

# Initialize settings DB (creates tables)
init_settings_db(DATA_DIR)


# ── VAPID public key helper ───────────────────────────────────────────
def _read_vapid_public_key() -> str | None:
    p = DATA_DIR / "vapid_public.txt"
    return p.read_text().strip() if p.exists() else None


# ── Installed apps (populated at startup) ─────────────────────────────
_all_apps: list[AppInfo] = []


# ── Eagerly mount shell static assets (before SPA catch-all) ──────────
_dist_assets = DIST_DIR / "assets"
if _dist_assets.is_dir():
    # Must be mounted before @app.get("/{path}") catch-all
    pass  # Will mount on app object after creation

# ── Lifespan (startup / shutdown) ─────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global _all_apps

    log.info(f"Loading apps from {APPS_DIR}")
    log.info(f"Loading registry from {REGISTRY_DIR}")

    # Note: frontend static files were pre-mounted in _premount_app_frontends()
    # Note: app routers were pre-registered in _preregister_app_routers()
    # We pass fastapi_app=None to skip re-mounting/registering.
    app_infos, _routers = load_apps(APPS_DIR, REGISTRY_DIR, fastapi_app=None)
    _all_apps = app_infos

    _configure_file_browser()

    builtin_count = sum(1 for a in app_infos if a.builtin)
    external_count = sum(1 for a in app_infos if a.external)
    vapid_key = _read_vapid_public_key()
    log.info(
        f"Private App ready — {builtin_count} built-in app(s), "
        f"{external_count} registry app(s), "
        f"VAPID {'✓' if vapid_key else '✗ (run install.py)'}, "
        f"port {CONFIG['port']}"
    )
    if DIST_DIR.is_dir():
        log.info(f"Serving React build from {DIST_DIR}")
    else:
        log.warning(
            f"React build not found at {DIST_DIR}; "
            "run: cd frontend && npm install && npm run build"
        )

    yield
    # Shutdown: nothing to clean up


def _configure_file_browser() -> None:
    """Inject config into the file-browser app module after it is loaded."""
    try:
        mod = sys.modules.get("privateapp_app_file_browser")
        if mod and hasattr(mod, "configure"):
            fb_cfg = CONFIG.get("file_browser", {})
            root = fb_cfg.get("root", "~")
            mod.configure(root=root)
            log.info(f"  file-browser configured: root={root}")
    except Exception as e:
        log.warning(f"Could not configure file-browser: {e}")


# ── FastAPI app ───────────────────────────────────────────────────────
app = FastAPI(title="privateapp", docs_url=None, redoc_url=None, lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pre-mount app static files (must happen BEFORE route registration) ──
# ── Use app_loader's discovery ──
def _discover_app_dirs() -> list[tuple[Path, dict]]:
    """Wrapper: returns (app_dir, meta) tuples."""
    return [(d, m) for d, m, _s in discover_app_dirs(APPS_DIR)]


# StaticFiles mounts need to be in the route list before the SPA catch-all.
def _premount_app_frontends() -> None:
    """Eagerly mount app frontend/dist/ before routes are registered."""
    for app_dir, meta in _discover_app_dirs():
        app_id = meta.get("id", app_dir.name)
        dist = app_dir / "frontend" / "dist"
        if dist.is_dir():
            mount_path = f"/app/{app_id}"
            try:
                app.mount(mount_path, StaticFiles(directory=str(dist), html=True), name=f"app-{app_id}")
                log.info(f"Pre-mounted app frontend: {mount_path}/ → {dist}")
            except Exception as e:
                log.warning(f"Could not pre-mount app '{app_id}': {e}")

_premount_app_frontends()

# ── Mount shell assets (Vite-generated JS/CSS) before SPA catch-all ───
_dist_assets = DIST_DIR / "assets"
if _dist_assets.is_dir():
    app.mount("/assets", StaticFiles(directory=str(_dist_assets)), name="vite-assets")
    log.info(f"Mounted /assets/ → {_dist_assets}")

# Also serve static files in dist root (icons, sw.js, manifest)
for _static_file in ["sw.js", "manifest.json", "icon-192.png", "icon-512.png"]:
    _sf = DIST_DIR / _static_file
    if _sf.exists():
        pass  # These are handled by explicit routes or the SPA fallback

# ── Pre-register app API routers (must happen BEFORE the SPA catch-all) ──
def _preregister_app_routers() -> None:
    """Eagerly load and mount app backend routers before routes are defined."""
    for app_dir, meta in _discover_app_dirs():
        app_id = meta.get("id", app_dir.name)
        shortcode = meta.get("shortcode", app_id)
        api_prefix = f"/api/app/{shortcode}"
        routes_py = app_dir / "backend" / "routes.py"
        if not routes_py.exists():
            continue
        module_name = f"privateapp_app_{app_id.replace('-', '_')}"
        if module_name in sys.modules:
            continue
        try:
            spec = importlib.util.spec_from_file_location(module_name, str(routes_py))
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            if hasattr(module, "router"):
                app.include_router(module.router, prefix=api_prefix)
                log.info(f"Pre-registered router for '{app_id}' at {api_prefix}")
        except Exception as e:
            log.warning(f"Could not pre-register router for '{app_id}': {e}")

_preregister_app_routers()
# Configure apps immediately (in case requests arrive before lifespan startup)
_configure_file_browser()


@app.get("/api/apps")
async def api_apps():
    """List all apps in a flat list with status fields."""
    result = []

    for a in _all_apps:
        if a.external:
            is_enabled = a.detected and _is_app_enabled(a.id, default=False)
            if a.detected:
                status = "active" if is_enabled else "available"
            else:
                status = "not-installed"
        else:
            is_enabled = _is_app_enabled(a.id, default=True)
            status = "active" if is_enabled else "available"

        app_dict: dict = {
            "id": a.id,
            "name": a.name,
            "icon": a.icon,
            "version": a.version,
            "description": a.description,
            "author": a.author,
            "builtin": a.builtin,
            "enabled": is_enabled,
            "status": status,
            "url": a.url,
            "source": a.source,
        }

        if a.external:
            app_dict.update({
                "external": True,
                "detected": a.detected,
                "installed": a.detected,
                "skill": a.skill,
                "skill_url": a.skill_url,
                "install_hint": a.install_hint,
            })

        result.append(app_dict)

    return {"apps": result}


@app.post("/api/apps/{app_id}/enable")
async def api_app_enable(app_id: str):
    """Enable an app (show on home screen)."""
    # Verify app exists
    found = next((a for a in _all_apps if a.id == app_id), None)
    if not found:
        raise HTTPException(404, f"App '{app_id}' not found")
    if found.external and not found.detected:
        raise HTTPException(400, f"App '{app_id}' is not installed (skill not detected)")
    _set_app_enabled(app_id, True)
    return {"ok": True, "app_id": app_id, "enabled": True}


@app.post("/api/apps/{app_id}/disable")
async def api_app_disable(app_id: str):
    """Disable an app (hide from home screen)."""
    found = next((a for a in _all_apps if a.id == app_id), None)
    if not found:
        raise HTTPException(404, f"App '{app_id}' not found")
    _set_app_enabled(app_id, False)
    return {"ok": True, "app_id": app_id, "enabled": False}


@app.get("/api/info")
async def api_info():
    """Server info for the Settings page."""
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "version": "3.0.0",
        "port": CONFIG["port"],
        "data_dir": str(DATA_DIR),
        "apps_count": len(_all_apps),
        "builtin_count": sum(1 for a in _all_apps if a.builtin),
        "registry_count": sum(1 for a in _all_apps if a.external),
    }


# ── Discovery Paths API (Settings) ───────────────────────────────────

@app.get("/api/settings/paths")
async def api_settings_paths():
    """List all discovery paths."""
    return {"paths": get_discovery_paths()}


@app.post("/api/settings/paths")
async def api_settings_paths_add(request: Request):
    """Add a new discovery path.

    Body: {"path": "/home/user/my-apps", "label": "My Apps"}
    Each subdirectory in the path with an app.json will be loaded as an app.
    """
    data = await request.json()
    path = data.get("path", "").strip()
    if not path:
        raise HTTPException(400, "Missing 'path'")
    label = data.get("label", "")
    try:
        result = add_discovery_path(path, label)
        return {"ok": True, **result}
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.delete("/api/settings/paths/{path_id}")
async def api_settings_paths_remove(path_id: int):
    """Remove a discovery path."""
    if remove_discovery_path(path_id):
        return {"ok": True}
    raise HTTPException(404, f"Path ID {path_id} not found")


@app.post("/api/settings/paths/{path_id}/toggle")
async def api_settings_paths_toggle(path_id: int, request: Request):
    """Enable or disable a discovery path."""
    data = await request.json()
    enabled = data.get("enabled", True)
    if toggle_discovery_path(path_id, enabled):
        return {"ok": True, "enabled": enabled}
    raise HTTPException(404, f"Path ID {path_id} not found")


@app.post("/api/settings/rescan")
async def api_settings_rescan():
    """Force re-scan all app directories and reload app list.

    Note: newly discovered backend routes require a server restart to mount.
    Frontend-only apps and state changes take effect immediately.
    """
    global _all_apps

    app_infos, _routers = load_apps(APPS_DIR, REGISTRY_DIR, fastapi_app=None)
    _all_apps = app_infos
    _configure_file_browser()

    return {
        "ok": True,
        "apps_count": len(app_infos),
        "builtin": sum(1 for a in app_infos if a.builtin),
        "local": sum(1 for a in app_infos if a.source == "local"),
        "registry": sum(1 for a in app_infos if a.source == "registry"),
    }


# ── Preferences API ──────────────────────────────────────────────────

@app.get("/api/settings/preferences")
async def api_settings_preferences_get():
    """Get user preferences."""
    return {
        "timezone": get_preference("timezone", "America/Los_Angeles"),
        "language": get_preference("language", "English"),
        "app_order": get_preference("app_order", ""),
    }


@app.post("/api/settings/preferences")
async def api_settings_preferences_set(request: Request):
    """Save user preferences."""
    data = await request.json()
    if "timezone" in data:
        set_preference("timezone", data["timezone"])
    if "language" in data:
        set_preference("language", data["language"])
    if "app_order" in data:
        set_preference("app_order", data["app_order"])
    return {
        "ok": True,
        "timezone": get_preference("timezone", "America/Los_Angeles"),
        "language": get_preference("language", "English"),
        "app_order": get_preference("app_order", ""),
    }


# ── Push API ──────────────────────────────────────────────────────────

@app.get("/api/push/vapid-key")
async def push_vapid_key():
    key = _read_vapid_public_key()
    if not key:
        raise HTTPException(503, "VAPID not configured — run install.py")
    return {"publicKey": key}


@app.post("/api/push/subscribe")
async def push_subscribe(request: Request):
    sub = await request.json()
    if not sub.get("endpoint"):
        raise HTTPException(400, "Missing endpoint")
    return {"ok": save_subscription(sub)}


@app.post("/api/push/unsubscribe")
async def push_unsubscribe(request: Request):
    data = await request.json()
    return {"ok": remove_subscription(data.get("endpoint", ""))}


@app.post("/api/push/send")
async def push_send(request: Request):
    data = await request.json()
    sent = send_push_notification(
        data.get("title", "Notification"),
        data.get("body", ""),
        url=data.get("url", "/"),
        tag=data.get("tag"),
    )
    return {"sent": sent, "total_subscribers": len(get_all_subscriptions())}


@app.get("/api/push/test")
async def push_test():
    sent = send_push_notification(
        "Test", "Push notifications are working! 🎉", url="/", tag="test"
    )
    return {"sent": sent, "subscribers": len(get_all_subscriptions())}


# ── PWA manifest & service worker ────────────────────────────────────

@app.get("/manifest.json")
async def manifest():
    return JSONResponse({
        "name": "privateapp",
        "short_name": "Apps",
        "description": "Personal app dashboard",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": "#000000",
        "orientation": "portrait",
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
    })


@app.get("/sw.js")
async def service_worker():
    for candidate in [DIST_DIR / "sw.js", REPO_DIR / "frontend" / "public" / "sw.js"]:
        if candidate.exists():
            return Response(
                content=candidate.read_text(),
                media_type="application/javascript",
                headers={"Service-Worker-Allowed": "/", "Cache-Control": "no-cache"},
            )
    raise HTTPException(404, "Service worker not found")


@app.get("/icon-192.png")
async def icon_192():
    for c in [DIST_DIR / "icon-192.png", REPO_DIR / "frontend" / "public" / "icon-192.png"]:
        if c.exists():
            return FileResponse(str(c), media_type="image/png")
    raise HTTPException(404)


@app.get("/icon-512.png")
async def icon_512():
    for c in [DIST_DIR / "icon-512.png", REPO_DIR / "frontend" / "public" / "icon-512.png"]:
        if c.exists():
            return FileResponse(str(c), media_type="image/png")
    raise HTTPException(404)


# ── SPA catch-all: serve React index.html for all non-API routes ───────

@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    if full_path.startswith(("api/", "app/")):
        raise HTTPException(404, "Not found")

    # Serve actual static files from dist if they exist
    if full_path and not full_path.endswith("/"):
        static_file = DIST_DIR / full_path
        if static_file.is_file():
            return FileResponse(str(static_file))

    # Everything else → React SPA
    index = DIST_DIR / "index.html"
    if index.exists():
        return HTMLResponse(index.read_text(), headers={"Cache-Control": "no-cache"})

    return HTMLResponse(
        """<!DOCTYPE html><html><head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>Private App</title>
        <style>body{font-family:system-ui;max-width:500px;margin:60px auto;padding:20px;line-height:1.6}</style>
        </head><body>
        <h2>Private App</h2>
        <p>⚠️ Frontend not built yet.</p>
        <pre style="background:#f5f5f5;padding:12px;border-radius:8px">cd frontend\nnpm install\nnpm run build</pre>
        <p><a href="/api/apps">/api/apps ↗</a> · <a href="/api/info">/api/info ↗</a></p>
        </body></html>"""
    )


# ── Entry point ───────────────────────────────────────────────────────
if __name__ == "__main__":
    host = CONFIG["host"]
    port = CONFIG["port"]
    log.info(f"Starting Private App on http://{host}:{port}/")
    log.info(f"Data directory: {DATA_DIR}")
    uvicorn.run(app, host=host, port=port, log_level="info", access_log=True)
