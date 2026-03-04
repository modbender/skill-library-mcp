---
name: stratos-storage
description: >
  Upload and download files to/from Stratos Decentralized Storage (SDS) network.
  Use when the user wants to store files on Stratos, retrieve files from Stratos,
  upload to decentralized storage, or download from SDS.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env: [STRATOS_SPFS_GATEWAY, STRATOS_NODE_DIR]
      bins: [curl]
    primaryEnv: STRATOS_SPFS_GATEWAY
---

# Stratos Decentralized Storage

## When to use
- User wants to upload a file to Stratos SDS network
- User wants to download a file from Stratos SDS using file hash or share link
- User mentions "Stratos", "SDS", "SPFS", or "decentralized storage upload/download"

## Steps

### Upload a file
1. Verify ppd or SPFS gateway is available
2. Run the upload script: `bash $SKILL_DIR/scripts/upload.sh <file_path>`
3. Return the file hash (CID) to the user

### Download a file
1. Verify ppd or SPFS gateway is available
2. Run the download script: `bash $SKILL_DIR/scripts/download.sh <file_hash_or_cid> <output_path>`
3. Confirm download success

## Examples

Upload: "Upload /tmp/report.pdf to Stratos"
→ Run: bash scripts/upload.sh /tmp/report.pdf
→ Output: File uploaded. CID: Qm...xxx

Download: "Download file Qm...xxx from Stratos to ~/Downloads/"
→ Run: bash scripts/download.sh Qm...xxx ~/Downloads/report.pdf
→ Output: File downloaded to ~/Downloads/report.pdf

## Constraints
- Always confirm file path with user before uploading
- Never overwrite existing files without user confirmation
- Verify SDS node is running before operations
- Large files may take significant time; inform user of progress
