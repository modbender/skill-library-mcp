#!/usr/bin/env python3
"""Archive extraction and creation tool - zip, tar, gz, rar, 7z"""

import argparse
import os
import sys
import zipfile
import tarfile
import gzip
import shutil
import subprocess
from pathlib import Path

def extract_zip(filepath, output_dir, password=None):
    """Extract zip file using Python stdlib"""
    try:
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(output_dir, pwd=password.encode() if password else None)
        return True
    except RuntimeError as e:
        if "encrypted" in str(e).lower() or "password" in str(e).lower():
            print("🔐 PASSWORD_REQUIRED")
            print(f"ERROR: {e}")
            return "PASSWORD_REQUIRED"
        raise

def extract_tar(filepath, output_dir):
    """Extract tar/tar.gz/tgz file using Python stdlib"""
    with tarfile.open(filepath, 'r:*') as tar_ref:
        tar_ref.extractall(output_dir)
    return True

def extract_gz(filepath, output_dir):
    """Extract single gz file"""
    output_path = Path(output_dir) / Path(filepath).stem
    if output_path.suffix == '.tar':
        output_path = output_path.with_suffix('')
    with gzip.open(filepath, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    return True

def extract_rar(filepath, output_dir):
    """Extract rar using unar (system tool)"""
    try:
        result = subprocess.run(
            ['unar', '-o', output_dir, filepath],
            capture_output=True, text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ 'unar' not found. Install with: brew install unar")
        return False

def extract_7z(filepath, output_dir):
    """Extract 7z using p7zip (system tool)"""
    try:
        result = subprocess.run(
            ['7z', 'x', f'-o{output_dir}', '-y', filepath],
            capture_output=True, text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ '7z' not found. Install with: brew install p7zip")
        return False

def extract_file(filepath, output_dir, password=None):
    """Auto-detect and extract based on extension"""
    filepath = Path(filepath)
    
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return False
    
    os.makedirs(output_dir, exist_ok=True)
    
    ext = filepath.suffix.lower()
    name = filepath.name
    
    # Check compound extensions
    if name.endswith('.tar.gz') or name.endswith('.tgz'):
        ext = '.tar.gz'
    elif name.endswith('.tar.bz2'):
        ext = '.tar.bz2'
    elif name.endswith('.tar.xz'):
        ext = '.tar.xz'
    
    print(f"📦 Extracting {name}...")
    
    if ext == '.zip':
        result = extract_zip(filepath, output_dir, password)
        if result == "PASSWORD_REQUIRED":
            return False
        else:
            if result:
                print(f"✅ Extracted to: {output_dir}")
                return True
            else:
                print(f"❌ Failed to extract {ext} file")
                return False
    elif ext in ['.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tar.xz']:
        success = extract_tar(filepath, output_dir)
    elif ext == '.gz':
        success = extract_gz(filepath, output_dir)
    elif ext == '.rar':
        success = extract_rar(filepath, output_dir)
    elif ext == '.7z':
        success = extract_7z(filepath, output_dir)
    else:
        print(f"❌ Unsupported format: {ext}")
        return False
    
    if success:
        print(f"✅ Extracted to: {output_dir}")
        return True
    else:
        print(f"❌ Failed to extract {ext} file")
        return False

def create_zip(output_path, source):
    """Create zip archive"""
    source_path = Path(source)
    
    if source_path.is_file():
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(source_path, source_path.name)
    else:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in source_path.rglob('*'):
                if file.is_file():
                    zipf.write(file, file.relative_to(source_path.parent))
    
    print(f"✅ Created: {output_path}")
    return True

def create_tar(output_path, source, compress=False):
    """Create tar or tar.gz archive"""
    source_path = Path(source)
    mode = 'w:gz' if compress else 'w'
    
    with tarfile.open(output_path, mode) as tar:
        if source_path.is_file():
            tar.add(source_path, arcname=source_path.name)
        else:
            tar.add(source_path, arcname=source_path.name)
    
    print(f"✅ Created: {output_path}")
    return True

def list_contents(filepath):
    """List archive contents"""
    filepath = Path(filepath)
    ext = filepath.suffix.lower()
    name = filepath.name
    
    if name.endswith('.tar.gz') or name.endswith('.tgz'):
        ext = '.tar.gz'
    
    print(f"📋 Contents of {filepath.name}:\n")
    
    if ext == '.zip':
        with zipfile.ZipFile(filepath, 'r') as zipf:
            for info in zipf.infolist()[:20]:  # Limit to 20
                print(f"  {info.file_size:>10}  {info.filename}")
            if len(zipf.infolist()) > 20:
                print(f"  ... and {len(zipf.infolist()) - 20} more files")
    
    elif ext in ['.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tar.xz']:
        with tarfile.open(filepath, 'r:*') as tar:
            members = tar.getmembers()[:20]
            for member in members:
                print(f"  {member.size:>10}  {member.name}")
            if len(tar.getmembers()) > 20:
                print(f"  ... and {len(tar.getmembers()) - 20} more files")
    
    else:
        print(f"❌ Cannot list {ext} files")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Archive tool - extract and create archives')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract archive')
    extract_parser.add_argument('file', help='Archive file to extract')
    extract_parser.add_argument('-o', '--output', default='.', help='Output directory')
    extract_parser.add_argument('--password', help='Password for protected archives')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create archive')
    create_parser.add_argument('output', help='Output archive name')
    create_parser.add_argument('source', help='File or folder to compress')
    create_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List archive contents')
    list_parser.add_argument('file', help='Archive file to list')
    
    args = parser.parse_args()
    
    if args.command == 'extract':
        success = extract_file(args.file, args.output, args.password)
        sys.exit(0 if success else 1)
    
    elif args.command == 'create':
        output = Path(args.output)
        
        if output.suffix == '.zip':
            success = create_zip(output, args.source)
        elif output.suffix == '.tar':
            success = create_tar(output, args.source, compress=False)
        elif output.suffix in ['.tar.gz', '.tgz']:
            success = create_tar(output, args.source, compress=True)
        else:
            print("❌ Supported formats: .zip, .tar, .tar.gz, .tgz")
            sys.exit(1)
        
        sys.exit(0 if success else 1)
    
    elif args.command == 'list':
        success = list_contents(args.file)
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
