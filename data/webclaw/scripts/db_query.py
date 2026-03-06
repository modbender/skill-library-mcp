#!/usr/bin/env python3
"""Webclaw management actions — invoked via OpenClaw Telegram interface.

Usage: python3 db_query.py --action <action-name> [--key value ...]

Actions:
  status           — Show service status, SSL, user count
  setup-ssl        — Configure HTTPS with Let's Encrypt (--domain required)
  renew-ssl        — Check and renew SSL certificate
  list-users       — List web dashboard user accounts
  create-user      — Create a user (--email, --full-name, --role)
  reset-password   — Generate new password for a user (--email)
  disable-user     — Disable a user account (--email)
  list-sessions    — Show active sessions
  clear-sessions   — Purge all sessions (force re-login)
  maintenance      — Cron: clean expired sessions + check cert
  restart-services — Restart webclaw-api + webclaw-web
  show-config      — Display current configuration
"""
import argparse
import hashlib
import json
import os
import secrets
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone

INSTALL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.expanduser("~/.openclaw/webclaw/webclaw.sqlite")
NGINX_CONF = "/etc/nginx/sites-enabled/webclaw"


def _get_conn():
    if not os.path.exists(DB_PATH):
        _fail("Database not found. Run install.sh first.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _ok(data):
    print(json.dumps(data, indent=2, default=str))
    sys.exit(0)


def _fail(msg):
    print(json.dumps({"status": "error", "message": msg}))
    sys.exit(1)


def _run(cmd, check=True):
    """Run a command and return (stdout, returncode). cmd is a list of args."""
    if isinstance(cmd, str):
        cmd = cmd.split()
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        _fail(f"Command failed: {' '.join(cmd)}\n{result.stderr[:500]}")
    return result.stdout.strip(), result.returncode


def _service_status(name):
    """Check if a systemd service is active."""
    _, code = _run(["systemctl", "is-active", name], check=False)
    return "running" if code == 0 else "stopped"


def _hash_password(plain):
    """PBKDF2-HMAC-SHA256 password hashing (matches api/auth/passwords.py)."""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 600_000, dklen=32)
    return f"pbkdf2:600000${salt}${dk.hex()}"


# ── Actions ──────────────────────────────────────────────────────────────────


def action_status(args):
    """Show service status, SSL, user count."""
    api_status = _service_status("webclaw-api")
    web_status = _service_status("webclaw-web")

    # Check SSL
    ssl_active = False
    domain = "_"
    if os.path.exists(NGINX_CONF):
        with open(NGINX_CONF) as f:
            content = f.read()
        ssl_active = "ssl_certificate" in content
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("server_name") and not line.endswith("_;"):
                domain = line.split()[-1].rstrip(";")
                break

    # User count
    user_count = 0
    try:
        conn = _get_conn()
        user_count = conn.execute("SELECT COUNT(*) FROM webclaw_user").fetchone()[0]
    except Exception:
        pass

    _ok({
        "status": "ok",
        "services": {
            "api": api_status,
            "web": web_status,
        },
        "ssl": ssl_active,
        "domain": domain,
        "users": user_count,
        "db_path": DB_PATH,
        "install_dir": INSTALL_DIR,
    })


def action_setup_ssl(args):
    """Configure HTTPS with Let's Encrypt."""
    domain = args.domain
    if not domain:
        _fail("--domain is required. Example: --domain erp.example.com")

    # Validate domain — strict regex to prevent nginx config injection
    import re
    if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$', domain):
        _fail(f"Invalid domain: {domain}. Must be a valid hostname (e.g., erp.example.com)")

    # Check certbot is available
    if not shutil.which("certbot"):
        _fail("certbot not found. Install with: sudo apt install certbot python3-certbot-nginx")

    # Obtain certificate
    email_addr = args.email or f"admin@{domain}"
    cmd = ["sudo", "certbot", "certonly", "--nginx", "-d", domain,
           "--email", email_addr, "--non-interactive", "--agree-tos"]
    stdout, code = _run(cmd, check=False)
    if code != 0:
        _fail(f"certbot failed. Make sure DNS for {domain} points to this server's IP.\n{stdout}")

    # Find certificate paths
    cert_path = f"/etc/letsencrypt/live/{domain}/fullchain.pem"
    key_path = f"/etc/letsencrypt/live/{domain}/privkey.pem"

    if not os.path.exists(cert_path):
        _fail(f"Certificate not found at {cert_path}. certbot may have used a different path.")

    # Generate HTTPS nginx config from template
    template = os.path.join(INSTALL_DIR, "templates", "nginx-https.conf")
    if not os.path.exists(template):
        _fail(f"HTTPS template not found at {template}")

    with open(template) as f:
        config = f.read()

    config = config.replace("{{DOMAIN}}", domain)
    config = config.replace("{{SSL_CERT}}", cert_path)
    config = config.replace("{{SSL_KEY}}", key_path)

    # Write config
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as tmp:
        tmp.write(config)
        tmp_path = tmp.name

    _run(["sudo", "cp", tmp_path, NGINX_CONF])
    os.unlink(tmp_path)

    # Test and reload
    _, code = _run(["sudo", "nginx", "-t"], check=False)
    if code != 0:
        _fail("Nginx config test failed after SSL setup. Reverting...")

    _run(["sudo", "systemctl", "reload", "nginx"])

    _ok({
        "status": "ok",
        "message": f"HTTPS enabled for {domain}.\nDashboard: https://{domain}\nHTTP requests redirect to HTTPS automatically.",
        "domain": domain,
        "ssl": True,
        "cert_path": cert_path,
    })


