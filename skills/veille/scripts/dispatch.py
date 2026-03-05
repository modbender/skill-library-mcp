#!/usr/bin/env python3
"""
dispatch.py - Output dispatcher for the OpenClaw veille skill.

Reads a digest JSON from stdin and dispatches to configured outputs.

Supported output types:
  telegram_bot  - Direct Telegram Bot API (token auto-read from OpenClaw config)
  mail-client   - Delegates to mail-client skill CLI (fallback: SMTP config)
  nextcloud     - Delegates to nextcloud-files skill CLI
  file          - Writes digest to a local file path

Content types per output:
  recap         - Short text summary (Telegram notifications)
  full_digest   - Full HTML (email) or Markdown (Nextcloud, file)

Input formats accepted (auto-detected):
  - Raw fetch:       {"hours": N, "count": N, "articles": [...], ...}
  - Processed LLM:   {"categories": [...], "ghost_picks": [...]}

Usage:
  python3 veille.py fetch --hours 24 --filter-seen | python3 veille.py send
  python3 veille.py fetch ... | python3 dispatch.py [--profile NAME]
"""

import html
import json
import pathlib
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_CONFIG_DIR = pathlib.Path.home() / ".openclaw" / "config" / "veille"
_SKILLS_DIR = pathlib.Path.home() / ".openclaw" / "workspace" / "skills"
_OC_CONFIG  = pathlib.Path.home() / ".openclaw" / "openclaw.json"
CONFIG_PATH = _CONFIG_DIR / "config.json"


def _validate_skill_script(script_path: pathlib.Path, skill_name: str) -> bool:
    """Validate that a skill script path is under the expected skills directory.

    Security: prevents path traversal by ensuring subprocess targets are
    within ~/.openclaw/workspace/skills/. Logs the resolved path for audit.
    """
    try:
        resolved = script_path.resolve()
        skills_resolved = _SKILLS_DIR.resolve()
        if not str(resolved).startswith(str(skills_resolved)):
            print(f"[dispatch] BLOCKED: {skill_name} script path {resolved} "
                  f"is outside {skills_resolved}", file=sys.stderr)
            return False
    except (OSError, ValueError):
        return False
    return True


# ---------------------------------------------------------------------------
# File output safety
# ---------------------------------------------------------------------------

_BLOCKED_PATH_PATTERNS = [
    ".ssh", ".gnupg", ".config/systemd", "crontab",
    "/etc/", ".bashrc", ".profile", ".bash_profile", ".zshrc",
    ".env",
]

_DEFAULT_ALLOWED_DIR = pathlib.Path.home() / ".openclaw"

_MAX_OUTPUT_SIZE = 1_048_576  # 1 MB

_BLOCKED_CONTENT_PATTERNS = [
    "#!/",
    "ssh-rsa ", "ssh-ed25519 ", "ssh-ecdsa ",
    "BEGIN OPENSSH PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
    "BEGIN PGP",
    "eval(", "exec(", "__import__(",
    "import os", "import subprocess",
]


def _validate_output_path(file_path: str, config: dict) -> pathlib.Path | None:
    """Validate that a file output path is safe to write to."""
    try:
        p = pathlib.Path(file_path).expanduser().resolve()
    except (OSError, ValueError):
        print(f"[dispatch:file] BLOCKED: cannot resolve path {file_path!r}",
              file=sys.stderr)
        return None

    p_str = str(p)
    for pattern in _BLOCKED_PATH_PATTERNS:
        if pattern in p_str:
            print(f"[dispatch:file] BLOCKED: path {p} matches blocked "
                  f"pattern {pattern!r}", file=sys.stderr)
            return None

    allowed_dirs = [_DEFAULT_ALLOWED_DIR.resolve()]
    for extra in config.get("security", {}).get("allowed_output_dirs", []):
        try:
            allowed_dirs.append(pathlib.Path(extra).expanduser().resolve())
        except (OSError, ValueError):
            pass

    for allowed in allowed_dirs:
        if str(p).startswith(str(allowed)):
            return p

    print(f"[dispatch:file] BLOCKED: {p} is outside allowed directories "
          f"{[str(d) for d in allowed_dirs]} - add to "
          f"config.security.allowed_output_dirs to allow", file=sys.stderr)
    return None


