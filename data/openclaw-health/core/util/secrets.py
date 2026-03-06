import json
import os
import subprocess
from typing import Optional


def set_secret(item_title: str, field_name: str, value: str) -> bool:
    """Best-effort secret writeback to 1Password.

    This is intentionally opt-in and designed for rotated refresh tokens.

    Enabled only when:
    - `OPENCLAW_1P_WRITEBACK=1`
    - `op` CLI is available

    Returns True on success, False otherwise.
    """

    if os.getenv("OPENCLAW_1P_WRITEBACK") != "1":
        return False

    if not _op_available():
        return False

    vault = os.getenv("OPENCLAW_1P_VAULT")

    # 1Password CLI supports editing fields by label.
    # We avoid printing secrets; callers should also avoid logging values.
    try:
        cmd = ["op", "item", "edit", item_title, f"{field_name}={value}"]
        if vault:
            cmd.extend(["--vault", vault])
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, text=True)
        return res.returncode == 0
    except Exception:
        return False


def _op_available() -> bool:
    try:
        subprocess.run(["op", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        return True
    except Exception:
        return False


def get_secret(item_title: str, field_name: str) -> Optional[str]:
    """Best-effort secret fetch from 1Password via op. Returns None if unavailable.

    Notes:
    - Requires OP_SERVICE_ACCOUNT_TOKEN (or an op session) to be present in the environment.
    - Optionally set OPENCLAW_1P_VAULT to force a specific vault name.

    Implementation:
    - `op item get "<title>" --vault <vault> --format json`
    - Then search item.fields[] for a matching label.
    """

    if not _op_available():
        return None

    vault = os.getenv("OPENCLAW_1P_VAULT")

    try:
        cmd = ["op", "item", "get", item_title, "--format", "json"]
        if vault:
            cmd.extend(["--vault", vault])

        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            text=True,
        )
        if res.returncode != 0:
            return None

        item = json.loads(res.stdout)
        fields = item.get("fields", []) if isinstance(item, dict) else []

        want = field_name.strip().lower()
        for f in fields if isinstance(fields, list) else []:
            label = (f.get("label") or f.get("name") or "").strip().lower()
            if label == want:
                return f.get("value")

        return None
    except Exception:
        return None