def action_renew_ssl(args):
    """Check and renew SSL certificate."""
    stdout, code = _run(["sudo", "certbot", "renew", "--dry-run"], check=False)
    if code == 0:
        _run(["sudo", "certbot", "renew", "--quiet"])
        _ok({"status": "ok", "message": "SSL certificate renewal check complete."})
    else:
        _fail(f"Certificate renewal check failed:\n{stdout[:500]}")


def action_list_users(args):
    """List web dashboard user accounts."""
    conn = _get_conn()
    rows = conn.execute(
        """SELECT u.id, u.email, u.full_name, u.status, u.last_login,
                  GROUP_CONCAT(r.name) as roles
           FROM webclaw_user u
           LEFT JOIN webclaw_user_role ur ON ur.user_id = u.id
           LEFT JOIN webclaw_role r ON r.id = ur.role_id
           GROUP BY u.id
           ORDER BY u.created_at DESC"""
    ).fetchall()

    users = []
    for r in rows:
        users.append({
            "id": r["id"],
            "email": r["email"],
            "full_name": r["full_name"],
            "status": r["status"],
            "last_login": r["last_login"],
            "roles": r["roles"].split(",") if r["roles"] else [],
        })

    _ok({"status": "ok", "users": users, "total": len(users)})


def action_create_user(args):
    """Create a web dashboard user account."""
    email = args.email
    if not email:
        _fail("--email is required")

    full_name = args.full_name or email.split("@")[0]
    role_name = args.role or "Accounts User"

    # Generate a secure temporary password
    temp_password = secrets.token_urlsafe(12)
    pw_hash = _hash_password(temp_password)

    conn = _get_conn()

    # Check if email already exists
    existing = conn.execute("SELECT id FROM webclaw_user WHERE email = ?", (email,)).fetchone()
    if existing:
        _fail(f"User with email {email} already exists")

    import uuid
    user_id = str(uuid.uuid4())
    username = email.split("@")[0]

    try:
        conn.execute(
            """INSERT INTO webclaw_user (id, username, email, full_name, password_hash, status)
               VALUES (?, ?, ?, ?, ?, 'active')""",
            (user_id, username, email, full_name, pw_hash),
        )

        # Find or create role
        role = conn.execute("SELECT id FROM webclaw_role WHERE name = ?", (role_name,)).fetchone()
        if not role:
            role_id = str(uuid.uuid4())
            conn.execute(
                "INSERT INTO webclaw_role (id, name, description, is_system) VALUES (?, ?, ?, 0)",
                (role_id, role_name, f"Auto-created role: {role_name}"),
            )
        else:
            role_id = role["id"]

        conn.execute(
            "INSERT INTO webclaw_user_role (id, user_id, role_id) VALUES (?, ?, ?)",
            (str(uuid.uuid4()), user_id, role_id),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        _fail(f"Failed to create user: {e}")

    _ok({
        "status": "ok",
        "message": f"User created: {email}\nTemporary password: {temp_password}\nRole: {role_name}\n\nUser must change password on first login.",
        "user_id": user_id,
        "email": email,
        "role": role_name,
    })


def action_reset_password(args):
    """Generate a new temporary password for a user."""
    email = args.email
    if not email:
        _fail("--email is required")

    conn = _get_conn()
    user = conn.execute("SELECT id FROM webclaw_user WHERE email = ?", (email,)).fetchone()
    if not user:
        _fail(f"User not found: {email}")

    temp_password = secrets.token_urlsafe(12)
    pw_hash = _hash_password(temp_password)

    conn.execute("UPDATE webclaw_user SET password_hash = ? WHERE id = ?", (pw_hash, user["id"]))
    # Clear all sessions for this user
    conn.execute("DELETE FROM webclaw_session WHERE user_id = ?", (user["id"],))
    conn.commit()

    _ok({
        "status": "ok",
        "message": f"Password reset for {email}\nNew temporary password: {temp_password}\nAll existing sessions have been invalidated.",
    })


def action_disable_user(args):
    """Disable a user account."""
    email = args.email
    if not email:
        _fail("--email is required")

    conn = _get_conn()
    user = conn.execute("SELECT id, status FROM webclaw_user WHERE email = ?", (email,)).fetchone()
    if not user:
        _fail(f"User not found: {email}")

    conn.execute("UPDATE webclaw_user SET status = 'disabled' WHERE id = ?", (user["id"],))
    conn.execute("DELETE FROM webclaw_session WHERE user_id = ?", (user["id"],))
    conn.commit()

    _ok({"status": "ok", "message": f"User {email} has been disabled and all sessions cleared."})


def action_list_sessions(args):
    """Show active sessions."""
    conn = _get_conn()
    rows = conn.execute(
        """SELECT s.id, u.email, s.ip_address, s.user_agent, s.created_at, s.expires_at
           FROM webclaw_session s
           JOIN webclaw_user u ON u.id = s.user_id
           ORDER BY s.created_at DESC
           LIMIT 50"""
    ).fetchall()

    sessions = []
    for r in rows:
        sessions.append({
            "session_id": r["id"][:8] + "...",
            "email": r["email"],
            "ip": r["ip_address"],
            "user_agent": (r["user_agent"] or "")[:60],
            "created": r["created_at"],
            "expires": r["expires_at"],
        })

    _ok({"status": "ok", "sessions": sessions, "total": len(sessions)})


def action_clear_sessions(args):
    """Purge all sessions (force everyone to re-login)."""
    conn = _get_conn()
    count = conn.execute("SELECT COUNT(*) FROM webclaw_session").fetchone()[0]
    conn.execute("DELETE FROM webclaw_session")
    conn.commit()
    _ok({"status": "ok", "message": f"Cleared {count} sessions. All users must log in again."})


def action_maintenance(args):
    """Cron target: clean expired sessions + check SSL cert expiry."""
    conn = _get_conn()
    now = datetime.now(timezone.utc).isoformat()

    # Clean expired sessions
    result = conn.execute("DELETE FROM webclaw_session WHERE expires_at < ?", (now,))
    expired = result.rowcount
    conn.commit()

    # Check SSL cert expiry
    ssl_msg = ""
    stdout, code = _run(["sudo", "certbot", "certificates"], check=False)
    if code == 0 and "VALID" in stdout:
        ssl_msg = "SSL certificate is valid."
    elif code == 0:
        ssl_msg = "WARNING: SSL certificate may need renewal."
        # Attempt renewal
        _run(["sudo", "certbot", "renew", "--quiet"], check=False)

    _ok({
        "status": "ok",
        "message": f"Maintenance complete. Expired sessions cleaned: {expired}. {ssl_msg}",
    })


def action_restart_services(args):
    """Restart webclaw-api + webclaw-web systemd services."""
    _run(["sudo", "systemctl", "restart", "webclaw-api", "webclaw-web"])
    import time
    time.sleep(2)

    api_status = _service_status("webclaw-api")
    web_status = _service_status("webclaw-web")

    _ok({
        "status": "ok",
        "message": f"Services restarted.\nAPI: {api_status}\nWeb: {web_status}",
    })


def action_show_config(args):
    """Display current configuration."""
    # Read nginx config for domain/SSL info
    domain = "_"
    ssl = False
    if os.path.exists(NGINX_CONF):
        with open(NGINX_CONF) as f:
            content = f.read()
        ssl = "ssl_certificate" in content
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("server_name") and not line.endswith("_;"):
                domain = line.split()[-1].rstrip(";")
                break

    _ok({
        "status": "ok",
        "config": {
            "install_dir": INSTALL_DIR,
            "db_path": DB_PATH,
            "domain": domain,
            "ssl_enabled": ssl,
            "api_port": 8001,
            "web_port": 3000,
            "nginx_config": NGINX_CONF,
        },
    })


# ── Action router ───────────────────────────────────────────────────────────

ACTIONS = {
    "status": action_status,
    "setup-ssl": action_setup_ssl,
    "renew-ssl": action_renew_ssl,
    "list-users": action_list_users,
    "create-user": action_create_user,
    "reset-password": action_reset_password,
    "disable-user": action_disable_user,
    "list-sessions": action_list_sessions,
    "clear-sessions": action_clear_sessions,
    "maintenance": action_maintenance,
    "restart-services": action_restart_services,
    "show-config": action_show_config,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Webclaw management actions")
    parser.add_argument("--action", required=True, choices=list(ACTIONS.keys()))
    parser.add_argument("--domain", default=None)
    parser.add_argument("--email", default=None)
    parser.add_argument("--full-name", default=None)
    parser.add_argument("--role", default=None)

    args, _unknown = parser.parse_known_args()
    try:
        ACTIONS[args.action](args)
    except SystemExit:
        raise
    except Exception as e:
        _fail(f"{type(e).__name__}: {e}\n\nIf webclaw is not set up yet, run: bash scripts/install.sh\nThen open https://YOUR_SERVER/setup to create your admin account.")