def _validate_file_content(text: str) -> bool:
    """Validate that digest content does not contain suspicious patterns."""
    if len(text.encode("utf-8")) > _MAX_OUTPUT_SIZE:
        print(f"[dispatch:file] BLOCKED: content too large "
              f"({len(text.encode('utf-8'))} bytes, max {_MAX_OUTPUT_SIZE})",
              file=sys.stderr)
        return False

    for pattern in _BLOCKED_CONTENT_PATTERNS:
        if pattern in text:
            print(f"[dispatch:file] BLOCKED: content contains suspicious "
                  f"pattern {pattern!r}", file=sys.stderr)
            return False

    return True


# ---------------------------------------------------------------------------
# i18n strings
# ---------------------------------------------------------------------------

_STRINGS: dict = {
    "fr": {
        "title":       "Veille technique",
        "subtitle":    "{count} articles",
        "featured":    "Selections",
        "no_articles": "Aucun article.",
        "filtered":    "{n} filtre(s)",
        "footer":      "OpenClaw veille skill",
        "date_fmt":    "%d/%m/%Y %H:%M",
        "recap_title": "Veille tech",
    },
    "en": {
        "title":       "Tech Watch",
        "subtitle":    "{count} articles",
        "featured":    "Highlights",
        "no_articles": "No articles.",
        "filtered":    "{n} filtered",
        "footer":      "OpenClaw veille skill",
        "date_fmt":    "%Y-%m-%d %H:%M",
        "recap_title": "Tech watch",
    },
}

_DEFAULT_LANG = "fr"


def _t(lang: str, key: str, **kwargs) -> str:
    """Return translated string, with optional format kwargs."""
    s = _STRINGS.get(lang, _STRINGS[_DEFAULT_LANG]).get(key, key)
    return s.format(**kwargs) if kwargs else s


# ---------------------------------------------------------------------------
# Timezone helper
# ---------------------------------------------------------------------------


def _get_tz(config: dict):
    """
    Resolve timezone for date formatting.
    Priority: config['timezone'] > system (/etc/timezone, timedatectl) > UTC.
    """
    # 1. Explicit config
    tz_name = config.get("timezone", "").strip()

    # 2. System timezone
    if not tz_name:
        etc_tz = pathlib.Path("/etc/timezone")
        if etc_tz.exists():
            tz_name = etc_tz.read_text(encoding="utf-8").strip()

    # 3. Try to load, fallback to UTC
    if tz_name:
        try:
            return ZoneInfo(tz_name)
        except (ZoneInfoNotFoundError, Exception):
            print(f"[dispatch] unknown timezone '{tz_name}', using UTC", file=sys.stderr)

    return timezone.utc


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------


def _is_processed(data: dict) -> bool:
    """True if data is an LLM-processed digest with categories."""
    return "categories" in data


def _featured_items(data: dict) -> list:
    """Return featured/highlighted articles - supports ghost_picks and featured keys."""
    return data.get("featured", data.get("ghost_picks", []))


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------


