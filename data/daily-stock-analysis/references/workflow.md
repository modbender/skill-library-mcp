# Workflow (Command-First)

Use this sequence exactly.

## 0) Choose Execution Mode

Use `script` mode by default.

Switch to `compatibility` mode when:

- `python3` is unavailable, or
- model capability is low and deterministic minimal output is preferred.

## 1) Resolve Instrument

- Resolve `ticker`, `exchange`, `market`, and next valid trading day.
- If ticker is ambiguous, stop and ask user.

## 2) Plan Files and History

Run:

```bash
python3 {baseDir}/scripts/report_manager.py plan \
  --workdir <working_directory> \
  --ticker <TICKER> \
  --run-date <YYYY-MM-DD> \
  --versioning auto \
  --history-limit 5
```

Use returned JSON fields:

- `selected_output_file`
- `requires_user_choice`
- `history_files`
- `legacy_files`

If `requires_user_choice=true`, ask user `overwrite` vs `new_version`.
Read only `history_files` returned by script (default max 5).

## 3) Legacy Compatibility (Optional Migration)

- Read legacy files from `legacy_files` for review history.
- If user agrees to migrate, run:

```bash
python3 {baseDir}/scripts/report_manager.py migrate \
  --workdir <working_directory> \
  --file <ABS_PATH_1> --file <ABS_PATH_2>
```

Security: only process files under `working_directory`.

## 4) Collect New Data

- Use `references/sources.md` tier priority.
- Use `references/search_queries.md` templates.
- For critical values, cross-check with at least 2 sources.

## 5) Compute Accuracy via Script

Run:

```bash
python3 {baseDir}/scripts/calc_accuracy.py \
  --workdir <working_directory> \
  --ticker <TICKER> \
  --windows 1,3,7,30 \
  --history-limit 60
```

Use script output to fill rolling accuracy fields.

## 6) Generate Report

- Render with `references/report_template.md`.
- Keep all required frontmatter keys.
- Include `improvement_actions`.

## 7) Persist and Return

- Save to `selected_output_file` from step 2.
- Return summary + absolute file path + pending/blocked status.

## 8) Recommended Operation

Use recurring weekday schedule to stabilize review windows and success rate.

## Compatibility Mode (Fallback)

When scripts cannot run:

1. Manually locate report files only under `working_directory`.
2. Read at most 3 recent same-ticker reports.
3. Collect minimal sources:
- one official disclosure source
- one reliable market data source
4. Produce minimal output:
- recommendation
- `pred_close_t1`
- prior review metrics (if available)
- one `improvement_action`
5. Save report in canonical reports directory using standard filename rules.
