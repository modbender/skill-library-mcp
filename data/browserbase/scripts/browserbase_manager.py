#!/usr/bin/env python3
"""
Browserbase Session Manager for OpenClaw
=========================================
A CLI tool for creating and managing persistent Browserbase cloud browser
sessions with authentication persistence via Contexts.

Usage:
    python3 browserbase_manager.py <command> [options]

Commands:
    setup               Validate credentials and run a smoke test
    create-context      Create a new persistent context
    delete-context      Delete a context
    create-session      Create a new browser session
    list-sessions       List all sessions
    get-session         Get session details
    terminate-session   Terminate a running session
    navigate            Navigate to a URL in a session
    execute-js          Execute JavaScript in a session
    screenshot          Take a screenshot of the current page
    get-cookies         Get cookies from a session
    get-recording       Download session recording video
    get-logs            Get session logs
    live-url            Get live debug URL for a session

Environment Variables:
    BROWSERBASE_API_KEY       Your Browserbase API key (required)
    BROWSERBASE_PROJECT_ID    Your Browserbase project ID (required)
"""

import argparse
import json
import os
import sys
from typing import Any


# ---------------------------------------------------------------------------
# Config file for named contexts (persists across sessions)
# ---------------------------------------------------------------------------

def _config_path() -> str:
    """Return path to the local config file that stores named contexts."""
    base = os.environ.get("BROWSERBASE_CONFIG_DIR", os.path.expanduser("~/.browserbase"))
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "contexts.json")


def _load_contexts() -> dict[str, str]:
    """Load the name→context_id map from disk."""
    path = _config_path()
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def _save_contexts(data: dict[str, str]) -> None:
    """Save the name→context_id map to disk."""
    path = _config_path()
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _resolve_context(name_or_id: str) -> str:
    """Resolve a context name to its ID, or return the raw ID if not found."""
    contexts = _load_contexts()
    return contexts.get(name_or_id, name_or_id)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def get_env(name: str) -> str:
    """Get a required environment variable or exit with an error."""
    value = os.environ.get(name)
    if not value:
        output_error(f"Environment variable {name} is not set. "
                     f"Set it or configure via OpenClaw's skills.entries.browserbase-sessions.env")
        sys.exit(1)
    return value


def output_json(data: dict[str, Any]) -> None:
    """Print JSON output to stdout."""
    print(json.dumps(data, indent=2, default=str))


def output_error(message: str) -> None:
    """Print an error as JSON to stdout."""
    output_json({"error": message})


def get_client():
    """Initialize and return a Browserbase client."""
    try:
        from browserbase import Browserbase
    except ImportError:
        output_error(
            "browserbase package not installed. Run: pip install browserbase"
        )
        sys.exit(1)

    api_key = get_env("BROWSERBASE_API_KEY")
    return Browserbase(api_key=api_key)


def get_project_id() -> str:
    """Get the Browserbase project ID."""
    return get_env("BROWSERBASE_PROJECT_ID")


# ---------------------------------------------------------------------------
# Setup & Validation
# ---------------------------------------------------------------------------

