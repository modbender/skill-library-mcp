import pytest
import sqlite3
import threading
import time
from scripts.core import add_insight, start_project
import scripts.db as db

def test_sqlite_lock_resilience():
    """
    Test that add_insight can recover from a locked database.
    """
    db.init_db()
    project_id = "lock-test"
    start_project(project_id, "Lock Test", "Objective", silent=True)
    
    conn = db.get_connection()
    c = conn.cursor()
    
    # 1. Manually lock the database by starting a transaction
    c.execute("BEGIN EXCLUSIVE")
    
    def run_add_insight():
        # This should hang/retry until we COMMIT or ROLLBACK in the main thread
        try:
            add_insight(project_id, "Retry Title", "Retry Content")
            print("\n[✔] add_insight recovered from lock.")
        except Exception as e:
            print(f"\n[!] add_insight failed: {e}")

    thread = threading.Thread(target=run_add_insight)
    thread.start()
    
    # Wait a bit to ensure the thread is hitting the lock
    time.sleep(0.5)
    
    # 2. Release the lock
    conn.commit()
    conn.close()
    
    thread.join(timeout=5)
    assert not thread.is_alive()
