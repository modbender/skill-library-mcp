---
name: apple-photos-cleaner
description: Analyze, clean up, and organize Apple Photos libraries. Find and report junk photos (screenshots, low-quality, burst leftovers, duplicates), analyze storage usage, generate photo timeline recaps, plan smart exports, analyze Live Photos, check iCloud sync, audit shared libraries, detect similar photos, curate seasonal highlights, and score face quality. All analysis operations are READ-ONLY on the database (safe). macOS only. Requires Python 3.9+ (stdlib only) and access to the Apple Photos SQLite database. Trigger on: Photos cleanup, photo storage, duplicate photos, junk photos, screenshot cleanup, Photos analysis, photo timeline, photo export, Photos library stats, burst cleanup, storage hogs, photo organization, Live Photos, iCloud sync, shared library, similar photos, seasonal highlights, face quality, portraits.
license: MIT
metadata: {"openclaw": {"os": ["darwin"], "emoji": "📸", "homepage": "https://github.com/and3rn3t/apple-photos-cleaner", "requires": {"bins": ["python3"]}}}
---

# Apple Photos Cleaner

Comprehensive toolkit for analyzing and cleaning up Apple Photos libraries. Goes beyond what Photos.app offers: intelligent junk detection, detailed storage analysis, duplicate finding with quality scoring, timeline recaps for storytelling, and smart export planning.

## Overview

Apple Photos is great at organizing and syncing photos, but it's not so great at cleanup. This skill fills that gap:

- **Library Analysis** — Get the big picture: counts, storage, date ranges, people, quality distribution
- **Junk Finder** — Identify screenshots, low-quality photos, burst leftovers, old screenshots
- **Duplicate Finder** — Find duplicates using Apple's detection + timestamp/dimension matching
- **Storage Analyzer** — Detailed breakdown by year, type, file format, growth trends, storage hogs
- **Timeline Recap** — Generate narrative summaries of photo activity for any date range
- **Smart Export** — Plan organized exports by year/month, person, album, or location; AppleScript export
- **Best Photos / Hidden Gems** — Surface high-quality photos you haven't favorited
- **People Analyzer** — Deep analysis of people: co-occurrence, trends over time, best photos per person
- **Location Mapper** — Cluster GPS coordinates into locations, identify trips, offline reverse geocoding
- **Scene Search** — Search by ML-detected content (beach, dog, food) or generate content inventory
- **Photo Habits** — Behavioral analytics: time-of-day, day-of-week, streaks, seasonal trends
- **On This Day** — See what you photographed on today's date in prior years
- **Album Auditor** — Find orphan photos, empty albums, overlap between albums
- **Cleanup Executor** — Batch move junk to trash via AppleScript with confirmation
- **Live Photo Analyzer** — Compare Live Photos vs stills, find conversion candidates, storage impact
- **Shared Library** — Analyze Shared Library vs personal: contributors, content splits, storage
- **iCloud Status** — Check iCloud sync coverage: synced vs local-only, large unsynced items
- **Similarity Finder** — Detect visually similar photos using computed quality feature vectors
- **Seasonal Highlights** — Curate the best photos per season using quality scores and favorites
- **Face Quality Scoring** — Rank face photos per person: find best/worst portraits

**Safety:** All operations are READ-ONLY database queries. No photos are modified or deleted without explicit user action.

## When to Use This Skill

Use when users mention:
- Cleaning up Photos / freeing up photo storage
- Finding duplicate photos
- Removing old screenshots
- Analyzing Photos library storage
- Finding junk or low-quality photos
- Organizing photo exports
- Getting photo timeline summaries ("what did I do last week?")
- Burst photo cleanup
- Finding storage hogs in Photos
- Finding best or hidden gem photos
- People in photos, who appears together
- Where photos were taken, travel, trips, locations
- Searching photos by content (beach, sunset, dog, food)
- Photo-taking habits, patterns, streaks
- "On this day" / photo memories from past years
- Album organization, orphan photos, album cleanup
- Actually deleting junk photos (batch cleanup)
- Live Photos analysis, converting Live Photos to stills
- Shared Library content, who contributed what
- iCloud sync status, unsynced photos, cloud coverage
- Finding similar-looking photos
- Seasonal photo highlights, best of each season
- Face/portrait quality, best/worst portraits per person

## Quick Start

All scripts work standalone. The Photos database is automatically located at:
`~/Pictures/Photos Library.photoslibrary/database/Photos.sqlite`

**Basic workflow:**
1. Run `library_analysis.py` to get overview
2. Run `junk_finder.py` to identify cleanup candidates
3. Run `duplicate_finder.py` to find duplicates
4. Use results to guide manual cleanup in Photos.app

## Commands

### 1. Library Analysis

Get comprehensive library statistics: counts, storage, date ranges, people, quality scores.

```bash
python3 scripts/library_analysis.py [--human] [--output FILE]
```

**Options:**
- `--human` — Human-readable summary instead of JSON
- `--output FILE` — Write JSON to file
- `--db-path PATH` — Custom database path
- `--library PATH` — Custom Photos library path

