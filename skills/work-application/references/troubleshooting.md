# Troubleshooting - Work Application Skill

## Setup issues

### "Master profile not found"
**Cause**: `setup.py` hasn't been run yet, or the profile was deleted.
**Fix**: Run `python3 scripts/setup.py` to create or import your master profile.

### "Permission denied: allow_write=false"
**Cause**: Config blocks writes to the master profile.
**Fix**: Edit `~/.openclaw/config/work-application/config.json` and set `"allow_write": true`, or re-run `setup.py`.

### "readonly_mode is enabled"
**Cause**: `readonly_mode: true` in config overrides all permissions.
**Fix**: Set `"readonly_mode": false` in config.json.

## CV Rendering

### "Adapted profile not found"
**Cause**: No adapted profile has been generated yet. The render command uses the adapted profile by default.
**Fix**: First adapt the master profile for a job offer, or use the master profile directly.

### HTML output looks broken
**Cause**: The profile may have missing fields or empty sections.
**Fix**: Run `python3 scripts/work_application.py profile validate` to check for errors.

### Missing sections in rendered CV
**Cause**: The profile sections (experiences, skills, etc.) may be empty or missing.
**Fix**: Check your master profile with `profile show` and ensure all sections have data.

## Scraper

### "Permission denied: allow_scrape=false"
**Cause**: Scraping is disabled by default.
**Fix**: Set `"allow_scrape": true` in config.json or re-run `setup.py`.

### "playwright not installed"
**Cause**: Playwright is required for job scraping.
**Fix**:
```bash
pip install playwright playwright-stealth
playwright install chromium
```

### Scraper returns empty results
**Cause**: Possible reasons:
1. Search queries don't match any jobs
2. Platform has changed its HTML structure
3. Anti-bot detection is blocking requests
**Fix**:
- Check your search configuration in config.json
- Try running with a single platform: `--platforms free-work`
- Increase `rate_limit_ms` in config (default: 2000)

### "TimeoutError" during scraping
**Cause**: Page load or scroll took too long.
**Fix**: Increase `scroll_timeout_ms` in config (default: 5000).

### Scraper blocked by cookies popup
**Cause**: New cookie consent dialog not recognized.
**Fix**: The scraper tries 7 common selectors. If a new one appears, it will be added in a future update.

## Tracking

### "Permission denied: allow_tracking=false"
**Cause**: Tracking is disabled in config.
**Fix**: Set `"allow_tracking": true` in config.json.

### Candidature not found for update
**Cause**: Company name doesn't match exactly (case-insensitive comparison is used).
**Fix**: Use `track list` to see exact company names, then retry the update.

### Duplicate candidatures
**Cause**: The tracker doesn't prevent duplicates by default.
**Fix**: Check existing applications with `track list` before adding.

## Analyzer

### "jobs-found.md not found"
**Cause**: The scraper hasn't been run yet.
**Fix**: Run `python3 scripts/work_application.py scrape` first.

### Low scores for all jobs
**Cause**: Keywords in `_analyzer.py` may not match your profile's skills.
**Fix**: The scoring is based on hard-coded keywords. Scores are relative - even low scores may indicate relevant jobs.

## Report

### "Impossible de scraper la page de l'offre"
**Cause**: The job page could not be loaded or returned too little text.
**Fix**:
- Check the URL is valid and accessible in a browser
- Some pages require authentication or have anti-bot protections
- Try again - transient network issues are common

### Report shows "non communique" for salary
**Cause**: No salary or TJM was detected in the job page text.
**Fix**: This is expected for many offers. The report still provides market references for comparison.

### Market data uses wrong region
**Cause**: The `market-data.json` file was generated from your profile location, which may not match.
**Fix**: Edit `~/.openclaw/data/work-application/market-data.json` manually with correct values for your region.

### Company ratings not scraped
**Cause**: `allow_scrape=false` in config, or Glassdoor/Indeed blocked the request.
**Fix**: Set `allow_scrape: true` in config. Note that review sites frequently block automated access.

## General

### init.py shows failures
**Cause**: One or more checks failed during validation.
**Fix**: Read the error messages for each failed check and fix accordingly. Most common:
- Missing master profile → run `setup.py`
- Playwright not installed → install it or set `allow_scrape: false`

### Python version error
**Cause**: Python 3.9+ is required.
**Fix**: Check your Python version: `python3 --version`. Upgrade if needed.

### File encoding issues
**Cause**: All files use UTF-8 encoding. Some terminals may not display Unicode correctly.
**Fix**: Ensure your terminal supports UTF-8 (most modern terminals do).

## Cleanup

To remove all skill data and configuration:

```bash
python3 scripts/setup.py --cleanup
```

This removes:
- `~/.openclaw/config/work-application/config.json`
- `~/.openclaw/data/work-application/profile-master.json`

It does NOT remove:
- Adapted profiles
- Candidature tracking data
- Scraped job results

To remove everything:
```bash
rm -rf ~/.openclaw/data/work-application/
rm -rf ~/.openclaw/config/work-application/
```
