# Apple Photos Database Schema Reference

This document describes the key tables and fields in the Apple Photos SQLite database (`Photos.sqlite`).

**Database Location:** `~/Pictures/Photos Library.photoslibrary/database/Photos.sqlite`

**⚠️ Important:** Always access the database in **read-only mode**. Never write to it directly.

## Core Data Timestamps

Apple Photos uses Core Data timestamps, which are **seconds since January 1, 2001 00:00:00 UTC**.

To convert to Python datetime:

```python
from datetime import datetime, timedelta
EPOCH = datetime(2001, 1, 1, 0, 0, 0)
dt = EPOCH + timedelta(seconds=timestamp)
```

To convert to Unix timestamp (for SQLite datetime functions):

```sql
-- Core Data timestamp + 978307200 = Unix timestamp
datetime(ZDATECREATED + 978307200, 'unixepoch')
```

## Key Tables

### ZASSET

Main table containing all photos and videos.

**Important Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `Z_PK` | INTEGER | Primary key (unique asset ID) |
| `ZFILENAME` | TEXT | Original filename |
| `ZDIRECTORY` | TEXT | Directory path within library |
| `ZDATECREATED` | REAL | Timestamp when photo/video was taken (Core Data format) |
| `ZWIDTH` | INTEGER | Width in pixels |
| `ZHEIGHT` | INTEGER | Height in pixels |
| `ZKIND` | INTEGER | Asset type: `0` = photo, `1` = video |
| `ZISDETECTEDSCREENSHOT` | INTEGER | `1` if detected as screenshot, `0` otherwise |
| `ZFAVORITE` | INTEGER | `1` if marked as favorite, `0` otherwise |
| `ZHIDDEN` | INTEGER | `1` if hidden, `0` otherwise |
| `ZTRASHEDSTATE` | INTEGER | `0` = not trashed, `1` = in trash |
| `ZLATITUDE` | REAL | GPS latitude (if available) |
| `ZLONGITUDE` | REAL | GPS longitude (if available) |
| `ZUNIFORMTYPEIDENTIFIER` | TEXT | File type (e.g., `public.jpeg`, `public.heic`) |
| `ZDUPLICATEASSETVISIBILITYSTATE` | INTEGER | Duplicate detection state (see below) |
| `ZAVALANCHEKIND` | INTEGER | Burst photo indicator (see below) |
| `ZAVALANCHEPICKTYPE` | INTEGER | Burst selection: `2` = user-selected, `4` = auto-picked, `NULL`/`0` = not picked |

**Filtering Non-Trashed Items:**
Always use `WHERE ZTRASHEDSTATE != 1` to exclude items in the trash.

### ZADDITIONALASSETATTRIBUTES

Extended metadata for assets. Joined via `Z_PK` matching `ZASSET.Z_PK`.

**Important Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `ZASSET` | INTEGER | Foreign key to `ZASSET.Z_PK` |
| `ZORIGINALFILESIZE` | INTEGER | File size in bytes |
| `ZORIGINALHEIGHT` | INTEGER | Original height (may differ from ZASSET.ZHEIGHT if edited) |
| `ZORIGINALWIDTH` | INTEGER | Original width |
| `ZTIMEZONEOFFSET` | INTEGER | Timezone offset in seconds |
| `ZTIMEZONENAME` | TEXT | Timezone name |

**Join Example:**

```sql
SELECT a.*, aa.ZORIGINALFILESIZE
FROM ZASSET a
LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
```

### ZCOMPUTEDASSETATTRIBUTES

Apple's computed quality scores for photos. Joined via `Z_PK` matching `ZASSET.Z_PK`.

**Important Fields:**

