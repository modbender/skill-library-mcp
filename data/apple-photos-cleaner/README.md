# Apple Photos Cleaner

Analyze, audit, and clean up your Apple Photos library by querying its SQLite database directly.

Goes beyond what Photos.app offers: intelligent junk detection, detailed storage analysis, duplicate finding with quality scoring, timeline recaps, people analytics, location mapping, and more.

> **Safety:** All operations are read-only database queries. No photos are modified or deleted without explicit user action through the cleanup executor.

## Requirements

- **macOS** (accesses the Photos SQLite database)
- **Python 3.9+** (uses stdlib only — no external runtime dependencies)

## Setup

```bash
# Clone the repo
git clone https://github.com/and3rn3t/apple-photos-cleaner.git
cd apple-photos-cleaner

# Install dev/test dependencies
make install
```

## Commands

Every script lives in `scripts/` and outputs **JSON** by default (for piping / AI consumption). Add `--human` for readable terminal output.

| Script | Purpose |
|---|---|
| `library_analysis.py` | Big-picture stats: counts, storage, date ranges, quality distribution |
| `junk_finder.py` | Identify screenshots, low-quality photos, burst leftovers |
| `duplicate_finder.py` | Find duplicates via Apple's detection + timestamp/dimension matching |
| `storage_analyzer.py` | Breakdown by year, type, format; growth trends; storage hogs |
| `timeline_recap.py` | Narrative summaries of photo activity for any date range |
| `smart_export.py` | Plan organized exports by year/month, person, album, or location |
| `best_photos.py` | Surface high-quality photos you haven't favorited |
| `people_analyzer.py` | People co-occurrence, trends over time, best photos per person |
| `location_mapper.py` | Cluster GPS coordinates into locations, identify trips |
| `scene_search.py` | Search by ML-detected content (beach, dog, food) or browse inventory |
| `photo_habits.py` | Time-of-day, day-of-week, streaks, seasonal trends |
| `on_this_day.py` | Photos from today's date in prior years |
| `album_auditor.py` | Find orphan photos, empty albums, album overlap |
| `cleanup_executor.py` | Batch move junk to trash via AppleScript (with confirmation) |
| `live_photo_analyzer.py` | Analyze Live Photos vs stills, find conversion candidates |
| `shared_library.py` | Audit Shared Library vs personal: contributors, storage splits |
| `icloud_status.py` | Check iCloud sync coverage: synced vs local-only items |
| `similarity_finder.py` | Detect visually similar photos using quality feature vectors |
| `seasonal_highlights.py` | Curate best photos per season with favorite boosting |
| `face_quality.py` | Score face/portrait quality using Apple's ML face attributes |

### Examples

```bash
# Quick library overview
python3 scripts/library_analysis.py --human

# Find junk photos
python3 scripts/junk_finder.py --human

# Best photos you forgot to favorite
python3 scripts/best_photos.py --hidden-gems --human

# What happened on this day in past years
python3 scripts/on_this_day.py --human

# Search for beach photos
python3 scripts/scene_search.py --search beach --human

# Preview cleanup (dry run by default)
python3 scripts/cleanup_executor.py --category old_screenshots --human
```

## Development

```bash
make test        # Run tests
make coverage    # Tests with coverage report
make lint        # Lint with ruff
make format      # Auto-format with ruff
make check       # Lint + format check + tests (CI equivalent)
make clean       # Remove cache/build artifacts
```

### Project structure

```
scripts/          # All analysis scripts + shared _common.py
tests/            # Pytest test suite
references/       # Database schema documentation
SKILL.md          # AI skill definition (trigger words, workflows, tips)
pyproject.toml    # Tool config (pytest, ruff, mypy)
```

## How it works

Apple Photos stores its metadata in a SQLite database at:

```
~/Pictures/Photos Library.photoslibrary/database/Photos.sqlite
```

This project queries that database in **read-only mode** to surface insights. Core Data timestamps (seconds since 2001-01-01) are converted to Python datetimes. ML-detected attributes like quality scores, scene classifications, and face data are all available in the database.

## License

MIT
