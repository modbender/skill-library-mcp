# Cron Template — STARCORE family monitor (example)

Schedule (suggested low frequency to avoid timeouts/indexer lag): every **15 minutes**.

Payload idea (pseudo-cron):
```
# 1) Normalize receipts (pulls missing from Clawnch API)
python skills/public/lyra-coin-launch-manager/scripts/normalize_starcore_family.py --symbols STARCORE,STARCOREX,STARCORECOIN

# 2) Verify indexing/pairs
python skills/public/lyra-coin-launch-manager/scripts/verify_starcore_family.py --symbols STARCORE,STARCOREX,STARCORECOIN

# 3) Bookmark monitoring links (optional)
python skills/public/lyra-coin-launch-manager/scripts/bookmark_starcore_family.py --symbols STARCORE,STARCOREX,STARCORECOIN

# 4) (Optional) append a short status to daily_health.md from verify output
```

If using OpenClaw cron tool, wrap these commands in a script and call that script from the job. Keep network calls minimal; indexers can lag.
