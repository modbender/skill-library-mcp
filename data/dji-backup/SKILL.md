---
name: "SKILL: DJI Video Backup"
description: This skill automates backing up DJI camera footage from an SD card
  (or USB share) to a NAS archive folder.
---

# SKILL: DJI Video Backup

This skill automates backing up DJI camera footage from an SD card (or USB share) to a NAS archive folder.

## Description
Use when the user asks to "copy DJI videos", "backup camera", or similar requests involving DJI footage and the NAS. It detects the source SD card, finds the next available destination folder (incrementing from DJI_001, DJI_002...), and copies the files.

## Usage
1.  **Check Source**: Verify `/Volumes/SD_Card/DCIM` (or similar) exists.
2.  **Check Destination**: Look at `/Volumes/File/DJI_Video/` to find the highest numbered folder (e.g., `DJI_005`).
3.  **Create New Folder**: Create the next number (e.g., `DJI_006`).
4.  **Copy**: Copy the contents of the source `DCIM` subfolder (e.g., `100MEDIA` or `DJI_001`) into the new destination folder.
5.  **Notify**: Tell the user when started and when finished.

## Paths
- **Source**: `/Volumes/SD_Card/DCIM` (Look for subfolders like `DJI_xxx` or `100MEDIA`)
- **Destination**: `/Volumes/File/DJI_Video`

## Example Logic
```bash
# Find next folder index
last_dir=$(ls -d /Volumes/File/DJI_Video/DJI_* | sort | tail -1)
# extract number, add 1, mkdir new_dir
# cp -R /source/* /new_dir/
```