def format_recap(data: dict, lang: str = _DEFAULT_LANG, tz=timezone.utc) -> str:
    """Short plain-text recap (Telegram or similar)."""
    now = datetime.now(tz).strftime("%d/%m %H:%M")
    title = _t(lang, "recap_title")
    if _is_processed(data):
        categories = data.get("categories", [])
        count = sum(len(c.get("articles", [])) for c in categories)
        picks = _featured_items(data)
        lines = [f"*{title} - {now}*", f"{count} articles"]
        for cat in categories:
            n = len(cat.get("articles", []))
            if n:
                lines.append(f"- {cat['name']}: {n}")
        if picks:
            featured_label = _t(lang, "featured")
            lines.append(f"\n✍️ {len(picks)} {featured_label.lower()}")
    else:
        count = data.get("count", 0)
        skipped = data.get("skipped_url", 0) + data.get("skipped_topic", 0)
        hours = data.get("hours", 24)
        lines = [f"*{title} - {now}*", f"{count} articles ({hours}h)"]
        if skipped:
            lines.append(_t(lang, "filtered", n=skipped))
    return "\n".join(lines)


def format_digest_markdown(data: dict, lang: str = _DEFAULT_LANG, tz=timezone.utc) -> str:
    """Full Markdown digest for Nextcloud or file."""
    date_fmt = _t(lang, "date_fmt")
    now = datetime.now(tz).strftime(date_fmt)
    title = _t(lang, "title")
    lines = [f"# {title} - {now}", ""]

    if _is_processed(data):
        for cat in data.get("categories", []):
            lines += [f"## {cat['name']}", ""]
            for a in cat.get("articles", []):
                reason = a.get("reason", "")
                lines.append(f"- **[{a['title']}]({a['url']})**  ")
                lines.append(f"  *{a['source']} - {a.get('published', '')}*  ")
                if reason:
                    lines.append(f"  {reason}")
                lines.append("")
        picks = _featured_items(data)
        if picks:
            featured_label = _t(lang, "featured")
            lines += [f"## ✍️ {featured_label}", ""]
            for p in picks:
                lines.append(f"- **[{p['title']}]({p['url']})**  ")
                lines.append(f"  *{p['source']}* - {p.get('reason', '')}")
                lines.append("")
    else:
        articles = data.get("articles", [])
        skipped = data.get("skipped_url", 0) + data.get("skipped_topic", 0)
        filtered_str = _t(lang, "filtered", n=skipped)
        lines += [f"*{len(articles)} articles | {filtered_str}*", ""]
        by_src: dict = {}
        for a in articles:
            by_src.setdefault(a.get("source", "?"), []).append(a)
        for src, arts in sorted(by_src.items()):
            lines += [f"## {src}", ""]
            for a in arts:
                lines.append(f"- **[{a['title']}]({a['url']})**  ")
                lines.append(f"  *{a.get('published', '')}*")
                lines.append("")

    return "\n".join(lines)


_CATEGORY_COLORS = ["#ef4444", "#f97316", "#3b82f6", "#8b5cf6", "#10b981", "#06b6d4"]

JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS_FR  = ["janvier", "fevrier", "mars", "avril", "mai", "juin",
             "juillet", "aout", "septembre", "octobre", "novembre", "decembre"]


def _date_fr(dt=None) -> str:
    d = dt or datetime.now()
    return f"{JOURS_FR[d.weekday()]} {d.day} {MOIS_FR[d.month - 1]} {d.year}"


def _article_rows(articles: list, accent: str) -> str:
    rows = ""
    for a in articles:
        source  = html.escape(str(a.get("source", "")))
        pub     = html.escape(str(a.get("published", "")))
        title   = html.escape(str(a.get("title", "(sans titre)")))
        url     = html.escape(str(a.get("url", "#")), quote=True)
        reason  = html.escape(str(a.get("reason", "")))
        rows += (
            f'<tr><td style="padding:0 0 14px 14px;border-left:3px solid {accent};">'
            f'<div style="font-size:11px;color:#9ca3af;margin-bottom:3px;'
            f'text-transform:uppercase;letter-spacing:0.4px;">{source} &middot; {pub}</div>'
            f'<a href="{url}" style="font-size:14px;font-weight:600;color:#111827;'
            f'text-decoration:none;line-height:1.4;display:block;">{title}</a>'
            + (f'<div style="font-size:13px;color:#6b7280;margin-top:4px;line-height:1.5;">{reason}</div>'
               if reason else "")
            + f'</td></tr>'
        )
    return rows


