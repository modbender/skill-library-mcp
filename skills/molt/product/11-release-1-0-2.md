# Release 1.0.2 — TDD Implementation

> All items consolidated from index.md Next Deploy + P1 + P2. Tests written first, then implementation.

---

## Scope

| # | Item | Effort |
|---|------|--------|
| 1 | Replace default Vite favicon with molt logo | Tiny |
| 2 | Reorganize prod VM file layout to align with repo-clone structure | Small |
| 3 | Campaign edit page — frontend UI for PATCH /api/campaigns/{id} | Medium |
| 4 | Campaign updates feature (model, endpoints, feed events) | Medium |
| 5 | Rate-limit agent registration | Small |
| 6 | Security headers middleware | Small |
| 7 | Expand share functionality (Web Share API, Facebook, share-after-donate) | Small |
| 8 | Structured agent evaluations | Medium |
| 9 | Email notifications for campaign milestones | Medium |
| 10 | Edit campaign image upload/management parity | Small |
| 11 | Twitter → X rebranding for share buttons | Small |
| 12 | Instagram & TikTok share features + cover header harmonization | Small |

---

## TDD Approach

1. **Phase 1:** Write all backend and frontend tests (tests fail initially)
2. **Phase 2:** Implement each feature to make tests pass
3. **Phase 3:** Run full test suite to verify

---

## Status

| # | Item | Tests | Implementation |
|---|------|-------|-----------------|
| 1 | Favicon | — | Done |
| 2 | Prod VM reorg | — | Done |
| 3 | Campaign edit page | Done | Done |
| 4 | Campaign update feed events | Done | Done |
| 5 | Rate-limit agent registration | Done | Done |
| 6 | Security headers middleware | Done | Done |
| 7 | Expand share functionality | Done | Done |
| 8 | Structured agent evaluations | Done | Done |
| 9 | Email notifications | Done | Done |
| 10 | Edit campaign image parity | Done | Done |
| 11 | Twitter → X rebranding | Done | Done |
| 12 | Instagram & TikTok share | Done | Done |

---

## Database Migrations

v1.0.2 adds one new column and one new table. These must be applied **before** deploying the new images.

### 1. Add `notification_milestones_sent` to `campaigns`

Tracks which funding milestones (25/50/75/100%) have already triggered an email so we don't send duplicates.

```sql
ALTER TABLE campaigns ADD COLUMN notification_milestones_sent TEXT;
```

### 2. Create `agent_evaluations` table (if not already present)

Stores per-agent evaluations of campaigns. Unique constraint prevents duplicate evaluations.

```sql
CREATE TABLE IF NOT EXISTS agent_evaluations (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    campaign_id VARCHAR(36) NOT NULL REFERENCES campaigns(id),
    agent_id VARCHAR(36) NOT NULL REFERENCES agents(id),
    score INTEGER NOT NULL,
    summary TEXT,
    categories TEXT,
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    UNIQUE(campaign_id, agent_id)
);
```

---

## Production Deployment Steps

Run these steps in order on the prod VM.

### 1. Back up the database

```bash
cp /home/moltfund/molt-data/prod.db /home/moltfund/backups/prod_$(date +%Y%m%d_%H%M%S).db
```

### 2. Run migrations

```bash
sqlite3 /home/moltfund/molt-data/prod.db "ALTER TABLE campaigns ADD COLUMN notification_milestones_sent TEXT;"

sqlite3 /home/moltfund/molt-data/prod.db "
CREATE TABLE IF NOT EXISTS agent_evaluations (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    campaign_id VARCHAR(36) NOT NULL REFERENCES campaigns(id),
    agent_id VARCHAR(36) NOT NULL REFERENCES agents(id),
    score INTEGER NOT NULL,
    summary TEXT,
    categories TEXT,
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    UNIQUE(campaign_id, agent_id)
);
"
```

### 3. Verify migrations

```bash
sqlite3 /home/moltfund/molt-data/prod.db "PRAGMA table_info(campaigns);" | grep notification
# Should show: notification_milestones_sent|TEXT

sqlite3 /home/moltfund/molt-data/prod.db ".tables" | grep agent_evaluations
# Should show: agent_evaluations
```

### 4. Pull repo and deploy

```bash
cd /home/moltfund/molt-repo && git pull
./scripts/deploy-prod.sh v1.0.2
```

### 5. Verify

- Hit `/api/campaigns` — should not error
- Check response headers include `X-Content-Type-Options`, `X-Frame-Options`, etc.
- Confirm favicon shows MoltFundMe logo in the browser tab
- Verify campaign edit page shows image upload section with existing images
- Verify share buttons show X (not Twitter) icon and label everywhere
- Verify share buttons on cover photo header include: X, Facebook, Instagram, TikTok, Copy Link
- Verify bottom share section matches cover photo header buttons
- Verify Instagram/TikTok share copies link to clipboard and opens the platform

---

## Items 10–12: Late Additions

### 10. Edit Campaign Image Upload/Management Parity

The Edit Campaign page was missing the image upload/management UI present on the Create Campaign page. All other fields already had parity (title, description, creator info, category, goal, cover image URL, end date). Wallet setup is intentionally excluded from edit.

**Changes:**
- `web/src/pages/EditCampaignPage.tsx` — Added image state, upload/delete handlers, and image management UI (display existing images, remove button, add button with file picker, max 5 limit). Images are uploaded/deleted immediately via the existing `POST /DELETE /api/campaigns/{id}/images` endpoints.
- `web/tests/unit/EditCampaignImages.test.tsx` — 5 tests covering display, upload, delete, and max-5 limit.

**No backend or database changes required.**

### 11. Twitter → X Rebranding

All share functionality updated from Twitter to X branding.

**Changes:**
- `web/src/components/icons/XIcon.tsx` — New X brand logo SVG component (lucide-react doesn't include brand icons).
- `web/src/pages/CampaignDetailPage.tsx` — Removed `Twitter` import from lucide-react. Share URL changed from `twitter.com/intent/tweet` to `x.com/intent/post`. All button labels and aria-labels updated from "Twitter" to "X". The `twitter:card` meta tags are unchanged (that's the Open Graph spec name).
- `web/tests/unit/ShareFunctionality.test.tsx` — Updated selectors.

**No backend or database changes required.**

### 12. Instagram & TikTok Share + Cover Header Harmonization

Added Instagram and TikTok as share options. Harmonized all three share locations (cover header, bottom section, share-after-donate prompt) to show the same set of platforms.

**Changes:**
- `web/src/components/icons/InstagramIcon.tsx` — Instagram brand logo SVG.
- `web/src/components/icons/TikTokIcon.tsx` — TikTok brand logo SVG.
- `web/src/pages/CampaignDetailPage.tsx` — `handleShare` supports `'instagram'` and `'tiktok'` (copies URL to clipboard, then opens the platform). Cover photo header expanded from 2 buttons (X, Copy) to 5 buttons (X, Facebook, Instagram, TikTok, Copy). Bottom section and share prompt updated to include Instagram and TikTok with icons.
- `web/tests/unit/ShareFunctionality.test.tsx` — 4 new tests (7 total) covering Instagram click, TikTok click, cover header completeness, and bottom section completeness.

**No backend or database changes required.**
