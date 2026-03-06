#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
install_osquery - openclaw-os-activity
Install osquery for OpenClaw
"""
import requests
import sys
import os
import shutil
import tarfile
import zipfile
import hashlib
from pathlib import Path

# Find the user's os
OS = sys.platform
if OS.startswith("win"):
    OS = "windows"
elif OS.startswith("linux"):
    OS = "linux"
elif OS.startswith("darwin"):
    OS = "darwin"
else:
    print(f"Unsupported OS: {OS}")
    sys.exit(1)

# Version
VERSION = "5.21.0"

# Base URL for osquery releases
BASE_URL = f"https://github.com/osquery/osquery/releases/download/{VERSION}"

# SHA256 checksums for osquery releases
# NOTE: These checksums should be periodically verified against official osquery
# releases at: https://github.com/osquery/osquery/releases/
# To update checksums: download the release and run:
#   python3 -c "import hashlib; print(hashlib.sha256(open('file','rb').read()).hexdigest())"
CHECKSUMS = {
    "windows": "cc9a8a177338dcda13eaa6c5a2bcdb70d5922a2a6e7174a24c8009ab5b7a6630",
    "linux": "b6cf1db2c541863725b934d758a3a66ba295aa7bda94b6a3547a8b36f556a859",
    "darwin": "c45e6a6dfe9ca9c5fc567b7224069060e7d1d02a257684667a23d40e9b01d8be",
}

def get_download_url():
    """Get the download URL based on the OS"""
    if OS == "windows":
        return [
            (f"{BASE_URL}/osquery-{VERSION}.windows_x86_64.zip", "osquery.zip"),
        ]
    elif OS == "linux":
        return [
            (f"{BASE_URL}/osquery-{VERSION}_1.linux_x86_64.tar.gz", "osquery.tar.gz"),
        ]
    elif OS == "darwin":
        return [
            (f"{BASE_URL}/osquery-{VERSION}_1.macos_arm64.tar.gz", "osquery.tar.gz"),
        ]
    else:
        raise ValueError(f"Unsupported OS: {OS}")

def verify_checksum(filepath, expected_checksum):
    """Verify the SHA256 checksum of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        actual_checksum = sha256_hash.hexdigest()
        if actual_checksum.lower() == expected_checksum.lower():
            print(f"Checksum verified: {actual_checksum}")
            return True
        else:
            print(f"Checksum mismatch!")
            print(f"  Expected: {expected_checksum}")
            print(f"  Actual:   {actual_checksum}")
            return False
    except Exception as e:
        print(f"Failed to verify checksum: {e}")
        return False

def download_file(url, filepath, filename):
    """Download a file with progress bar"""
    print(f"Downloading from {url}...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to download from {url}: {e}")
        return False
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filepath, 'wb') as f:
        if total_size > 0:
            try:
                import tqdm
                with tqdm.tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            except ImportError:
                # tqdm not available, fall back to simple download
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        else:
            f.write(response.content)
    
    print(f"Downloaded to {filepath}")
    return True

def validate_archive_member_path(member_path, target_dir):
    """
    Validate that a member path is safe and doesn't contain path traversal.
    Returns the safe path or None if invalid.
    """
    # Convert to Path object for safe resolution
    target_path = Path(target_dir).resolve()
    
    # Normalize the member path and remove leading slashes
    normalized_path = member_path.lstrip('/\\')
    
    # Check for null bytes (path traversal technique)
    if '\0' in normalized_path:
        return None
    
    # Check for dangerous patterns
    parts = Path(normalized_path).parts
    for part in parts:
        if part in ('..', '.', '') or part.startswith('~'):
            return None
    
    # Construct the final path
    final_path = target_path / normalized_path
    final_path_resolved = final_path.resolve()
    
    # Ensure the resolved path is within target directory
    try:
        final_path_resolved.relative_to(target_path)
        return final_path
    except ValueError:
        # Path is outside target directory
        return None

def extract_tar_safe(archive_path, target_dir):
    """Safely extract a tar.gz archive with path validation"""
    print(f"Extracting tar.gz to {target_dir}...")
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    
    try:
        with tarfile.open(archive_path, 'r:gz') as tar:
            for member in tar.getmembers():
                # Validate member path
                safe_path = validate_archive_member_path(member.name, target_dir)
                if safe_path is None:
                    print(f"Skipping unsafe path in archive: {member.name}")
                    return False
                
                # Extract to safe location
                member.name = str(safe_path.relative_to(target_path))
                tar.extract(member, target_dir)
        return True
    except Exception as e:
        print(f"Failed to extract tar archive: {e}")
        return False

