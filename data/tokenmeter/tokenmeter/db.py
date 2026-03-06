"""SQLite database for storing usage data."""

import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class UsageRecord:
    """A single usage record."""
    id: Optional[int]
    timestamp: datetime
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    source: str  # 'manual', 'import', 'proxy'
    app: Optional[str]  # Application name (e.g., 'claude-code', 'cursor')
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0


DB_PATH = Path.home() / ".tokenmeter" / "usage.db"


def get_db_path() -> Path:
    """Get the database path, creating directory if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return DB_PATH


def init_db() -> sqlite3.Connection:
    """Initialize the database and return connection."""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            input_tokens INTEGER NOT NULL,
            output_tokens INTEGER NOT NULL,
            cost REAL NOT NULL,
            source TEXT NOT NULL DEFAULT 'manual',
            app TEXT,
            cache_read_tokens INTEGER DEFAULT 0,
            cache_write_tokens INTEGER DEFAULT 0
        )
    """)
    
    # Migration: Add cache columns if they don't exist (for existing databases)
    try:
        conn.execute("ALTER TABLE usage ADD COLUMN cache_read_tokens INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        conn.execute("ALTER TABLE usage ADD COLUMN cache_write_tokens INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON usage(timestamp)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_usage_provider ON usage(provider)
    """)
    
    conn.commit()
    return conn


def log_usage(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost: float,
    source: str = "manual",
    app: Optional[str] = None,
    timestamp: Optional[datetime] = None,
    cache_read_tokens: int = 0,
    cache_write_tokens: int = 0,
) -> int:
    """Log a usage record and return the ID."""
    conn = init_db()
    ts = timestamp or datetime.now()
    
    cursor = conn.execute(
        """
        INSERT INTO usage (timestamp, provider, model, input_tokens, output_tokens, cost, source, app, cache_read_tokens, cache_write_tokens)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (ts.isoformat(), provider, model, input_tokens, output_tokens, cost, source, app, cache_read_tokens, cache_write_tokens)
    )
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id


def get_usage(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    min_cost: Optional[float] = None,
    exclude_zero_cost: bool = False,
) -> list[UsageRecord]:
    """Query usage records with optional filters."""
    conn = init_db()
    
    query = "SELECT * FROM usage WHERE 1=1"
    params = []
    
    if start:
        query += " AND timestamp >= ?"
        params.append(start.isoformat())
    if end:
        query += " AND timestamp <= ?"
        params.append(end.isoformat())
    if provider:
        query += " AND provider = ?"
        params.append(provider)
    if model:
        query += " AND model = ?"
        params.append(model)
    if exclude_zero_cost:
        query += " AND cost > 0"
    elif min_cost is not None:
        query += " AND cost >= ?"
        params.append(min_cost)
    
    query += " ORDER BY timestamp DESC"
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    records = []
    for row in rows:
        # Handle cache tokens which may not exist in older databases
        try:
            cache_read = row["cache_read_tokens"] or 0
        except (KeyError, IndexError):
            cache_read = 0
        try:
            cache_write = row["cache_write_tokens"] or 0
        except (KeyError, IndexError):
            cache_write = 0
        
        records.append(UsageRecord(
            id=row["id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            provider=row["provider"],
            model=row["model"],
            input_tokens=row["input_tokens"],
            output_tokens=row["output_tokens"],
            cost=row["cost"],
            source=row["source"],
            app=row["app"],
            cache_read_tokens=cache_read,
            cache_write_tokens=cache_write,
        ))
    return records


def get_summary(
    period: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    provider: Optional[str] = None,
    min_cost: Optional[float] = None,
    exclude_zero_cost: bool = False,
) -> dict:
    """Get aggregated summary for a time period or custom range."""
    now = datetime.now()
    
    # Use explicit start/end if provided
    if start is None and period:
        if period == "day":
            start = datetime.combine(date.today(), datetime.min.time())
        elif period == "week":
            start = datetime.combine(date.today() - timedelta(days=7), datetime.min.time())
        elif period == "month":
            start = datetime.combine(date.today() - timedelta(days=30), datetime.min.time())
    
    # Get filtered records
    records = get_usage(start=start, end=end, provider=provider, min_cost=min_cost, exclude_zero_cost=exclude_zero_cost)
    
    # Count excluded for display
    if exclude_zero_cost or min_cost is not None:
        all_records = get_usage(start=start, end=end, provider=provider)
        excluded_count = len(all_records) - len(records)
    else:
        excluded_count = 0
    
    # Aggregate by provider
    by_provider = {}
    for r in records:
        if r.provider not in by_provider:
            by_provider[r.provider] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "total_tokens": 0,
                "cost": 0.0,
                "requests": 0,
            }
        by_provider[r.provider]["input_tokens"] += r.input_tokens
        by_provider[r.provider]["output_tokens"] += r.output_tokens
        by_provider[r.provider]["cache_read_tokens"] += r.cache_read_tokens
        by_provider[r.provider]["cache_write_tokens"] += r.cache_write_tokens
        by_provider[r.provider]["total_tokens"] += r.input_tokens + r.output_tokens
        by_provider[r.provider]["cost"] += r.cost
        by_provider[r.provider]["requests"] += 1
    
    # Totals
    total_input = sum(r.input_tokens for r in records)
    total_output = sum(r.output_tokens for r in records)
    total_cache_read = sum(r.cache_read_tokens for r in records)
    total_cache_write = sum(r.cache_write_tokens for r in records)
    total_cost = sum(r.cost for r in records)
    
    return {
        "period": period,
        "start": start.isoformat() if start else None,
        "end": now.isoformat(),
        "by_provider": by_provider,
        "totals": {
            "input_tokens": total_input,
            "output_tokens": total_output,
            "cache_read_tokens": total_cache_read,
            "cache_write_tokens": total_cache_write,
            "total_tokens": total_input + total_output,
            "cost": total_cost,
            "requests": len(records),
        },
        "excluded_count": excluded_count,
    }


def get_model_breakdown(
    period: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    min_cost: Optional[float] = None,
    exclude_zero_cost: bool = False,
) -> dict:
    """Get usage breakdown by model."""
    now = datetime.now()
    
    # Use explicit start/end if provided
    if start is None and period:
        if period == "day":
            start = datetime.combine(date.today(), datetime.min.time())
        elif period == "week":
            start = datetime.combine(date.today() - timedelta(days=7), datetime.min.time())
        elif period == "month":
            start = datetime.combine(date.today() - timedelta(days=30), datetime.min.time())
    
    records = get_usage(start=start, end=end, min_cost=min_cost, exclude_zero_cost=exclude_zero_cost)
    
    # Count excluded
    if exclude_zero_cost or min_cost is not None:
        all_records = get_usage(start=start, end=end)
        excluded_count = len(all_records) - len(records)
    else:
        excluded_count = 0
    
    # Aggregate by model
    by_model = {}
    for r in records:
        key = f"{r.provider}/{r.model}"
        if key not in by_model:
            by_model[key] = {
                "provider": r.provider,
                "model": r.model,
                "input_tokens": 0,
                "output_tokens": 0,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "cost": 0.0,
                "requests": 0,
            }
        by_model[key]["input_tokens"] += r.input_tokens
        by_model[key]["output_tokens"] += r.output_tokens
        by_model[key]["cache_read_tokens"] += r.cache_read_tokens
        by_model[key]["cache_write_tokens"] += r.cache_write_tokens
        by_model[key]["cost"] += r.cost
        by_model[key]["requests"] += 1
    
    return {
        "period": period,
        "models": list(by_model.values()),
        "excluded_count": excluded_count,
    }
