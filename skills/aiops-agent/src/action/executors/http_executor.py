"""
HTTP executor for webhook-based remediation actions.
"""

from typing import Any

import httpx
import structlog

logger = structlog.get_logger()


class HTTPExecutor:
    """
    Executor for HTTP webhook-based actions.

    Features:
    - Generic webhook calls
    - Retry logic
    - Timeout handling
    """

    def __init__(
        self,
        timeout_seconds: int = 30,
        retry_attempts: int = 3,
    ):
        self.timeout_seconds = timeout_seconds
        self.retry_attempts = retry_attempts

    async def call_webhook(
        self,
        target: str,
        namespace: str,  # Not used for HTTP
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Call a webhook URL.

        Target is the webhook URL.
        Parameters can include:
        - method: HTTP method (default: POST)
        - headers: Custom headers
        - body: Request body
        """
        url = target
        method = parameters.get("method", "POST").upper()
        headers = parameters.get("headers", {})
        body = parameters.get("body", {})

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            for attempt in range(self.retry_attempts):
                try:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=body if method in ("POST", "PUT", "PATCH") else None,
                    )

                    success = response.status_code < 400

                    if success:
                        logger.info(
                            "Webhook call successful",
                            url=url,
                            status=response.status_code,
                        )
                        return {
                            "success": True,
                            "status_code": response.status_code,
                            "response": response.text[:500],
                        }
                    else:
                        logger.warning(
                            "Webhook call failed",
                            url=url,
                            status=response.status_code,
                            attempt=attempt + 1,
                        )
                        if attempt == self.retry_attempts - 1:
                            return {
                                "success": False,
                                "error": f"HTTP {response.status_code}: {response.text[:200]}",
                            }

                except httpx.RequestError as e:
                    logger.warning(
                        "Webhook request error",
                        url=url,
                        error=str(e),
                        attempt=attempt + 1,
                    )
                    if attempt == self.retry_attempts - 1:
                        return {"success": False, "error": str(e)}

        return {"success": False, "error": "Max retries exceeded"}