def format_digest_html(data: dict, lang: str = _DEFAULT_LANG, tz=timezone.utc) -> str:
    """Full HTML digest for email - styled layout matching Jarvis email standard."""
    now_dt   = datetime.now(tz)
    today    = _date_fr(now_dt)
    time_str = now_dt.strftime("%H:%M")

    sections = ""

    if _is_processed(data):
        # Featured section (yellow accent)
        picks = _featured_items(data)
        if picks:
            featured_label = _t(lang, "featured")
            rows = _article_rows(picks, "#f59e0b")
            sections += (
                f'<tr><td style="padding:20px 0 12px 0;border-bottom:2px solid #f59e0b;">'
                f'<span style="display:inline-block;width:4px;height:16px;background:#f59e0b;'
                f'border-radius:2px;vertical-align:middle;"></span>'
                f'<span style="margin-left:10px;font-size:12px;font-weight:700;color:#92400e;'
                f'text-transform:uppercase;letter-spacing:0.8px;vertical-align:middle;">'
                f'✍️ {html.escape(featured_label)}</span></td></tr>'
                f'<tr><td style="background:#fffbeb;border-radius:6px;padding:4px 0;">'
                f'<table width="100%" cellpadding="0" cellspacing="0">{rows}</table>'
                f'</td></tr>'
            )

        # Categories
        for i, cat in enumerate(data.get("categories", [])):
            arts = cat.get("articles", [])
            if not arts:
                continue
            accent = _CATEGORY_COLORS[i % len(_CATEGORY_COLORS)]
            name   = html.escape(str(cat.get("name", "")))
            count  = len(arts)
            rows   = _article_rows(arts, accent)
            sections += (
                f'<tr><td style="padding:20px 0 12px 0;">'
                f'<span style="display:inline-block;width:4px;height:16px;background:{accent};'
                f'border-radius:2px;vertical-align:middle;"></span>'
                f'<span style="margin-left:10px;font-size:12px;font-weight:700;color:#374151;'
                f'text-transform:uppercase;letter-spacing:0.8px;vertical-align:middle;">{name}</span>'
                f'<span style="margin-left:6px;font-size:11px;color:#9ca3af;vertical-align:middle;">'
                f'({count})</span></td></tr>'
                f'<tr><td><table width="100%" cellpadding="0" cellspacing="0">{rows}</table></td></tr>'
            )
        total = sum(len(c.get("articles", [])) for c in data.get("categories", []))
        subtitle = f'{total} articles · {len(data.get("categories", []))} categories'
    else:
        articles = data.get("articles", [])
        total    = data.get("count", len(articles))
        skipped  = data.get("skipped_url", 0) + data.get("skipped_topic", 0)
        by_src: dict = {}
        for a in articles:
            by_src.setdefault(a.get("source", "?"), []).append(a)
        for i, (src, arts) in enumerate(sorted(by_src.items())):
            accent = _CATEGORY_COLORS[i % len(_CATEGORY_COLORS)]
            rows   = _article_rows(arts, accent)
            src_e  = html.escape(src)
            sections += (
                f'<tr><td style="padding:20px 0 12px 0;">'
                f'<span style="display:inline-block;width:4px;height:16px;background:{accent};'
                f'border-radius:2px;vertical-align:middle;"></span>'
                f'<span style="margin-left:10px;font-size:12px;font-weight:700;color:#374151;'
                f'text-transform:uppercase;letter-spacing:0.8px;vertical-align:middle;">{src_e}</span>'
                f'</td></tr>'
                f'<tr><td><table width="100%" cellpadding="0" cellspacing="0">{rows}</table></td></tr>'
            )
        subtitle = f'{total} articles'
        if skipped:
            subtitle += f' · {skipped} filtres'

    html_title = _t(lang, "title")
    no_art     = _t(lang, "no_articles")
    body       = sections or (
        f'<tr><td style="color:#9ca3af;font-size:14px;padding:16px 0;">'
        f'{html.escape(no_art)}</td></tr>'
    )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td style="padding:24px 16px;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:800px;margin:0 auto;background:#ffffff;border-radius:10px;border:1px solid #e5e7eb;">
          <!-- Header -->
          <tr>
            <td style="padding:24px 32px 16px 32px;border-bottom:1px solid #f3f4f6;">
              <div style="font-size:11px;color:#9ca3af;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">{today}</div>
              <div style="font-size:22px;font-weight:800;color:#111827;">📡 {html.escape(html_title)}</div>
              <div style="font-size:13px;color:#6b7280;margin-top:4px;">{html.escape(subtitle)}</div>
            </td>
          </tr>
          <!-- Content -->
          <tr>
            <td style="padding:8px 32px 24px 32px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                {body}
              </table>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding:14px 32px;background:#f9fafb;border-top:1px solid #f3f4f6;border-radius:0 0 10px 10px;">
              <div style="font-size:11px;color:#9ca3af;">Jarvis · {time_str} · digest automatique quotidien</div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