| Field | Type | Description | Range |
|-------|------|-------------|-------|
| `ZASSET` | INTEGER | Foreign key to `ZASSET.Z_PK` | - |
| `ZFAILURESCORE` | REAL | **Lower is better** - indicates technical failures | 0.0 - 1.0 |
| `ZNOISESCORE` | REAL | **Lower is better** - amount of noise/grain | 0.0 - 1.0 |
| `ZPLEASANTCOMPOSITIONSCORE` | REAL | **Higher is better** - composition quality | 0.0 - 1.0 |
| `ZPLEASANTLIGHTINGSCORE` | REAL | **Higher is better** - lighting quality | 0.0 - 1.0 |
| `ZPLEASANTPATTERNSCORE` | REAL | **Higher is better** - pattern aesthetics | 0.0 - 1.0 |
| `ZPLEASANTPERSPECTIVESCORE` | REAL | **Higher is better** - perspective quality | 0.0 - 1.0 |
| `ZPLEASANTPOSTPROCESSINGSCORE` | REAL | **Higher is better** - post-processing quality | 0.0 - 1.0 |
| `ZPLEASANTREFLECTIONSSCORE` | REAL | **Higher is better** - reflection quality | 0.0 - 1.0 |
| `ZPLEASANTSYMMETRYSCORE` | REAL | **Higher is better** - symmetry | 0.0 - 1.0 |

**Interpreting Scores:**

- Scores are typically in range 0.0 to 1.0
- Not all photos have all scores computed
- Use multiple scores combined for best quality assessment
- Low `ZFAILURESCORE` + high `ZPLEASANTCOMPOSITIONSCORE` = likely a good photo

**Join Example:**

```sql
SELECT a.*, ca.ZFAILURESCORE, ca.ZPLEASANTCOMPOSITIONSCORE
FROM ZASSET a
LEFT JOIN ZCOMPUTEDASSETATTRIBUTES ca ON a.Z_PK = ca.ZASSET
WHERE a.ZKIND = 0  -- photos only
```

### ZPERSON

Detected and named people in photos.

**Important Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `Z_PK` | INTEGER | Primary key (person ID) |
| `ZFULLNAME` | TEXT | Person's name (user-assigned) |
| `ZFACECOUNT` | INTEGER | Number of face detections for this person |

### ZDETECTEDFACE

Face detections linked to assets and people.

**Important Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `ZASSET` | INTEGER | Foreign key to `ZASSET.Z_PK` |
| `ZPERSON` | INTEGER | Foreign key to `ZPERSON.Z_PK` (may be NULL for unidentified faces) |

**Find Photos of a Person:**

```sql
SELECT a.*
FROM ZASSET a
JOIN ZDETECTEDFACE df ON a.Z_PK = df.ZASSET
JOIN ZPERSON p ON df.ZPERSON = p.Z_PK
WHERE p.ZFULLNAME = 'Person Name'
AND a.ZTRASHEDSTATE != 1
```

### ZGENERICALBUM

User-created albums and smart albums.

**Important Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `Z_PK` | INTEGER | Primary key (album ID) |
| `ZTITLE` | TEXT | Album name |
| `ZKIND` | INTEGER | Album type (varies) |

**Photos in Albums:**
Photos are linked to albums through `Z_27ASSETS` junction table:

```sql
SELECT a.*
FROM ZASSET a
JOIN Z_27ASSETS ga ON a.Z_PK = ga.Z_3ASSETS
JOIN ZGENERICALBUM album ON ga.Z_27ALBUMS = album.Z_PK
WHERE album.ZTITLE = 'Album Name'
AND a.ZTRASHEDSTATE != 1
```

### ZSCENECLASSIFICATION

Machine learning scene/object classifications.

**Important Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `ZASSET` | INTEGER | Foreign key to `ZASSET.Z_PK` |
| `ZSCENENAME` | TEXT | Scene label (e.g., "beach", "sunset", "dog") |
| `ZCONFIDENCE` | REAL | Confidence score (0.0 - 1.0) |

**Find Photos by Scene:**

```sql
SELECT a.*
FROM ZASSET a
JOIN ZSCENECLASSIFICATION sc ON a.Z_PK = sc.ZASSET
WHERE sc.ZSCENENAME = 'beach'
AND a.ZTRASHEDSTATE != 1
```

### ZINTERNALRESOURCE

Internal file paths and resources for assets.

