---
name: Photos
description: Organize, index, and search local photo libraries with AI-powered metadata and safe file handling.
metadata: {"clawdbot":{"emoji":"🖼️","requires":{"bins":["exiftool"]},"os":["linux","darwin","win32"]}}
---

## Safety First

- **Never delete photos directly** — move to `.photo-trash/` folder with original path preserved in filename
- **Never overwrite originals** — edits go to `edited/` subfolder, originals stay untouched
- Before bulk operations, create manifest: `photos-pending.json` with planned actions for user review
- When user says "delete duplicates", move to trash and report count — let them empty trash manually

## Indexing Strategy

- Create `.photo-index/` in library root with one JSON sidecar per photo
- Sidecar filename: `{original-hash}.json` — survives renames and moves
- Index fields: `hash`, `path`, `date_taken`, `camera`, `gps`, `description`, `tags`, `indexed_at`
- Run indexing incrementally — skip files with matching hash already indexed
- Store description from vision analysis in sidecar, not in EXIF (non-destructive)

## Vision Analysis (Token-Efficient)

- Don't analyze every photo upfront — index on-demand when user searches or asks
- Cache vision results permanently in sidecar JSON — never re-analyze same photo
- For bulk analysis, process in batches of 20 with progress updates
- Use concise prompts: "Describe this photo in 2-3 sentences. List people, objects, location, activity."
- Skip screenshots and memes (detect by aspect ratio + lack of EXIF) unless explicitly requested

## Duplicate Detection

- Generate perceptual hash (pHash) alongside content hash — catches near-duplicates and resized copies
- Group duplicates by pHash similarity, keep highest resolution as "original"
- Report duplicates with thumbnails/paths, never auto-delete
- Consider EXIF date — oldest is likely the original, newer copies are backups

## Search Patterns

- **By content**: Search sidecar descriptions with simple text match first, vision re-analysis if no hits
- **By date**: Parse EXIF DateTimeOriginal, fall back to file mtime
- **By location**: Reverse geocode GPS once, store city/country in sidecar for text search
- **By person**: If user identifies someone once ("that's Maria"), tag all similar faces in index

## EXIF Handling

- Read: `exiftool -json photo.jpg` — returns all metadata as JSON
- Write date: `exiftool -DateTimeOriginal="2024:03:15 14:30:00" photo.jpg`
- Strip GPS before sharing: `exiftool -gps:all= photo.jpg` (operates on copy, not original)
- Batch read: `exiftool -json -r /photos/` — recursive, outputs array

## File Organization

- Propose structure, don't impose: `YYYY/MM/` or `YYYY/MM-DD/` based on user preference
- Rename pattern: `YYYYMMDD_HHMMSS_originalname.ext` — preserves original name, adds sortable prefix
- Handle timezone: EXIF dates are local time — ask user's timezone once, store in `.photo-index/config.json`
- HEIC to JPEG: `sips -s format jpeg input.heic --out output.jpg` (macOS) or `heif-convert` (Linux)

## NAS/Remote Libraries

- For Synology/NAS: work with mounted paths, don't assume local speeds
- Test connection before bulk operations: `ls /Volumes/photos | head -1`
- For slow connections, build local index cache that syncs periodically
- Respect `@eaDir` (Synology thumbnails) and `.DS_Store` — skip in indexing