# ---------------------------------------------------------------------------
# OpenClaw config helpers
# ---------------------------------------------------------------------------


def _oc_telegram_token() -> str:
    """Read Telegram bot token from ~/.openclaw/openclaw.json (read-only).

    Cross-config read: this is the only file read outside the skill's own
    config directory. To avoid this read entirely, set 'bot_token' explicitly
    in the telegram_bot output config.
    """
    if not _OC_CONFIG.exists():
        return ""
    try:
        print(f"[dispatch:telegram] reading bot token from {_OC_CONFIG} "
              f"(set bot_token in output config to skip this)", file=sys.stderr)
        d = json.loads(_OC_CONFIG.read_text(encoding="utf-8"))
        return d.get("channels", {}).get("telegram", {}).get("botToken", "")
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def _out_telegram(cfg: dict, data: dict, lang: str = _DEFAULT_LANG, tz=timezone.utc) -> bool:
    """Send to Telegram via Bot API."""
    token = cfg.get("bot_token") or _oc_telegram_token()
    chat_id = str(cfg.get("chat_id", ""))
    if not token:
        print("[dispatch:telegram] bot_token not found - set in output config or configure Telegram in OpenClaw", file=sys.stderr)
        return False
    if not chat_id:
        print("[dispatch:telegram] chat_id required", file=sys.stderr)
        return False

    content = cfg.get("content", "recap")
    text = format_recap(data, lang, tz) if content == "recap" else format_digest_markdown(data, lang, tz)

    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
        if result.get("ok"):
            print("[dispatch:telegram] OK", file=sys.stderr)
            return True
        print(f"[dispatch:telegram] API error: {result.get('description','?')}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[dispatch:telegram] error: {e}", file=sys.stderr)
        return False


def _out_mail(cfg: dict, data: dict, lang: str = _DEFAULT_LANG, tz=timezone.utc) -> bool:
    """Send via mail-client skill CLI, fallback to raw SMTP."""
    mail_to = cfg.get("mail_to", "")
    if not mail_to:
        print("[dispatch:mail-client] mail_to required", file=sys.stderr)
        return False

    date_fmt = _t(lang, "date_fmt")
    now = datetime.now(tz).strftime(date_fmt)
    subject = cfg.get("subject", f"{_t(lang, 'title')} - {now}")
    content = cfg.get("content", "full_digest")
    body_plain = format_recap(data, lang, tz) if content == "recap" else format_digest_markdown(data, lang, tz)
    body_html  = None if content == "recap" else format_digest_html(data, lang, tz)

    # Try mail-client skill
    mail_script = _SKILLS_DIR / "mail-client" / "scripts" / "mail.py"
    if mail_script.exists() and _validate_skill_script(mail_script, "mail-client"):
        cmd = [sys.executable, str(mail_script), "send",
               "--to", mail_to, "--subject", subject, "--body", body_plain]
        if body_html:
            cmd += ["--html", body_html]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if r.returncode == 0:
                print("[dispatch:mail-client] OK", file=sys.stderr)
                return True
            print(f"[dispatch:mail-client] skill error: {r.stderr[:200]}", file=sys.stderr)
        except Exception as e:
            print(f"[dispatch:mail-client] skill call error: {e}", file=sys.stderr)
        print("[dispatch:mail-client] falling back to SMTP config", file=sys.stderr)

    # SMTP fallback
    return _smtp_fallback(cfg, subject, body_plain, body_html, tz=tz)


