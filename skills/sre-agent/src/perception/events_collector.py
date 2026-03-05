"""
Events collector for Kubernetes events and configuration changes.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from src.config.constants import EventType
from src.config.settings import get_settings
from src.models.metrics import Event
from src.perception.base_collector import BaseCollector, CollectorError, ConnectionError

logger = structlog.get_logger()


class EventsCollector(BaseCollector):
    """
    Collector for Kubernetes events.

    Features:
    - Collects pod events (restarts, OOMKilled, etc.)
    - Collects deployment events (rollouts, scaling)
    - Collects node events (pressure, NotReady)
    - Tracks configuration changes
    """

    def __init__(
        self,
        in_cluster: Optional[bool] = None,
        kubeconfig: Optional[str] = None,
        namespace: Optional[str] = None,
    ):
        settings = get_settings()
        # Not calling super().__init__ with URL since K8s uses different connection
        self.url = ""
        self.timeout_seconds = 30
        self.retry_attempts = 3
        self.retry_delay_seconds = 1
        self._client: client.Optional[CoreV1Api] = None
        self._apps_client: client.Optional[AppsV1Api] = None
        self._connected = False

        self._in_cluster = in_cluster if in_cluster is not None else settings.kubernetes.in_cluster
        self._kubeconfig = kubeconfig or settings.kubernetes.kubeconfig
        self._namespace = namespace or settings.kubernetes.namespace

    async def connect(self) -> None:
        """Connect to Kubernetes API."""
        try:
            if self._in_cluster:
                config.load_incluster_config()
            else:
                config.load_kube_config(config_file=self._kubeconfig)

            self._client = client.CoreV1Api()
            self._apps_client = client.AppsV1Api()

            if await self.health_check():
                self._connected = True
                logger.info(
                    "Connected to Kubernetes",
                    in_cluster=self._in_cluster,
                )
            else:
                raise ConnectionError("Health check failed")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Kubernetes: {e}")

    async def disconnect(self) -> None:
        """Disconnect from Kubernetes (no-op for K8s client)."""
        self._client = None
        self._apps_client = None
        self._connected = False
        logger.info("Disconnected from Kubernetes")

    async def health_check(self) -> bool:
        """Check Kubernetes API health."""
        try:
            if self._client:
                self._client.get_api_resources()
                return True
            return False
        except Exception:
            return False

    async def collect(
        self, start_time: datetime, end_time: datetime
    ) -> List[Event]:
        """
        Collect Kubernetes events.

        Args:
            start_time: Start of collection window
            end_time: End of collection window

        Returns:
            List of Event objects
        """
        events: List[Event] = []

        try:
            k8s_events = await self._collect_k8s_events(start_time, end_time)
            events.extend(k8s_events)
        except Exception as e:
            logger.warning("Failed to collect K8s events", error=str(e))

        return events

    async def _collect_k8s_events(
        self, start_time: datetime, end_time: datetime
    ) -> List[Event]:
        """Collect raw Kubernetes events."""
        if not self._client:
            raise CollectorError("Not connected to Kubernetes")

        events: List[Event] = []

        try:
            # Get events from all namespaces or specific namespace
            if self._namespace == "all":
                api_response = self._client.list_event_for_all_namespaces()
            else:
                api_response = self._client.list_namespaced_event(self._namespace)

            for item in api_response.items:
                # Filter by time
                event_time = item.last_timestamp or item.event_time or item.metadata.creation_timestamp
                if event_time:
                    if isinstance(event_time, str):
                        event_time = datetime.fromisoformat(event_time.replace("Z", "+00:00"))
                    elif hasattr(event_time, "timestamp"):
                        event_time = datetime.fromtimestamp(event_time.timestamp())

                    if not (start_time <= event_time <= end_time):
                        continue
                else:
                    continue

                event = self._parse_k8s_event(item, event_time)
                if event:
                    events.append(event)

        except ApiException as e:
            logger.error("K8s API error", status=e.status, reason=e.reason)

        return events

    def _parse_k8s_event(self, item: Any, event_time: datetime) -> Optional[Event]:
        """Parse Kubernetes event into our Event model."""
        try:
            event_type = EventType.WARNING if item.type == "Warning" else EventType.NORMAL

            first_seen = None
            if item.first_timestamp:
                if isinstance(item.first_timestamp, datetime):
                    first_seen = item.first_timestamp
                else:
                    first_seen = datetime.fromtimestamp(item.first_timestamp.timestamp())

            return Event(
                timestamp=event_time,
                event_type=event_type,
                reason=item.reason or "",
                message=item.message or "",
                source=f"{item.source.component}/{item.source.host}" if item.source else "unknown",
                namespace=item.metadata.namespace,
                kind=item.involved_object.kind if item.involved_object else None,
                name=item.involved_object.name if item.involved_object else None,
                count=item.count or 1,
                first_seen=first_seen,
                last_seen=event_time,
                labels={
                    "namespace": item.metadata.namespace or "",
                    "kind": item.involved_object.kind if item.involved_object else "",
                    "name": item.involved_object.name if item.involved_object else "",
                },
            )
        except Exception as e:
            logger.debug("Failed to parse K8s event", error=str(e))
            return None

    async def get_pod_events(
        self,
        namespace: str,
        pod_name: str,
        since_minutes: int = 30,
    ) -> List[Event]:
        """Get events for a specific pod."""
        if not self._client:
            raise CollectorError("Not connected to Kubernetes")

        events: List[Event] = []
        start_time = datetime.utcnow() - timedelta(minutes=since_minutes)

        try:
            field_selector = f"involvedObject.name={pod_name},involvedObject.kind=Pod"
            api_response = self._client.list_namespaced_event(
                namespace,
                field_selector=field_selector,
            )

            for item in api_response.items:
                event_time = item.last_timestamp or item.event_time
                if event_time:
                    if hasattr(event_time, "timestamp"):
                        event_time = datetime.fromtimestamp(event_time.timestamp())
                    if event_time >= start_time:
                        event = self._parse_k8s_event(item, event_time)
                        if event:
                            events.append(event)

        except ApiException as e:
            logger.error("Failed to get pod events", error=str(e))

        return events

    async def get_deployment_events(
        self,
        namespace: str,
        deployment_name: str,
        since_minutes: int = 60,
    ) -> List[Event]:
        """Get events for a specific deployment."""
        if not self._client:
            raise CollectorError("Not connected to Kubernetes")

        events: List[Event] = []
        start_time = datetime.utcnow() - timedelta(minutes=since_minutes)

        try:
            field_selector = f"involvedObject.name={deployment_name},involvedObject.kind=Deployment"
            api_response = self._client.list_namespaced_event(
                namespace,
                field_selector=field_selector,
            )

            for item in api_response.items:
                event_time = item.last_timestamp or item.event_time
                if event_time:
                    if hasattr(event_time, "timestamp"):
                        event_time = datetime.fromtimestamp(event_time.timestamp())
                    if event_time >= start_time:
                        event = self._parse_k8s_event(item, event_time)
                        if event:
                            events.append(event)

        except ApiException as e:
            logger.error("Failed to get deployment events", error=str(e))

        return events

    async def get_warning_events(
        self,
        namespace: Optional[str] = None,
        since_minutes: int = 30,
    ) -> List[Event]:
        """Get all warning events."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=since_minutes)

        events = await self._collect_k8s_events(start_time, end_time)
        return [e for e in events if e.event_type == EventType.WARNING]

    async def get_recent_restarts(
        self,
        namespace: Optional[str] = None,
        since_minutes: int = 30,
    ) -> List[Event]:
        """Get recent pod restart events."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=since_minutes)

        events = await self._collect_k8s_events(start_time, end_time)
        restart_reasons = {"Killing", "BackOff", "Started", "Created"}
        return [e for e in events if e.reason in restart_reasons and e.kind == "Pod"]
