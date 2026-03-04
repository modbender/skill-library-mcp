---
name: influencer-report
description: Generate a comprehensive influencer vetting report. Use when someone asks to vet, analyze, or review an influencer/creator. Takes a creator profile URL or video URLs and produces a brand safety and content quality report powered by Memories.ai video intelligence.
---

# Influencer Report Skill

Vet influencers by analyzing their recent videos with Memories.ai V1 + V2 APIs.

## Setup

Required environment variables:
- `MEMORIES_V1_API_KEY` — Memories.ai V1 API key (scraper, library, search)
- `MEMORIES_API_KEY` — Memories.ai V2 API key (MAI transcript, metadata)

## Quick Start

**From a profile URL (auto-scrapes recent videos):**
```bash
python3 scripts/influencer_report.py --handle charlidamelio \
  --profile-url "https://www.tiktok.com/@charlidamelio" --scrape-count 5
```

**From direct video URLs:**
```bash
python3 scripts/influencer_report.py --handle creator_name --platform tiktok \
  --videos https://tiktok.com/@user/video/1 https://tiktok.com/@user/video/2
```

## Workflow

1. **Scrape** — V1 `/scraper` ingests creator's recent videos from their profile URL
2. **List & Search** — V1 `/list_videos` and `/search` retrieve the ingested content
3. **Analyze** — V2 MAI Transcript API provides visual + audio analysis per video
4. **Metadata** — V2 Metadata API pulls engagement stats (views, likes, comments)
5. **Score & Report** — Content quality scoring + formatted markdown report

## API Endpoints Used

| Step | API | Endpoint |
|------|-----|----------|
| Scrape profile | V1 | `POST /serve/api/v1/scraper` |
| List library | V1 | `POST /serve/api/v1/list_videos` |
| Search library | V1 | `POST /serve/api/v1/search` |
| MAI transcript | V2 | `POST /serve/api/v2/{platform}/video/mai/transcript` |
| Video metadata | V2 | `POST /serve/api/v2/{platform}/video/metadata` |

## Report Format

See `references/report-format.md` for the full template and scoring guide.
