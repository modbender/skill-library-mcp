# Trinity Compress

**Price:** $9

**License:** MIT

Trinity Compress is a local, pre-run prompt compression tool for iterative AI development loops.

## What it does
- Compresses prompt/instruction files *before* you run your loop to reduce input tokens.
- Makes `.bak` backups for instant rollback.
- No model calls (runs locally).

## Install
### Windows (PowerShell)
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File skills/trinity-compress/scripts/install.ps1 -RepoPath .
```

### bash
```bash
bash skills/trinity-compress/scripts/install.sh .
```

## Run
```bash
bash scripts/trinity-compress.sh balanced
```

## Undo
```bash
bash scripts/trinity-compress.sh undo
```

## Requirements
- bash 4+
- `jq`
- `bc`

## Notes
- Review diffs before committing.
- Aggressive mode can reduce clarity.

## ClawHub packaging (maintainers)
Run a quick local preflight scan before uploading, then build a clean ZIP:

```powershell
# From repo root
powershell -NoProfile -File skills/trinity-compress/scripts/scan-banned-terms.ps1 -FailOnFind
powershell -NoProfile -File skills/trinity-compress/scripts/zip-skill.ps1 -ScanFirst
```

The ZIP will be written to `dist/` and will exclude common noisy/unsafe artifacts (`node_modules`, `*.bak*`, `.env`, etc.).

### Preflight knobs
Useful flags for tuning the scan:
- `-MaxFileSizeKb 512` (default) — skip big files (avoid slow/binary-ish scans)
- `-ExcludeDirs @('.git','node_modules',...)` — skip directories
- `-ExcludeFiles @('*.zip','*.png',...)` — skip filename patterns
- `-OutputJson` — machine-readable output (CI)
- `-NoRedact` — show raw matching lines (only use locally; can leak secrets into logs)

### Automation / CI
If you need a pipeline-friendly output (e.g., to attach the ZIP artifact), use `-OutputJson`:

```powershell
$p = powershell -NoProfile -File skills/trinity-compress/scripts/zip-skill.ps1 -ScanFirst -OutputJson
$info = $p | ConvertFrom-Json
$info.zipPath
$info.sha256
```