**Example Output:**
```
📊 APPLE PHOTOS LIBRARY ANALYSIS
==================================================

Total Assets: 12,453
Total Storage: 48.3 GB
Average Size: 4.1 MB
Date Range: 2020-01-15 to 2025-03-03

By Type:
  Photo: 11,234
  Video: 891
  Screenshots: 328
  Favorites: 456
  Bursts: 1,234

By Year:
  2025: 1,203 items, 5.2 GB
  2024: 3,456 items, 15.1 GB
  2023: 2,987 items, 12.4 GB
  ...

Top People:
  Jonah: 3,456 photos
  Silas: 3,234 photos
  ...
```

**Usage in Conversation:**

**User:** "How many photos do I have?"  
**AI:** *Runs library_analysis.py with --human flag, reports summary*

**User:** "Show me my Photos storage breakdown"  
**AI:** *Runs library_analysis.py, highlights key stats*

---

### 2. Junk Finder

Identify cleanup candidates: screenshots, low-quality photos, burst leftovers, duplicates.

```bash
python3 scripts/junk_finder.py [--screenshot-age DAYS] [--quality-threshold N] [--human]
```

**Options:**
- `--screenshot-age DAYS` — Consider screenshots older than N days as junk (default: 30)
- `--quality-threshold N` — Quality score threshold for low-quality (default: 0.3, range: 0.0-1.0)
- `--no-duplicates` — Skip duplicate detection
- `--human` — Human-readable summary
- `--output FILE` — Write JSON to file

**Example Output:**
```
🗑️  JUNK FINDER RESULTS
==================================================

Found:
  📸 Screenshots: 328
     └─ Old (>30 days): 287
  📉 Low Quality: 156
  📸 Burst Leftovers: 1,089
  👥 Possible Duplicates: 45

Estimated Savings:
  Conservative: 2.3 GB
    (Old screenshots + burst leftovers)
  Aggressive: 5.7 GB
    (All screenshots + low quality + bursts + ~50% of duplicates)
```

**What It Finds:**
- **Screenshots** — Detected via `ZISDETECTEDSCREENSHOT` flag
- **Old screenshots** — Screenshots older than specified age (safe to delete)
- **Low quality** — Photos with low quality scores (high failure/noise, low composition/lighting)
- **Burst leftovers** — Unpicked photos from burst sequences
- **Possible duplicates** — Using Apple's built-in detection

**Usage in Conversation:**

**User:** "Find junk in my Photos"  
**AI:** *Runs junk_finder.py, reports totals and estimated savings*

**User:** "How many old screenshots do I have?"  
**AI:** *Runs junk_finder.py, focuses on screenshot stats*

**User:** "What can I delete to free up 5GB?"  
**AI:** *Runs junk_finder.py, shows conservative/aggressive estimates, suggests next steps*

---

### 3. Duplicate Finder

Find duplicate photos and recommend which to keep based on quality, favorite status, and file size.

```bash
python3 scripts/duplicate_finder.py [--human] [--output FILE]
```

**Detection Methods:**
1. **Apple's built-in** — Uses `ZDUPLICATEASSETVISIBILITYSTATE`
2. **Timestamp + dimensions** — Photos taken at same second with same dimensions

**Recommendation Logic:**
- Favorites get priority
- Screenshots get penalty
- Highest quality score preferred
- Largest file size as tiebreaker

**Example Output:**
```
👥 DUPLICATE FINDER RESULTS
==================================================

Found 12 duplicate groups
Total duplicates: 27
Can safely delete: 15
Total size: 156 MB
Potential savings: 89 MB

Sample groups (showing first 5):

Group 1 (apple_builtin):
  ✓ KEEP ★ IMG_1234.jpg (4.2 MB, Q:0.823)
    DELETE   IMG_1234-2.jpg (4.1 MB, Q:0.801)

Group 2 (timestamp_dimensions):
  ✓ KEEP   IMG_5678.heic (2.8 MB, Q:0.756)
    DELETE   IMG_5678-edited.jpg (3.1 MB, Q:0.654)
```

**Usage in Conversation:**

**User:** "Do I have duplicate photos?"  
**AI:** *Runs duplicate_finder.py, reports findings*

**User:** "Find duplicates and tell me which to delete"  
**AI:** *Runs duplicate_finder.py, explains recommendations*

---

### 4. Storage Analyzer

Detailed storage breakdown: by year, type, source, growth trends, file types, storage hogs.

```bash
python3 scripts/storage_analyzer.py [--human] [--output FILE]
```

**Analyzes:**
- Total storage and breakdown by photo/video
- Storage by year and month
- Screenshots vs regular photos
- File types (JPEG, HEIC, MOV, etc.)
- Growth trends over time
- Top 20 largest files

