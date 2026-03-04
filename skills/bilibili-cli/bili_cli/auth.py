"""Authentication for Bilibili.

Strategy:
1. Try loading saved credential from ~/.bilibili-cli/credential.json
2. Try extracting cookies from local browsers via browser-cookie3
3. Fallback: QR code login via bilibili-api-python + terminal display
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path

from bilibili_api.utils.network import Credential
from bilibili_api.login_v2 import QrCodeLogin, QrCodeLoginEvents

logger = logging.getLogger(__name__)

CONFIG_DIR = Path.home() / ".bilibili-cli"
CREDENTIAL_FILE = CONFIG_DIR / "credential.json"

# Required cookies for a valid Bilibili session
REQUIRED_COOKIES = {"SESSDATA"}


def get_credential() -> Credential | None:
    """Try all auth methods in order. Returns validated Credential or None."""
    # 1. Saved credential file
    cred = _load_saved_credential()
    if cred:
        if _validate_credential(cred):
            logger.info("Loaded valid credential from %s", CREDENTIAL_FILE)
            return cred
        else:
            logger.warning("Saved credential is expired, clearing")
            clear_credential()

    # 2. Browser cookie extraction
    cred = _extract_browser_credential()
    if cred:
        if _validate_credential(cred):
            logger.info("Extracted valid credential from local browser")
            save_credential(cred)
            return cred
        else:
            logger.warning("Browser cookies are expired/invalid")

    return None


def _validate_credential(cred: Credential) -> bool:
    """Check if a credential is still valid by calling the API."""
    import asyncio
    from bilibili_api import user

    async def _check():
        try:
            await user.get_self_info(cred)
            return True
        except Exception:
            return False

    try:
        return asyncio.run(_check())
    except Exception:
        return False


def _load_saved_credential() -> Credential | None:
    """Load credential from saved file."""
    if not CREDENTIAL_FILE.exists():
        return None

    try:
        data = json.loads(CREDENTIAL_FILE.read_text())
        sessdata = data.get("sessdata", "")
        if not sessdata:
            return None
        return Credential(
            sessdata=sessdata,
            bili_jct=data.get("bili_jct", ""),
            ac_time_value=data.get("ac_time_value", ""),
        )
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("Failed to load saved credential: %s", e)
        return None


def _extract_browser_credential() -> Credential | None:
    """Extract Bilibili cookies from local browsers using browser-cookie3.

    Runs extraction in a subprocess with timeout to avoid hanging
    when the browser is running (Chrome DB lock issue).
    """
    extract_script = '''
import json, sys
try:
    import browser_cookie3 as bc3
except ImportError:
    print(json.dumps({"error": "not_installed"}))
    sys.exit(0)

browsers = [
    ("Chrome", bc3.chrome),
    ("Firefox", bc3.firefox),
    ("Edge", bc3.edge),
    ("Brave", bc3.brave),
]

for name, loader in browsers:
    try:
        cj = loader(domain_name=".bilibili.com")
        cookies = {c.name: c.value for c in cj if "bilibili.com" in (c.domain or "")}
        if "SESSDATA" in cookies:
            print(json.dumps({"browser": name, "cookies": cookies}))
            sys.exit(0)
    except Exception:
        pass

print(json.dumps({"error": "no_cookies"}))
'''

    try:
        result = subprocess.run(
            [sys.executable, "-c", extract_script],
            capture_output=True, text=True, timeout=15,
        )

        if result.returncode != 0:
            logger.debug("Cookie extraction subprocess failed: %s", result.stderr)
            return None

        data = json.loads(result.stdout.strip())

        if "error" in data:
            if data["error"] == "not_installed":
                logger.debug("browser-cookie3 not installed, skipping")
            else:
                logger.debug("No valid Bilibili cookies found in any browser")
            return None

        cookies = data["cookies"]
        browser_name = data["browser"]
        logger.info(
            "Found valid cookies in %s (%d cookies)", browser_name, len(cookies)
        )

        return Credential(
            sessdata=cookies.get("SESSDATA", ""),
            bili_jct=cookies.get("bili_jct", ""),
            ac_time_value=cookies.get("ac_time_value", ""),
        )

    except subprocess.TimeoutExpired:
        logger.warning(
            "Cookie extraction timed out (browser may be running). "
            "Try closing your browser or use `bili login`."
        )
        return None
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("Cookie extraction parse error: %s", e)
        return None


def save_credential(credential: Credential):
    """Save credential to config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    data = {
        "sessdata": credential.sessdata,
        "bili_jct": credential.bili_jct,
        "ac_time_value": credential.ac_time_value or "",
    }
    CREDENTIAL_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    CREDENTIAL_FILE.chmod(0o600)  # Owner-only read/write
    logger.info("Credential saved to %s", CREDENTIAL_FILE)


def clear_credential():
    """Remove saved credential file."""
    if CREDENTIAL_FILE.exists():
        CREDENTIAL_FILE.unlink()
        logger.info("Credential removed: %s", CREDENTIAL_FILE)


async def qr_login() -> Credential:
    """QR code login via terminal.

    Displays a QR code in the terminal, polls until login completes,
    then saves and returns the credential.
    """
    login = QrCodeLogin()
    await login.generate_qrcode()

    # Display QR code in terminal
    print("\n📱 请使用 Bilibili App 扫描以下二维码登录:\n")
    print(login.get_qrcode_terminal())
    print("\n⭐ 扫码后请在手机上确认登录...")

    # Poll login state
    while True:
        state = await login.check_state()

        if state == QrCodeLoginEvents.DONE:
            credential = login.get_credential()
            save_credential(credential)
            print("\n✅ 登录成功！凭证已保存")
            return credential

        elif state == QrCodeLoginEvents.TIMEOUT:
            raise RuntimeError("二维码已过期，请重试")

        elif state == QrCodeLoginEvents.CONF:
            print("  📲 已扫码，请在手机上确认...")

        await asyncio.sleep(2)
