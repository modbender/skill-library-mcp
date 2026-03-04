#!/usr/bin/env python3
"""
Obsidian Attachment Cleaner
Automatically finds and moves loose images/attachments to the Attachments folder.
"""
import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# Configuration
DEFAULT_VAULT_PATH = os.path.expanduser("~/Documents/Obsidian Vault")
DEFAULT_ATTACHMENTS = "Attachments"

# Supported file extensions
SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.pdf', '.docx', '.doc', '.txt', '.md'}


def find_loose_attachments(vault_path: str) -> list:
    """Find all loose attachment files in vault root."""
    attachments = []
    
    if not os.path.exists(vault_path):
        return attachments
    
    for item in os.listdir(vault_path):
        item_path = os.path.join(vault_path, item)
        
        # Skip directories and symlinks
        if os.path.isdir(item_path) or os.path.islink(item_path):
            continue
        
        # Check if it's a supported attachment file
        ext = Path(item).suffix.lower()
        if ext in SUPPORTED_EXTENSIONS:
            # Exclude the attachments folder itself if it exists in root
            if item.lower() != DEFAULT_ATTACHMENTS.lower():
                attachments.append(item)
    
    return sorted(attachments)


def ensure_attachments_folder(vault_path: str, attachments_folder: str) -> str:
    """Ensure the attachments folder exists and return its full path."""
    attachments_path = os.path.join(vault_path, attachments_folder)
    os.makedirs(attachments_path, exist_ok=True)
    return attachments_path


def move_file(src_path: str, dst_path: str, dry_run: bool = False) -> tuple:
    """Move a file from src to dst. Returns (success, error_msg)."""
    try:
        if dry_run:
            return True, None
        
        # If destination file exists, add timestamp to make unique
        if os.path.exists(dst_path):
            name = Path(dst_path).stem
            ext = Path(dst_path).suffix
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dst_path = str(Path(dst_path).parent / f"{name}_{timestamp}{ext}")
        
        shutil.move(src_path, dst_path)
        return True, None
    
    except Exception as e:
        return False, str(e)


def clean_obsidian(vault_path: str, attachments_folder: str = DEFAULT_ATTACHMENTS, 
                   dry_run: bool = False) -> dict:
    """
    Main function to clean loose attachments from Obsidian vault.
    
    Returns dict with:
    - found: number of files found
    - moved: number of files successfully moved
    - skipped: number of files skipped
    - errors: list of error messages
    - files: list of moved/skipped files with details
    """
    result = {
        'found': 0,
        'moved': 0,
        'skipped': 0,
        'errors': [],
        'files': []
    }
    
    # Find loose attachments
    loose_files = find_loose_attachments(vault_path)
    result['found'] = len(loose_files)
    
    if not loose_files:
        return result
    
    # Ensure attachments folder exists
    attachments_path = ensure_attachments_folder(vault_path, attachments_folder)
    
    # Process each file
    for filename in loose_files:
        src_path = os.path.join(vault_path, filename)
        dst_path = os.path.join(attachments_path, filename)
        
        # Check if destination already exists
        if os.path.exists(dst_path):
            result['skipped'] += 1
            result['files'].append({
                'file': filename,
                'action': 'skipped',
                'reason': 'Already exists'
            })
            continue
        
        # Move the file
        success, error = move_file(src_path, dst_path, dry_run)
        
        if success:
            result['moved'] += 1
            result['files'].append({
                'file': filename,
                'action': 'moved' if not dry_run else 'would move',
                'destination': os.path.join(attachments_folder, filename)
            })
        else:
            result['skipped'] += 1
            result['errors'].append(f"{filename}: {error}")
            result['files'].append({
                'file': filename,
                'action': 'error',
                'reason': error
            })
    
    return result


def print_report(result: dict, vault_path: str, attachments_folder: str):
    """Print a formatted report of the cleaning operation."""
    print(f"\n🔍 Scanning {vault_path}...")
    
    if result['found'] == 0:
        print("✅ No loose attachments found! Your vault is already clean.")
        return
    
    print(f"\n📁 Found {result['found']} loose file(s):")
    
    for f in result['files']:
        if f['action'] == 'moved':
            print(f"  ├── {f['file']} → {f['destination']}")
        elif f['action'] == 'would move':
            print(f"  ├── {f['file']} → {f['destination']} (DRY RUN)")
        elif f['action'] == 'skipped':
            print(f"  ├── {f['file']} ⏭️  ({f['reason']})")
        else:
            print(f"  ├── {f['file']} ❌ ({f.get('reason', 'Unknown')})")
    
    print(f"\n📊 Summary:")
    print(f"  ├── Moved: {result['moved']}")
    print(f"  ├── Skipped: {result['skipped']}")
    
    if result['errors']:
        print(f"  └── Errors: {len(result['errors'])}")
        for error in result['errors']:
            print(f"      - {error}")
    else:
        print("  └── Errors: 0")
    
    print(f"\n🎉 Done! Files moved to {attachments_folder}/")


def main():
    parser = argparse.ArgumentParser(description="Clean loose attachments from Obsidian vault")
    parser.add_argument('--vault', '-v', default=DEFAULT_VAULT_PATH,
                       help=f"Obsidian vault path (default: {DEFAULT_VAULT_PATH})")
    parser.add_argument('--attachments', '-a', default=DEFAULT_ATTACHMENTS,
                       help=f"Attachments folder name (default: {DEFAULT_ATTACHMENTS})")
    parser.add_argument('--dry-run', '-d', action='store_true',
                       help="Preview what will be moved without actually moving")
    
    args = parser.parse_args()
    
    # Run cleaning
    result = clean_obsidian(args.vault, args.attachments, args.dry_run)
    
    # Print report
    print_report(result, args.vault, args.attachments)
    
    # Exit with appropriate code
    if result['errors']:
        exit(1)


if __name__ == '__main__':
    main()