**Example Output:**
```
💾 STORAGE ANALYSIS
==================================================

Total Storage: 48.3 GB

By Type:
  Photo: 32.1 GB (66.5%)
    11,234 items, avg 2.9 MB
  Video: 16.2 GB (33.5%)
    891 items, avg 18.7 MB

By Source:
  Photos & Videos: 46.1 GB (95.4%)
  Screenshots: 2.2 GB (4.6%)

By Year:
  2025: 5.2 GB (1,203 items)
  2024: 15.1 GB (3,456 items)
  2023: 12.4 GB (2,987 items)
  ...

Top 10 Largest Files:
  1. 📹 287 MB - VID_2024_vacation.mov
  2. 📹 245 MB - VID_2024_swim_meet.mov
  3. 📹 198 MB - VID_2023_birthday.mov
  ...

Recent Growth (last 12 months):
  Total added: 18.7 GB
  Average per month: 1.6 GB
```

**Usage in Conversation:**

**User:** "What's taking up space in my Photos?"  
**AI:** *Runs storage_analyzer.py, highlights biggest categories*

**User:** "Show me my largest videos"  
**AI:** *Runs storage_analyzer.py, focuses on storage_hogs section filtered by videos*

**User:** "How much storage am I adding per month?"  
**AI:** *Runs storage_analyzer.py, reports recent growth stats*

---

### 5. Timeline Recap

Generate narrative summaries of photo activity for any date range. Groups photos into events and includes context: people, locations, scenes.

```bash
python3 scripts/timeline_recap.py --start-date YYYY-MM-DD [--end-date YYYY-MM-DD] [--narrative]
```

**Options:**
- `--start-date` — Start date (required)
- `--end-date` — End date (optional, defaults to today)
- `--cluster-hours N` — Hours between photos to consider separate events (default: 4)
- `--narrative` — Output narrative text instead of JSON
- `--output FILE` — Write to file

**What It Generates:**
- Day-by-day photo activity
- Event clustering (groups photos taken close together)
- People detected in each event
- Scene classifications (beach, sunset, dog, etc.)
- Location data (if available)
- Favorites count

**Example Output:**
```
📅 PHOTO TIMELINE RECAP
==================================================

Period: 2025-03-01 to 2025-03-07
Total: 156 photos across 5 days
Events: 12

📆 2025-03-01 (Saturday) - 45 photos

  🕐 09:15 (2h 15m)
     32 photos, 2 videos ⭐ 5 favorites
     👥 Jonah, Silas
     🏷️  swimming, pool, sports
     📍 41.5369, -90.5776

  🕐 18:30 (45m)
     13 photos
     👥 Jonah, Silas
     🏷️  dinner, food, family
```

**Usage in Conversation:**

**User:** "What did I do last week?"  
**AI:** *Runs timeline_recap.py with last week's dates, narrates the timeline in story form*

**User:** "Show me my photo activity for February"  
**AI:** *Runs timeline_recap.py with Feb 1 - Feb 28, summarizes highlights*

**User:** "Tell me about our vacation photos from August"  
**AI:** *Runs timeline_recap.py with August dates, creates a narrative story*

**AI Tip:** When presenting timeline results, narrate them like a story! Don't just dump the JSON. Example:

> "You had a busy Saturday on March 1st! In the morning around 9:15, you spent about 2 hours at the pool — 32 photos with Jonah and Silas, mostly swimming and sports shots. You marked 5 as favorites. Then in the evening around 6:30, you captured a family dinner with 13 photos. Looks like a great day!"

---

### 6. Smart Export

Plan organized exports by year/month, person, album, or location. Shows what will be exported without actually doing it (unless confirmed).

```bash
python3 scripts/smart_export.py --output-dir PATH [--organize-by MODE] [--plan-only]
```

**Options:**
- `--output-dir PATH` — Where to export (required)
- `--organize-by MODE` — How to organize: `year_month`, `person`, `album`, `location` (default: year_month)
- `--favorites` — Export only favorites
- `--start-date YYYY-MM-DD` — Filter by start date
- `--end-date YYYY-MM-DD` — Filter by end date
- `--person NAME` — Export only photos with this person
- `--album NAME` — Export only from this album
- `--plan-only` — Show plan without exporting (recommended first step)

**Example Output:**
```
📤 EXPORT PLAN
==================================================
Organization: year_month
Total photos: 3,456
Total size: 15.2 GB
Folders: 36

Folders:
  2025/01-January/
    123 items, 542 MB
  2025/02-February/
    156 items, 687 MB
  2025/03-March/
    89 items, 398 MB
  ...
```

**Note:** Actual export via AppleScript is not fully implemented. This command generates the export plan and folder structure. For now, use this to identify what to export, then do it manually in Photos.app.

**Usage in Conversation:**

**User:** "I want to export all my 2024 photos organized by month"  
**AI:** *Runs smart_export.py with year filter and --plan-only, shows the plan*

**User:** "Export all photos with Jonah"  
**AI:** *Runs smart_export.py with --person "Jonah" and --plan-only, shows what would be exported*

---

### 7. Best Photos / Hidden Gems

Surface your highest-quality photos using Apple's computed quality scores. Find hidden gems — great photos you never favorited.

