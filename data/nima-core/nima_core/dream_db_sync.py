#!/usr/bin/env python3
"""
Dream Database Sync
===================
Persists dream consolidation outputs (insights, patterns, dream runs)
to both LadybugDB and SQLite so they're searchable and queryable.

The dream engine writes to JSON files. This module reads those outputs
and syncs them into the databases.

Can be called:
  1. After each dream cycle (from dream_consolidation.py)
  2. Standalone to backfill historical dream data
  3. From cron for periodic sync

CRITICAL: LadybugDB requires `conn.execute("LOAD VECTOR")` before any
SET/CREATE/DELETE on tables with FLOAT[512] columns (like MemoryNode).
Without it → SIGSEGV crash. This is handled in _get_ladybug_conn().

Part of nima-core — Living Memory Ecology
"""

import os
import sys
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("nima.dream_db_sync")


# --- Security: Escape function for Cypher queries ---
def _escape_cypher(s: str) -> str:
    """Escape strings for safe use in Cypher queries.
    
    LadybugDB (Kùzu) does NOT support parameterized Cypher queries,
    so string escaping is the only defense against injection.
    
    Backslashes MUST be escaped before single quotes to avoid
    double-escaping (e.g. \\' becoming \\\\' instead of \\').
    
    Must be applied to ALL user-controlled or external data before
    embedding in Cypher query strings.
    
    Args:
        s: String to escape
        
    Returns:
        Escaped string safe for Cypher string literals
    """
    if not isinstance(s, str):
        s = str(s)
    return s.replace("\\", "\\\\").replace("'", "\\'")


# --- Config (all overridable via env vars) ---
NIMA_HOME = os.environ.get("NIMA_HOME", os.path.expanduser("~/.nima"))
NIMA_WORKSPACE = os.environ.get("NIMA_WORKSPACE", os.environ.get(
    "OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")))
BOT_NAME = os.environ.get("NIMA_BOT_NAME", "")

# Data paths
DREAMS_DIR = Path(os.environ.get("NIMA_DREAMS_DIR", ""))
if not DREAMS_DIR.name:
    # Try common locations
    for candidate in [
        Path(NIMA_WORKSPACE) / "lilu_core" / "storage" / "data" / "dreams",
        Path(NIMA_HOME) / "dreams",
        Path(NIMA_WORKSPACE) / "data" / "dreams",
    ]:
        if candidate.exists():
            DREAMS_DIR = candidate
            break
    else:
        DREAMS_DIR = Path(NIMA_HOME) / "dreams"

INSIGHTS_FILE = DREAMS_DIR / "insights.json"
PATTERNS_FILE = DREAMS_DIR / "patterns.json"
DREAM_LOG_FILE = DREAMS_DIR / "dream_log.json"

SQLITE_DB = Path(os.environ.get("NIMA_SQLITE_DB",
    os.path.join(NIMA_HOME, "memory", "graph.sqlite")))
LADYBUG_DB = Path(os.environ.get("NIMA_LADYBUG_DB",
    os.path.join(NIMA_HOME, "memory", "ladybug.lbug")))

# Memory/pruner state files
MEMORY_DIR = Path(os.environ.get("NIMA_MEMORY_DIR",
    os.path.join(NIMA_WORKSPACE, "memory")))
SUPPRESSION_REGISTRY = MEMORY_DIR / "suppression_registry.json"
PRUNER_LOG = MEMORY_DIR / "pruner_log.json"
LUCID_STATE = MEMORY_DIR / "lucid_moments_state.json"


def _get_ladybug_conn():
    """
    Get LadybugDB connection with LOAD VECTOR extension.
    
    CRITICAL: LOAD VECTOR must be called before any SET/CREATE/DELETE
    on tables with FLOAT[512] columns (like MemoryNode). Without it,
    mutations cause SIGSEGV (segfault) in the Kùzu engine.
    """
    try:
        import real_ladybug as lb
    except ImportError:
        # Try venv fallback
        venv_paths = [
            os.path.join(NIMA_WORKSPACE, ".venv", "lib", f"python{v}", "site-packages")
            for v in ["3.11", "3.12", "3.13", "3.14"]
        ]
        for vp in venv_paths:
            if os.path.exists(vp) and vp not in sys.path:
                sys.path.insert(0, vp)
                try:
                    import real_ladybug as lb
                    break
                except ImportError:
                    continue
        else:
            logger.warning("real_ladybug not available")
            return None

    if not LADYBUG_DB.exists():
        return None

    try:
        db = lb.Database(str(LADYBUG_DB))
        conn = lb.Connection(db)
        try:
            conn.execute("LOAD VECTOR")
        except Exception:
            pass  # Extension may not exist yet (read-only is fine)
        return conn
    except RuntimeError as e:
        logger.warning(f"LadybugDB connection failed: {e}")
        return None


