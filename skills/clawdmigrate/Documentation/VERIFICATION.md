# Post-Migration Verification

**Added in v0.2.0**

After migration completes, clawd-migrate now automatically verifies that every discovered source file was successfully copied to its openclaw destination.

---

## What it checks

1. **Memory files** – Each source memory file (SOUL.md, USER.md, etc.) exists in `memory/`
2. **Config files** – Each config file exists in `.config/openclaw/`
3. **Clawdbook files** – Credential files exist in `.config/clawdbook/`
4. **Extra files** – Project files preserved in their original layout
5. **File size match** – Destination file size matches source (catches truncated copies)
6. **Cross-check** – If migration reported copying a file, that file actually exists on disk

---

## Verification in TUI (interactive mode)

When you run `clawd-migrate` and choose option 3 (full migration), verification runs automatically after all files are copied:

```
  Verification PASSED: 5/5 files confirmed
  Verified files:
    [memory] SOUL.md (size OK)
    [memory] USER.md (size OK)
    [memory] TOOLS.md (size OK)
    [clawdbook] credentials.json (size OK)
    [extra] readme.txt (size OK)
```

If any files are missing:

```
  Verification FAILED: 4/5 files confirmed
  MISSING files:
    [memory] SOUL.md -> expected at /path/to/memory/SOUL.md
```

---

## Verification in CLI mode

Verification is on by default. Use `--skip-verify` to disable (not recommended):

```bash
clawd-migrate migrate                      # verification enabled (default)
clawd-migrate migrate --skip-verify        # skip verification
```

---

## Openclaw reinstall

After verification, openclaw is automatically reinstalled (`npm i -g openclaw`) and `openclaw onboard` runs in the migration output directory. This ensures your openclaw installation is fresh and the migrated workspace is properly set up.

In v0.1.x, this was an optional prompt. In v0.2.0, it runs automatically as part of the migration flow.

---

## Programmatic usage

```python
from clawd_migrate import verify_migration

# Verify after migration
result = verify_migration(root="/path/to/source", output_root="/path/to/output")

print(result["passed"])          # True/False
print(result["total_expected"])  # number of source files
print(result["total_verified"])  # number confirmed at destination
print(result["missing"])         # list of missing file details
print(result["verified"])        # list of verified file details
```

---

## Tests

Three new test cases cover verification:

- `TestVerify.test_verify_passes_after_migration` – confirms all files present after full migration
- `TestVerify.test_verify_detects_missing_files` – manually removes a file, confirms detection
- `TestVerify.test_verify_standalone` – runs verification before and after migration independently