def _smtp_fallback(cfg: dict, subject: str, body_plain: str, body_html: str = None, tz=timezone.utc) -> bool:
    """Raw SMTP send when mail-client skill is unavailable."""
    import smtplib
    import ssl as _ssl
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import email.utils

    host     = cfg.get("smtp_host", "")
    port     = int(cfg.get("smtp_port", 587))
    user     = cfg.get("smtp_user", "")
    password = cfg.get("smtp_pass", "")
    from_    = cfg.get("mail_from", user)
    to_      = cfg.get("mail_to", "")

    if not all([host, user, password, to_]):
        print("[dispatch:smtp-fallback] missing smtp_host/smtp_user/smtp_pass/mail_to in output config", file=sys.stderr)
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"]    = subject
    msg["From"]       = from_
    msg["To"]         = to_
    msg["Date"]       = email.utils.formatdate(localtime=False)
    msg["Message-ID"] = email.utils.make_msgid()
    msg.attach(MIMEText(body_plain, "plain", "utf-8"))
    if body_html:
        msg.attach(MIMEText(body_html, "html", "utf-8"))

    try:
        ctx = _ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=30) as s:
            s.ehlo(); s.starttls(context=ctx); s.ehlo()
            s.login(user, password)
            s.sendmail(from_, [to_], msg.as_string())
        print("[dispatch:smtp-fallback] OK", file=sys.stderr)
        return True
    except Exception as e:
        print(f"[dispatch:smtp-fallback] error: {e}", file=sys.stderr)
        return False


def _out_nextcloud(cfg: dict, data: dict, lang: str = _DEFAULT_LANG, tz=timezone.utc) -> bool:
    """Write to Nextcloud via nextcloud skill CLI (append mode with date separator)."""
    nc_path = cfg.get("path", "")
    if not nc_path:
        print("[dispatch:nextcloud] path required", file=sys.stderr)
        return False

    content = cfg.get("content", "full_digest")
    text = format_recap(data, lang, tz) if content == "recap" else format_digest_markdown(data, lang, tz)

    nc_script = _SKILLS_DIR / "nextcloud-files" / "scripts" / "nextcloud.py"
    if not nc_script.exists():
        print(f"[dispatch:nextcloud] skill not installed ({nc_script})", file=sys.stderr)
        return False
    if not _validate_skill_script(nc_script, "nextcloud-files"):
        return False

    mode = cfg.get("mode", "append")

    if mode == "append":
        now = datetime.now(tz)
        date_str = now.strftime("%Y-%m-%d %H:%M")
        separator = f"\n\n---\n\n## {date_str}\n\n"
        text = separator + text
        cmd = [sys.executable, str(nc_script), "write", nc_path, "--content", text, "--append"]
    else:
        cmd = [sys.executable, str(nc_script), "write", nc_path, "--content", text]

    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            action = "appended to" if mode == "append" else "written to"
            print(f"[dispatch:nextcloud] {action} {nc_path} OK", file=sys.stderr)
            return True
        print(f"[dispatch:nextcloud] error: {r.stderr[:200]}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[dispatch:nextcloud] error: {e}", file=sys.stderr)
        return False


