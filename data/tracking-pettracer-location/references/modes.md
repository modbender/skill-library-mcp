# Tracking modes and “stale fix” expectations

How “fresh” a PetTracer GPS fix should be depends heavily on the collar’s **mode**.
PetTracer may add hidden modes, and naming can vary across collar generations.

This file is **best-effort guidance** based on public community clients and observed portal behaviour.
Treat values as heuristics, not guarantees.

## Common user-facing modes

| Mode name | Mode id | Notes |
|---|---:|---|
| Slow | 3 | Low power / less frequent fixes. |
| Slow+ | 7 | Variant; behaviour can differ by collar generation. |
| Normal | 2 | Default-ish mode. |
| Normal+ | 14 | Variant; often “more frequent” than Normal. |
| Fast | 1 | More frequent contact than Normal. |
| Fast+ | 8 | Variant; often “more frequent” than Fast. |
| Live | 11 | Often behaves like a search/live tracking mode. |

## “Expected” age of last_fix

When deciding whether a fix is “stale”, prefer:
1. `last_fix_age_s` (seconds since last fix)
2. Current `mode_id/mode_name` (if present)
3. User context (“is the cat likely moving outdoors right now?”)

A reasonable heuristic:
- **Live (11)**: a fix older than a couple of minutes is likely stale.
- **Fast/Fast+**: tens of minutes may still be expected.
- **Normal/Normal+**: an hour or two may be expected.
- **Slow/Slow+**: hours to a day may be expected.

If you need more precision, check the official portal/app for the user’s collar model and settings.

## Extra/hidden modes

Some accounts/devices may show additional internal mode ids. If you see an unknown `mode_id`, report it as numeric and avoid guessing.
