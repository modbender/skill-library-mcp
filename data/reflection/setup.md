# Setup — Self Reflection

## First Activation

On first use:

1. **Register in workspace memory** — Add to MEMORY.md:
   ```
   ## Self Reflection
   - Installed: YYYY-MM-DD
   - Memory: ~/reflection/
   - Status: active
   ```

2. **Create folder** — `mkdir -p ~/reflection/archive`

3. **Initialize memory** — Copy structure from `memory-template.md` to `~/reflection/memory.md`

4. **Create reflections.md** — Empty file, will populate as lessons are logged

5. **Create patterns.md** — Empty file, will populate when patterns emerge

## Integration Points

### Heartbeat (Optional)
Add to HEARTBEAT.md:
```markdown
## Self Reflection Check
Every heartbeat, quick scan:
1. Pending reflection to log?
2. Pattern threshold reached (5 reflections)?
3. Weekly review due?
If any → handle. Otherwise → continue.
```

### Pre-Delivery Trigger
Before important deliverables, run 7-dimension scan (30 seconds):
- All clear → deliver
- Issue found → fix first, then deliver

## Configuration

No external config required. All state lives in `~/reflection/`.

Optional: Set review cadence in `~/reflection/memory.md`:
```markdown
## Preferences
- review_day: Sunday
- archive_threshold: 20 reflections
```

## Status Fields

Track in `~/reflection/memory.md`:
- `streak_days` — days without repeated mistake
- `total_reflections` — count by category
- `patterns_active` — count of active patterns
- `patterns_resolved` — count of resolved patterns
- `last_review` — date of last weekly review
