#!/usr/bin/env python3
import os
import sys
import subprocess
import hashlib
import argparse
import shlex

def calculate_sha256(filepath):
    """Calculates the SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def check_adb_installed():
    """Checks if adb is installed and in PATH."""
    try:
        subprocess.run(["adb", "version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_device_authorized():
    """Checks if a device is connected and authorized."""
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')[1:] # Skip header
        valid_devices = [line for line in lines if "device" in line and "offline" not in line and "unauthorized" not in line]
        
        if not valid_devices:
            print("Error: No authorized Android device found.")
            print("Please connect your device, enable USB Debugging, and authorize this computer.")
            return False
        
        if len(valid_devices) > 1:
            print(f"Warning: Multiple devices found. Using the first one: {valid_devices[0].split()[0]}")
        
        return True
    except subprocess.CalledProcessError:
        return False

def sanitize_path(path):
    """Sanitizes user input path to prevent traversal."""
    # This is a basic check. Real security might need more strict rules depending on OS.
    if ".." in path:
        raise ValueError("Invalid path: Directory traversal ('..') is not allowed.")
    return path

def get_remote_checksum(remote_path):
    """Gets SHA256 (or MD5 fallback) checksum from the device."""
    # Try sha256sum first (standard on newer Androids)
    cmd = ["adb", "shell", "sha256sum", shlex.quote(remote_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.split()[0]
        
    # Fallback to md5sum if sha256sum fails/missing (older Androids/Toybox)
    # Note: MD5 is less secure but better than nothing for basic integrity
    cmd = ["adb", "shell", "md5sum", shlex.quote(remote_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
         # If we fallback to MD5, we must re-calculate local MD5 to compare. 
         # This function just returns the remote hash string. The caller needs to handle the algo mismatch?
         # To keep it simple: we return a tuple (algo, hash)
         return ("md5", result.stdout.split()[0])
    
    return ("unknown", None)

def main():
    parser = argparse.ArgumentParser(description="Secure Android File Transfer")
    parser.add_argument("source", help="Path to the source file on Mac")
    parser.add_argument("--dest", help="Destination path on Android (default: /sdcard/Download/)", default="/sdcard/Download/")
    parser.add_argument("--force", action="store_true", help="Overwrite existing file on device")
    args = parser.parse_args()

    # 1. Environment Check
    if not check_adb_installed():
        print("Error: 'adb' is not found. Please install Android Platform Tools.")
        print("Run: brew install android-platform-tools")
        sys.exit(1)

    if not check_device_authorized():
        sys.exit(1)

    # 2. Path Validation & Sanitization
    try:
        source_path = os.path.abspath(sanitize_path(args.source))
        if not os.path.exists(source_path):
             print(f"Error: Source file does not exist: {source_path}")
             sys.exit(1)
             
        # Determine destination filename
        filename = os.path.basename(source_path)
        dest_dir = args.dest
        if not dest_dir.endswith("/"):
            dest_dir += "/"
        
        # We don't sanitize dest_dir as strictly because it's on the remote device, 
        # but we should ensure it's absolute
        if not dest_dir.startswith("/"):
             print("Error: Destination path must be absolute (start with /).")
             sys.exit(1)
             
        dest_path = dest_dir + filename
        
    except ValueError as e:
        print(f"Security Error: {e}")
        sys.exit(1)

    # 3. Overwrite Protection
    print(f"Checking destination: {dest_path}...")
    check_cmd = ["adb", "shell", "[ -f " + shlex.quote(dest_path) + " ] && echo 'EXISTS'"]
    check_res = subprocess.run(check_cmd, capture_output=True, text=True)
    if "EXISTS" in check_res.stdout and not args.force:
        print(f"Error: File already exists at {dest_path}. Use --force to overwrite.")
        sys.exit(1)

    # 4. Calculate Local Checksum
    print(f"Calculating local SHA256 for {source_path}...")
    local_sha256 = calculate_sha256(source_path)
    print(f"Local SHA256: {local_sha256}")

    # 5. Transfer
    print(f"Transferring to {dest_path}...")
    push_res = subprocess.run(["adb", "push", source_path, dest_path], capture_output=True, text=True)
    if push_res.returncode != 0:
        print(f"Transfer Failed: {push_res.stderr}")
        sys.exit(1)

    # 6. Verify Integrity
    print("Verifying remote checksum...")
    remote_res = subprocess.run(["adb", "shell", "sha256sum", shlex.quote(dest_path)], capture_output=True, text=True)
    
    remote_hash = None
    if remote_res.returncode == 0 and remote_res.stdout.strip():
        remote_hash = remote_res.stdout.split()[0]
    else:
        # Check if sha256sum was missing
        if "not found" in remote_res.stderr:
            print("Warning: 'sha256sum' not found on device. Trying md5sum...")
            # Fallback to MD5 logic would go here, but for "Highest Security" requested by user,
            # we should probably enforce SHA256 or fail if the device is too old to support it.
            # Let's fail for now to adhere to "Highest Security".
            print("Error: Device does not support sha256sum verification. Cannot guarantee highest security.")
            # Cleanup
            subprocess.run(["adb", "shell", "rm", shlex.quote(dest_path)])
            sys.exit(1)
    
    if remote_hash == local_sha256:
        print("Success! detailed verification passed. File transferred securely.")
    else:
        print("CRITICAL ERROR: Checksum mismatch!")
        print(f"Local:  {local_sha256}")
        print(f"Remote: {remote_hash}")
        print("Deleting corrupted file from device...")
        subprocess.run(["adb", "shell", "rm", shlex.quote(dest_path)])
        sys.exit(1)

if __name__ == "__main__":
    main()
