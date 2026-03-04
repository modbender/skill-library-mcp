"""clawctl — Click-based command interface for OpenClaw agent fleets."""

import json
import os
import signal
import subprocess
import sys
import unicodedata
from pathlib import Path

import click

from clawctl import db

# ANSI colors
R = "\033[0;31m"
G = "\033[0;32m"
Y = "\033[1;33m"
C = "\033[0;36m"
B = "\033[1m"
N = "\033[0m"

_agent_warned = False


def _warn_agent_fallback():
    """Warn once if CLAW_AGENT wasn't explicitly set."""
    global _agent_warned
    if not db.AGENT_EXPLICIT and not _agent_warned:
        click.echo(
            f"{Y}Note: CLAW_AGENT not set, using $USER ({db.AGENT}){N}", err=True
        )
        _agent_warned = True


def _char_width(ch):
    """Return display width of a character (2 for wide/fullwidth, 1 otherwise)."""
    w = unicodedata.east_asian_width(ch)
    return 2 if w in ("F", "W") else 1


def _str_width(s):
    """Return display width of a string, accounting for multi-byte characters."""
    return sum(_char_width(ch) for ch in s)


def print_columnar(rows, columns):
    """Print rows as aligned columns. columns is a list of (header, key) tuples."""
    if not rows:
        return
    # Convert sqlite3.Row to dicts
    data = [dict(r) for r in rows]
    # Calculate widths
    widths = {}
    for header, key in columns:
        vals = [str(v) if (v := d.get(key)) is not None else "" for d in data]
        widths[key] = max(
            _str_width(header), max((_str_width(v) for v in vals), default=0)
        )
    # Print header
    hdr = "  ".join(h.ljust(widths[k]) for h, k in columns)
    click.echo(hdr)
    click.echo("  ".join("-" * widths[k] for _, k in columns))
    # Print rows
    for d in data:
        parts = []
        for _, k in columns:
            val = str(v) if (v := d.get(k)) is not None else ""
            pad = widths[k] - _str_width(val)
            parts.append(val + " " * pad)
        click.echo("  ".join(parts))


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """clawctl — Coordination layer for OpenClaw agent fleets"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return
    if ctx.invoked_subcommand not in ("init", "help"):
        if not os.path.exists(db.DB_PATH):
            click.echo(f"{Y}No database found. Run: clawctl init{N}", err=True)
            ctx.exit(1)


@cli.command()
def init():
    """Initialize the database"""
    db.init_db()
    click.echo(f"{G}Initialized{N} {db.DB_PATH}")


@cli.command()
@click.argument("name")
@click.option("--role", default="", help="Agent role")
def register(name, role):
    """Register an agent"""
    with db.get_db() as conn:
        db.register_agent(conn, name, role)
    click.echo(f"{G}Registered{N} {name}{f' as {role}' if role else ''}")


@cli.command()
def checkin():
    """Heartbeat — register presence"""
    _warn_agent_fallback()
    agent = db.AGENT
    with db.get_db() as conn:
        db.checkin_agent(conn, agent)
        unread = db.get_unread_count(conn, agent)
    if unread > 0:
        click.echo(f"{Y}{unread} unread messages{N} — run: clawctl inbox --unread")
    else:
        click.echo(f"{G}HEARTBEAT_OK{N} ({agent})")


@cli.command()
@click.argument("subject")
@click.option("-d", "--desc", default="", help="Description")
@click.option("-p", "--priority", type=int, default=0, help="Priority (0, 1, 2)")
@click.option("--for", "assignee", default="", help="Assign to agent")
@click.option("--parent", type=int, default=None, help="Parent task ID")
def add(subject, desc, priority, assignee, parent):
    """Create a task"""
    with db.get_db() as conn:
        ok, task_id = db.add_task(
            conn, subject, desc, priority, assignee, db.AGENT, parent
        )
    click.echo(f"{G}#{task_id}{N} {subject}{f' → {assignee}' if assignee else ''}")


@cli.command("list")
@click.option("--status", default=None, help="Filter by status")
@click.option("--owner", default=None, help="Filter by owner")
@click.option("--mine", is_flag=True, help="Show only my tasks")
@click.option("--all", "include_all", is_flag=True, help="Include done/cancelled")
def list_cmd(status, owner, mine, include_all):
    """List tasks (excludes done/cancelled by default)"""
    if mine:
        _warn_agent_fallback()
    with db.get_db() as conn:
        rows = db.list_tasks(
            conn, status, owner, db.AGENT if mine else None, include_all
        )
    if not rows:
        click.echo("No tasks found.")
        return
    print_columnar(
        rows,
        [
            ("ID", "id"),
            ("Subject", "subject"),
            ("Status", "icon"),
            ("Owner", "owner"),
            ("Pri", "pri"),
        ],
    )
    scope = "mine" if mine else "all agents"
    if not include_all and not status:
        click.echo(
            f"\n{len(rows)} active ({scope}). Use --all to include done/cancelled."
        )


@cli.command("next")
def next_cmd():
    """Show the next task to work on (highest priority, actionable)"""
    _warn_agent_fallback()
    agent = db.AGENT
    with db.get_db() as conn:
        row = db.get_next_task(conn, agent)
    if not row:
        click.echo("No actionable tasks.")
        return
    pri = "!!!" if row["priority"] == 2 else "!" if row["priority"] == 1 else ""
    click.echo(
        f"#{row['id']} {row['subject']} [{row['status']}]{f' {pri}' if pri else ''}"
    )


@cli.command()
@click.argument("id", type=int)
@click.option("--force", is_flag=True, help="Force claim even if owned by another")
@click.option("--meta", default=None, help="JSON metadata blob for activity log")
def claim(id, force, meta):
    """Claim a task"""
    _warn_agent_fallback()
    agent = db.AGENT
    with db.get_db() as conn:
        ok, err = db.claim_task(conn, id, agent, force, meta=meta)
    if ok:
        click.echo(f"{G}Claimed #{id}{N}")
    else:
        click.echo(f"{R}{err}{N}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("id", type=int)
@click.option("--meta", default=None, help="JSON metadata blob for activity log")
def start(id, meta):
    """Begin work on a task"""
    _warn_agent_fallback()
    agent = db.AGENT
    with db.get_db() as conn:
        ok, err = db.start_task(conn, id, agent, meta=meta)
    if ok:
        click.echo(f"{C}▶ Working on #{id}{N}")
    else:
        click.echo(f"{R}{err}{N}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("id", type=int)
@click.option("-m", "--message", "note", default="", help="Completion note")
@click.option("--force", is_flag=True, help="Complete even if not the owner")
@click.option("--meta", default=None, help="JSON metadata blob for activity log")
def done(id, note, force, meta):
    """Complete a task"""
    _warn_agent_fallback()
    agent = db.AGENT
    with db.get_db() as conn:
        ok, info = db.complete_task(conn, id, agent, note, meta=meta, force=force)
    if not ok:
        click.echo(f"{R}{info}{N}", err=True)
        sys.exit(1)
    if info == "already done":
        click.echo(f"{Y}#{id} already done{N}")
    else:
        msg = f"{G}✓ Done #{id}{N}"
        if note:
            msg += f" — {note}"
        click.echo(msg)


@cli.command()
@click.argument("id", type=int)
@click.option("--meta", default=None, help="JSON metadata blob for activity log")
def review(id, meta):
    """Mark a task as ready for review"""
    _warn_agent_fallback()
    agent = db.AGENT
    with db.get_db() as conn:
        ok, err = db.review_task(conn, id, agent, meta=meta)
    if ok:
        click.echo(f"{C}⟳ #{id} ready for review{N}")
    else:
        click.echo(f"{R}{err}{N}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("id", type=int)
@click.option("--meta", default=None, help="JSON metadata blob for activity log")
def cancel(id, meta):
    """Cancel a task"""
    _warn_agent_fallback()
    agent = db.AGENT
    with db.get_db() as conn:
        ok, info = db.cancel_task(conn, id, agent, meta=meta)
    if not ok:
        click.echo(f"{R}{info}{N}", err=True)
        sys.exit(1)
    if info and info.startswith("already"):
        click.echo(f"{Y}#{id} {info}{N}")
    else:
        click.echo(f"{Y}✗ Cancelled #{id}{N}")


@cli.command()
@click.argument("id", type=int)
@click.option("--by", "blocked_by", type=int, required=True, help="Blocking task ID")
@click.option("--meta", default=None, help="JSON metadata blob for activity log")
def block(id, blocked_by, meta):
    """Mark a task as blocked by another task"""
    with db.get_db() as conn:
        ok, err = db.block_task(conn, id, blocked_by, meta=meta)
    if ok:
        click.echo(f"{R}✗ #{id} blocked by #{blocked_by}{N}")
    else:
        click.echo(f"{R}{err}{N}", err=True)
        sys.exit(1)


@cli.command()
def board():
    """Kanban board view"""
    agent = db.AGENT
    click.echo(f"{B}═══ CLAWCTL ═══{N}  agent: {C}{agent}{N}")
    click.echo()
    icons = {
        "pending": "○",
        "claimed": "◉",
        "in_progress": "▶",
        "review": "⟳",
        "blocked": "✗",
        "done": "✓",
    }
    with db.get_db() as conn:
        board_data = db.get_board(conn)
    for status in ("pending", "claimed", "in_progress", "review", "blocked", "done"):
        if status not in board_data:
            continue
        info = board_data[status]
        icon = icons[status]
        click.echo(f"{B}── {icon} {status} ({info['count']}) ──{N}")
        for t in info["tasks"]:
            owner_str = f" [{t['owner']}]" if t["owner"] else ""
            click.echo(f"  #{t['id']} {t['subject']}{owner_str}")
        click.echo()


@cli.command()
@click.argument("to")
@click.argument("body")
@click.option("--task", "task_id", type=int, default=None, help="Related task ID")
@click.option("--type", "msg_type", default="comment", help="Message type")
def msg(to, body, task_id, msg_type):
    """Send a message to an agent"""
    with db.get_db() as conn:
        db.send_message(conn, db.AGENT, to, body, task_id, msg_type)
    click.echo(f"{G}→ {to}{N}: {body}")


@cli.command()
@click.argument("body")
def broadcast(body):
    """Broadcast a message to all agents"""
    with db.get_db() as conn:
        db.broadcast(conn, db.AGENT, body)
    click.echo(f"{Y}Broadcast:{N} {body}")


@cli.command()
@click.option("--unread", is_flag=True, help="Show only unread messages")
def inbox(unread):
    """Read messages"""
    agent = db.AGENT
    with db.get_db() as conn:
        rows = db.get_inbox(conn, agent, unread)
        if rows:
            displayed_ids = [row["id"] for row in rows]
            db.mark_messages_read(conn, agent, displayed_ids)
    if not rows:
        click.echo("No messages.")
        return
    print_columnar(
        rows,
        [
            ("ID", "id"),
            ("From", "from_agent"),
            ("Body", "body"),
            ("Type", "msg_type"),
            ("New", "new"),
            ("At", "at"),
        ],
    )


@cli.command()
def fleet():
    """Show fleet status"""
    click.echo(f"{B}═══ FLEET STATUS ═══{N}")
    with db.get_db() as conn:
        rows = db.get_fleet(conn)
    if not rows:
        click.echo("No agents registered.")
        return
    print_columnar(
        rows,
        [
            ("Name", "name"),
            ("Role", "role"),
            ("Status", "status"),
            ("Working On", "working_on"),
            ("Last Seen", "last_seen"),
        ],
    )


@cli.command()
@click.option("--last", "limit", type=int, default=20, help="Number of entries")
@click.option("--agent", "agent_filter", default=None, help="Filter by agent")
@click.option("--meta", "show_meta", is_flag=True, help="Show metadata column")
def feed(limit, agent_filter, show_meta):
    """Activity log"""
    with db.get_db() as conn:
        rows = db.get_feed(conn, limit, agent_filter)
    if not rows:
        click.echo("No activity.")
        return
    cols = [
        ("At", "at"),
        ("Agent", "agent"),
        ("Action", "action"),
        ("Detail", "detail"),
    ]
    if show_meta:
        cols.append(("Meta", "meta"))
    print_columnar(rows, cols)


@cli.command()
def summary():
    """Fleet summary"""
    with db.get_db() as conn:
        data = db.get_summary(conn)
    click.echo(f"{B}═══ SUMMARY ═══{N}")
    click.echo()
    click.echo(f"{C}Fleet:{N}")
    for a in data["agents"]:
        role_str = f" — {a['role']}" if a["role"] else ""
        click.echo(f"  {a['name']} ({a['status']}){role_str}")
    click.echo()
    click.echo(f"{C}Open tasks:{N} {data['open']}")
    click.echo(f"{C}In progress:{N} {data['in_progress']}")
    click.echo(f"{C}Blocked:{N} {data['blocked']}")
    click.echo()
    click.echo(f"{C}Last 5 events:{N}")
    for e in data["recent"]:
        detail_str = f" — {e['detail']}" if e["detail"] else ""
        click.echo(f"  [{e['at']}] {e['agent']}: {e['action']}{detail_str}")


@cli.command()
def whoami():
    """Show agent identity"""
    agent = db.AGENT
    click.echo(f"Agent: {C}{agent}{N}")
    click.echo(f"DB:    {db.DB_PATH}")
    with db.get_db() as conn:
        role = db.get_agent_info(conn, agent)
    click.echo(f"Role:  {role}")


@cli.command()
@click.option("--port", default=3737, help="Port to run on")
@click.option("--stop", is_flag=True, help="Stop the running dashboard")
@click.option(
    "--verbose", is_flag=True, help="Log dashboard output to ~/.openclaw/dashboard.log"
)
def dashboard(port, stop, verbose):
    """Start (or stop) the web dashboard"""
    pid_file = Path(db.DB_PATH).parent / ".dashboard.pid"

    if stop:
        if not pid_file.exists():
            click.echo("No dashboard running.")
            return
        pid = int(pid_file.read_text().strip())
        try:
            os.kill(pid, signal.SIGTERM)
            click.echo(f"{G}Dashboard stopped{N} (pid {pid})")
        except ProcessLookupError:
            click.echo(f"{Y}Dashboard was not running{N} (stale pid {pid})")
        pid_file.unlink(missing_ok=True)
        return

    if pid_file.exists():
        pid = int(pid_file.read_text().strip())
        try:
            os.kill(pid, 0)
            from dashboard.server import load_or_create_token

            token = load_or_create_token()
            click.echo(f"{Y}Dashboard already running{N} (pid {pid})")
            click.echo(f"\n  {C}http://localhost:{port}/?token={token}{N}\n")
            return
        except ProcessLookupError:
            pid_file.unlink(missing_ok=True)

    # Ensure token exists before starting (server creates it on import)
    from dashboard.server import load_or_create_token

    token = load_or_create_token()

    if verbose:
        log_path = Path(db.DB_PATH).parent / "dashboard.log"
        log_file = open(log_path, "a")
        stdout_target = log_file
        stderr_target = log_file
    else:
        log_file = None
        stdout_target = subprocess.DEVNULL
        stderr_target = subprocess.DEVNULL

    proc = subprocess.Popen(
        [sys.executable, "-m", "dashboard", "--port", str(port)],
        stdout=stdout_target,
        stderr=stderr_target,
        start_new_session=True,
    )
    if log_file:
        log_file.close()

    pid_file.write_text(str(proc.pid))
    click.echo(f"{G}Dashboard started{N} on port {port} (pid {proc.pid})")
    click.echo(f"\n  {C}http://localhost:{port}/?token={token}{N}\n")
    if verbose:
        click.echo(f"Logging to: {log_path}")
    click.echo(f"Stop with: clawctl dashboard --stop")


@cli.command("help")
@click.pass_context
def help_cmd(ctx):
    """Show help"""
    click.echo(ctx.parent.get_help())
