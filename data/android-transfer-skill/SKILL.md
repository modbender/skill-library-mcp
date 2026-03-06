---
name: android-transfer-secure
description: Securely transfers files from macOS to Android with checksum verification and path validation.
author: tempguest
version: 0.1.0
license: MIT
---

# Secure Android File Transfer

This skill allows you to transfer files to an Android device with high security standards:
- **Checksum Verification**: Ensures data integrity by comparing SHA256 hashes.
- **Path Validation**: Prevents directory traversal and unauthorized path access.
- **Overwrite Protection**: Prevents accidental data loss on the device.

## Commands

- `transfer`: Push a file to the connected Android device.
