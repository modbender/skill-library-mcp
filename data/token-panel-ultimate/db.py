"""
Budget Collector - SQLite Database Schema

Stores usage data from multiple AI providers:
- Anthropic (Claude)
- Manus AI
- Google Gemini
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

DEFAULT_DB_PATH = Path.home() / ".openclaw" / "data" / "budget.db"


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Get a database connection, creating tables if needed."""
    path = db_path or DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection):
    """Initialize database schema."""
    conn.executescript("""
        -- Provider usage records (tokens, costs)
        CREATE TABLE IF NOT EXISTS usage_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT NOT NULL,           -- 'anthropic', 'gemini', 'openai'
            model TEXT,                       -- 'claude-opus-4', 'gemini-2.5-pro', etc.
            session_key TEXT,                 -- OpenClaw session identifier
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            cache_read_tokens INTEGER DEFAULT 0,
            cache_write_tokens INTEGER DEFAULT 0,
            cost_usd REAL DEFAULT 0,
            recorded_at TEXT NOT NULL,        -- ISO timestamp
            metadata TEXT,                    -- JSON for extra fields
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_usage_provider ON usage_records(provider);
        CREATE INDEX IF NOT EXISTS idx_usage_recorded ON usage_records(recorded_at);
        CREATE INDEX IF NOT EXISTS idx_usage_session ON usage_records(session_key);
        
        -- Manus task records (credit-based)
        CREATE TABLE IF NOT EXISTS manus_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT UNIQUE NOT NULL,
            credits_used INTEGER NOT NULL,
            status TEXT,                      -- 'completed', 'error', 'running'
            description TEXT,
            started_at TEXT,
            completed_at TEXT,
            metadata TEXT,                    -- JSON for extra fields
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_manus_task ON manus_tasks(task_id);
        CREATE INDEX IF NOT EXISTS idx_manus_completed ON manus_tasks(completed_at);
        
        -- Budget configuration
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT UNIQUE NOT NULL,
            monthly_limit REAL,               -- USD for tokens, credits for Manus
            alert_threshold REAL DEFAULT 0.8, -- Alert at 80%
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Daily aggregates (for fast dashboard queries)
        CREATE TABLE IF NOT EXISTS daily_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,               -- YYYY-MM-DD
            provider TEXT NOT NULL,
            total_input_tokens INTEGER DEFAULT 0,
            total_output_tokens INTEGER DEFAULT 0,
            total_cost_usd REAL DEFAULT 0,
            total_credits INTEGER DEFAULT 0,  -- For Manus
            request_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, provider)
        );
        
        CREATE INDEX IF NOT EXISTS idx_daily_date ON daily_summary(date);
    """)
    conn.commit()


# ============================================================================
# Usage Records (Anthropic, Gemini, OpenAI)
# ============================================================================

