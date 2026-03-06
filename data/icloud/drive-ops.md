# iCloud Drive Operations - iCloud

Use `pyicloud` Python APIs for iCloud Drive operations with read-first behavior.

## Read-Only Preflight Example

```bash
python3 - <<'PY'
from pyicloud import PyiCloudService
api = PyiCloudService("user@icloud.com")
print(api.drive.dir())
PY
```

If keyring/session is unavailable, recover auth first from `auth-session.md`.

## Safe Download Pattern

1. Resolve exact folder and filename from read listing.
2. Download one file.
3. Verify local size/hash before continuing batch.

## Safe Upload Pattern

1. Confirm destination folder and overwrite expectations.
2. Upload one file first.
3. Re-list folder and verify file metadata.

## Write Guardrails

- Never delete or rename without explicit confirmation.
- Never run broad path modifications without pre-action snapshot listing.