def extract_zip_safe(archive_path, target_dir):
    """Safely extract a zip archive with path validation"""
    print(f"Extracting zip to {target_dir}...")
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    
    try:
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            for info in zip_ref.infolist():
                # Validate member path
                safe_path = validate_archive_member_path(info.filename, target_dir)
                if safe_path is None:
                    print(f"Skipping unsafe path in archive: {info.filename}")
                    return False
                
                # Extract to safe location
                with zip_ref.open(info) as source:
                    safe_path.parent.mkdir(parents=True, exist_ok=True)
                    if not info.filename.endswith('/'):
                        with open(safe_path, 'wb') as target:
                            target.write(source.read())
        return True
    except Exception as e:
        print(f"Failed to extract zip archive: {e}")
        return False

def extract_archive(archive_path, target_dir):
    """Extract archive based on file type with path traversal protection"""
    if archive_path.endswith('.tar.gz'):
        return extract_tar_safe(archive_path, target_dir)
    elif archive_path.endswith('.zip'):
        return extract_zip_safe(archive_path, target_dir)
    else:
        return False

def install_windows(temp_dir, target_dir):
    """Install osquery for Windows"""
    print("Installing osquery for Windows...")
    
    # Look for the osquery directory structure
    # Expected: osquery-5.21.0.windows_x86_64/Program Files/osquery
    for root, dirs, files in os.walk(temp_dir):
        if "Program Files" in dirs:
            program_files_dir = os.path.join(root, "Program Files")
            if os.path.exists(os.path.join(program_files_dir, "osquery")):
                osquery_src = os.path.join(program_files_dir, "osquery")
                print(f"Found osquery directory at: {osquery_src}")
                
                # Remove existing target directory if it exists
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                
                # Copy the entire osquery directory to target
                try:
                    shutil.copytree(osquery_src, str(target_dir))
                    print(f"Copied osquery directory to {target_dir}")
                    
                    # Verify osqueryi.exe exists
                    osqueryi_path = target_dir / "osqueryi.exe"
                    if osqueryi_path.exists():
                        print(f"osqueryi.exe found at: {osqueryi_path}")
                        return True
                    else:
                        print(f"osqueryi.exe not found in {target_dir}")
                        return False
                except Exception as e:
                    print(f"Failed to copy osquery directory: {e}")
                    return False
    
    print(f"osquery directory not found in {temp_dir}")
    return False

def install_linux_macos(temp_dir, target_dir):
    """Install osquery for Linux/macOS"""
    print(f"Installing osquery for {OS.upper()}...")
    
    # Look for osqueryd in the extracted directory
    # Expected path: opt/osquery/bin/osqueryd
    osqueryd_path = None
    for root, dirs, files in os.walk(temp_dir):
        if "osqueryd" in files:
            candidate_path = os.path.join(root, "osqueryd")
            # Prefer the one in opt/osquery/bin
            if "bin" in root and "osquery" in root:
                osqueryd_path = candidate_path
                break
            elif osqueryd_path is None:
                osqueryd_path = candidate_path
    
    if not osqueryd_path:
        print(f"osqueryd binary not found in {temp_dir}")
        return False
    
    print(f"Found osqueryd at: {osqueryd_path}")
    
    # Create target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy osqueryd to target as osqueryi
    try:
        target_file = target_dir / "osqueryi"
        shutil.copy2(osqueryd_path, str(target_file))
        # Make it executable
        os.chmod(str(target_file), 0o755)
        print(f"Copied osqueryd to {target_file}")
        print(f"osqueryi has been made executable")
        return True
    except Exception as e:
        print(f"Failed to copy osqueryd: {e}")
        return False

def main():
    # Create target directory
    home_dir = Path.home()
    target_dir = home_dir / ".openclaw" / "tools" / "os-activity" / "osquery"
    
    print(f"Target directory: {target_dir}")
    
    # Create directories if they don't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Get download URLs
    download_urls = get_download_url()
    
    # Download file
    temp_dir = Path.home() / ".openclaw" / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    success = False
    for download_url, filename in download_urls:
        archive_path = temp_dir / filename
        extract_dir = temp_dir / "osquery_extract"
        
        try:
            if not download_file(download_url, str(archive_path), filename):
                continue
            
            # Verify checksum
            if OS in CHECKSUMS:
                if not verify_checksum(str(archive_path), CHECKSUMS[OS]):
                    print(f"Checksum verification failed for {filename}")
                    continue
            else:
                print(f"Warning: No checksum defined for {OS}")
            
            # Create extract directory
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract the archive
            if not extract_archive(str(archive_path), str(extract_dir)):
                continue
            
            # Install based on OS
            if OS == "windows":
                success = install_windows(extract_dir, target_dir)
            else:
                success = install_linux_macos(extract_dir, target_dir)
            
            if success:
                break
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
        finally:
            # Clean up extract directory
            if extract_dir.exists():
                shutil.rmtree(extract_dir, ignore_errors=True)
            # Clean up archive
            if archive_path.exists():
                archive_path.unlink()
    
    if success:
        print(f"Successfully installed osquery")
        return 0
    else:
        print(f"Failed to install osquery")
        return 1


if __name__ == "__main__":
    sys.exit(main())