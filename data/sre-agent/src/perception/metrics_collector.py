"""
Metrics collector for Prometheus/Mimir.

Collects time series metrics using PromQL queries.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import structlog
import yaml

from src.config.constants import MetricCategory
from src.config.settings import get_settings
from src.models.metrics import MetricDataPoint, MetricQuery, MetricSeries
from src.perception.base_collector import (
    BaseCollector,
    CollectorError,
    ConnectionError,
    QueryError,
)

logger = structlog.get_logger()


class MetricsCollector(BaseCollector):
    """
    Collector for Prometheus/Mimir metrics.

    Features:
    - Loads PromQL queries from configuration
    - Supports range queries and instant queries
    - Handles metric label extraction
    - Provides retry logic for reliability
    """

    def __init__(
        self,
        url: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        retry_attempts: Optional[int] = None,
        queries_file: Optional[str] = None,
    ):
        settings = get_settings()
        super().__init__(
            url=url or settings.prometheus.url,
            timeout_seconds=timeout_seconds or settings.prometheus.timeout_seconds,
            retry_attempts=retry_attempts or settings.prometheus.retry_attempts,
        )
        self._queries: Dict[str, MetricQuery] = {}
        self._queries_file = queries_file or str(
            Path(__file__).parent.parent.parent / "config" / "promql_queries.yaml"
        )
        self._load_queries()

    def _load_queries(self) -> None:
        """Load PromQL queries from configuration file."""
        try:
            queries_path = Path(self._queries_file)
            if not queries_path.exists():
                logger.warning(
                    "PromQL queries file not found",
                    path=self._queries_file,
                )
                return

            with open(queries_path) as f:
                config = yaml.safe_load(f) or {}

            for category_name, queries in config.items():
                if not isinstance(queries, dict):
                    continue

                try:
                    category = MetricCategory(category_name)
                except ValueError:
                    logger.warning(
                        "Unknown metric category",
                        category=category_name,
                    )
                    continue

                for metric_name, query_def in queries.items():
                    if not isinstance(query_def, dict):
                        continue

                    self._queries[metric_name] = MetricQuery(
                        name=metric_name,
                        query=query_def.get("query", ""),
                        category=category,
                        unit=query_def.get("unit", ""),
                        description=query_def.get("description", ""),
                    )

            logger.info(
                "Loaded PromQL queries",
                count=len(self._queries),
            )

        except Exception as e:
            logger.error(
                "Failed to load PromQL queries",
                error=str(e),
            )

    async def connect(self) -> None:
        """Connect to Prometheus/Mimir."""
        try:
            self._client = httpx.AsyncClient(
                base_url=self.url,
                timeout=self.timeout_seconds,
            )
            # Test connection
            if await self.health_check():
                self._connected = True
                logger.info(
                    "Connected to Prometheus",
                    url=self.url,
                )
            else:
                raise ConnectionError("Health check failed")
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to connect to Prometheus: {e}")

    async def disconnect(self) -> None:
        """Disconnect from Prometheus."""
        if self._client:
            await self._client.aclose()
            self._client = None
            self._connected = False
            logger.info("Disconnected from Prometheus")

    async def health_check(self) -> bool:
        """Check Prometheus health."""
        try:
            response = await self._client.get("/-/healthy")
            return response.status_code == 200
        except Exception:
            return False

    async def collect(
        self, start_time: datetime, end_time: datetime
    ) -> List[MetricSeries]:
        """
        Collect all configured metrics.

        Args:
            start_time: Start of collection window
            end_time: End of collection window

        Returns:
            List of MetricSeries with collected data
        """
        results: List[MetricSeries] = []

        for metric_name, query_def in self._queries.items():
            try:
                series = await self.query_range(
                    query=query_def.query,
                    start_time=start_time,
                    end_time=end_time,
                    metric_name=metric_name,
                    category=query_def.category,
                    unit=query_def.unit,
                    description=query_def.description,
                )
                results.extend(series)
            except Exception as e:
                logger.warning(
                    "Failed to collect metric",
                    metric=metric_name,
                    error=str(e),
                )

        logger.debug(
            "Collected metrics",
            series_count=len(results),
            total_points=sum(len(s.data_points) for s in results),
        )
        return results

    async def query_range(
        self,
        query: str,
        start_time: datetime,
        end_time: datetime,
        metric_name: str,
        category: MetricCategory,
        unit: str = "",
        description: str = "",
        step: str = "1m",
    ) -> List[MetricSeries]:
        """
        Execute a range query.

        Args:
            query: PromQL query
            start_time: Query start time
            end_time: Query end time
            metric_name: Name for the metric
            category: Metric category
            unit: Unit of measurement
            description: Metric description
            step: Query resolution step

        Returns:
            List of MetricSeries (one per label combination)
        """
        if not self._client:
            raise CollectorError("Not connected to Prometheus")

        try:
            response = await self._client.get(
                "/api/v1/query_range",
                params={
                    "query": query,
                    "start": start_time.timestamp(),
                    "end": end_time.timestamp(),
                    "step": step,
                },
            )
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "success":
                raise QueryError(f"Query failed: {data.get('error', 'Unknown error')}")

            return self._parse_range_response(
                data, metric_name, category, unit, description
            )

        except httpx.HTTPStatusError as e:
            raise QueryError(f"HTTP error: {e}")
        except httpx.RequestError as e:
            raise ConnectionError(f"Request error: {e}")

    async def query_instant(
        self,
        query: str,
        time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute an instant query.

        Args:
            query: PromQL query
            time: Query time (defaults to now)

        Returns:
            List of instant query results
        """
        if not self._client:
            raise CollectorError("Not connected to Prometheus")

        params = {"query": query}
        if time:
            params["time"] = str(time.timestamp())

        try:
            response = await self._client.get(
                "/api/v1/query",
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "success":
                raise QueryError(f"Query failed: {data.get('error', 'Unknown error')}")

            return data.get("data", {}).get("result", [])

        except httpx.HTTPStatusError as e:
            raise QueryError(f"HTTP error: {e}")
        except httpx.RequestError as e:
            raise ConnectionError(f"Request error: {e}")

    def _parse_range_response(
        self,
        data: Dict[str, Any],
        metric_name: str,
        category: MetricCategory,
        unit: str,
        description: str,
    ) -> List[MetricSeries]:
        """Parse Prometheus range query response into MetricSeries."""
        results: List[MetricSeries] = []
        result_data = data.get("data", {}).get("result", [])

        for result in result_data:
            labels = result.get("metric", {})
            # Remove __name__ from labels as it's redundant
            labels.pop("__name__", None)

            data_points = [
                MetricDataPoint(
                    timestamp=datetime.fromtimestamp(ts),
                    value=float(val),
                    labels=labels,
                )
                for ts, val in result.get("values", [])
                if val != "NaN"
            ]

            if data_points:
                series = MetricSeries(
                    name=metric_name,
                    category=category,
                    unit=unit,
                    description=description,
                    labels=labels,
                    data_points=data_points,
                )
                results.append(series)

        return results

    async def get_metric_names(self) -> List[str]:
        """Get list of all available metric names."""
        if not self._client:
            raise CollectorError("Not connected to Prometheus")

        try:
            response = await self._client.get("/api/v1/label/__name__/values")
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.warning("Failed to get metric names", error=str(e))
            return []

    @property
    def configured_metrics(self) -> List[str]:
        """Get list of configured metric names."""
        return list(self._queries.keys())

    def get_query(self, metric_name: str) -> Optional[MetricQuery]:
        """Get query definition for a metric."""
        return self._queries.get(metric_name)
