# Secure Android File Transfer Skill

This skill provides a **secure** way to transfer files from your Mac to an Android device.

## Security Features
1.  **Checksum Verification**: Calculates SHA256 hash locally and remotely to ensure perfect file integrity.
2.  **Overwrite Protection**: Will NOT overwrite existing files on the phone unless you force it.
3.  **Path Sanitization**: Blocks directory traversal attempts (e.g. `../`) to prevent accessing unauthorized files.
4.  **Device Authorization**: Verifies the device is authorized before attempting transfer.

## Prerequisites

- **Android Debug Bridge (adb)**: Must be installed.
    - Install via Homebrew: `brew install android-platform-tools`
- **USB Debugging**: Must be enabled on your Android phone (Settings > Developer Options).
- **Authorization**: When you plug in the phone, tap "Allow" on the "Allow USB debugging?" prompt.

## Usage

### Transfer a file
```bash
python3 scripts/secure_transfer.py /path/to/local/file.jpg
```
*Transfers to `/sdcard/Download/` by default.*

### Specify destination
```bash
python3 scripts/secure_transfer.py myfile.txt --dest /sdcard/Documents/
```

### Force overwrite
```bash
python3 scripts/secure_transfer.py myfile.txt --force
```

## Troubleshooting
- **"adb not found"**: Run `brew install android-platform-tools`.
- **"No authorized Android device found"**: Check your USB cable and unlock your phone to accept the authorization prompt.
- **"checksum mismatch"**: The transfer was corrupted. The script automatically deleted the partial file. Try again.
