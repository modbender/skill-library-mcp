"""
Logs collector for Loki.

Collects structured logs using LogQL queries.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
import structlog

from src.config.constants import LogLevel
from src.config.settings import get_settings
from src.models.metrics import LogEntry
from src.perception.base_collector import (
    BaseCollector,
    CollectorError,
    ConnectionError,
    QueryError,
)

logger = structlog.get_logger()


class LogsCollector(BaseCollector):
    """
    Collector for Loki logs.

    Features:
    - Supports LogQL queries
    - Extracts structured data from JSON logs
    - Filters by service, level, and time range
    """

    # Default log queries for trading system
    DEFAULT_QUERIES = {
        "error_logs": '{level=~"error|critical"} |~ ""',
        "trading_engine": '{service="trading-engine"}',
        "matching_engine": '{service="matching-engine"}',
        "risk_service": '{service="risk-service"}',
        "wallet_service": '{service="wallet-service"}',
        "api_gateway": '{service="api-gateway"}',
    }

    def __init__(
        self,
        url: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        retry_attempts: Optional[int] = None,
    ):
        settings = get_settings()
        super().__init__(
            url=url or settings.loki.url,
            timeout_seconds=timeout_seconds or settings.loki.timeout_seconds,
            retry_attempts=retry_attempts or settings.loki.retry_attempts,
        )

    async def connect(self) -> None:
        """Connect to Loki."""
        try:
            self._client = httpx.AsyncClient(
                base_url=self.url,
                timeout=self.timeout_seconds,
            )
            if await self.health_check():
                self._connected = True
                logger.info("Connected to Loki", url=self.url)
            else:
                raise ConnectionError("Health check failed")
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to connect to Loki: {e}")

    async def disconnect(self) -> None:
        """Disconnect from Loki."""
        if self._client:
            await self._client.aclose()
            self._client = None
            self._connected = False
            logger.info("Disconnected from Loki")

    async def health_check(self) -> bool:
        """Check Loki health."""
        try:
            response = await self._client.get("/ready")
            return response.status_code == 200
        except Exception:
            return False

    async def collect(
        self, start_time: datetime, end_time: datetime
    ) -> List[LogEntry]:
        """
        Collect logs using default queries.

        Args:
            start_time: Start of collection window
            end_time: End of collection window

        Returns:
            List of LogEntry objects
        """
        all_logs: List[LogEntry] = []

        for query_name, query in self.DEFAULT_QUERIES.items():
            try:
                logs = await self.query_range(query, start_time, end_time)
                all_logs.extend(logs)
                logger.debug(
                    "Collected logs",
                    query=query_name,
                    count=len(logs),
                )
            except Exception as e:
                logger.warning(
                    "Failed to collect logs",
                    query=query_name,
                    error=str(e),
                )

        # Deduplicate and sort by timestamp
        seen = set()
        unique_logs = []
        for log in sorted(all_logs, key=lambda x: x.timestamp, reverse=True):
            key = (log.timestamp, log.message[:100])
            if key not in seen:
                seen.add(key)
                unique_logs.append(log)

        return unique_logs

    async def query_range(
        self,
        query: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> List[LogEntry]:
        """
        Execute a LogQL range query.

        Args:
            query: LogQL query
            start_time: Query start time
            end_time: Query end time
            limit: Maximum number of entries to return

        Returns:
            List of LogEntry objects
        """
        if not self._client:
            raise CollectorError("Not connected to Loki")

        try:
            response = await self._client.get(
                "/loki/api/v1/query_range",
                params={
                    "query": query,
                    "start": int(start_time.timestamp() * 1e9),
                    "end": int(end_time.timestamp() * 1e9),
                    "limit": limit,
                },
            )
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "success":
                raise QueryError(f"Query failed: {data.get('error', 'Unknown error')}")

            return self._parse_response(data)

        except httpx.HTTPStatusError as e:
            raise QueryError(f"HTTP error: {e}")
        except httpx.RequestError as e:
            raise ConnectionError(f"Request error: {e}")

    async def query_by_service(
        self,
        service: str,
        start_time: datetime,
        end_time: datetime,
        level: Optional[str] = None,
        limit: int = 500,
    ) -> List[LogEntry]:
        """
        Query logs for a specific service.

        Args:
            service: Service name
            start_time: Query start time
            end_time: Query end time
            level: Optional log level filter
            limit: Maximum entries

        Returns:
            List of LogEntry objects
        """
        query = f'{{service="{service}"}}'
        if level:
            query += f' |= "{level}"'

        return await self.query_range(query, start_time, end_time, limit)

    async def query_errors(
        self,
        start_time: datetime,
        end_time: datetime,
        service: Optional[str] = None,
        limit: int = 500,
    ) -> List[LogEntry]:
        """
        Query error logs.

        Args:
            start_time: Query start time
            end_time: Query end time
            service: Optional service filter
            limit: Maximum entries

        Returns:
            List of LogEntry objects
        """
        if service:
            query = f'{{service="{service}", level=~"error|critical"}}'
        else:
            query = '{level=~"error|critical"}'

        return await self.query_range(query, start_time, end_time, limit)

    async def search_logs(
        self,
        pattern: str,
        start_time: datetime,
        end_time: datetime,
        service: Optional[str] = None,
        limit: int = 500,
    ) -> List[LogEntry]:
        """
        Search logs by pattern.

        Args:
            pattern: Search pattern (regex supported)
            start_time: Query start time
            end_time: Query end time
            service: Optional service filter
            limit: Maximum entries

        Returns:
            List of LogEntry objects
        """
        if service:
            query = f'{{service="{service}"}} |~ "{pattern}"'
        else:
            query = f'{{}} |~ "{pattern}"'

        return await self.query_range(query, start_time, end_time, limit)

    def _parse_response(self, data: Dict[str, Any]) -> List[LogEntry]:
        """Parse Loki query response into LogEntry objects."""
        entries: List[LogEntry] = []
        results = data.get("data", {}).get("result", [])

        for stream in results:
            labels = stream.get("stream", {})
            service = labels.get("service", labels.get("app", "unknown"))

            for ts_ns, line in stream.get("values", []):
                try:
                    timestamp = datetime.fromtimestamp(int(ts_ns) / 1e9)
                    entry = self._parse_log_line(line, timestamp, service, labels)
                    if entry:
                        entries.append(entry)
                except Exception as e:
                    logger.debug(
                        "Failed to parse log line",
                        error=str(e),
                        line=line[:100],
                    )

        return entries

    def _parse_log_line(
        self,
        line: str,
        timestamp: datetime,
        service: str,
        labels: Dict[str, str],
    ) -> Optional[LogEntry]:
        """Parse a single log line into LogEntry."""
        # Try to parse as JSON
        structured_data: Dict[str, Any] = {}
        message = line
        level = LogLevel.INFO

        try:
            parsed = json.loads(line)
            if isinstance(parsed, dict):
                structured_data = parsed
                message = parsed.get("message", parsed.get("msg", line))
                level_str = parsed.get("level", parsed.get("severity", "info")).lower()
                level = self._parse_level(level_str)
        except json.JSONDecodeError:
            # Not JSON, try to extract level from plain text
            level = self._extract_level_from_text(line)

        return LogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            service=service,
            labels=labels,
            structured_data=structured_data,
            trace_id=structured_data.get("trace_id"),
            span_id=structured_data.get("span_id"),
            request_id=structured_data.get("request_id"),
            user_id=structured_data.get("user_id"),
            error_code=structured_data.get("error_code"),
            error_message=structured_data.get("error", structured_data.get("error_message")),
        )

    @staticmethod
    def _parse_level(level_str: str) -> LogLevel:
        """Parse level string to LogLevel enum."""
        level_map = {
            "debug": LogLevel.DEBUG,
            "info": LogLevel.INFO,
            "warn": LogLevel.WARNING,
            "warning": LogLevel.WARNING,
            "error": LogLevel.ERROR,
            "err": LogLevel.ERROR,
            "critical": LogLevel.CRITICAL,
            "fatal": LogLevel.CRITICAL,
        }
        return level_map.get(level_str.lower(), LogLevel.INFO)

    @staticmethod
    def _extract_level_from_text(text: str) -> LogLevel:
        """Extract log level from plain text log line."""
        text_lower = text.lower()
        if "critical" in text_lower or "fatal" in text_lower:
            return LogLevel.CRITICAL
        elif "error" in text_lower or "err]" in text_lower:
            return LogLevel.ERROR
        elif "warn" in text_lower:
            return LogLevel.WARNING
        elif "debug" in text_lower:
            return LogLevel.DEBUG
        return LogLevel.INFO