```bash
python3 scripts/best_photos.py [--min-quality N] [--top N] [--hidden-gems] [--human]
```

**Options:**
- `--min-quality N` — Minimum quality score threshold (default: 0.7, range: 0.0-1.0)
- `--top N` — Number of top photos to return (default: 50)
- `--hidden-gems` — Only show photos that are NOT favorited
- `--year YYYY` — Filter to specific year
- `--human` — Human-readable summary
- `--output FILE` — Write JSON to file

**What It Shows:**
- Quality score distribution across your library (excellent/good/average/poor)
- Top N photos ranked by quality with detailed score breakdowns
- Hidden gems: high-quality photos you haven't favorited yet
- Per-photo scores for composition, lighting, symmetry, patterns, etc.

**Example Output:**
```
⭐ BEST PHOTOS / HIDDEN GEMS
==================================================

Photos with quality scores: 11,234
Above threshold (0.7): 2,456
Hidden gems (great but not favorited): 2,100
Already favorited high-quality: 356

Quality Distribution:
  🌟 Excellent (≥0.85): 456
  ✅ Good (≥0.70):      2,000
  📊 Average (≥0.50):   5,234
  📉 Below avg (≥0.30): 2,544
  ❌ Poor (<0.30):       1,000

Top 20 Photos:
    1. IMG_1234.jpg
       Q:0.952 | 4.2 MB | 4032x3024 💎
       📐 composition:0.95, lighting:0.92, symmetry:0.88
```

**Usage in Conversation:**

**User:** "Show me my best photos"  
**AI:** *Runs best_photos.py with --human flag, highlights top shots*

**User:** "Find hidden gems I haven't favorited"  
**AI:** *Runs best_photos.py with --hidden-gems, suggests which to favorite*

**User:** "What are my best photos from 2025?"  
**AI:** *Runs best_photos.py with --year 2025, shows quality distribution and top picks*

---

### 8. People Analyzer

Deep analysis of people detected in your photos: who appears most, who's photographed together, trends over time, best photo of each person.

```bash
python3 scripts/people_analyzer.py [--min-photos N] [--top N] [--human]
```

**Options:**
- `--min-photos N` — Minimum photos to include a person (default: 5)
- `--top N` — Number of top people to analyze in detail (default: 20)
- `--human` — Human-readable summary
- `--output FILE` — Write JSON to file

**What It Shows:**
- All named people ranked by photo count
- Per-person yearly trends (are you photographing them more or less?)
- Co-occurrence analysis (who appears together most)
- Best quality photo for each person
- Favorites count per person
- Unnamed face count

**Example Output:**
```
👥 PEOPLE ANALYZER
==================================================

Named people (≥5 photos): 15
Photos with unnamed faces: 1,234

Top People:
  Jonah: 3,456 photos (★ 89)
    📅 2023:890, 2024:1,200, 2025:1,366
  Silas: 3,234 photos (★ 76)
    📅 2023:845, 2024:1,100, 2025:1,289

Frequently Photographed Together:
  Jonah + Silas: 2,100 photos
  Jonah + Mom: 456 photos
```

**Usage in Conversation:**

**User:** "Who's in my photos the most?"  
**AI:** *Runs people_analyzer.py, reports top people with counts*

**User:** "Who do I photograph together?"  
**AI:** *Runs people_analyzer.py, focuses on co-occurrence analysis*

---

### 9. Location / Travel Mapper

Analyze where your photos were taken. Clusters GPS coordinates into locations, identifies trips, and shows most-photographed places.

```bash
python3 scripts/location_mapper.py [--radius N] [--year YYYY] [--human]
```

**Options:**
- `--radius N` — Cluster radius in km (default: 1.0)
- `--year YYYY` — Filter to specific year
- `--min-photos N` — Minimum photos per location cluster (default: 3)
- `--human` — Human-readable summary
- `--output FILE` — Write JSON to file

**What It Shows:**
- GPS coverage percentage
- Location clusters with photo counts, date ranges, and people
- Identified trips (clusters with 5+ photos spanning 4+ hours)
- Per-location monthly breakdown

**Example Output:**
```
📍 LOCATION / TRAVEL MAPPER
==================================================

Photos with GPS: 8,456 (67.9%)
Without GPS: 3,997
Unique locations: 45
Possible trips: 12

Top Locations:
    1. (41.5369, -90.5776)
       1,234 photos ⭐12 🧳 | 5.2 GB
       📅 2020-01-15 → 2025-03-03
       👥 Jonah, Silas
```

**Usage in Conversation:**

**User:** "Where have I taken the most photos?"  
**AI:** *Runs location_mapper.py, reports top locations*

**User:** "Show me my trips from 2025"  
**AI:** *Runs location_mapper.py with --year 2025, highlights identified trips*

---

### 10. Scene / Content Search

Search photos by ML-detected scene classifications (beach, sunset, dog, food, etc.) or generate a complete content inventory.

```bash
python3 scripts/scene_search.py [--search TERM] [--min-confidence N] [--human]
```

