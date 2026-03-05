"""clawctl — shared database layer.

All SQL uses parameterized queries. Mutating functions return (ok, payload):
  Success: (True, result_data)
  Failure: (False, error_string)
"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = os.environ.get("CLAW_DB", os.path.expanduser("~/.openclaw/clawctl.db"))
AGENT_EXPLICIT = "CLAW_AGENT" in os.environ
AGENT = os.environ.get("CLAW_AGENT", os.getenv("USER", "unknown"))


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    schema_path = Path(__file__).parent / "schema.sql"
    conn.executescript(schema_path.read_text())
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.close()


def log_activity(conn, agent, action, target_type, target_id, detail="", meta=None):
    conn.execute(
        "INSERT INTO activity(agent,action,target_type,target_id,detail,meta) VALUES(?,?,?,?,?,?)",
        (agent, action, target_type, target_id, detail, meta),
    )


# ── Agents ──────────────────────────────────────────────


def register_agent(conn, name, role=""):
    conn.execute(
        "INSERT OR REPLACE INTO agents(name,role,last_seen,status) VALUES(?,?,datetime('now'),'idle')",
        (name, role),
    )
    log_activity(conn, name, "agent_registered", "agent", 0, f"{name} ({role})")
    return True, None


def checkin_agent(conn, agent):
    conn.execute(
        """INSERT OR REPLACE INTO agents(name,role,last_seen,status,session_id,registered_at)
        VALUES(?,
          COALESCE((SELECT role FROM agents WHERE name=?),''),
          datetime('now'),
          COALESCE((SELECT CASE WHEN (SELECT COUNT(*) FROM tasks WHERE owner=? AND status='in_progress')>0 THEN 'busy' ELSE 'idle' END),'idle'),
          COALESCE((SELECT session_id FROM agents WHERE name=?),''),
          COALESCE((SELECT registered_at FROM agents WHERE name=?),datetime('now')))""",
        (agent, agent, agent, agent, agent),
    )
    log_activity(conn, agent, "checkin", "agent", 0)
    return True, None


def get_unread_count(conn, agent):
    row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM messages WHERE to_agent=? AND read_at IS NULL",
        (agent,),
    ).fetchone()
    return row["cnt"]


def get_agent_info(conn, agent):
    row = conn.execute("SELECT role FROM agents WHERE name=?", (agent,)).fetchone()
    return row["role"] if row else "unregistered"


# ── Tasks ───────────────────────────────────────────────


def add_task(
    conn, subject, desc="", priority=0, assignee="", created_by="", parent_id=None
):
    status = "claimed" if assignee else "pending"
    claimed_at = "datetime('now')" if assignee else None

    if assignee:
        cur = conn.execute(
            """INSERT INTO tasks(subject,description,status,owner,created_by,priority,parent_id,claimed_at)
            VALUES(?,?,?,?,?,?,?,datetime('now'))""",
            (subject, desc, status, assignee, created_by, priority, parent_id),
        )
    else:
        cur = conn.execute(
            """INSERT INTO tasks(subject,description,status,owner,created_by,priority,parent_id)
            VALUES(?,?,?,NULL,?,?,?)""",
            (subject, desc, status, created_by, priority, parent_id),
        )
    task_id = cur.lastrowid
    log_activity(conn, created_by, "task_created", "task", task_id, subject)
    return True, task_id


def list_tasks(conn, status=None, owner=None, mine_agent=None, include_all=False):
    clauses = []
    params = []
    if status:
        clauses.append("status=?")
        params.append(status)
    elif not include_all:
        clauses.append("status NOT IN ('done','cancelled')")
    if owner:
        clauses.append("owner=?")
        params.append(owner)
    if mine_agent:
        clauses.append("owner=?")
        params.append(mine_agent)
    where = " AND ".join(clauses) if clauses else "1=1"
    # Active work: status order then oldest first. --all: newest first.
    if include_all:
        order = "id DESC"
    else:
        order = """CASE status
            WHEN 'in_progress' THEN 1 WHEN 'claimed' THEN 2 WHEN 'blocked' THEN 3
            WHEN 'review' THEN 4 WHEN 'pending' THEN 5
            ELSE 6 END, created_at ASC"""
    rows = conn.execute(
        f"""SELECT id, subject,
            CASE status WHEN 'done' THEN '✓' WHEN 'in_progress' THEN '▶' WHEN 'claimed' THEN '◉'
                 WHEN 'blocked' THEN '✗' WHEN 'review' THEN '⟳' ELSE '○' END AS icon,
            status, COALESCE(owner,'-') AS owner,
            CASE priority WHEN 2 THEN '!!!' WHEN 1 THEN '!' ELSE '' END AS pri
            FROM tasks WHERE {where} ORDER BY {order}""",
        params,
    ).fetchall()
    return rows


def get_next_task(conn, agent):
    """Return the single highest-priority actionable task for this agent.

    Priority: tasks already owned by agent (in_progress > claimed) first,
    then unowned pending tasks. Within each group: highest priority, oldest first.
    """
    row = conn.execute(
        """SELECT id, subject, status, priority
        FROM tasks
        WHERE status NOT IN ('done','cancelled','blocked')
          AND (owner=? OR owner IS NULL OR owner='')
        ORDER BY
            CASE WHEN owner=? THEN 0 ELSE 1 END,
            CASE status
                WHEN 'in_progress' THEN 1 WHEN 'claimed' THEN 2
                WHEN 'review' THEN 3 WHEN 'pending' THEN 4
                ELSE 5 END,
            priority DESC,
            created_at ASC
        LIMIT 1""",
        (agent, agent),
    ).fetchone()
    return row


def claim_task(conn, task_id, agent, force=False, meta=None):
    if force:
        cur = conn.execute(
            """UPDATE tasks SET owner=?, status='claimed',
                claimed_at=datetime('now'), updated_at=datetime('now')
            WHERE id=?""",
            (agent, task_id),
        )
    else:
        cur = conn.execute(
            """UPDATE tasks SET owner=?, status='claimed',
                claimed_at=datetime('now'), updated_at=datetime('now')
            WHERE id=? AND (owner IS NULL OR owner='' OR owner=?)""",
            (agent, task_id, agent),
        )
    if cur.rowcount == 1:
        log_activity(conn, agent, "task_claimed", "task", task_id, meta=meta)
        return True, None
    row = conn.execute("SELECT owner FROM tasks WHERE id=?", (task_id,)).fetchone()
    if not row:
        return False, "not found"
    return False, f"already claimed by {row['owner']}"


def start_task(conn, task_id, agent, meta=None):
    cur = conn.execute(
        "UPDATE tasks SET status='in_progress', updated_at=datetime('now') WHERE id=? AND owner=?",
        (task_id, agent),
    )
    if cur.rowcount == 0:
        row = conn.execute("SELECT owner FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not row:
            return False, "not found"
        return False, f"not owned by you (owner: {row['owner']})"
    conn.execute("UPDATE agents SET status='busy' WHERE name=?", (agent,))
    log_activity(conn, agent, "task_started", "task", task_id, meta=meta)
    return True, None


def complete_task(conn, task_id, agent, note="", meta=None, force=False):
    if force:
        cur = conn.execute(
            """UPDATE tasks SET status='done', completed_at=datetime('now'),
                updated_at=datetime('now')
            WHERE id=? AND status != 'done'""",
            (task_id,),
        )
    else:
        cur = conn.execute(
            """UPDATE tasks SET status='done', completed_at=datetime('now'),
                updated_at=datetime('now')
            WHERE id=? AND owner=? AND status != 'done'""",
            (task_id, agent),
        )
    if cur.rowcount == 0:
        row = conn.execute(
            "SELECT id, owner, status FROM tasks WHERE id=?", (task_id,)
        ).fetchone()
        if not row:
            return False, "not found"
        if row["status"] == "done":
            return True, "already done"
        if row["owner"] != agent:
            return (
                False,
                f"not owned by you (owner: {row['owner'] or 'unassigned'}). Use --force to override",
            )
    conn.execute("UPDATE agents SET status='idle' WHERE name=?", (agent,))
    log_activity(conn, agent, "task_completed", "task", task_id, note, meta=meta)
    if note:
        conn.execute(
            "INSERT INTO messages(from_agent,task_id,body,msg_type) VALUES(?,?,?,'status')",
            (agent, task_id, note),
        )
    return True, None


def cancel_task(conn, task_id, agent, meta=None):
    cur = conn.execute(
        """UPDATE tasks SET status='cancelled', updated_at=datetime('now')
        WHERE id=? AND status NOT IN ('done','cancelled')""",
        (task_id,),
    )
    if cur.rowcount == 0:
        row = conn.execute("SELECT status FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not row:
            return False, "not found"
        return True, f"already {row['status']}"
    log_activity(conn, agent, "task_cancelled", "task", task_id, meta=meta)
    return True, None


def review_task(conn, task_id, agent, meta=None):
    cur = conn.execute(
        "UPDATE tasks SET status='review', updated_at=datetime('now') WHERE id=? AND owner=?",
        (task_id, agent),
    )
    if cur.rowcount == 0:
        row = conn.execute("SELECT owner FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not row:
            return False, "not found"
        return False, f"not owned by you (owner: {row['owner']})"
    log_activity(conn, agent, "task_reviewed", "task", task_id, meta=meta)
    return True, None


def block_task(conn, task_id, blocked_by_id, meta=None):
    try:
        conn.execute(
            "INSERT INTO task_deps(task_id, blocked_by) VALUES(?,?)",
            (task_id, blocked_by_id),
        )
        conn.execute(
            "UPDATE tasks SET status='blocked', updated_at=datetime('now') WHERE id=?",
            (task_id,),
        )
        log_activity(
            conn,
            AGENT,
            "task_blocked",
            "task",
            task_id,
            f"by #{blocked_by_id}",
            meta=meta,
        )
        return True, None
    except sqlite3.IntegrityError:
        return False, "dependency already exists"


def get_blockers(conn, task_id):
    rows = conn.execute(
        """SELECT d.blocked_by AS id, t.subject, t.status
        FROM task_deps d JOIN tasks t ON t.id = d.blocked_by
        WHERE d.task_id=?""",
        (task_id,),
    ).fetchall()
    return rows


def get_board(conn):
    result = {}
    for status in ("pending", "claimed", "in_progress", "review", "blocked", "done"):
        rows = conn.execute(
            """SELECT id, subject, owner, priority FROM tasks
            WHERE status=? ORDER BY priority DESC, id LIMIT 10""",
            (status,),
        ).fetchall()
        count = conn.execute(
            "SELECT COUNT(*) AS cnt FROM tasks WHERE status=?", (status,)
        ).fetchone()["cnt"]
        if count > 0:
            result[status] = {"count": count, "tasks": rows}
    return result


# ── Messages ────────────────────────────────────────────


def send_message(conn, from_agent, to_agent, body, task_id=None, msg_type="comment"):
    conn.execute(
        "INSERT INTO messages(from_agent,to_agent,task_id,body,msg_type) VALUES(?,?,?,?,?)",
        (from_agent, to_agent, task_id, body, msg_type),
    )
    log_activity(
        conn, from_agent, "message_sent", "message", 0, f"to:{to_agent} type:{msg_type}"
    )
    return True, None


def broadcast(conn, from_agent, body):
    conn.execute(
        "INSERT INTO messages(from_agent,to_agent,body,msg_type) VALUES(?,NULL,?,'alert')",
        (from_agent, body),
    )
    log_activity(conn, from_agent, "broadcast", "message", 0, body)
    return True, None


def get_inbox(conn, agent, unread_only=False):
    where = "(to_agent=? OR to_agent IS NULL)"
    params = [agent]
    if unread_only:
        where += " AND read_at IS NULL"
    rows = conn.execute(
        f"""SELECT id, from_agent, body, msg_type,
            CASE WHEN read_at IS NULL THEN '●' ELSE '' END AS new,
            substr(created_at,1,16) AS at
        FROM messages WHERE {where} ORDER BY created_at DESC LIMIT 20""",
        params,
    ).fetchall()
    return rows


def mark_messages_read(conn, agent, message_ids=None):
    if message_ids:
        placeholders = ",".join("?" for _ in message_ids)
        conn.execute(
            f"UPDATE messages SET read_at=datetime('now') WHERE id IN ({placeholders}) AND read_at IS NULL",
            message_ids,
        )
    else:
        conn.execute(
            "UPDATE messages SET read_at=datetime('now') WHERE to_agent=? AND read_at IS NULL",
            (agent,),
        )


# ── Fleet ───────────────────────────────────────────────


def get_fleet(conn):
    rows = conn.execute(
        """SELECT name, role,
            CASE status WHEN 'busy' THEN '▶ busy' WHEN 'idle' THEN '○ idle' ELSE '✗ offline' END AS status,
            COALESCE((SELECT subject FROM tasks WHERE owner=agents.name AND status='in_progress' LIMIT 1), '-') AS working_on,
            substr(last_seen,1,16) AS last_seen
        FROM agents ORDER BY status, name"""
    ).fetchall()
    return rows


# ── Feed ────────────────────────────────────────────────


def get_feed(conn, limit=20, agent_filter=None):
    where = "1=1"
    params = []
    if agent_filter:
        where = "agent=?"
        params.append(agent_filter)
    params.append(limit)
    rows = conn.execute(
        f"""SELECT substr(created_at,1,16) AS at, agent, action, detail, meta
        FROM activity WHERE {where} ORDER BY id DESC LIMIT ?""",
        params,
    ).fetchall()
    return rows


def get_summary(conn):
    agents = conn.execute("SELECT name, status, role FROM agents").fetchall()
    open_count = conn.execute(
        "SELECT COUNT(*) AS cnt FROM tasks WHERE status NOT IN ('done','cancelled')"
    ).fetchone()["cnt"]
    in_progress = conn.execute(
        "SELECT COUNT(*) AS cnt FROM tasks WHERE status='in_progress'"
    ).fetchone()["cnt"]
    blocked = conn.execute(
        "SELECT COUNT(*) AS cnt FROM tasks WHERE status='blocked'"
    ).fetchone()["cnt"]
    recent = conn.execute(
        """SELECT substr(created_at,1,16) AS at, agent, action, detail
        FROM activity ORDER BY id DESC LIMIT 5"""
    ).fetchall()
    return {
        "agents": agents,
        "open": open_count,
        "in_progress": in_progress,
        "blocked": blocked,
        "recent": recent,
    }


# ── API helpers (for Flask) ─────────────────────────────


def get_board_api(conn):
    tasks = conn.execute(
        """SELECT id, subject, description, status, owner, priority,
               created_at, updated_at, claimed_at, completed_at
        FROM tasks
        ORDER BY
            CASE status
                WHEN 'in_progress' THEN 1
                WHEN 'claimed' THEN 2
                WHEN 'pending' THEN 3
                WHEN 'blocked' THEN 4
                WHEN 'review' THEN 5
                WHEN 'done' THEN 6
            END,
            priority DESC, id"""
    ).fetchall()
    agents = conn.execute(
        "SELECT name, role, status, last_seen FROM agents ORDER BY status, name"
    ).fetchall()
    return tasks, agents


def get_task_detail(conn, task_id):
    task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    messages = conn.execute(
        """SELECT id, from_agent, body, msg_type, created_at
        FROM messages WHERE task_id=? ORDER BY created_at""",
        (task_id,),
    ).fetchall()
    return task, messages
