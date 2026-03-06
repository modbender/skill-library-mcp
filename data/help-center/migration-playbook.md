# Migration Playbook — Help Center

Use this flow when moving from spreadsheets, legacy docs, or another provider.

## Phase 1: Discovery

1. Export all current articles, categories, and redirects.
2. Build an inventory with status: keep, merge, rewrite, archive.
3. Capture top ticket intents from the last 90 days.
4. Identify compliance or legal retention requirements.

## Phase 2: Mapping

1. Define target taxonomy and URL conventions.
2. Map source categories and tags to target structure.
3. Draft redirect table from old URLs to new URLs.
4. Assign article owners for each category.

## Phase 3: Dry Run

1. Import sample content into staging environment.
2. Validate formatting, links, search quality, and permissions.
3. Test escalation routes from article failure to ticket queue.
4. Run user acceptance tests with support and product teams.

## Phase 4: Launch

1. Freeze source edits during cutover window.
2. Import final content and apply redirect rules.
3. Monitor errors, search misses, and ticket spikes for 48 hours.
4. Keep rollback script ready until stability is confirmed.

## Post-Launch Checks

- Redirect hit rate above 95%
- No critical broken links
- Search miss rate trending down week over week
- Support agents trained on new taxonomy and tagging
