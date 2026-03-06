"""
Base class for all data collectors.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, TypeVar

import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = structlog.get_logger()

T = TypeVar("T")


class CollectorError(Exception):
    """Base exception for collector errors."""

    pass


class ConnectionError(CollectorError):
    """Error connecting to data source."""

    pass


class QueryError(CollectorError):
    """Error executing query."""

    pass


class BaseCollector(ABC):
    """
    Base class for all data collectors.

    Provides common functionality for:
    - Connection management
    - Retry logic
    - Error handling
    - Logging
    """

    def __init__(
        self,
        url: str,
        timeout_seconds: int = 30,
        retry_attempts: int = 3,
        retry_delay_seconds: int = 1,
    ):
        self.url = url
        self.timeout_seconds = timeout_seconds
        self.retry_attempts = retry_attempts
        self.retry_delay_seconds = retry_delay_seconds
        self._client: Any = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if collector is connected."""
        return self._connected

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to data source."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to data source."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if data source is healthy."""
        pass

    @abstractmethod
    async def collect(
        self, start_time: datetime, end_time: datetime
    ) -> list[Any]:
        """
        Collect data within the specified time range.

        Args:
            start_time: Start of collection window
            end_time: End of collection window

        Returns:
            List of collected data items
        """
        pass

    def _create_retry_decorator(self):
        """Create a retry decorator with current settings."""
        return retry(
            stop=stop_after_attempt(self.retry_attempts),
            wait=wait_exponential(
                multiplier=self.retry_delay_seconds, min=1, max=10
            ),
            retry=retry_if_exception_type((ConnectionError, QueryError)),
            before_sleep=lambda retry_state: logger.warning(
                "Retrying collector operation",
                attempt=retry_state.attempt_number,
                collector=self.__class__.__name__,
            ),
        )

    async def safe_collect(
        self, start_time: datetime, end_time: datetime
    ) -> tuple[list[Any], list[str]]:
        """
        Collect data with error handling.

        Returns:
            Tuple of (collected_data, errors)
        """
        errors: list[str] = []
        try:
            if not self._connected:
                await self.connect()
            data = await self.collect(start_time, end_time)
            return data, errors
        except Exception as e:
            error_msg = f"{self.__class__.__name__}: {str(e)}"
            errors.append(error_msg)
            logger.error(
                "Collection failed",
                collector=self.__class__.__name__,
                error=str(e),
            )
            return [], errors

    async def __aenter__(self) -> "BaseCollector":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()