def _get_sqlite_conn():
    """Get SQLite connection or None."""
    if SQLITE_DB.exists():
        conn = sqlite3.connect(str(SQLITE_DB))
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    return None


# ==============================================================================
# SQLite Sync Functions
# ==============================================================================

def sync_insights_to_sqlite(conn: sqlite3.Connection, insights: List[Dict]) -> int:
    """Sync insights to SQLite nima_insights table."""
    count = 0
    for ins in insights:
        try:
            conn.execute("""
                INSERT OR REPLACE INTO nima_insights 
                (id, type, content, confidence, sources, domains, timestamp, importance, bot_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ins.get('id', ''),
                ins.get('type', ''),
                ins.get('content', ''),
                ins.get('confidence', 0.5),
                json.dumps(ins.get('sources', [])),
                json.dumps(ins.get('domains', [])),
                ins.get('timestamp', datetime.now().isoformat()),
                ins.get('importance', 0.5),
                BOT_NAME
            ))
            count += 1
        except sqlite3.Error as e:
            logger.error(f"SQLite insight insert failed: {e}")
    conn.commit()
    return count


def sync_patterns_to_sqlite(conn: sqlite3.Connection, patterns: List[Dict]) -> int:
    """Sync patterns to SQLite nima_patterns table."""
    count = 0
    for pat in patterns:
        try:
            conn.execute("""
                INSERT OR REPLACE INTO nima_patterns
                (id, name, description, occurrences, domains, examples, 
                 first_seen, last_seen, strength, bot_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pat.get('id', ''),
                pat.get('name', ''),
                pat.get('description', ''),
                pat.get('occurrences', 1),
                json.dumps(pat.get('domains', [])),
                json.dumps(pat.get('examples', [])),
                pat.get('first_seen', datetime.now().isoformat()),
                pat.get('last_seen', datetime.now().isoformat()),
                pat.get('strength', 0.5),
                BOT_NAME
            ))
            count += 1
        except sqlite3.Error as e:
            logger.error(f"SQLite pattern insert failed: {e}")
    conn.commit()
    return count


