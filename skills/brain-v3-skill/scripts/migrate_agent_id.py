#!/usr/bin/env python3
"""Migrate all memories to a single agent_id."""
import sqlite3
import sys

db_path = sys.argv[1] if len(sys.argv) > 1 else "brain_data.db"
new_agent_id = sys.argv[2] if len(sys.argv) > 2 else "default"

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Show before
c.execute("SELECT DISTINCT agent_id, COUNT(*) FROM memories GROUP BY agent_id")
print("Before:", c.fetchall())

# Migrate
c.execute("UPDATE memories SET agent_id = ?", (new_agent_id,))
conn.commit()

# Show after
c.execute("SELECT DISTINCT agent_id, COUNT(*) FROM memories GROUP BY agent_id")
print("After:", c.fetchall())

conn.close()
print(f"Done! All memories migrated to agent_id='{new_agent_id}'")
