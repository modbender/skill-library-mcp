# Setup - iCloud

Read this on first activation when `~/icloud/` is missing or incomplete.

## Operating Attitude

- Answer the user request first, then harden execution.
- Prefer safe defaults over fast risky actions.
- Keep each step verifiable and reversible.

## First Activation

1. Confirm objective: Find My, Drive, Photos, or mixed operations.
2. Confirm whether local operational notes are allowed.
3. If notes are approved, create minimal structure:

```bash
mkdir -p ~/icloud
touch ~/icloud/{memory.md,operations-log.md,device-map.md,drive-map.md,safety-events.md}
chmod 700 ~/icloud
chmod 600 ~/icloud/{memory.md,operations-log.md,device-map.md,drive-map.md,safety-events.md}
```

4. If `memory.md` is empty, initialize from `memory-template.md`.
5. If `pyicloud` is missing, install dependency and verify import:

```bash
python3 -m pip install --user pyicloud==2.4.1
python3 - <<'PY'
from pyicloud import PyiCloudService
print("pyicloud import OK")
PY
```

6. Authenticate with local prompt flow (never via chat):

```bash
python3 - <<'PY'
import getpass
from pyicloud import PyiCloudService
user = input("Apple ID: ").strip()
pwd = getpass.getpass("Apple password: ")
api = PyiCloudService(user, pwd)
print("Authenticated:", bool(api.data))
PY
```

## Integration Priority

Capture and persist only these confirmed preferences:
- Allowed operation domains (Find My, Drive, Photos)
- Confirmation strictness for risky actions (strict or standard)
- Session-only mode vs persistent local notes

## Runtime Defaults

- Default to read-only discovery.
- Require explicit confirmation before risky actions.
- Verify post-state after every write operation.

## Session-Only Mode

If the user declines persistence:
- Do not create or update files under `~/icloud/`.
- Keep all context in current session output only.
