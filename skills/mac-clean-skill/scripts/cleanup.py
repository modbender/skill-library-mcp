#!/usr/bin/env python3
import os
import shutil
import time
import argparse
from datetime import datetime, timedelta

def get_file_age_days(filepath):
    """Returns the age of the file in days."""
    return (time.time() - os.path.getmtime(filepath)) / (24 * 3600)

def cleanup_directory(directory, max_age_days=0, dry_run=True):
    """
    Cleans up files in a directory.
    If max_age_days > 0, only deletes files older than that.
    """
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return

    print(f"Scanning {directory}...")
    count = 0
    size_freed = 0

    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            try:
                if os.path.isfile(item_path):
                    age = get_file_age_days(item_path)
                    if max_age_days > 0 and age < max_age_days:
                        continue
                    
                    size_freed += os.path.getsize(item_path)
                    if dry_run:
                        print(f"[DRY RUN] Would delete file: {item_path} (Age: {age:.1f} days)")
                    else:
                        os.remove(item_path)
                        print(f"Deleted file: {item_path}")
                    count += 1
                
                elif os.path.isdir(item_path):
                    # For directories like caches, we might want to delete the whole folder if it's safe
                    # For Downloads, we usually just delete files within it, stepping into subdirs is risky without clear rules
                    # Here we implemented a simple safe approach: only delete files in the top level of the target dir
                    # except for Trash where we nuke everything
                    if directory.endswith(".Trash"):
                         # In trash, delete directories too
                        if dry_run:
                            print(f"[DRY RUN] Would delete directory: {item_path}")
                        else:
                            shutil.rmtree(item_path)
                            print(f"Deleted directory: {item_path}")
                        count += 1
                    
            except Exception as e:
                print(f"Error processing {item_path}: {e}")

    except PermissionError:
        print(f"Permission denied accessing {directory}")

    print(f"Found {count} items to clean in {directory}. Est. space: {size_freed / (1024*1024):.2f} MB")


def main():
    parser = argparse.ArgumentParser(description="Mac Cleanup Skill")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without deleting files", default=True)
    parser.add_argument("--force", action="store_false", dest="dry_run", help="Actually delete files")
    args = parser.parse_args()

    print(f"Starting Cleanup (Dry Run: {args.dry_run})")

    # 1. Clean Trash
    trash_dir = os.path.expanduser("~/.Trash")
    cleanup_directory(trash_dir, dry_run=args.dry_run)

    # 2. Clean Caches
    caches_dir = os.path.expanduser("~/Library/Caches")
    # For caches, we are careful. Deleting currently used caches can crash apps.
    # A safer approach for a skill is to warn or only delete specific known heavy caches.
    # For this generic skill, we will list them but maybe NOT delete indiscriminately in a background task without user prompt.
    # However, the user asked for a cleanup skill. We will stick to the plan but be verbose.
    # Let's target specific subfolders to be safer if this was production, but for now we scan the root.
    # Actually, deleting ~/Library/Caches files is generally safe on macOS as they are regenerated, but doing it while apps are open is the risk.
    print(f"\n[WARNING] excessive cache cleaning can slow down system temporarily.")
    cleanup_directory(caches_dir, max_age_days=7, dry_run=args.dry_run) # Only delete old caches > 7 days

    # 3. Clean Downloads
    downloads_dir = os.path.expanduser("~/Downloads")
    cleanup_directory(downloads_dir, max_age_days=30, dry_run=args.dry_run)

    print("\nCleanup Complete.")

if __name__ == "__main__":
    main()