**Options:**
- `--search TERM` — Scene name to search for (omit for content inventory)
- `--min-confidence N` — Minimum confidence score (default: 0.0)
- `--top N` — Number of search results (default: 50)
- `--year YYYY` — Filter to specific year
- `--human` — Human-readable summary
- `--output FILE` — Write JSON to file

**Modes:**
1. **Search mode** (`--search beach`) — Find all photos matching a scene label
2. **Inventory mode** (no --search) — Show all scene labels with counts, grouped by category

**Example Output (inventory):**
```
🏷️  SCENE / CONTENT SEARCH
==================================================

Unique scene labels: 234
Scene-tagged entries: 45,678
Library total: 12,453

By Category:
  📂 Nature Outdoor (5,678 photos)
    beach: 234
    sunset: 189
    mountain: 156
  📂 Animals (2,345 photos)
    dog: 1,234
    cat: 567
  📂 Food Drink (1,890 photos)
    food: 890
    coffee: 234
```

**Usage in Conversation:**

**User:** "How many beach photos do I have?"  
**AI:** *Runs scene_search.py --search beach, reports count and related scenes*

**User:** "What kinds of photos do I take?"  
**AI:** *Runs scene_search.py (inventory mode), summarizes categories*

---

### 11. Photo Habits & Insights

Behavioral analytics: when you shoot most, busiest days, seasonal patterns, streaks, photo vs video ratio trends.

```bash
python3 scripts/photo_habits.py [--year YYYY] [--human]
```

**Options:**
- `--year YYYY` — Filter to specific year
- `--human` — Human-readable summary
- `--output FILE` — Write JSON to file

**What It Shows:**
- Time-of-day breakdown (morning/afternoon/evening/night)
- Peak hour, peak day of week, peak month
- Day-of-week distribution with visual bars
- Longest photo streak (consecutive days with photos)
- Busiest single day
- Year-over-year trends with video ratio
- Monthly trend with photos/videos/screenshots breakdown

**Example Output:**
```
📊 PHOTO HABITS & INSIGHTS
==================================================

Total: 11,234 photos, 891 videos, 328 screenshots
Average per active day: 8.3

⏰ When You Shoot:
  Peak hour: 14:00
  Peak day: Saturday
  Peak month: Jul

  Time of Day:
    Morning (6am-12pm):   3,456 (28.1%) █████████
    Afternoon (12pm-6pm): 5,123 (41.6%) █████████████
    Evening (6pm-12am):   2,987 (24.3%) ████████
    Night (12am-6am):       737 (6.0%)  ██

🔥 Streaks:
  Longest streak: 45 consecutive days
    (2024-06-15 → 2024-07-29)
```

**Usage in Conversation:**

**User:** "What are my photo-taking patterns?"  
**AI:** *Runs photo_habits.py, narrates key insights*

**User:** "When do I take the most photos?"  
**AI:** *Runs photo_habits.py, highlights peak times and days*

---

### 12. On This Day / Memory Lane

See what you photographed on today's date in previous years. Includes people, scenes, and quality context.

```bash
python3 scripts/on_this_day.py [--date YYYY-MM-DD] [--window N] [--human]
```

**Options:**
- `--date YYYY-MM-DD` — Target date (defaults to today)
- `--window N` — Include photos ±N days around target (default: 0)
- `--human` — Human-readable summary
- `--output FILE` — Write JSON to file

**What It Shows:**
- Photos from each previous year on the same date
- People, scenes, and best photo for each year
- Favorites count per year
- How many years ago each set of photos was taken

**Example Output:**
```
📅 ON THIS DAY
==================================================

Date: March 3
Photos found: 45 across 4 years

📆 2025 (1 year ago)
   12 photos, ⭐ 3
   👥 Jonah, Silas
   🏷️  swimming, pool
   📸 Best: IMG_1234.jpg Q:0.89

📆 2024 (2 years ago)
   8 photos
   👥 Jonah
   🏷️  park, outdoor
```

**Usage in Conversation:**

**User:** "What did I do on this day in past years?"  
**AI:** *Runs on_this_day.py, narrates memories year by year*

**User:** "Show me memories from March 3"  
**AI:** *Runs on_this_day.py --date 2026-03-03, tells the story*

**AI Tip:** Narrate memories warmly! "2 years ago today, you were at the pool with Jonah and Silas — you took 12 photos and favorited 3 of them. The best shot has a quality score of 0.89!"

---

### 13. Album Auditor

Find orphan photos (not in any album), empty albums, tiny albums, and overlapping albums.

```bash
python3 scripts/album_auditor.py [--human]
```

**Options:**
- `--human` — Human-readable summary
- `--output FILE` — Write JSON to file

**What It Shows:**
- Orphan photos count (not in any album)
- Empty albums that can be deleted
- Tiny albums (≤3 photos) that might be incomplete
- Album overlap (shared photos between albums, with percentages)
- Album size ranking

