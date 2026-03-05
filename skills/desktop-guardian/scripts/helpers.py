#!/usr/bin/env python3
"""Desktop Guardian v2 — helpers.py
Config parsing, snapshot evaluation, safe hs command generation, state management.
"""

import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

# Try to import yaml; if missing, provide a clear error
try:
    import yaml
except ImportError:
    if len(sys.argv) > 1 and sys.argv[1] != "install_pyyaml":
        print("ERROR: PyYAML not installed. Run: pip3 install pyyaml", file=sys.stderr)
        sys.exit(1)

# --- Constants ---
CONFIG_DIR = Path.home() / ".openclaw" / "skills" / "desktop-guardian"
CONFIG_FILE = CONFIG_DIR / "policy.yaml"
STATE_FILE = CONFIG_DIR / "state.json"
LOG_DIR = Path.home() / "Library" / "Logs" / "desktop-guardian"
KILL_SWITCH = CONFIG_DIR / "KILL_SWITCH"

APP_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9 ._-]{1,100}$')
VALID_ACTIONS = {"close", "force_close", "close_oldest", "close_newest", "ask"}
VALID_MODES = {"whitelist", "blacklist", "off"}
VALID_STRATEGIES = {"click_default", "escape", "ask"}

# Apps that must never be auto-closed (hardcoded safety)
PROTECTED_APPS = frozenset([
    "Finder", "loginwindow", "WindowServer", "SystemUIServer",
    "Dock", "Spotlight", "Hammerspoon",
])

DEFAULT_CONFIG = {
    "version": 2,
    "monitor": {"interval": 60, "osascript_timeout": 10},
    "browsers": {
        "chrome": {"enabled": True, "max_windows": 3, "max_tabs": 20, "cdp_port": 9222},
        "safari": {"enabled": True, "max_windows": 3, "max_tabs": 10, "webcontent_baseline": 1},
    },
    "cleanup": {
        "enabled": True,
        "apps": {
            "mode": "whitelist",
            "whitelist": ["Finder", "Google Chrome", "Safari", "Terminal", "TextEdit", "System Settings"],
            "action": "close",
        },
        "browser_windows": {
            "chrome": {"action": "close_oldest"},
            "safari": {"action": "close_oldest"},
        },
        "browser_tabs": {
            "chrome": {"action": "close_oldest", "protect_pinned": True},
        },
    },
    "dialogs": {
        "enabled": True,
        "auto_dismiss": ["UserNotificationCenter", "CoreServicesUIAgent"],
        "ask_before_dismiss": ["SecurityAgent"],
        "ignore": [],
        "dismiss_strategy": "click_default",
    },
    "alerts": {
        "cooldown": 1800,
        "methods": ["openclaw_wake", "osascript"],
        "notify_on_actions": True,
    },
    "quiet_hours": {"enabled": False, "start": "23:00", "end": "07:00"},
    "reporting": {
        "enabled": True,
        "daily_summary": True,
        "summary_time": "09:00",
        "log_file": str(CONFIG_DIR / "violations.log"),
        "max_log_size_mb": 10,
    },
}


