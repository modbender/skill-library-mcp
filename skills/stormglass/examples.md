# Stormglass Surf Skill Examples

## Example 1: Spot Name, 72h Horizon (JSON)

Command:

```bash
python scripts/surf_report.py --location "Highcliffe Beach" --horizon 72h --output json
```

What downstream agent should do:

- Parse JSON from stdout.
- Summarize current conditions.
- Highlight best surf windows in next 1-3 days.
- Mention tide timing around chosen windows.

## Example 2: Direct Coordinates, 24h Horizon

Command:

```bash
python scripts/surf_report.py --lat 50.735 --lon -1.705 --horizon 24h --output json
```

Use when:

- Coordinates are already known.
- You want to skip geocoding latency and ambiguity.

## Example 3: Ambiguous Location Input

Command:

```bash
python scripts/surf_report.py --location "Long Beach" --horizon 48h --output json
```

Expected behavior:

- Script returns a resolved top match in `location`.
- If ambiguity is detected, script includes a warning in `meta.warnings`.
- Downstream agent can ask user to confirm region/country.

## Example 4: Pretty Output for Manual Inspection

Command:

```bash
python scripts/surf_report.py --location "Highcliffe Beach" --horizon now --output pretty
```

Use when:

- Human operator is manually inspecting output in terminal.

## Example 5: Offline Mock Run (No API Keys Needed)

Command:

```bash
python scripts/surf_report.py --location "Highcliffe Beach" --horizon 72h --mock --output json
```

Use when:

- Validating cron wiring, parser behavior, and agent formatting logic without external API calls.

## Example 6: Cron Integration

Crontab entry:

```cron
*/30 * * * * cd /home/dgorissen/code/stormglass-skill && python scripts/surf_report.py --location "Highcliffe Beach" --horizon 72h --output json >> logs/surf_report.jsonl 2>> logs/surf_report.err
```

Operational notes:

- Ensure log directory exists.
- Rotate logs externally.
- Treat non-zero exit code as fetch failure; do not trust partial stdout.

## Example 7: Downstream Agent Prompt Pattern

Prompt:

```text
Interpret this surf JSON and produce a concise user summary with:
1) conditions now, 2) best 1-3 windows in next 72h, 3) tide timing, 4) confidence notes for null fields.
```

## Example 8: Normalization Pipeline (Optional)

Command:

```bash
python scripts/surf_report.py --lat 50.735 --lon -1.705 --horizon 72h --output json | python scripts/normalize_surf_data.py
```

Use when:

- You need strict JSON field consistency before another agent consumes the payload.