def _out_file(cfg: dict, data: dict, lang: str = _DEFAULT_LANG, tz=timezone.utc) -> bool:
    """Write digest to a local file."""
    file_path = cfg.get("path", "")
    if not file_path:
        print("[dispatch:file] path required", file=sys.stderr)
        return False

    global_config = cfg.get("_global_config", {})
    p = _validate_output_path(file_path, global_config)
    if p is None:
        return False

    content = cfg.get("content", "full_digest")
    text = format_recap(data, lang, tz) if content == "recap" else format_digest_markdown(data, lang, tz)

    if not _validate_file_content(text):
        return False

    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        print(f"[dispatch:file] written to {p} OK", file=sys.stderr)
        return True
    except Exception as e:
        print(f"[dispatch:file] error: {e}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Handler registry
# ---------------------------------------------------------------------------

_HANDLERS = {
    "telegram_bot": _out_telegram,
    "mail-client":  _out_mail,
    "nextcloud":    _out_nextcloud,
    "file":         _out_file,
}

# ---------------------------------------------------------------------------
# Main dispatch function
# ---------------------------------------------------------------------------


def dispatch(data: dict, config: dict, profile: str = None) -> dict:
    """
    Dispatch data to all enabled outputs.
    If profile is given, use config['profiles'][profile] instead of config['outputs'].
    Returns {"ok": [...], "fail": [...], "skip": [...]}.
    """
    if profile:
        outputs = config.get("profiles", {}).get(profile, [])
        if not outputs:
            print(f"[dispatch] profile '{profile}' not found or empty", file=sys.stderr)
    else:
        outputs = config.get("outputs", [])

    results: dict = {"ok": [], "fail": [], "skip": []}

    if not outputs:
        print("[dispatch] No outputs configured. Add 'outputs' to ~/.openclaw/config/veille/config.json", file=sys.stderr)
        return results

    # Resolve shared lang + tz from config
    lang = config.get("language", _DEFAULT_LANG)
    if lang not in _STRINGS:
        print(f"[dispatch] unknown language '{lang}', falling back to '{_DEFAULT_LANG}'", file=sys.stderr)
        lang = _DEFAULT_LANG
    tz = _get_tz(config)

    for out in outputs:
        out_type = out.get("type", "")
        if not out.get("enabled", True):
            print(f"[dispatch] {out_type}: skipped (disabled)", file=sys.stderr)
            results["skip"].append(out_type)
            continue
        handler = _HANDLERS.get(out_type)
        if not handler:
            print(f"[dispatch] unknown output type: {out_type!r}", file=sys.stderr)
            results["skip"].append(out_type)
            continue
        out["_global_config"] = config
        ok = handler(out, data, lang=lang, tz=tz)
        results["ok" if ok else "fail"].append(out_type)

    # Audit summary
    total = len(results["ok"]) + len(results["fail"]) + len(results["skip"])
    print(f"[dispatch] audit: {total} outputs processed "
          f"(ok={results['ok']}, fail={results['fail']}, skip={results['skip']})",
          file=sys.stderr)

    return results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog="dispatch.py",
        description="Dispatch a veille digest JSON (stdin) to configured outputs",
    )
    parser.add_argument("--profile", default=None, help="Named output profile")
    args = parser.parse_args()

    try:
        data = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        print(f"[dispatch] invalid JSON on stdin: {e}", file=sys.stderr)
        sys.exit(1)

    config: dict = {}
    if CONFIG_PATH.exists():
        try:
            config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[dispatch] could not read config: {e}", file=sys.stderr)

    results = dispatch(data, config, profile=args.profile)
    print(json.dumps({"dispatched": results}, ensure_ascii=False, indent=2))

    if results.get("fail"):
        sys.exit(1)


if __name__ == "__main__":
    main()
