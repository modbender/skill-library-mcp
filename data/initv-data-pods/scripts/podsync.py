#!/usr/bin/env python3
"""
PodSync v0.1 - Sync and share data pods across devices
Usage: podsync.py <command> [options]
"""

import sqlite3
import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import zipfile
import shutil
import hashlib

PODS_DIR = Path.home() / ".openclaw" / "data-pods"
SYNC_DIR = Path.home() / ".openclaw" / "sync"

def ensure_dir():
    PODS_DIR.mkdir(parents=True, exist_ok=True)
    SYNC_DIR.mkdir(parents=True, exist_ok=True)

def list_pods():
    """List available pods."""
    ensure_dir()
    pods = []
    for d in PODS_DIR.iterdir():
        if d.is_dir():
            pods.append(d.name)
    return pods

def export_pod(pod_name: str, output_path: str = None):
    """Export pod as a shareable zip."""
    ensure_dir()
    pod_path = PODS_DIR / pod_name
    if not pod_path.exists():
        print(f"Error: Pod '{pod_name}' not found")
        return False
    
    if output_path is None:
        output_path = SYNC_DIR / f"{pod_name}.vpod"
    else:
        output_path = Path(output_path)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create zip with .vpod extension
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in pod_path.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(pod_path)
                zipf.write(file, arcname)
    
    # Calculate hash for verification
    with open(output_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()[:16]
    
    print(f"Exported: {pod_name} -> {output_path}")
    print(f"Hash: {file_hash}")
    print(f"Size: {output_path.stat().st_size / 1024:.1f} KB")
    return True

def import_pod(input_path: str, pod_name: str = None):
    """Import a .vpod file as a pod."""
    ensure_dir()
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"Error: File '{input_path}' not found")
        return False
    
    if pod_name is None:
        pod_name = input_path.stem
    
    pod_path = PODS_DIR / pod_name
    if pod_path.exists():
        print(f"Warning: Pod '{pod_name}' already exists. Use --force to overwrite.")
        return False
    
    # Extract zip
    with zipfile.ZipFile(input_path, 'r') as zipf:
        zipf.extractall(pod_path)
    
    print(f"Imported: {input_path} -> {pod_name}")
    return True

def pack_for_llm(pod_name: str, output_path: str = None):
    """Export pod as a single markdown file for LLM/ChatGPT context."""
    ensure_dir()
    pod_path = PODS_DIR / pod_name
    if not pod_path.exists():
        print(f"Error: Pod '{pod_name}' not found")
        return False
    
    db_path = pod_path / "data.sqlite"
    if not db_path.exists():
        print(f"Error: No database in pod '{pod_name}'")
        return False
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT title, content, tags, created_at FROM notes ORDER BY created_at DESC")
    notes = c.fetchall()
    conn.close()
    
    if output_path is None:
        output_path = SYNC_DIR / f"{pod_name}_for_llm.md"
    else:
        output_path = Path(output_path)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write as markdown
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {pod_name}\n\n")
        f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"## Notes\n\n")
        for note in notes:
            title, content, tags, created = note
            f.write(f"### {title}\n")
            f.write(f"*Tags: {tags} | Created: {created}*\n\n")
            f.write(f"{content}\n\n")
            f.write("---\n\n")
    
    print(f"Packed for LLM: {pod_name} -> {output_path}")
    print(f"Size: {output_path.stat().st_size / 1024:.1f} KB")
    print(f"Ready to paste into ChatGPT!")
    return True

def list_exports():
    """List exported pods."""
    ensure_dir()
    files = list(SYNC_DIR.glob("*.vpod")) + list(SYNC_DIR.glob("*.md"))
    if files:
        print("Exported files:")
        for f in files:
            print(f"  - {f.name} ({f.stat().st_size / 1024:.1f} KB)")
    else:
        print("No exports found.")

def sync_status():
    """Show sync status."""
    ensure_dir()
    pods = list_pods()
    exports = list(SYNC_DIR.glob("*.vpod"))
    
    print(f"Pods: {len(pods)}")
    print(f"Exports: {len(exports)}")

def main():
    parser = argparse.ArgumentParser(description="PodSync v0.1 - Sync pods across devices")
    sub = parser.add_subparsers(dest="cmd")
    
    sub.add_parser("list", help="List pods")
    sub.add_parser("status", help="Show sync status")
    sub.add_parser("exports", help="List exported files")
    
    exp = sub.add_parser("export", help="Export pod as .vpod")
    exp.add_argument("pod", help="Pod name")
    exp.add_argument("--output", help="Output path")
    
    imp = sub.add_parser("import", help="Import .vpod file")
    imp.add_argument("file", help="Input file path")
    imp.add_argument("--name", help="Pod name (default: filename)")
    
    pack = sub.add_parser("pack", help="Pack for LLM/ChatGPT as markdown")
    pack.add_argument("pod", help="Pod name")
    pack.add_argument("--output", help="Output markdown path")
    
    args = parser.parse_args()
    
    if args.cmd == "list":
        pods = list_pods()
        if pods:
            print("Available pods:")
            for p in pods:
                print(f"  - {p}")
        else:
            print("No pods found.")
    elif args.cmd == "status":
        sync_status()
    elif args.cmd == "exports":
        list_exports()
    elif args.cmd == "export":
        export_pod(args.pod, args.output)
    elif args.cmd == "import":
        import_pod(args.file, args.name)
    elif args.cmd == "pack":
        pack_for_llm(args.pod, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