def sync_dream_runs_to_sqlite(conn: sqlite3.Connection, sessions: List[Dict]) -> int:
    """Sync dream run logs to SQLite nima_dream_runs table."""
    count = 0
    for sess in sessions:
        try:
            session_id = sess.get('id', '')
            existing = conn.execute(
                "SELECT id FROM nima_dream_runs WHERE session_id = ?", (session_id,)
            ).fetchone()
            if existing:
                continue
            
            conn.execute("""
                INSERT INTO nima_dream_runs
                (session_id, started_at, ended_at, hours, memories_processed,
                 patterns_found, insights_generated, top_domains, dominant_emotion,
                 narrative, bot_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                sess.get('start_time', ''),
                sess.get('end_time', ''),
                sess.get('hours', 0),
                sess.get('memories_processed', 0),
                sess.get('patterns_found', 0),
                sess.get('insights_generated', 0),
                json.dumps(sess.get('top_domains', [])),
                sess.get('dominant_emotion', ''),
                sess.get('summary', sess.get('narrative', '')),
                BOT_NAME
            ))
            count += 1
        except sqlite3.Error as e:
            logger.error(f"SQLite dream run insert failed: {e}")
    conn.commit()
    return count


def sync_pruner_to_sqlite(conn: sqlite3.Connection) -> Dict:
    """Sync suppression registry and pruner logs to SQLite."""
    results = {"suppressed": 0, "pruner_runs": 0, "lucid_moments": 0}
    
    # Sync suppression registry
    if SUPPRESSION_REGISTRY.exists():
        try:
            registry = json.loads(SUPPRESSION_REGISTRY.read_text())
            for mem_id, info in registry.items():
                if isinstance(info, dict):
                    try:
                        conn.execute("""
                            INSERT OR REPLACE INTO nima_suppressed_memories
                            (memory_id, suppressed_at, reason, distillate, expires)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            str(mem_id),
                            info.get('suppressed_at', ''),
                            info.get('reason', ''),
                            info.get('distillate', '')[:500],
                            info.get('expires', '')
                        ))
                        results["suppressed"] += 1
                    except (sqlite3.Error, ValueError):
                        pass
            conn.commit()
        except (json.JSONDecodeError, IOError):
            pass
    
    # Sync pruner log
    if PRUNER_LOG.exists():
        try:
            logs = json.loads(PRUNER_LOG.read_text())
            if isinstance(logs, list):
                for log in logs:
                    ts = log.get('timestamp', '')
                    existing = conn.execute(
                        "SELECT id FROM nima_pruner_runs WHERE timestamp = ?", (ts,)
                    ).fetchone()
                    if not existing:
                        conn.execute("""
                            INSERT INTO nima_pruner_runs 
                            (timestamp, suppressed, distilled, total_registry_size, bot_name)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            ts,
                            log.get('suppressed', 0),
                            log.get('distilled', 0),
                            log.get('candidates', 0),
                            BOT_NAME
                        ))
                        results["pruner_runs"] += 1
                conn.commit()
        except (json.JSONDecodeError, IOError):
            pass
    
    # Sync lucid moments
    if LUCID_STATE.exists():
        try:
            state = json.loads(LUCID_STATE.read_text())
            surfaced_ids = state.get('surfaced_ids', [])
            last_surfaced = state.get('last_surfaced_at', '')
            for mid in surfaced_ids:
                existing = conn.execute(
                    "SELECT id FROM nima_lucid_moments WHERE memory_id = ?", (mid,)
                ).fetchone()
                if not existing:
                    conn.execute("""
                        INSERT INTO nima_lucid_moments 
                        (memory_id, surfaced_at, bot_name)
                        VALUES (?, ?, ?)
                    """, (mid, last_surfaced, BOT_NAME))
                    results["lucid_moments"] += 1
            conn.commit()
        except (json.JSONDecodeError, IOError):
            pass
    
    return results


# ==============================================================================
# LadybugDB Sync Functions
# ==============================================================================

def sync_insights_to_ladybug(conn, insights: List[Dict]) -> int:
    """Sync insights to LadybugDB as InsightNode nodes."""
    count = 0
    for ins in insights:
        try:
            # SECURITY: Escape all external data before embedding in Cypher
            insight_id = _escape_cypher(ins.get('id', ''))
            
            # Check if exists
            r = conn.execute(
                f"MATCH (n:InsightNode) WHERE n.id = '{insight_id}' RETURN count(n) AS cnt"
            )
            if r.get_next()[0] > 0:
                continue
            
            # SECURITY: Escape all fields properly
            content = _escape_cypher(ins.get('content', ''))[:2000]
            domains = _escape_cypher(json.dumps(ins.get('domains', [])))
            sources = _escape_cypher(json.dumps(ins.get('sources', [])))
            ins_type = _escape_cypher(ins.get('type', ''))
            timestamp = _escape_cypher(ins.get('timestamp', ''))
            confidence = float(ins.get('confidence', 0.5))
            importance = float(ins.get('importance', 0.5))
            
            conn.execute(f"""
                CREATE (n:InsightNode {{
                    id: '{insight_id}',
                    content: '{content}',
                    type: '{ins_type}',
                    confidence: {confidence},
                    sources: '{sources}',
                    domains: '{domains}',
                    timestamp: '{timestamp}',
                    importance: {importance},
                    validated: false
                }})
            """)
            count += 1
        except Exception as e:
            logger.error(f"LadybugDB insight insert failed: {e}")
    return count


def sync_patterns_to_ladybug(conn, patterns: List[Dict]) -> int:
    """Sync patterns to LadybugDB as PatternNode nodes."""
    count = 0
    
    # Ensure PatternNode table exists
    try:
        conn.execute("""
            CREATE NODE TABLE IF NOT EXISTS PatternNode (
                id STRING,
                name STRING,
                description STRING,
                occurrences INT64,
                domains STRING,
                examples STRING,
                first_seen STRING,
                last_seen STRING,
                strength DOUBLE,
                PRIMARY KEY (id)
            )
        """)
    except Exception:
        pass
    
    for pat in patterns:
        try:
            # SECURITY: Escape all external data before embedding in Cypher
            pat_id = _escape_cypher(pat.get('id', ''))
            
            try:
                r = conn.execute(
                    f"MATCH (n:PatternNode) WHERE n.id = '{pat_id}' RETURN count(n) AS cnt"
                )
                if r.get_next()[0] > 0:
                    # SECURITY: Escape update fields
                    occurrences = int(pat.get('occurrences', 1))
                    last_seen = _escape_cypher(pat.get('last_seen', ''))
                    strength = float(pat.get('strength', 0.5))
                    
                    conn.execute(f"""
                        MATCH (n:PatternNode) WHERE n.id = '{pat_id}'
                        SET n.occurrences = {occurrences},
                            n.last_seen = '{last_seen}',
                            n.strength = {strength}
                    """)
                    count += 1
                    continue
            except Exception:
                pass
            
            # SECURITY: Escape all fields for CREATE
            name = _escape_cypher(pat.get('name', ''))
            desc = _escape_cypher(pat.get('description', ''))[:2000]
            domains = _escape_cypher(json.dumps(pat.get('domains', [])))
            examples = _escape_cypher(json.dumps(pat.get('examples', [])))
            first_seen = _escape_cypher(pat.get('first_seen', ''))
            last_seen = _escape_cypher(pat.get('last_seen', ''))
            occurrences = int(pat.get('occurrences', 1))
            strength = float(pat.get('strength', 0.5))
            
            conn.execute(f"""
                CREATE (n:PatternNode {{
                    id: '{pat_id}',
                    name: '{name}',
                    description: '{desc}',
                    occurrences: {occurrences},
                    domains: '{domains}',
                    examples: '{examples}',
                    first_seen: '{first_seen}',
                    last_seen: '{last_seen}',
                    strength: {strength}
                }})
            """)
            count += 1
        except Exception as e:
            logger.error(f"LadybugDB pattern insert failed: {e}")
    return count


def sync_dream_narratives_to_ladybug(conn, dream_files: List[Path]) -> int:
    """Sync dream narrative markdown files as DreamNode in LadybugDB."""
    count = 0
    
    try:
        conn.execute("""
            CREATE NODE TABLE IF NOT EXISTS DreamNode (
                id STRING,
                date STRING,
                narrative STRING,
                source_count INT64,
                created_at STRING,
                PRIMARY KEY (id)
            )
        """)
    except Exception:
        pass
    
    for dream_file in dream_files:
        try:
            # SECURITY: Escape filename-derived IDs
            date_str = _escape_cypher(dream_file.stem)
            dream_id = _escape_cypher(f"dream_{date_str}")
            
            try:
                r = conn.execute(
                    f"MATCH (n:DreamNode) WHERE n.id = '{dream_id}' RETURN count(n) AS cnt"
                )
                if r.get_next()[0] > 0:
                    continue
            except Exception:
                pass
            
            # SECURITY: Escape all external content
            content = dream_file.read_text()
            narrative = content.split("## Source Memories")[0].strip()
            narrative = _escape_cypher(narrative)[:2000]
            source_count = content.count("- [")
            created_at = _escape_cypher(datetime.now().isoformat())
            
            conn.execute(f"""
                CREATE (n:DreamNode {{
                    id: '{dream_id}',
                    date: '{date_str}',
                    narrative: '{narrative}',
                    source_count: {source_count},
                    created_at: '{created_at}'
                }})
            """)
            count += 1
        except Exception as e:
            logger.error(f"LadybugDB dream insert failed for {dream_file}: {e}")
    return count


def sync_pruner_to_ladybug(conn) -> Dict:
    """
    Sync suppression registry → LadybugDB ghost marks on MemoryNodes.
    
    CRITICAL: The connection MUST have LOAD VECTOR called first.
    This is handled by _get_ladybug_conn().
    
    The suppression registry format is a dict keyed by string node IDs:
        {"1234": {"suppressed_at": "...", "reason": "distilled", ...}}
    Extract IDs via: [int(k) for k in registry.keys() if k.isdigit()]
    
    Ghost-marking is batched in groups of 200 to avoid query size limits.
    """
    results = {"ghosted": 0}
    if not conn:
        return results
    
    try:
        if not SUPPRESSION_REGISTRY.exists():
            return results
        
        registry = json.loads(SUPPRESSION_REGISTRY.read_text())
        suppressed_ids = [int(k) for k in registry.keys() if k.isdigit()]
        if not suppressed_ids:
            return results
        
        total_ghosted = 0
        batch_size = 200
        for i in range(0, len(suppressed_ids), batch_size):
            batch = suppressed_ids[i:i + batch_size]
            ids_str = "[" + ",".join(str(x) for x in batch) + "]"
            try:
                # Count actual non-ghost nodes before marking, to avoid overcounting
                count_rows = list(conn.execute(f"""
                    MATCH (n:MemoryNode)
                    WHERE n.id IN {ids_str} AND n.is_ghost = false
                    RETURN count(n)
                """))
                actual_count = int(count_rows[0][0]) if count_rows else 0
                conn.execute(f"""
                    MATCH (n:MemoryNode)
                    WHERE n.id IN {ids_str} AND n.is_ghost = false
                    SET n.is_ghost = true, n.dismissal_count = n.dismissal_count + 1
                """)
                total_ghosted += actual_count
            except Exception as batch_err:
                logger.error(f"Ghost batch {i//batch_size} failed: {batch_err}")
        results["ghosted"] = total_ghosted
        logger.info(f"Synced {total_ghosted} suppressed IDs to LadybugDB ghost marks")
    except Exception as e:
        logger.error(f"Failed to sync pruner to LadybugDB: {e}")
    
    return results


# ==============================================================================
# Main Orchestrator
# ==============================================================================

def sync_all(verbose: bool = True) -> Dict:
    """
    Full sync: read JSON files + dream narratives → write to both databases.
    
    Returns dict with counts of synced items per database.
    """
    results = {
        "sqlite": {"insights": 0, "patterns": 0, "dream_runs": 0,
                   "suppressed": 0, "pruner_runs": 0, "lucid_moments": 0},
        "ladybug": {"insights": 0, "patterns": 0, "dreams": 0, "ghosted": 0},
    }
    
    # Load source data
    insights = []
    if INSIGHTS_FILE.exists():
        try:
            data = json.loads(INSIGHTS_FILE.read_text())
            insights = data if isinstance(data, list) else data.get("insights", [])
        except (json.JSONDecodeError, IOError):
            pass
    
    patterns = []
    if PATTERNS_FILE.exists():
        try:
            data = json.loads(PATTERNS_FILE.read_text())
            patterns = data if isinstance(data, list) else data.get("patterns", [])
        except (json.JSONDecodeError, IOError):
            pass
    
    sessions = []
    if DREAM_LOG_FILE.exists():
        try:
            data = json.loads(DREAM_LOG_FILE.read_text())
            sessions = data if isinstance(data, list) else data.get("sessions", [])
        except (json.JSONDecodeError, IOError):
            pass
    
    dream_files = sorted(DREAMS_DIR.glob("*.md")) if DREAMS_DIR.exists() else []
    
    if verbose:
        print(f"📊 Source data: {len(insights)} insights, {len(patterns)} patterns, "
              f"{len(sessions)} dream runs, {len(dream_files)} dream narratives")
    
    # Sync to SQLite
    sqlite_conn = _get_sqlite_conn()
    if sqlite_conn:
        try:
            results["sqlite"]["insights"] = sync_insights_to_sqlite(sqlite_conn, insights)
            results["sqlite"]["patterns"] = sync_patterns_to_sqlite(sqlite_conn, patterns)
            results["sqlite"]["dream_runs"] = sync_dream_runs_to_sqlite(sqlite_conn, sessions)
            pruner_results = sync_pruner_to_sqlite(sqlite_conn)
            results["sqlite"].update(pruner_results)
            
            if verbose:
                s = results["sqlite"]
                print(f"✅ SQLite: {s['insights']} insights, {s['patterns']} patterns, "
                      f"{s['dream_runs']} dream runs, {s['suppressed']} suppressed, "
                      f"{s['lucid_moments']} lucid moments")
        finally:
            sqlite_conn.close()
    elif verbose:
        print("⚠️ SQLite not available")
    
    # Sync to LadybugDB
    lb_conn = _get_ladybug_conn()
    if lb_conn:
        try:
            results["ladybug"]["insights"] = sync_insights_to_ladybug(lb_conn, insights)
            results["ladybug"]["patterns"] = sync_patterns_to_ladybug(lb_conn, patterns)
            results["ladybug"]["dreams"] = sync_dream_narratives_to_ladybug(lb_conn, dream_files)
            pruner_lb = sync_pruner_to_ladybug(lb_conn)
            results["ladybug"].update(pruner_lb)
            
            if verbose:
                lb = results["ladybug"]
                print(f"✅ LadybugDB: {lb['insights']} insights, {lb['patterns']} patterns, "
                      f"{lb['dreams']} dreams, {lb['ghosted']} ghosted")
        except Exception as e:
            if verbose:
                print(f"⚠️ LadybugDB sync error: {e}")
        finally:
            try:
                lb_conn.close()
            except Exception:
                pass
    elif verbose:
        print("⚠️ LadybugDB not available")
    
    # Auto-commit memory changes after sync completes
    try:
        from nima_core.memory_git import commit_memory
        commit_memory("dream", f"Synced {results['sqlite']['insights']} insights, {results['sqlite']['patterns']} patterns to databases")
    except Exception:
        pass
    
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Sync dream outputs to databases")
    parser.add_argument("--quiet", "-q", action="store_true")
    args = parser.parse_args()
    results = sync_all(verbose=not args.quiet)
    if not args.quiet:
        print(f"\n🌙 Dream DB sync complete")