def cmd_setup(args: argparse.Namespace) -> None:
    """Validate credentials and run a full smoke test."""
    steps = []

    # Step 1: Check env vars
    try:
        api_key = get_env("BROWSERBASE_API_KEY")
        project_id = get_env("BROWSERBASE_PROJECT_ID")
        steps.append({"step": "env_vars", "status": "ok",
                       "message": "BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID are set."})
    except SystemExit:
        return  # get_env already printed the error

    # Step 2: Check SDK import
    try:
        from browserbase import Browserbase
        steps.append({"step": "sdk_import", "status": "ok",
                       "message": "browserbase SDK imported successfully."})
    except ImportError:
        steps.append({"step": "sdk_import", "status": "error",
                       "message": "browserbase package not installed. Run: pip install browserbase"})
        output_json({"status": "error", "command": "setup", "steps": steps})
        sys.exit(1)

    # Step 3: Check Playwright
    try:
        from playwright.sync_api import sync_playwright
        steps.append({"step": "playwright_import", "status": "ok",
                       "message": "playwright imported successfully."})
    except ImportError:
        steps.append({"step": "playwright_import", "status": "error",
                       "message": "playwright not installed. Run: pip install playwright && playwright install chromium"})
        output_json({"status": "error", "command": "setup", "steps": steps})
        sys.exit(1)

    # Step 4: Test API connection — list sessions
    client = Browserbase(api_key=api_key)
    try:
        list(client.sessions.list())
        steps.append({"step": "api_connection", "status": "ok",
                       "message": "Successfully connected to Browserbase API."})
    except Exception as e:
        steps.append({"step": "api_connection", "status": "error",
                       "message": f"API connection failed: {e}"})
        output_json({"status": "error", "command": "setup", "steps": steps})
        sys.exit(1)

    # Step 5: Smoke test — create session, navigate, terminate
    try:
        session = client.sessions.create(
            project_id=project_id,
            browser_settings={"solve_captchas": True},
        )
        steps.append({"step": "create_session", "status": "ok",
                       "session_id": session.id,
                       "message": "Test session created."})
    except Exception as e:
        steps.append({"step": "create_session", "status": "error",
                       "message": f"Failed to create test session: {e}"})
        output_json({"status": "error", "command": "setup", "steps": steps})
        sys.exit(1)

    # Step 6: Navigate via Playwright CDP
    navigate_ok = False
    try:
        pw = sync_playwright().start()
        connect_url = session.connect_url
        if not connect_url:
            connect_url = f"wss://connect.browserbase.com?apiKey={api_key}&sessionId={session.id}"
        browser = pw.chromium.connect_over_cdp(connect_url)
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        resp = page.goto("https://example.com", wait_until="domcontentloaded", timeout=30000)
        title = page.title()
        browser.close()
        pw.stop()
        navigate_ok = True
        steps.append({"step": "playwright_navigate", "status": "ok",
                       "title": title,
                       "message": f"Navigated to example.com — title: '{title}'"})
    except Exception as e:
        steps.append({"step": "playwright_navigate", "status": "error",
                       "message": f"Playwright navigation failed: {e}"})

    # Step 7: Terminate test session
    try:
        client.sessions.update(session.id, status="REQUEST_RELEASE", project_id=project_id)
        steps.append({"step": "terminate_session", "status": "ok",
                       "message": "Test session terminated."})
    except Exception as e:
        steps.append({"step": "terminate_session", "status": "warning",
                       "message": f"Cleanup warning (non-fatal): {e}"})

    overall = "success" if navigate_ok else "partial"
    output_json({
        "status": overall,
        "command": "setup",
        "steps": steps,
        "message": "All checks passed. Skill is ready to use." if overall == "success"
                   else "Setup completed with warnings. Review steps above."
    })


# ---------------------------------------------------------------------------
# Context Management
# ---------------------------------------------------------------------------

def cmd_create_context(args: argparse.Namespace) -> None:
    """Create a new persistent context for storing authentication state."""
    client = get_client()
    project_id = get_project_id()

    try:
        context = client.contexts.create(project_id=project_id)

        # If a name was provided, save it locally
        if args.name:
            contexts = _load_contexts()
            contexts[args.name] = context.id
            _save_contexts(contexts)

        result: dict[str, Any] = {
            "status": "success",
            "command": "create-context",
            "context_id": context.id,
            "project_id": project_id,
            "message": "Context created. Use this context_id (or its name) when creating "
                       "sessions to persist authentication state (cookies, local storage)."
        }
        if args.name:
            result["name"] = args.name
        output_json(result)
    except Exception as e:
        output_error(f"Failed to create context: {e}")
        sys.exit(1)


def cmd_delete_context(args: argparse.Namespace) -> None:
    """Delete a persistent context. This is permanent and irreversible."""
    import urllib.request
    import urllib.error

    context_id = _resolve_context(args.context_id)
    api_key = get_env("BROWSERBASE_API_KEY")
    url = f"https://api.browserbase.com/v1/contexts/{context_id}"

    req = urllib.request.Request(url, method="DELETE", headers={
        "X-BB-API-Key": api_key,
    })

    try:
        with urllib.request.urlopen(req) as resp:
            _remove_named_context(context_id)
            output_json({
                "status": "success",
                "command": "delete-context",
                "context_id": context_id,
                "message": "Context deleted permanently."
            })
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        if e.code == 204:
            _remove_named_context(context_id)
            output_json({
                "status": "success",
                "command": "delete-context",
                "context_id": context_id,
                "message": "Context deleted permanently."
            })
        else:
            output_error(f"Failed to delete context (HTTP {e.code}): {body}")
            sys.exit(1)
    except Exception as e:
        output_error(f"Failed to delete context: {e}")
        sys.exit(1)