**Important Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `ZASSET` | INTEGER | Foreign key to `ZASSET.Z_PK` |
| `ZRESOURCETYPE` | INTEGER | Resource type |
| `ZFILEPATH` | TEXT | File path |

## Special Field Explanations

### Duplicate Detection (`ZDUPLICATEASSETVISIBILITYSTATE`)

Apple's built-in duplicate detection system.

- `0` = Not a duplicate
- `> 0` = Identified as duplicate (exact meaning varies)

Photos with the same `ZDUPLICATEASSETVISIBILITYSTATE` value (> 0) are likely duplicates of each other.

**Find Apple-Detected Duplicates:**

```sql
SELECT * FROM ZASSET
WHERE ZDUPLICATEASSETVISIBILITYSTATE > 0
AND ZTRASHEDSTATE != 1
ORDER BY ZDUPLICATEASSETVISIBILITYSTATE
```

### Burst Photos (`ZAVALANCHEKIND`, `ZAVALANCHEPICKTYPE`)

Burst mode photos (rapid sequence of shots).

**`ZAVALANCHEKIND`:**

- `0` or `NULL` = Not part of a burst
- `> 0` = Part of a burst sequence (specific values vary)

**`ZAVALANCHEPICKTYPE`:**

- `NULL` or `0` = Not picked (leftover from burst)
- `2` = User manually selected
- `4` = Auto-selected by Photos

**Find Unpicked Burst Photos (Potential Cleanup):**

```sql
SELECT * FROM ZASSET
WHERE ZAVALANCHEKIND > 0
AND (ZAVALANCHEPICKTYPE IS NULL OR ZAVALANCHEPICKTYPE = 0)
AND ZTRASHEDSTATE != 1
```

### Asset Kind (`ZKIND`)

- `0` = Photo
- `1` = Video

Some assets may have additional flags indicating special types (Live Photos, etc.).

## Query Best Practices

1. **Always filter trash:** `WHERE ZTRASHEDSTATE != 1`
2. **Use LEFT JOIN** for attributes tables (not all assets have all attributes)
3. **Check for NULL** when using quality scores or metadata
4. **Index-friendly queries:** Filter on indexed fields (`Z_PK`, `ZDATECREATED`)
5. **Read-only access:** Use `file:path?mode=ro` URI for SQLite connection

## Example Queries

### All Photos from a Specific Year

```sql
SELECT a.*, aa.ZORIGINALFILESIZE
FROM ZASSET a
LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
WHERE a.ZTRASHEDSTATE != 1
AND strftime('%Y', datetime(a.ZDATECREATED + 978307200, 'unixepoch')) = '2025'
```

### Low Quality Photos

```sql
SELECT a.*, ca.ZFAILURESCORE, ca.ZPLEASANTCOMPOSITIONSCORE
FROM ZASSET a
LEFT JOIN ZCOMPUTEDASSETATTRIBUTES ca ON a.Z_PK = ca.ZASSET
WHERE a.ZTRASHEDSTATE != 1
AND a.ZKIND = 0
AND ca.ZFAILURESCORE > 0.7
ORDER BY ca.ZFAILURESCORE DESC
```

### Storage by Year

```sql
SELECT 
    strftime('%Y', datetime(a.ZDATECREATED + 978307200, 'unixepoch')) as year,
    COUNT(*) as count,
    SUM(aa.ZORIGINALFILESIZE) as total_bytes
FROM ZASSET a
LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
WHERE a.ZTRASHEDSTATE != 1
GROUP BY year
ORDER BY year DESC
```

## Schema Version Notes

This documentation is based on Photos app schema versions from macOS Monterey through macOS Sequoia. Apple may change the schema in future releases. Always test queries on a small dataset first.

## Safety Reminders

- **READ ONLY:** Never `INSERT`, `UPDATE`, or `DELETE`
- **Backup first:** Work on a copy if experimenting
- **Close Photos.app:** For best results, close Photos.app before querying
- **No writes:** All operations in this skill are read-only queries
