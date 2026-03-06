## Media Server & Organization

### Folder Structure for Plex/Jellyfin

```
/volume1/media/
├── movies/
│   └── Movie Name (2024)/
│       ├── Movie Name (2024).mkv
│       └── Movie Name (2024).srt
├── tv/
│   └── Show Name/
│       └── Season 01/
│           └── Show Name - S01E01 - Title.mkv
├── music/
│   └── Artist/
│       └── Album (Year)/
│           └── 01 - Track.flac
└── photos/
    └── 2024/
        └── 2024-06-15 Event Name/
```

### Common Traps

1. **Wrong naming = no metadata** — Plex/Jellyfin guess from folder/file names. Follow format exactly or manual matching hell.

2. **Mixed content in one folder** — Movies and TV in same folder confuses scanners. Separate library roots mandatory.

3. **Transcoding melts NAS CPU** — Celeron can't transcode 4K HEVC. Direct play (capable clients) or hardware transcode (Intel QuickSync).

4. **Photo indexing is slow** — First Synology Photos/Immich index of 50K photos takes days. Let it finish before panicking.

5. **Don't trust NAS photo AI** — Face recognition, object detection are mediocre. Immich much better than Synology Photos.

### Hardware Transcoding

| Requirement | Solution |
|-------------|----------|
| 4K HEVC | Intel QuickSync (i3/i5 NAS) or capable clients |
| Multiple streams | Dedicated GPU (Plex Pass) or strong CPU |
| Budget NAS | Direct play only (Infuse, Kodi, Shield) |

### Photo Workflow

```
Phone → Auto-upload to NAS (Synology Photos/Immich)
Camera → Import to /photos/YYYY/ on NAS
RAW files → Separate /photos-raw/ folder
```

### Storage Planning

| Content | Per-item Size | Example Library |
|---------|---------------|-----------------|
| 1080p movie | 5-15 GB | 500 movies = 5 TB |
| 4K movie | 20-80 GB | 100 movies = 5 TB |
| TV episode | 1-4 GB | 50 series = 3 TB |
| Photo (RAW) | 25-50 MB | 10K photos = 400 GB |
| FLAC album | 300-600 MB | 200 albums = 100 GB |

Plan for 2x current library size. You'll fill it faster than expected.
