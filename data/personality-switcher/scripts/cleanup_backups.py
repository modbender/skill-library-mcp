#!/usr/bin/env python3
"""
Clean up old personality backups.
Usage: python3 cleanup_backups.py [--keep N] [--days D]

Options:
  --keep N   Keep the N most recent backups (default: 10)
  --days D   Also delete backups older than D days
"""

import sys
import json
import argparse
from pathlib import Path

# Add scripts dir to path for utils import
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    get_workspace, cleanup_old_backups, get_backup_info
)

def cleanup_backups(keep_count=10, max_age_days=None):
    """Perform cleanup and return result."""
    
    workspace = get_workspace()
    
    # Get backup info before cleanup
    backups_before = get_backup_info(workspace)
    
    # Perform cleanup
    deleted_count, error = cleanup_old_backups(workspace, keep_count=keep_count, max_age_days=max_age_days)
    
    # Get backup info after cleanup
    backups_after = get_backup_info(workspace)
    
    if error:
        return {
            "status": "error",
            "message": error,
            "code": "cleanup_failed"
        }
    
    return {
        "status": "success",
        "message": f"Cleanup complete. Deleted {deleted_count} old backup(s).",
        "deleted_count": deleted_count,
        "backups_before": len(backups_before),
        "backups_after": len(backups_after),
        "keep_count": keep_count,
        "max_age_days": max_age_days,
        "remaining_backups": backups_after
    }

def main():
    parser = argparse.ArgumentParser(description="Clean up old personality backups")
    parser.add_argument("--keep", type=int, default=10, help="Keep N most recent backups (default: 10)")
    parser.add_argument("--days", type=int, default=None, help="Also delete backups older than D days")
    
    args = parser.parse_args()
    
    result = cleanup_backups(keep_count=args.keep, max_age_days=args.days)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