def cmd_list_contexts(args: argparse.Namespace) -> None:
    """List all locally saved named contexts."""
    contexts = _load_contexts()
    output_json({
        "status": "success",
        "command": "list-contexts",
        "count": len(contexts),
        "contexts": [{"name": k, "context_id": v} for k, v in contexts.items()],
    })


def _remove_named_context(context_id: str) -> None:
    """Remove a context_id from the named contexts file."""
    contexts = _load_contexts()
    to_remove = [k for k, v in contexts.items() if v == context_id]
    if to_remove:
        for k in to_remove:
            del contexts[k]
        _save_contexts(contexts)


# ---------------------------------------------------------------------------
# Session Lifecycle
# ---------------------------------------------------------------------------

def cmd_create_session(args: argparse.Namespace) -> None:
    """Create a new Browserbase browser session."""
    client = get_client()
    project_id = get_project_id()

    # Resolve context name → ID if needed
    context_id = _resolve_context(args.context_id) if args.context_id else None

    # Build browser settings — captcha solving and recording ON by default
    browser_settings: dict[str, Any] = {
        "solve_captchas": True,
    }

    if context_id:
        browser_settings["context"] = {
            "id": context_id,
            "persist": args.persist,
        }

    if args.no_solve_captchas:
        browser_settings["solve_captchas"] = False

    if args.block_ads:
        browser_settings["block_ads"] = True

    if not args.no_record:
        browser_settings["record_session"] = True
        browser_settings["log_session"] = True

    if args.viewport_width and args.viewport_height:
        browser_settings["viewport"] = {
            "width": args.viewport_width,
            "height": args.viewport_height,
        }

    # Build session params
    session_params: dict[str, Any] = {
        "project_id": project_id,
        "browser_settings": browser_settings,
    }

    if args.keep_alive:
        session_params["keep_alive"] = True

    if args.timeout:
        session_params["timeout"] = max(60, min(21600, args.timeout))

    if args.proxy:
        session_params["proxies"] = True

    if args.region:
        session_params["region"] = args.region

    try:
        session = client.sessions.create(**session_params)

        result: dict[str, Any] = {
            "status": "success",
            "command": "create-session",
            "session_id": session.id,
            "connect_url": session.connect_url,
            "session_status": getattr(session, "status", "RUNNING"),
            "created_at": str(getattr(session, "created_at", "")),
            "expires_at": str(getattr(session, "expires_at", "")),
            "keep_alive": args.keep_alive,
            "region": getattr(session, "region", args.region or "us-west-2"),
            "captcha_solving": not args.no_solve_captchas,
            "recording": not args.no_record,
        }

        if context_id:
            result["context_id"] = context_id
            result["persist"] = args.persist

        if hasattr(session, "selenium_remote_url") and session.selenium_remote_url:
            result["selenium_remote_url"] = session.selenium_remote_url
            result["signing_key"] = getattr(session, "signing_key", None)

        result["message"] = (
            "Session created with captcha solving"
            + (" and recording" if not args.no_record else "")
            + " enabled. Use connect_url with Playwright's "
            "connect_over_cdp() or the navigate/execute-js commands. "
            "You have 5 minutes to connect before the session auto-terminates."
        )

        output_json(result)
    except Exception as e:
        output_error(f"Failed to create session: {e}")
        sys.exit(1)


def cmd_list_sessions(args: argparse.Namespace) -> None:
    """List all sessions."""
    client = get_client()

    try:
        sessions = client.sessions.list()
        session_list = []

        for s in sessions:
            entry = {
                "session_id": s.id,
                "status": getattr(s, "status", "unknown"),
                "created_at": str(getattr(s, "created_at", "")),
                "region": getattr(s, "region", ""),
                "keep_alive": getattr(s, "keep_alive", False),
                "context_id": getattr(s, "context_id", None),
            }

            if args.status and str(getattr(s, "status", "")).upper() != args.status.upper():
                continue

            session_list.append(entry)

        output_json({
            "status": "success",
            "command": "list-sessions",
            "count": len(session_list),
            "sessions": session_list,
        })
    except Exception as e:
        output_error(f"Failed to list sessions: {e}")
        sys.exit(1)