**Example Output:**
```
📁 ALBUM AUDITOR
==================================================

Total albums: 45
Albums with photos: 38
Empty albums: 4
Tiny albums (≤3 photos): 7
Photos in albums: 8,234 / 12,453
Orphan photos (no album): 4,219

📭 Orphan Photos:
  4,219 photos not in any album
  Total size: 18.3 GB

🗑️  Empty Albums (4):
  • Old Vacation
  • Test Album

🔄 Album Overlaps:
  "Vacation 2024" ∩ "Summer 2024"
    45 shared (12.3% / 8.9%)
```

**Usage in Conversation:**

**User:** "Are my photos well organized?"  
**AI:** *Runs album_auditor.py, reports orphans, empty albums, and overlap*

**User:** "How many photos aren't in any album?"  
**AI:** *Runs album_auditor.py, reports orphan count and size*

---

### 14. Cleanup Executor

Actually move junk photos to trash via AppleScript. Supports old screenshots, burst leftovers, low quality, and duplicates. All items go to Recently Deleted (recoverable for 30 days).

```bash
python3 scripts/cleanup_executor.py --category CATEGORY [--execute] [--human]
```

**Options:**
- `--category` — What to clean up: `old_screenshots`, `all_screenshots`, `burst_leftovers`, `low_quality`, `duplicates`
- `--screenshot-age N` — Screenshot age in days for old_screenshots (default: 30)
- `--quality-threshold N` — Quality threshold for low_quality (default: 0.3)
- `--limit N` — Maximum items to process (default: 500)
- `--execute` — Actually perform the cleanup (without this, preview only)
- `--batch-size N` — Items per AppleScript batch (default: 50)
- `--human` — Human-readable summary

**Safety:**
- Without `--execute`, shows preview only (dry run)
- With `--execute`, requires typing 'yes' to confirm
- Items are moved to Recently Deleted (not permanently deleted)
- 30-day recovery window in Photos.app
- Uses AppleScript through Photos.app (never touches database directly)

**Example Usage:**
```bash
# Preview what would be cleaned
python3 scripts/cleanup_executor.py --category old_screenshots --human

# Actually clean up (with confirmation prompt)
python3 scripts/cleanup_executor.py --category old_screenshots --execute

# Clean burst leftovers
python3 scripts/cleanup_executor.py --category burst_leftovers --execute
```

**Usage in Conversation:**

**User:** "Delete my old screenshots"  
**AI:** *Runs cleanup_executor.py --category old_screenshots --human first to show preview, then prompts user before running with --execute*

**User:** "Clean up burst photos"  
**AI:** *Runs cleanup_executor.py --category burst_leftovers --human, shows count and size, asks for confirmation*

**⚠️ AI Tip:** Always show the preview first! Never run with --execute without showing the user what will be affected and getting confirmation.

---

### 15. Live Photo Analyzer

Analyze Live Photos vs still photos: identify Live Photos, compare storage impact, find Live Photos that could be converted to stills to save space.

```bash
python3 scripts/live_photo_analyzer.py [--human] [--year YYYY] [--output FILE]
```

**Options:**
- `--year YYYY` — Filter to specific year
- `--human` — Human-readable summary
- `--output FILE` — Write JSON to file

**What it reports:**
- Total Live Photos vs stills (count and storage)
- Playback style breakdown (live, loop, bounce, long exposure)
- Year-over-year Live Photo trends
- Estimated savings if Live Photos were converted to stills (~50% of video component)
- Unfavorited Live Photos as conversion candidates
- Largest Live Photos (biggest savings first)

---

### 16. Shared Library Analysis

Analyze the Shared Library in Apple Photos: personal vs shared content, contributor breakdown, storage impact.

```bash
python3 scripts/shared_library.py [--human] [--output FILE]
```

**What it reports:**
- Whether Shared Library is enabled
- Personal vs shared asset counts and storage
- Contributor identifiers and their contributions
- Shared content by year and monthly trends
- Photo/video split for shared content

**Note:** Requires macOS 13+ / iOS 16+ database format for Shared Library columns.

---

### 17. iCloud Sync Status

Check iCloud sync coverage across the library: synced vs local-only, download status, large unsynced items.

```bash
python3 scripts/icloud_status.py [--human] [--output FILE]
```

**What it reports:**
- Sync coverage percentage (synced vs local-only)
- Storage breakdown by sync state
- Photo vs video sync comparison
- Year-over-year sync trends
- Large local-only items (>10 MB) that aren't synced
- My assets vs others' assets
- Downloadable (cloud-only) item count

---

### 18. Photo Similarity Detection

Find visually similar photos beyond exact duplicates using computed quality feature vectors (composition, lighting, color, patterns, etc.).

```bash
python3 scripts/similarity_finder.py [--threshold 0.95] [--year YYYY] [--limit 500] [--human]
```

**Options:**
- `--threshold` — Cosine similarity threshold 0-1 (default: 0.95, very similar)
- `--year YYYY` — Filter to specific year
- `--limit N` — Max photos to compare (default: 500, controls runtime)
- `--human` — Human-readable summary

**What it reports:**
- Groups of visually similar photos
- Potential storage savings per group
- Keep candidate (largest/highest quality in each group)
- Total extra (removable) similar photos

