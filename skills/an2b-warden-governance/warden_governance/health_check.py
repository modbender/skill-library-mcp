"""War/Den Health Check -- validates enterprise service connectivity at startup."""

from __future__ import annotations

import logging

from warden_governance.settings import Settings

logger = logging.getLogger("warden")


class HealthCheck:
    """Validates connectivity to enterprise services.

    Only runs checks for services with API keys configured.
    Never crashes on failures -- reports status and continues.
    """

    def run(self, config: Settings) -> dict:
        """Run health checks for configured services."""
        results: dict = {}

        if config.sentinel_api_key:
            results["sentinel"] = self._check_sentinel(config)

        if config.engramport_api_key:
            results["engramport"] = self._check_engramport(config)

        return results

    def _check_sentinel(self, config: Settings) -> dict:
        """Check Sentinel_OS connectivity."""
        try:
            import httpx

            with httpx.Client(timeout=10) as client:
                resp = client.get(
                    f"{config.sentinel_base_url}/api/healthz",
                    headers={
                        "Authorization": f"Bearer {config.sentinel_api_key}",
                    },
                )

            if resp.status_code == 200:
                return {"ok": True, "error": None}
            elif resp.status_code == 401:
                msg = "Invalid SENTINEL_API_KEY"
                print(
                    f"  Sentinel_OS: {msg}\n"
                    f"  Check your SENTINEL_API_KEY at getsentinelos.com"
                )
                return {"ok": False, "error": msg}
            else:
                msg = f"HTTP {resp.status_code}"
                return {"ok": False, "error": msg}

        except ImportError:
            msg = "httpx not installed"
            return {"ok": False, "error": msg}
        except Exception as exc:
            msg = str(exc)
            print(
                f"  Sentinel_OS unreachable: {msg}\n"
                f"  Check your SENTINEL_API_KEY and network connection"
            )
            return {"ok": False, "error": msg}

    def _check_engramport(self, config: Settings) -> dict:
        """Check EngramPort connectivity."""
        try:
            import httpx

            with httpx.Client(timeout=10) as client:
                resp = client.get(
                    f"{config.engramport_base_url}/stats",
                    headers={"X-API-Key": config.engramport_api_key},
                )

            if resp.status_code == 200:
                return {"ok": True, "error": None}
            elif resp.status_code == 401:
                msg = "Invalid ENGRAMPORT_API_KEY"
                return {"ok": False, "error": msg}
            else:
                msg = f"HTTP {resp.status_code}"
                return {"ok": False, "error": msg}

        except ImportError:
            msg = "httpx not installed"
            return {"ok": False, "error": msg}
        except Exception as exc:
            msg = str(exc)
            return {"ok": False, "error": msg}
