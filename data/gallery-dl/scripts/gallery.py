#!/usr/bin/env python3
"""gallery-dl wrapper - simple CLI wrapper for gallery-dl"""

import argparse
import subprocess
import sys
from pathlib import Path

def run_gallery_dl(args_list):
    """Run gallery-dl command"""
    # Check if gallery-dl is installed
    result = subprocess.run(['which', 'gallery-dl'], capture_output=True)
    if result.returncode != 0:
        print("❌ gallery-dl not found. Install with: pip install gallery-dl")
        sys.exit(1)
    
    result = subprocess.run(['gallery-dl'] + args_list, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def main():
    parser = argparse.ArgumentParser(description='gallery-dl wrapper')
    parser.add_argument('url', help='URL to download')
    parser.add_argument('-D', '--directory', default='./gallery-dl-output', help='Download directory')
    parser.add_argument('-f', '--filename', help='Filename format')
    parser.add_argument('--limit', type=int, help='Limit downloads')
    parser.add_argument('--range', help='Download range (e.g., 1-10)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--username', help='Username for authentication')
    parser.add_argument('--password', help='Password for authentication')
    parser.add_argument('--netrc', action='store_true', help='Use .netrc for authentication')
    parser.add_argument('--config', help='Custom config file')
    
    args = parser.parse_args()
    
    # Build gallery-dl command
    cmd = ['gallery-dl', args.url, '-D', args.directory]
    
    if args.filename:
        cmd.extend(['-f', args.filename])
    if args.limit:
        cmd.extend(['--limit', str(args.limit)])
    if args.range:
        cmd.extend(['--range', args.range])
    if args.verbose:
        cmd.append('-v')
    if args.username:
        cmd.extend(['--username', args.username])
    if args.password:
        cmd.extend(['--password', args.password])
    if args.netrc:
        cmd.append('--netrc')
    if args.config:
        cmd.extend(['--config', args.config])
    
    print(f"📥 Downloading: {args.url}")
    print(f"   To: {args.directory}")
    
    # Run gallery-dl
    code, stdout, stderr = run_gallery_dl(cmd)
    
    if code != 0:
        print(f"❌ Error: {stderr}")
        sys.exit(1)
    
    # Find downloaded files
    folder = Path(args.directory)
    if folder.exists():
        files = list(folder.rglob('*'))
        images = [f for f in files if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']]
        print(f"✅ Downloaded {len(images)} images to {args.directory}")
    else:
        print(f"✅ Downloaded to {args.directory}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