**Runtime note:** O(n²) comparison; use `--limit` to control runtime for large libraries.

---

### 19. Seasonal Highlights

Curate the best photos from each season using quality scores, favorites, and scene context.

```bash
python3 scripts/seasonal_highlights.py [--year YYYY] [--top 20] [--southern] [--human]
```

**Options:**
- `--year YYYY` — Filter to specific year
- `--top N` — Top N photos per season (default: 20)
- `--southern` — Use Southern Hemisphere season definitions
- `--human` — Human-readable summary

**What it reports:**
- Best photos per season (spring, summer, fall, winter)
- Season-by-season quality scores and favorite counts
- Year-over-season distribution matrix
- Busiest season identification
- Best single photo per season

---

### 20. Face Quality Scoring

Score face quality per person using Apple Photos' face detection attributes: quality measure, blur, yaw angle, smile, face size, and center position.

```bash
python3 scripts/face_quality.py [--person NAME] [--top 10] [--human]
```

**Options:**
- `--person NAME` — Filter to specific person name
- `--top N` — Top N best/worst per person (default: 10)
- `--human` — Human-readable summary

**What it reports:**
- Per-person face quality rankings
- Best and worst portraits per person
- Composite face score (quality, blur, size, yaw, smile, center)
- Overall library face quality average
- Most photographed person, highest quality person

---

## Database Schema Reference

Detailed schema documentation is in `references/database-schema.md`. Key tables:

- **ZASSET** — Main photos/videos table
- **ZADDITIONALASSETATTRIBUTES** — File sizes, dimensions
- **ZCOMPUTEDASSETATTRIBUTES** — Apple's quality scores
- **ZPERSON** — Detected people
- **ZDETECTEDFACE** — Face detections
- **ZGENERICALBUM** — Albums
- **ZSCENECLASSIFICATION** — ML scene labels

**Important:** Core Data timestamps are seconds since 2001-01-01, not Unix epoch.

## Common Workflows

### Workflow 1: Quick Cleanup Assessment

```bash
# Get overview
python3 scripts/library_analysis.py --human

# Find junk
python3 scripts/junk_finder.py --human

# Review and manually clean up in Photos.app
```

### Workflow 2: Free Up Storage

```bash
# Analyze storage
python3 scripts/storage_analyzer.py --human

# Find duplicates
python3 scripts/duplicate_finder.py --human

# Find junk with aggressive settings
python3 scripts/junk_finder.py --screenshot-age 14 --quality-threshold 0.4 --human

# Use findings to guide cleanup
```

### Workflow 3: Year-End Photo Recap

```bash
# Generate timeline for the year
python3 scripts/timeline_recap.py --start-date 2024-01-01 --end-date 2024-12-31 --narrative

# Get storage stats by year
python3 scripts/storage_analyzer.py | jq '.by_year'

# Get top people for the year
python3 scripts/library_analysis.py | jq '.top_people'

# Photo habits for the year
python3 scripts/photo_habits.py --year 2024 --human

# Best photos of the year
python3 scripts/best_photos.py --year 2024 --top 20 --human
```

### Workflow 4: Export Organized Archive

```bash
# Plan export
python3 scripts/smart_export.py --output-dir ~/Desktop/Photos-Export --favorites --start-date 2024-01-01 --plan-only

# Review plan, then execute (manual for now)
```

### Workflow 5: Deep Cleanup

```bash
# Find all junk
python3 scripts/junk_finder.py --human

# Preview old screenshots
python3 scripts/cleanup_executor.py --category old_screenshots --human

# Execute cleanup (with confirmation)
python3 scripts/cleanup_executor.py --category old_screenshots --execute

# Clean burst leftovers
python3 scripts/cleanup_executor.py --category burst_leftovers --execute

# Check album health
python3 scripts/album_auditor.py --human
```

### Workflow 6: Daily Memory Check

```bash
# See what happened on this day in past years
python3 scripts/on_this_day.py --human

# With a wider window
python3 scripts/on_this_day.py --window 2 --human
```

### Workflow 7: Location & Travel Review

```bash
# See all your locations
python3 scripts/location_mapper.py --human

# Focus on trips from a specific year
python3 scripts/location_mapper.py --year 2025 --human

# What content you shot at those places
python3 scripts/scene_search.py --human
```

### Workflow 8: People Deep Dive

```bash
# Who's in your photos
python3 scripts/people_analyzer.py --human

# Find hidden gems of specific people
python3 scripts/best_photos.py --hidden-gems --human

# Best and worst portraits per person
python3 scripts/face_quality.py --human
```

### Workflow 9: Live Photo & Storage Optimization

```bash
# Analyze Live Photos vs stills
python3 scripts/live_photo_analyzer.py --human

# Find similar photos (potential duplicates)
python3 scripts/similarity_finder.py --threshold 0.95 --human

# Check iCloud sync status
python3 scripts/icloud_status.py --human
```

### Workflow 10: Seasonal Year in Review