def record_usage(
    conn: sqlite3.Connection,
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float = 0,
    session_key: str = None,
    cache_read: int = 0,
    cache_write: int = 0,
    metadata: dict = None,
    recorded_at: datetime = None,
):
    """Record a usage event from a provider."""
    ts = (recorded_at or datetime.utcnow()).isoformat()
    conn.execute("""
        INSERT INTO usage_records 
        (provider, model, session_key, input_tokens, output_tokens, 
         cache_read_tokens, cache_write_tokens, cost_usd, recorded_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        provider, model, session_key, input_tokens, output_tokens,
        cache_read, cache_write, cost_usd, ts,
        json.dumps(metadata) if metadata else None
    ))
    conn.commit()
    
    # Update daily summary
    date = ts[:10]
    conn.execute("""
        INSERT INTO daily_summary (date, provider, total_input_tokens, total_output_tokens, total_cost_usd, request_count)
        VALUES (?, ?, ?, ?, ?, 1)
        ON CONFLICT(date, provider) DO UPDATE SET
            total_input_tokens = total_input_tokens + excluded.total_input_tokens,
            total_output_tokens = total_output_tokens + excluded.total_output_tokens,
            total_cost_usd = total_cost_usd + excluded.total_cost_usd,
            request_count = request_count + 1
    """, (date, provider, input_tokens, output_tokens, cost_usd))
    conn.commit()


# ============================================================================
# Manus Tasks
# ============================================================================

def record_manus_task(
    conn: sqlite3.Connection,
    task_id: str,
    credits_used: int,
    status: str = "completed",
    description: str = None,
    started_at: datetime = None,
    completed_at: datetime = None,
    metadata: dict = None,
):
    """Record a Manus task completion."""
    now = datetime.utcnow().isoformat()
    conn.execute("""
        INSERT INTO manus_tasks (task_id, credits_used, status, description, started_at, completed_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(task_id) DO UPDATE SET
            credits_used = excluded.credits_used,
            status = excluded.status,
            completed_at = excluded.completed_at
    """, (
        task_id, credits_used, status, description,
        started_at.isoformat() if started_at else None,
        (completed_at or datetime.utcnow()).isoformat(),
        json.dumps(metadata) if metadata else None
    ))
    conn.commit()
    
    # Update daily summary
    date = now[:10]
    conn.execute("""
        INSERT INTO daily_summary (date, provider, total_credits, request_count)
        VALUES (?, 'manus', ?, 1)
        ON CONFLICT(date, provider) DO UPDATE SET
            total_credits = total_credits + excluded.total_credits,
            request_count = request_count + 1
    """, (date, credits_used))
    conn.commit()


# ============================================================================
# Budget Management
# ============================================================================

def set_budget(conn: sqlite3.Connection, provider: str, monthly_limit: float, alert_threshold: float = 0.8):
    """Set or update a monthly budget for a provider."""
    conn.execute("""
        INSERT INTO budgets (provider, monthly_limit, alert_threshold, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(provider) DO UPDATE SET
            monthly_limit = excluded.monthly_limit,
            alert_threshold = excluded.alert_threshold,
            updated_at = CURRENT_TIMESTAMP
    """, (provider, monthly_limit, alert_threshold))
    conn.commit()


def get_budget(conn: sqlite3.Connection, provider: str) -> Optional[dict]:
    """Get budget for a provider."""
    row = conn.execute(
        "SELECT * FROM budgets WHERE provider = ?", (provider,)
    ).fetchone()
    return dict(row) if row else None


# ============================================================================
# Queries
# ============================================================================

def get_monthly_summary(conn: sqlite3.Connection, year: int, month: int) -> list[dict]:
    """Get summary for a specific month."""
    date_prefix = f"{year:04d}-{month:02d}"
    rows = conn.execute("""
        SELECT 
            provider,
            SUM(total_input_tokens) as input_tokens,
            SUM(total_output_tokens) as output_tokens,
            SUM(total_cost_usd) as cost_usd,
            SUM(total_credits) as credits,
            SUM(request_count) as requests
        FROM daily_summary
        WHERE date LIKE ?
        GROUP BY provider
    """, (f"{date_prefix}%",)).fetchall()
    return [dict(r) for r in rows]


def get_daily_breakdown(conn: sqlite3.Connection, provider: str, days: int = 30) -> list[dict]:
    """Get daily breakdown for a provider."""
    rows = conn.execute("""
        SELECT * FROM daily_summary
        WHERE provider = ?
        ORDER BY date DESC
        LIMIT ?
    """, (provider, days)).fetchall()
    return [dict(r) for r in rows]


def get_budget_status(conn: sqlite3.Connection) -> list[dict]:
    """Get current budget status for all providers."""
    now = datetime.utcnow()
    year, month = now.year, now.month
    
    results = []
    for budget in conn.execute("SELECT * FROM budgets").fetchall():
        budget = dict(budget)
        provider = budget["provider"]
        
        # Get month-to-date usage
        summary = conn.execute("""
            SELECT 
                SUM(total_cost_usd) as cost_usd,
                SUM(total_credits) as credits
            FROM daily_summary
            WHERE provider = ? AND date LIKE ?
        """, (provider, f"{year:04d}-{month:02d}%")).fetchone()
        
        if provider == "manus":
            used = (summary["credits"] or 0) if summary else 0
        else:
            used = (summary["cost_usd"] or 0) if summary else 0
        
        limit = budget["monthly_limit"] or 0
        pct = (used / limit * 100) if limit > 0 else 0
        
        results.append({
            "provider": provider,
            "limit": limit,
            "used": used,
            "remaining": max(0, limit - used),
            "percent": round(pct, 1),
            "status": "critical" if pct >= 100 else "warning" if pct >= budget["alert_threshold"] * 100 else "ok",
            "alert_threshold": budget["alert_threshold"],
        })
    
    return results


if __name__ == "__main__":
    # Test the database
    conn = get_connection()
    print("Database initialized at:", DEFAULT_DB_PATH)
    
    # Set some test budgets
    set_budget(conn, "anthropic", 100.0)
    set_budget(conn, "manus", 500)
    set_budget(conn, "gemini", 50.0)
    
    print("Budgets:", get_budget_status(conn))
