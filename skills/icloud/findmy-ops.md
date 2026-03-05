# Find My Operations - iCloud

Use Find My workflows with narrow target scope and explicit confirmation.

## Read-Only Discovery

```bash
python3 - <<'PY'
import getpass
from pyicloud import PyiCloudService
user = input("Apple ID: ").strip()
pwd = getpass.getpass("Apple password: ")
api = PyiCloudService(user, pwd, with_family=True)
for dev in api.devices:
    print(dev.content.get("id"), dev.content.get("name"))
PY
```

Extract and persist only stable identifiers (device ID, display name mapping).

## Controlled Actions

Risky actions include:
- `play_sound()`
- `display_message(...)`
- `lost_device(...)`

Before any risky action, confirm:
1. exact device ID,
2. action effect,
3. rollback expectation.

## Post-Action Verification

After any action:
1. rerun read-only device listing,
2. validate target device state,
3. log result in operations log if persistence is enabled.

## Failure Pattern

- Name-only targeting causes wrong device actions -> always use device ID.