```bash
# Get seasonal highlights
python3 scripts/seasonal_highlights.py --year 2024 --human

# Location review with place names
python3 scripts/location_mapper.py --year 2024 --human

# Photo habits for the year
python3 scripts/photo_habits.py --year 2024 --human
```

### Workflow 11: Shared Library Audit

```bash
# Check shared library status
python3 scripts/shared_library.py --human

# See who contributed what and storage impact
python3 scripts/shared_library.py --output shared_report.json
```

## Tips for AI Assistants

### When User Asks About Photos Cleanup

1. **Start with analysis** — Run `library_analysis.py` to understand the library
2. **Find junk** — Run `junk_finder.py` to quantify cleanup opportunities
3. **Be specific** — Don't just say "you have junk photos," say "you have 287 screenshots older than 30 days (2.1 GB) that could be deleted"
4. **Explain savings** — Always mention estimated storage savings
5. **Guide to Photos.app** — Scripts identify candidates, but user must delete via Photos.app

### When User Asks "What Did I Do?"

1. **Use timeline_recap** — Perfect for narrative summaries
2. **Narrate, don't dump** — Turn JSON into a story
3. **Highlight favorites** — Mention standout moments
4. **Use emojis** — Makes it more engaging

### When User Asks About Storage

1. **Run storage_analyzer** — Most comprehensive view
2. **Identify hogs** — Call out the biggest files/categories
3. **Show trends** — "You're adding about 1.5 GB per month"
4. **Suggest actions** — "Deleting old screenshots could free up 2 GB"

### When User Asks About Best/Favorite Photos

1. **Use best_photos** — Shows quality distribution and top picks
2. **Highlight hidden gems** — Use --hidden-gems to find unfavorited great shots
3. **Show scores** — Explain what makes a photo high quality (composition, lighting, etc.)

### When User Asks About People

1. **Use people_analyzer** — Comprehensive people stats
2. **Show co-occurrences** — "Jonah and Silas appear together in 2,100 photos"
3. **Show trends** — "You photographed Jonah 40% less in 2025"

### When User Asks "On This Day" / Memories

1. **Use on_this_day** — Perfect for nostalgia
2. **Narrate warmly** — Tell the story of each year
3. **Suggest window** — If nothing found, suggest --window 2 for nearby dates

### When User Wants to Actually Delete

1. **Always preview first** — Run cleanup_executor without --execute
2. **Show counts and sizes** — "287 old screenshots, 2.1 GB"
3. **Explain safety** — Items go to Recently Deleted, recoverable for 30 days
4. **Get confirmation** — Never auto-execute cleanup

### Output Format Guidance

**JSON output:** Default for programmatic use, includes full details

**Human output:** Use `--human` flag for readable summaries

**In conversation:** Synthesize the data into natural language, don't just read the output

## Requirements

- **Python:** 3.9+ (tested with 3.13)
- **Platform:** macOS only (Apple Photos database)
- **Dependencies:** None (uses only Python stdlib)
- **Database:** Read-only access to `~/Pictures/Photos Library.photoslibrary/database/Photos.sqlite`

## Safety & Permissions

- ✅ **All operations are READ-ONLY** — No photos are modified or deleted
- ✅ **No external dependencies** — Pure Python stdlib
- ✅ **No Photos.app API** — Direct SQLite reads (safe)
- ⚠️ **Smart export uses AppleScript** — Requires Photos.app to be running
- ⚠️ **Cleanup executor uses AppleScript** — Moves items to Recently Deleted (recoverable)

## Limitations

- **Read-only analysis** — Scripts identify candidates, but cleanup must be confirmed by user
- **Export via AppleScript** — Requires Photos.app to be running
- **Reverse geocoding** — Offline lookup covers ~100 major world cities; remote locations show coordinates
- **Similarity detection** — Uses computed quality vectors (not pixel-level); O(n²) comparison limited by `--limit`
- **Shared Library columns** — Requires macOS 13+ / iOS 16+ database format
- **Empty library support** — Scripts work on any library, but Matt's Mac mini library is empty (synced elsewhere)
- **Schema changes** — Apple may change database schema in future macOS versions

## Troubleshooting

**"Database not found"**  
→ Specify path with `--library ~/Path/To/Photos Library.photoslibrary`

**"Permission denied"**  
→ Close Photos.app first, or run script while Photos.app is open (read-only is safe)

**"No quality scores"**  
→ Not all photos have computed quality attributes; scripts handle NULLs gracefully

**"Results don't match Photos.app counts"**  
→ Scripts exclude trashed items; Photos.app may show different views

## Future Enhancements

All previously planned features have been implemented! Possible further expansions:
- Machine learning model export for custom photo classifiers
- Photo deduplication across multiple Photos libraries
- Integration with external photo services (Google Photos, Flickr)
- Time-lapse generation from photo sequences
- Custom smart album rule builder
- Photo metadata repair / bulk editing suggestions

---

**Bottom line:** This skill gives you X-ray vision into your Photos library. Use it to understand what you have, find what you don't need, and make cleanup decisions with confidence.