def load_config():
    """Load and validate config, returning merged with defaults."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG

    # Check permissions
    stat = CONFIG_FILE.stat()
    mode = oct(stat.st_mode)[-3:]
    if mode not in ("600", "640", "644"):
        print(f"WARNING: config file has mode {mode}, expected 600", file=sys.stderr)

    with open(CONFIG_FILE) as f:
        cfg = yaml.safe_load(f) or {}

    if cfg.get("version") != 2:
        print("WARNING: config version is not 2. Merging with v2 defaults. "
              "Please update your policy.yaml to version 2 — see assets/config.example.yaml", file=sys.stderr)
        # Treat as partial config — merge user values on top of v2 defaults
        # but force version to 2 so the merged result is valid
        cfg["version"] = 2

    # Deep merge with defaults (user overrides win, missing keys get defaults)
    return _deep_merge(DEFAULT_CONFIG, cfg)


def _deep_merge(base, override):
    result = base.copy()
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def validate_app_name(name):
    return bool(APP_NAME_PATTERN.match(name))


# --- Subcommands ---

def cmd_parse_config():
    """Output config as flat key=value pairs for bash."""
    cfg = load_config()

    def flatten(d, prefix=""):
        for k, v in d.items():
            key = f"{prefix}{k}" if not prefix else f"{prefix}_{k}"
            if isinstance(v, dict):
                flatten(v, key)
            elif isinstance(v, list):
                print(f'{key}="{"|".join(str(x) for x in v)}"')
            elif isinstance(v, bool):
                print(f'{key}={"true" if v else "false"}')
            else:
                print(f'{key}="{v}"')

    flatten(cfg)


def cmd_validate_config():
    """Validate config file, exit 0 if valid."""
    try:
        cfg = load_config()
        errors = []
        interval = cfg.get("monitor", {}).get("interval", 60)
        if interval < 30:
            errors.append(f"monitor.interval must be >= 30, got {interval}")

        cleanup = cfg.get("cleanup", {})
        apps_cfg = cleanup.get("apps", {})
        mode = apps_cfg.get("mode", "whitelist")
        if mode not in VALID_MODES:
            errors.append(f"cleanup.apps.mode must be one of {VALID_MODES}, got {mode}")

        action = apps_cfg.get("action", "close")
        if action not in VALID_ACTIONS:
            errors.append(f"cleanup.apps.action must be one of {VALID_ACTIONS}, got {action}")

        strategy = cfg.get("dialogs", {}).get("dismiss_strategy", "click_default")
        if strategy not in VALID_STRATEGIES:
            errors.append(f"dialogs.dismiss_strategy must be one of {VALID_STRATEGIES}, got {strategy}")

        # Upper bounds on numeric values
        for browser_key in ("chrome", "safari"):
            bcfg = cfg.get("browsers", {}).get(browser_key, {})
            mw = bcfg.get("max_windows", 3)
            if mw > 100:
                errors.append(f"browsers.{browser_key}.max_windows must be <= 100, got {mw}")
            mt = bcfg.get("max_tabs", 20)
            if mt > 500:
                errors.append(f"browsers.{browser_key}.max_tabs must be <= 500, got {mt}")

        if interval > 3600:
            errors.append(f"monitor.interval must be <= 3600, got {interval}")

        cooldown = cfg.get("alerts", {}).get("cooldown", 1800)
        if cooldown < 60:
            errors.append(f"alerts.cooldown must be >= 60, got {cooldown}")
        if cooldown > 86400:
            errors.append(f"alerts.cooldown must be <= 86400, got {cooldown}")

        whitelist = apps_cfg.get("whitelist", [])
        if len(whitelist) > 50:
            errors.append(f"cleanup.apps.whitelist must have <= 50 entries, got {len(whitelist)}")

        # Validate app names in whitelist
        for app in whitelist:
            if not validate_app_name(app):
                errors.append(f"invalid app name in whitelist: {app}")

        if errors:
            for e in errors:
                print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
        print("OK")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_check_quiet():
    """Exit 0 if NOT in quiet hours (ok to run). Exit 1 if in quiet hours."""
    cfg = load_config()
    qh = cfg.get("quiet_hours", {})
    if not qh.get("enabled", False):
        sys.exit(0)

    now = datetime.now()
    current = now.hour * 60 + now.minute
    start_parts = qh.get("start", "23:00").split(":")
    end_parts = qh.get("end", "07:00").split(":")
    start = int(start_parts[0]) * 60 + int(start_parts[1])
    end_ = int(end_parts[0]) * 60 + int(end_parts[1])

    if start > end_:  # crosses midnight
        if current >= start or current < end_:
            sys.exit(1)
    else:
        if start <= current < end_:
            sys.exit(1)
    sys.exit(0)


def cmd_evaluate_snapshot(json_str):
    """Evaluate a DG.queryAll() snapshot against policy. Output JSON with violations and actions."""
    cfg = load_config()
    snapshot = json.loads(json_str)

    violations = []
    actions = []

    cleanup = cfg.get("cleanup", {})
    cleanup_enabled = cleanup.get("enabled", True)
    browsers_cfg = cfg.get("browsers", {})
    apps_cfg = cleanup.get("apps", {})
    dialogs_cfg = cfg.get("dialogs", {})

    # --- Check browser windows ---
    browser_map = {
        "Google Chrome": "chrome",
        "Safari": "safari",
    }

    apps_in_snapshot = {a["name"]: a for a in snapshot.get("apps", [])}

    for app_name, browser_key in browser_map.items():
        bcfg = browsers_cfg.get(browser_key, {})
        if not bcfg.get("enabled", True):
            continue
        max_win = bcfg.get("max_windows", 3)
        app_data = apps_in_snapshot.get(app_name)
        if app_data and app_data["windowCount"] > max_win:
            excess = app_data["windowCount"] - max_win
            violations.append({
                "type": "excess_browser_windows",
                "app": app_name,
                "count": app_data["windowCount"],
                "max": max_win,
                "excess": excess,
            })
            if cleanup_enabled:
                bw_cfg = cleanup.get("browser_windows", {}).get(browser_key, {})
                act = bw_cfg.get("action", "close_oldest")
                if act == "close_oldest":
                    # Close windows from the end (oldest = highest index)
                    windows = sorted(app_data.get("windows", []), key=lambda w: w.get("index", 0), reverse=True)
                    for w in windows[:excess]:
                        idx = w.get("index", 1)
                        actions.append({
                            "type": "close_window",
                            "app": app_name,
                            "windowIndex": idx,
                            "title": w.get("title", ""),
                            "hs_command": _safe_hs_close_window(app_name, idx),
                        })
                elif act == "ask":
                    actions.append({"type": "ask_user", "message": f"{app_name} has {app_data['windowCount']} windows (max {max_win})"})

    # --- Check Chrome tabs via CDP ---
    chrome_cfg = browsers_cfg.get("chrome", {})
    max_tabs = chrome_cfg.get("max_tabs", 20)
    chrome_tabs = snapshot.get("chromeTabs", {})
    if chrome_tabs and chrome_tabs.get("cdpAvailable") and chrome_tabs.get("count", 0) > max_tabs:
        excess = chrome_tabs["count"] - max_tabs
        violations.append({
            "type": "excess_chrome_tabs",
            "count": chrome_tabs["count"],
            "max": max_tabs,
            "excess": excess,
        })
        if cleanup_enabled:
            tab_cfg = cleanup.get("browser_tabs", {}).get("chrome", {})
            tab_action = tab_cfg.get("action", "close_oldest")
            if tab_action in ("close_oldest", "close_newest"):
                tabs = chrome_tabs.get("tabs", [])
                if tab_action == "close_oldest":
                    tabs_to_close = tabs[:excess]
                else:
                    tabs_to_close = tabs[-excess:]
                for t in tabs_to_close:
                    tid = t.get("id", "")
                    if re.match(r'^[a-zA-Z0-9-]+$', tid):
                        actions.append({
                            "type": "close_tab",
                            "tabId": tid,
                            "title": t.get("title", ""),
                            "hs_command": _safe_hs_close_tab(tid),
                        })
            elif tab_action == "ask":
                actions.append({"type": "ask_user", "message": f"Chrome has {chrome_tabs['count']} tabs (max {max_tabs})"})

    # --- Check unexpected apps ---
    if apps_cfg.get("mode") == "whitelist":
        whitelist = set(apps_cfg.get("whitelist", []))
        # Always allow protected apps and Hammerspoon
        whitelist.update(PROTECTED_APPS)
        whitelist.add("Hammerspoon")

        for app_data in snapshot.get("apps", []):
            name = app_data["name"]
            if name not in whitelist and name not in PROTECTED_APPS:
                violations.append({
                    "type": "unexpected_app",
                    "app": name,
                    "windowCount": app_data["windowCount"],
                })
                if cleanup_enabled:
                    action = apps_cfg.get("action", "close")
                    if action == "close":
                        actions.append({
                            "type": "close_app",
                            "app": name,
                            "hs_command": _safe_hs_close_app(name),
                        })
                    elif action == "force_close":
                        actions.append({
                            "type": "force_close_app",
                            "app": name,
                            "hs_command": _safe_hs_force_close_app(name),
                        })
                    elif action == "ask":
                        actions.append({"type": "ask_user", "message": f"Unexpected app: {name}"})

    # --- Check dialogs ---
    if dialogs_cfg.get("enabled", True):
        auto_dismiss = set(dialogs_cfg.get("auto_dismiss", []))
        ask_before = set(dialogs_cfg.get("ask_before_dismiss", []))
        ignore_list = set(dialogs_cfg.get("ignore", []))
        strategy = dialogs_cfg.get("dismiss_strategy", "click_default")

        for dialog in snapshot.get("dialogs", []):
            dapp = dialog.get("app", "")
            if dapp in ignore_list:
                continue

            violations.append({
                "type": "dialog",
                "app": dapp,
                "title": dialog.get("title", ""),
                "buttons": dialog.get("buttons", []),
            })

            if dapp in auto_dismiss and cleanup_enabled:
                if strategy == "click_default":
                    btn = dialog.get("defaultButton") or "OK"
                    actions.append({
                        "type": "dismiss_dialog",
                        "app": dapp,
                        "button": btn,
                        "hs_command": _safe_hs_dismiss_dialog(dapp, "DEFAULT"),
                    })
                elif strategy == "escape":
                    actions.append({
                        "type": "dismiss_dialog_escape",
                        "app": dapp,
                        "hs_command": 'hs -c \'spoon.DesktopGuardian.sendKeystroke("escape", nil)\'',
                    })
            elif dapp in ask_before or "*" in ask_before:
                actions.append({
                    "type": "ask_user",
                    "message": f"Dialog from {dapp}: {dialog.get('title', '')} — Buttons: {dialog.get('buttons', [])}",
                })

    output = {"violations": violations, "actions": actions}
    print(json.dumps(output))


def _lua_escape(s):
    """Escape a string for safe embedding in a Lua string literal."""
    # Use Lua long string if possible, otherwise escape
    s = s.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'")
    return s


def _safe_hs_close_window(app_name, index):
    if not validate_app_name(app_name):
        return None
    return f'hs -c \'spoon.DesktopGuardian.closeWindow("{_lua_escape(app_name)}", {int(index)})\''


def _safe_hs_close_app(app_name):
    if not validate_app_name(app_name):
        return None
    return f'hs -c \'spoon.DesktopGuardian.closeApp("{_lua_escape(app_name)}")\''


def _safe_hs_force_close_app(app_name):
    if not validate_app_name(app_name):
        return None
    return f'hs -c \'spoon.DesktopGuardian.forceCloseApp("{_lua_escape(app_name)}")\''


def _safe_hs_close_tab(tab_id):
    if not re.match(r'^[a-zA-Z0-9-]+$', tab_id):
        return None
    return f'hs -c \'spoon.DesktopGuardian.closeTab("{tab_id}")\''


def _safe_hs_dismiss_dialog(app_name, button_text):
    if not validate_app_name(app_name):
        return None
    return f'hs -c \'spoon.DesktopGuardian.dismissDialog("{_lua_escape(app_name)}", "{_lua_escape(button_text)}")\''


def cmd_safe_hs_command(action, *args):
    """Generate a safe hs -c command string."""
    generators = {
        "close_window": lambda: _safe_hs_close_window(args[0], int(args[1])) if len(args) >= 2 else None,
        "close_app": lambda: _safe_hs_close_app(args[0]) if len(args) >= 1 else None,
        "force_close_app": lambda: _safe_hs_force_close_app(args[0]) if len(args) >= 1 else None,
        "close_tab": lambda: _safe_hs_close_tab(args[0]) if len(args) >= 1 else None,
        "dismiss_dialog": lambda: _safe_hs_dismiss_dialog(args[0], args[1]) if len(args) >= 2 else None,
    }
    gen = generators.get(action)
    if not gen:
        print(f"ERROR: unknown action: {action}", file=sys.stderr)
        sys.exit(1)
    result = gen()
    if result is None:
        print("ERROR: invalid arguments", file=sys.stderr)
        sys.exit(1)
    print(result)


def cmd_update_state(alert_type, timestamp=None):
    """Update cooldown state for an alert type."""
    ts = int(timestamp) if timestamp else int(time.time())
    state = _load_state()
    state.setdefault("last_alerts", {})[alert_type] = ts
    _save_state(state)


def cmd_log_violation(vtype, detail):
    """Append a violation to the log file."""
    cfg = load_config()
    log_file = Path(cfg.get("reporting", {}).get("log_file", str(CONFIG_DIR / "violations.log")))
    log_file = Path(str(log_file).replace("~", str(Path.home())))
    log_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

    # Rotate if too large
    max_mb = cfg.get("reporting", {}).get("max_log_size_mb", 10)
    if log_file.exists() and log_file.stat().st_size > max_mb * 1024 * 1024:
        rotated = log_file.with_suffix(".log.1")
        if rotated.exists():
            rotated.unlink()
        log_file.rename(rotated)

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{ts}] {vtype}: {detail}\n")


def cmd_daily_summary():
    """Generate daily summary from state."""
    state = _load_state()
    summary = state.get("daily_summary", {})
    print(json.dumps(summary, indent=2))


def cmd_check_cooldown(alert_type):
    """Exit 0 if alert can be sent (cooldown expired), exit 1 if still cooling down."""
    cfg = load_config()
    cooldown = cfg.get("alerts", {}).get("cooldown", 1800)
    state = _load_state()
    last = state.get("last_alerts", {}).get(alert_type, 0)
    if time.time() - last >= cooldown:
        sys.exit(0)
    else:
        remaining = int(cooldown - (time.time() - last))
        print(f"cooldown: {remaining}s remaining", file=sys.stderr)
        sys.exit(1)


def cmd_list_apps():
    """List apps from the most recent snapshot in state (for reference)."""
    state = _load_state()
    apps = state.get("last_snapshot_apps", [])
    for app in apps:
        print(app)


def _default_state():
    return {"version": 2, "last_alerts": {}, "daily_summary": {"date": "", "violations": [], "actions_taken": []}, "stats": {"checks_today": 0, "alerts_today": 0}}

def _load_state():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("state is not a dict")
            return data
        except (json.JSONDecodeError, ValueError) as e:
            print(f"WARNING: corrupt state.json, resetting to defaults: {e}", file=sys.stderr)
            default = _default_state()
            _save_state(default)
            return default
    return _default_state()


def _save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = STATE_FILE.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(str(tmp), str(STATE_FILE))
    os.chmod(str(STATE_FILE), 0o600)


def cmd_parse_query(json_str):
    """Convert snapshot JSON to key=value pairs."""
    data = json.loads(json_str)
    summary = data.get("summary", {})
    print(f'total_windows={summary.get("totalWindows", 0)}')
    print(f'dialog_count={summary.get("dialogCount", 0)}')
    print(f'frontmost_app="{data.get("frontmostApp", "")}"')
    wba = summary.get("windowsByApp", {})
    for app, count in wba.items():
        safe = app.replace(" ", "_").replace(".", "_")
        print(f'windows_{safe}={count}')
    ct = data.get("chromeTabs", {})
    if ct:
        print(f'chrome_tabs_cdp={ct.get("cdpAvailable", False)}')
        print(f'chrome_tabs_count={ct.get("count", -1)}')


# --- Main ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: helpers.py <command> [args...]", file=sys.stderr)
        print("Commands: parse_config, validate_config, check_quiet, evaluate_snapshot,", file=sys.stderr)
        print("          parse_query, safe_hs_command, update_state, log_violation,", file=sys.stderr)
        print("          daily_summary, list_apps, check_cooldown", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "parse_config":
        cmd_parse_config()
    elif cmd == "validate_config":
        cmd_validate_config()
    elif cmd == "check_quiet":
        cmd_check_quiet()
    elif cmd == "evaluate_snapshot":
        if len(sys.argv) < 3:
            print("Usage: helpers.py evaluate_snapshot <json>", file=sys.stderr)
            sys.exit(1)
        cmd_evaluate_snapshot(sys.argv[2])
    elif cmd == "parse_query":
        if len(sys.argv) < 3:
            print("Usage: helpers.py parse_query <json>", file=sys.stderr)
            sys.exit(1)
        cmd_parse_query(sys.argv[2])
    elif cmd == "safe_hs_command":
        if len(sys.argv) < 3:
            print("Usage: helpers.py safe_hs_command <action> <args...>", file=sys.stderr)
            sys.exit(1)
        cmd_safe_hs_command(sys.argv[2], *sys.argv[3:])
    elif cmd == "update_state":
        if len(sys.argv) < 3:
            print("Usage: helpers.py update_state <type> [timestamp]", file=sys.stderr)
            sys.exit(1)
        cmd_update_state(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == "log_violation":
        if len(sys.argv) < 4:
            print("Usage: helpers.py log_violation <type> <detail>", file=sys.stderr)
            sys.exit(1)
        cmd_log_violation(sys.argv[2], sys.argv[3])
    elif cmd == "daily_summary":
        cmd_daily_summary()
    elif cmd == "list_apps":
        cmd_list_apps()
    elif cmd == "check_cooldown":
        if len(sys.argv) < 3:
            print("Usage: helpers.py check_cooldown <type>", file=sys.stderr)
            sys.exit(1)
        cmd_check_cooldown(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
