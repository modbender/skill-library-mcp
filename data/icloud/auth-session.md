# Authentication and Session - iCloud

Use this flow to minimize auth errors and avoid unsafe credential handling.

## Safe Authentication Sequence

1. Verify dependency import:

```bash
python3 - <<'PY'
from pyicloud import PyiCloudService
print("pyicloud import OK")
PY
```

2. Start login with local prompt:

```bash
python3 - <<'PY'
import getpass
from pyicloud import PyiCloudService
user = input("Apple ID: ").strip()
pwd = getpass.getpass("Apple password: ")
api = PyiCloudService(user, pwd)
print("Session loaded:", bool(api.data))
PY
```

3. If 2FA is required, complete code validation in local prompt flow:

```bash
python3 - <<'PY'
import getpass
from pyicloud import PyiCloudService
user = input("Apple ID: ").strip()
pwd = getpass.getpass("Apple password: ")
api = PyiCloudService(user, pwd)
if api.requires_2fa:
    code = input("2FA code: ").strip()
    ok = api.validate_2fa_code(code)
    print("2FA OK:", ok)
PY
```

4. If prompted, storing password in keyring is allowed; never store in plain text files.
5. Re-run a read command to confirm trusted session is active.

## Session Failure Recovery

| Symptom | Cause | Safe Recovery |
|---------|-------|---------------|
| Login was working, now auth/API failures | Session expired | Re-auth with same local flow |
| 2FA loop repeats | Session not trusted | Complete trust step and retry read-only command |
| Local prompt asks for password unexpectedly | Missing keyring entry | Re-auth interactively, then continue |

## Hard Boundaries

- Never request user password or 2FA code in chat.
- Never persist credential material in `~/icloud/` files.
- Stop write operations immediately when session health is uncertain.