def cmd_get_session(args: argparse.Namespace) -> None:
    """Get details for a specific session."""
    client = get_client()

    try:
        s = client.sessions.retrieve(args.session_id)
        output_json({
            "status": "success",
            "command": "get-session",
            "session_id": s.id,
            "session_status": getattr(s, "status", "unknown"),
            "created_at": str(getattr(s, "created_at", "")),
            "started_at": str(getattr(s, "started_at", "")),
            "ended_at": str(getattr(s, "ended_at", "")),
            "expires_at": str(getattr(s, "expires_at", "")),
            "region": getattr(s, "region", ""),
            "keep_alive": getattr(s, "keep_alive", False),
            "context_id": getattr(s, "context_id", None),
            "avg_cpu_usage": getattr(s, "avg_cpu_usage", None),
            "memory_usage": getattr(s, "memory_usage", None),
            "proxy_bytes": getattr(s, "proxy_bytes", None),
        })
    except Exception as e:
        output_error(f"Failed to get session: {e}")
        sys.exit(1)


def cmd_terminate_session(args: argparse.Namespace) -> None:
    """Terminate a running session."""
    client = get_client()
    project_id = get_project_id()

    try:
        client.sessions.update(
            args.session_id,
            status="REQUEST_RELEASE",
            project_id=project_id,
        )
        output_json({
            "status": "success",
            "command": "terminate-session",
            "session_id": args.session_id,
            "message": "Session termination requested. If using a context with "
                       "persist=true, wait a few seconds for context sync before "
                       "creating a new session with the same context."
        })
    except Exception as e:
        output_error(f"Failed to terminate session: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Browser Automation (via Playwright CDP)
# ---------------------------------------------------------------------------

def _connect_playwright(session_id: str):
    """Connect to a session via Playwright CDP and return (playwright, browser, page)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        output_error(
            "playwright package not installed. Run: pip install playwright && playwright install chromium"
        )
        sys.exit(1)

    client = get_client()

    try:
        session = client.sessions.retrieve(session_id)
    except Exception as e:
        output_error(f"Failed to retrieve session {session_id}: {e}")
        sys.exit(1)

    connect_url = getattr(session, "connect_url", None)
    if not connect_url:
        api_key = get_env("BROWSERBASE_API_KEY")
        connect_url = f"wss://connect.browserbase.com?apiKey={api_key}&sessionId={session_id}"

    pw = sync_playwright().start()
    try:
        browser = pw.chromium.connect_over_cdp(connect_url)
        contexts = browser.contexts
        if contexts:
            context = contexts[0]
            pages = context.pages
            page = pages[0] if pages else context.new_page()
        else:
            context = browser.new_context()
            page = context.new_page()
        return pw, browser, page
    except Exception as e:
        pw.stop()
        output_error(f"Failed to connect to session via CDP: {e}")
        sys.exit(1)


def cmd_navigate(args: argparse.Namespace) -> None:
    """Navigate to a URL in a browser session."""
    pw, browser, page = _connect_playwright(args.session_id)

    try:
        response = page.goto(args.url, wait_until="domcontentloaded", timeout=30000)

        result: dict[str, Any] = {
            "status": "success",
            "command": "navigate",
            "session_id": args.session_id,
            "url": args.url,
            "final_url": page.url,
            "title": page.title(),
            "http_status": response.status if response else None,
        }

        if args.extract_text:
            text = page.evaluate("""
                () => {
                    const body = document.body;
                    if (!body) return '';
                    const clone = body.cloneNode(true);
                    clone.querySelectorAll('script, style, noscript').forEach(el => el.remove());
                    return clone.innerText || clone.textContent || '';
                }
            """)
            max_len = 50000
            if len(text) > max_len:
                text = text[:max_len] + f"\n\n... [truncated, total {len(text)} chars]"
            result["text_content"] = text

        if args.screenshot:
            full = getattr(args, "full_page", False)
            page.screenshot(path=args.screenshot, full_page=full)
            result["screenshot_path"] = args.screenshot

        output_json(result)
    except Exception as e:
        output_error(f"Navigation failed: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_screenshot(args: argparse.Namespace) -> None:
    """Take a screenshot of the current page without navigating."""
    pw, browser, page = _connect_playwright(args.session_id)

    try:
        full = getattr(args, "full_page", False)
        page.screenshot(path=args.output, full_page=full)
        output_json({
            "status": "success",
            "command": "screenshot",
            "session_id": args.session_id,
            "current_url": page.url,
            "title": page.title(),
            "screenshot_path": args.output,
            "full_page": full,
        })
    except Exception as e:
        output_error(f"Screenshot failed: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_execute_js(args: argparse.Namespace) -> None:
    """Execute JavaScript code in a browser session."""
    pw, browser, page = _connect_playwright(args.session_id)

    try:
        result_value = page.evaluate(args.code)
        output_json({
            "status": "success",
            "command": "execute-js",
            "session_id": args.session_id,
            "code": args.code,
            "result": result_value,
        })
    except Exception as e:
        output_error(f"JavaScript execution failed: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


def cmd_get_cookies(args: argparse.Namespace) -> None:
    """Get all cookies from a browser session."""
    pw, browser, page = _connect_playwright(args.session_id)

    try:
        context = page.context
        cookies = context.cookies()
        output_json({
            "status": "success",
            "command": "get-cookies",
            "session_id": args.session_id,
            "cookie_count": len(cookies),
            "cookies": cookies,
        })
    except Exception as e:
        output_error(f"Failed to get cookies: {e}")
        sys.exit(1)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Recordings, Logs & Debug
# ---------------------------------------------------------------------------

def cmd_get_recording(args: argparse.Namespace) -> None:
    """Download the session recording video."""
    client = get_client()

    try:
        recording = client.sessions.recording.retrieve(args.session_id)

        # The recording object may contain chunks of webm data or a URL
        # Try to save it as a file
        if hasattr(recording, "content") and recording.content:
            with open(args.output, "wb") as f:
                f.write(recording.content)
        elif hasattr(recording, "url") and recording.url:
            import urllib.request
            urllib.request.urlretrieve(recording.url, args.output)
        else:
            # Recording data may be directly iterable or be a response object
            data = recording if isinstance(recording, bytes) else bytes(str(recording), "utf-8")
            with open(args.output, "wb") as f:
                f.write(data)

        file_size = os.path.getsize(args.output) if os.path.exists(args.output) else 0
        output_json({
            "status": "success",
            "command": "get-recording",
            "session_id": args.session_id,
            "output_path": args.output,
            "file_size_bytes": file_size,
            "message": f"Recording saved to {args.output} ({file_size:,} bytes)."
        })
    except Exception as e:
        output_error(f"Failed to get recording: {e}")
        sys.exit(1)


def cmd_get_logs(args: argparse.Namespace) -> None:
    """Get logs from a session."""
    client = get_client()

    try:
        logs_response = client.sessions.logs.list(args.session_id)

        # Parse the log entries
        log_entries = []
        if hasattr(logs_response, "__iter__"):
            for entry in logs_response:
                log_entries.append({
                    "timestamp": str(getattr(entry, "timestamp", "")),
                    "method": getattr(entry, "method", ""),
                    "params": getattr(entry, "params", None),
                })
        else:
            log_entries = [str(logs_response)]

        output_json({
            "status": "success",
            "command": "get-logs",
            "session_id": args.session_id,
            "log_count": len(log_entries),
            "logs": log_entries[:200],  # Cap at 200 entries to avoid huge output
        })
    except Exception as e:
        output_error(f"Failed to get logs: {e}")
        sys.exit(1)


def cmd_live_url(args: argparse.Namespace) -> None:
    """Get the live debug URL for a session."""
    client = get_client()

    try:
        live_urls = client.sessions.debug(args.session_id)
        output_json({
            "status": "success",
            "command": "live-url",
            "session_id": args.session_id,
            "debug_connection_url": getattr(live_urls, "debug_connection_url", None),
            "ws_url": getattr(live_urls, "ws_url", None),
            "pages": [
                {"id": p.id, "url": getattr(p, "url", None), "favicon_url": getattr(p, "favicon_url", None)}
                for p in getattr(live_urls, "pages", [])
            ] if getattr(live_urls, "pages", None) else [],
        })
    except Exception as e:
        output_error(f"Failed to get live URL: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI Parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Browserbase Session Manager for OpenClaw",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # -- setup --
    p_setup = subparsers.add_parser("setup", help="Validate credentials and smoke test")
    p_setup.set_defaults(func=cmd_setup)

    # -- create-context --
    p_cc = subparsers.add_parser("create-context", help="Create a persistent context")
    p_cc.add_argument("--name", default=None,
                       help="Friendly name for this context (e.g. 'github', 'slack')")
    p_cc.set_defaults(func=cmd_create_context)

    # -- delete-context --
    p_dc = subparsers.add_parser("delete-context", help="Delete a context (permanent)")
    p_dc.add_argument("--context-id", required=True,
                       help="Context ID or name to delete")
    p_dc.set_defaults(func=cmd_delete_context)

    # -- list-contexts --
    p_lc = subparsers.add_parser("list-contexts", help="List saved named contexts")
    p_lc.set_defaults(func=cmd_list_contexts)

    # -- create-session --
    p_cs = subparsers.add_parser("create-session", help="Create a new browser session")
    p_cs.add_argument("--context-id",
                       help="Context ID or name for auth persistence")
    p_cs.add_argument("--persist", action="store_true", default=False,
                       help="Save auth state back to context on session close")
    p_cs.add_argument("--keep-alive", action="store_true", default=False,
                       help="Keep session alive after disconnection")
    p_cs.add_argument("--timeout", type=int, default=None,
                       help="Session timeout in seconds (60-21600)")
    p_cs.add_argument("--region", default=None,
                       choices=["us-west-2", "us-east-1", "eu-central-1", "ap-southeast-1"],
                       help="Session region")
    p_cs.add_argument("--proxy", action="store_true", default=False,
                       help="Enable proxy")
    p_cs.add_argument("--block-ads", action="store_true", default=False,
                       help="Block ads")
    p_cs.add_argument("--no-record", action="store_true", default=False,
                       help="Disable session recording (recording is ON by default)")
    p_cs.add_argument("--no-solve-captchas", action="store_true", default=False,
                       help="Disable captcha solving (captcha solving is ON by default)")
    p_cs.add_argument("--viewport-width", type=int, default=None,
                       help="Viewport width in pixels")
    p_cs.add_argument("--viewport-height", type=int, default=None,
                       help="Viewport height in pixels")
    p_cs.set_defaults(func=cmd_create_session)

    # -- list-sessions --
    p_ls = subparsers.add_parser("list-sessions", help="List all sessions")
    p_ls.add_argument("--status", default=None,
                       choices=["RUNNING", "COMPLETED", "ERROR", "TIMED_OUT"],
                       help="Filter by status")
    p_ls.set_defaults(func=cmd_list_sessions)

    # -- get-session --
    p_gs = subparsers.add_parser("get-session", help="Get session details")
    p_gs.add_argument("--session-id", required=True, help="Session ID")
    p_gs.set_defaults(func=cmd_get_session)

    # -- terminate-session --
    p_ts = subparsers.add_parser("terminate-session", help="Terminate a session")
    p_ts.add_argument("--session-id", required=True, help="Session ID to terminate")
    p_ts.set_defaults(func=cmd_terminate_session)

    # -- navigate --
    p_nav = subparsers.add_parser("navigate", help="Navigate to a URL")
    p_nav.add_argument("--session-id", required=True, help="Session ID")
    p_nav.add_argument("--url", required=True, help="URL to navigate to")
    p_nav.add_argument("--extract-text", action="store_true", default=False,
                        help="Extract visible text content from the page")
    p_nav.add_argument("--screenshot", default=None,
                        help="Path to save a screenshot")
    p_nav.add_argument("--full-page", action="store_true", default=False,
                        help="Capture full scrollable page (not just viewport)")
    p_nav.set_defaults(func=cmd_navigate)

    # -- screenshot --
    p_ss = subparsers.add_parser("screenshot", help="Screenshot current page")
    p_ss.add_argument("--session-id", required=True, help="Session ID")
    p_ss.add_argument("--output", required=True, help="Path to save screenshot")
    p_ss.add_argument("--full-page", action="store_true", default=False,
                       help="Capture full scrollable page")
    p_ss.set_defaults(func=cmd_screenshot)

    # -- execute-js --
    p_js = subparsers.add_parser("execute-js", help="Execute JavaScript")
    p_js.add_argument("--session-id", required=True, help="Session ID")
    p_js.add_argument("--code", required=True, help="JavaScript code to execute")
    p_js.set_defaults(func=cmd_execute_js)

    # -- get-cookies --
    p_ck = subparsers.add_parser("get-cookies", help="Get session cookies")
    p_ck.add_argument("--session-id", required=True, help="Session ID")
    p_ck.set_defaults(func=cmd_get_cookies)

    # -- get-recording --
    p_rec = subparsers.add_parser("get-recording", help="Download session recording")
    p_rec.add_argument("--session-id", required=True, help="Session ID")
    p_rec.add_argument("--output", required=True,
                        help="Path to save recording (e.g. /tmp/session.webm)")
    p_rec.set_defaults(func=cmd_get_recording)

    # -- get-logs --
    p_log = subparsers.add_parser("get-logs", help="Get session logs")
    p_log.add_argument("--session-id", required=True, help="Session ID")
    p_log.set_defaults(func=cmd_get_logs)

    # -- live-url --
    p_lu = subparsers.add_parser("live-url", help="Get live debug URL")
    p_lu.add_argument("--session-id", required=True, help="Session ID")
    p_lu.set_defaults(func=cmd_live_url)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
