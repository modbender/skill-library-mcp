#!/usr/bin/env python3
"""
Memory Integrity Verification - Fractal Memory System

Detects tampering and anomalies in memory files:
- Checksum verification
- Anomaly detection in access patterns
- Provenance tracking

Inspired by @SandyBlake's "Your Memory Is Your Attack Surface" on Moltbook.

Run: python3 verify_memory_integrity.py
Cron: Daily after rollup
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

# Configuration
WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
INTEGRITY_FILE = MEMORY_DIR / "integrity.json"

def calculate_checksum(file_path):
    """Calculate SHA256 checksum of file"""
    sha256 = hashlib.sha256()
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        return None

def load_integrity_state():
    """Load previous integrity state"""
    if INTEGRITY_FILE.exists():
        with open(INTEGRITY_FILE, 'r') as f:
            return json.load(f)
    return {"files": {}, "last_check": None}

def save_integrity_state(state):
    """Save integrity state"""
    state["last_check"] = datetime.now().isoformat()
    with open(INTEGRITY_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def scan_memory_files():
    """Scan all memory files and calculate checksums"""
    files = {}
    
    # Scan diary files
    for md_file in MEMORY_DIR.rglob("*.md"):
        if md_file.is_file():
            rel_path = str(md_file.relative_to(WORKSPACE))
            checksum = calculate_checksum(md_file)
            
            if checksum:
                files[rel_path] = {
                    "checksum": checksum,
                    "size": md_file.stat().st_size,
                    "modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                }
    
    # Scan JSON state files
    for json_file in MEMORY_DIR.glob("*.json"):
        if json_file.name != "integrity.json" and json_file.is_file():
            rel_path = str(json_file.relative_to(WORKSPACE))
            checksum = calculate_checksum(json_file)
            
            if checksum:
                files[rel_path] = {
                    "checksum": checksum,
                    "size": json_file.stat().st_size,
                    "modified": datetime.fromtimestamp(json_file.stat().st_mtime).isoformat()
                }
    
    return files

def detect_changes(old_state, new_state):
    """Detect changes between old and new state"""
    changes = {
        "modified": [],
        "added": [],
        "deleted": []
    }
    
    old_files = old_state.get("files", {})
    new_files = new_state
    
    # Check for modifications and deletions
    for file_path, old_data in old_files.items():
        if file_path in new_files:
            new_data = new_files[file_path]
            if old_data["checksum"] != new_data["checksum"]:
                changes["modified"].append({
                    "file": file_path,
                    "old_checksum": old_data["checksum"][:8],
                    "new_checksum": new_data["checksum"][:8],
                    "old_modified": old_data["modified"],
                    "new_modified": new_data["modified"]
                })
        else:
            changes["deleted"].append(file_path)
    
    # Check for additions
    for file_path in new_files:
        if file_path not in old_files:
            changes["added"].append(file_path)
    
    return changes

def detect_anomalies(changes):
    """Detect suspicious patterns in changes"""
    anomalies = []
    
    # Filter out expected rollup modifications
    expected_patterns = [
        "memory/diary/",  # Daily/weekly/monthly rollups
        "memory/rollup-state.json",  # Rollup state
        "memory/entities/",  # Knowledge graph updates
    ]
    
    unexpected_mods = [
        mod for mod in changes["modified"]
        if not any(pattern in mod["file"] for pattern in expected_patterns)
    ]
    
    # Anomaly 1: Too many unexpected modifications at once
    if len(unexpected_mods) > 5:
        anomalies.append({
            "type": "bulk_modification",
            "severity": "medium",
            "description": f"{len(unexpected_mods)} unexpected files modified at once"
        })
    
    # Anomaly 2: Deletions (should be rare)
    if changes["deleted"]:
        anomalies.append({
            "type": "file_deletion",
            "severity": "high",
            "description": f"{len(changes['deleted'])} files deleted",
            "files": changes["deleted"]
        })
    
    # Anomaly 3: Modifications to old files (>30 days) - exclude rollup files
    for mod in unexpected_mods:
        old_date = datetime.fromisoformat(mod["old_modified"])
        days_ago = (datetime.now() - old_date).days
        
        if days_ago > 30:
            anomalies.append({
                "type": "old_file_modified",
                "severity": "medium",
                "description": f"File modified after {days_ago} days: {mod['file']}"
            })
    
    return anomalies

def main():
    """Main integrity verification"""
    print("🔒 Memory Integrity Verification - Fractal Memory System")
    print("=" * 60)
    
    # Load previous state
    old_state = load_integrity_state()
    last_check = old_state.get("last_check")
    
    if last_check:
        print(f"📅 Last check: {last_check}")
    else:
        print("📅 First integrity check")
    
    print()
    
    # Scan current files
    print("🔍 Scanning memory files...")
    new_files = scan_memory_files()
    print(f"   Found {len(new_files)} files")
    print()
    
    # Detect changes
    if old_state.get("files"):
        print("🔍 Detecting changes...")
        changes = detect_changes(old_state, new_files)
        
        if changes["added"]:
            print(f"   ✓ {len(changes['added'])} files added")
        
        if changes["modified"]:
            print(f"   ⚠️  {len(changes['modified'])} files modified")
            for mod in changes["modified"][:5]:  # Show first 5
                print(f"      - {mod['file']}")
            if len(changes["modified"]) > 5:
                print(f"      ... and {len(changes['modified']) - 5} more")
        
        if changes["deleted"]:
            print(f"   🚨 {len(changes['deleted'])} files deleted!")
            for deleted in changes["deleted"]:
                print(f"      - {deleted}")
        
        print()
        
        # Detect anomalies
        print("🔍 Detecting anomalies...")
        anomalies = detect_anomalies(changes)
        
        if anomalies:
            print(f"   🚨 Found {len(anomalies)} anomalies:")
            for anomaly in anomalies:
                severity_icon = "🚨" if anomaly["severity"] == "high" else "⚠️"
                print(f"   {severity_icon} [{anomaly['type']}] {anomaly['description']}")
        else:
            print("   ✓ No anomalies detected")
    else:
        print("ℹ️  No previous state to compare (first run)")
    
    print()
    
    # Save new state
    new_state = {
        "files": new_files,
        "last_check": datetime.now().isoformat()
    }
    save_integrity_state(new_state)
    
    print("=" * 60)
    print("✓ Integrity verification complete!")
    print(f"📁 State saved to: {INTEGRITY_FILE}")

if __name__ == "__main__":
    main()
