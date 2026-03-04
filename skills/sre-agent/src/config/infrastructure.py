"""
Infrastructure Configuration Center

Manages connections to all infrastructure components:
- If configured: use existing infrastructure
- If not configured: optionally auto-create local services

Supported components:
- Prometheus / Mimir (metrics)
- Loki (logs)
- Grafana (visualization)
- SkyWalking (tracing)
- Kafka (message queue)
- MySQL (database)
- Redis (cache)
- Qdrant / Milvus (vector database)
"""

import asyncio
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import structlog
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = structlog.get_logger()


class ServiceStatus(str, Enum):
    """Service connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    NOT_CONFIGURED = "not_configured"
    AUTO_CREATED = "auto_created"
    FAILED = "failed"


class ServiceType(str, Enum):
    """Types of infrastructure services."""
    PROMETHEUS = "prometheus"
    MIMIR = "mimir"
    LOKI = "loki"
    GRAFANA = "grafana"
    SKYWALKING = "skywalking"
    KAFKA = "kafka"
    MYSQL = "mysql"
    REDIS = "redis"
    QDRANT = "qdrant"
    MILVUS = "milvus"


# ============================================================
# Service Configuration Models
# ============================================================

class PrometheusConfig(BaseModel):
    """Prometheus/Mimir configuration."""
    enabled: bool = True
    url: str = ""
    timeout_seconds: int = 30
    retry_attempts: int = 3
    # Mimir specific
    use_mimir: bool = False
    mimir_url: str = ""
    # Auth (optional)
    username: str = ""
    password: str = ""
    bearer_token: str = ""


class LokiConfig(BaseModel):
    """Loki configuration."""
    enabled: bool = True
    url: str = ""
    timeout_seconds: int = 30
    retry_attempts: int = 3
    # Auth
    username: str = ""
    password: str = ""
    tenant_id: str = ""


class GrafanaConfig(BaseModel):
    """Grafana configuration."""
    enabled: bool = False
    url: str = ""
    api_key: str = ""
    org_id: int = 1


class SkyWalkingConfig(BaseModel):
    """SkyWalking configuration."""
    enabled: bool = False
    oap_url: str = ""  # OAP server URL
    ui_url: str = ""   # UI URL
    username: str = ""
    password: str = ""


class KafkaConfig(BaseModel):
    """Kafka configuration."""
    enabled: bool = False
    bootstrap_servers: str = ""  # comma-separated list
    security_protocol: str = "PLAINTEXT"  # PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL
    sasl_mechanism: str = ""  # PLAIN, SCRAM-SHA-256, SCRAM-SHA-512
    sasl_username: str = ""
    sasl_password: str = ""
    # Topics
    anomaly_topic: str = "sre-agent-anomalies"
    action_topic: str = "sre-agent-actions"
    audit_topic: str = "sre-agent-audit"


class MySQLConfig(BaseModel):
    """MySQL configuration."""
    enabled: bool = False
    host: str = ""
    port: int = 3306
    database: str = "sre_agent"
    username: str = ""
    password: str = ""
    pool_size: int = 5
    # Connection string override
    connection_string: str = ""


class RedisConfig(BaseModel):
    """Redis configuration."""
    enabled: bool = False
    url: str = ""  # redis://[:password@]host[:port][/db]
    host: str = ""
    port: int = 6379
    password: str = ""
    db: int = 0
    # Cluster mode
    cluster_mode: bool = False
    cluster_nodes: List[str] = Field(default_factory=list)
    # Sentinel mode
    sentinel_mode: bool = False
    sentinel_master: str = ""
    sentinel_nodes: List[str] = Field(default_factory=list)


class VectorDBConfig(BaseModel):
    """Vector database configuration (Qdrant/Milvus)."""
    enabled: bool = True
    provider: str = "qdrant"  # qdrant, milvus
    # Qdrant
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    # Milvus
    milvus_host: str = ""
    milvus_port: int = 19530
    milvus_username: str = ""
    milvus_password: str = ""
    # Common
    collection_name: str = "sre_incidents"


class AutoCreateConfig(BaseModel):
    """Auto-create configuration for local development."""
    enabled: bool = True
    docker_compose_file: str = "docker-compose.yaml"
    services_to_create: List[str] = Field(default_factory=lambda: [
        "prometheus", "loki", "qdrant"
    ])
    timeout_seconds: int = 60


# ============================================================
# Main Infrastructure Settings
# ============================================================

class InfrastructureSettings(BaseSettings):
    """
    Central configuration for all infrastructure components.

    Configuration priority:
    1. Environment variables (highest)
    2. .env file
    3. Default values (auto-create if enabled)

    Environment variable format:
    - INFRA_PROMETHEUS_URL
    - INFRA_LOKI_URL
    - INFRA_KAFKA_BOOTSTRAP_SERVERS
    - etc.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="INFRA_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # Service configurations
    prometheus: PrometheusConfig = Field(default_factory=PrometheusConfig)
    loki: LokiConfig = Field(default_factory=LokiConfig)
    grafana: GrafanaConfig = Field(default_factory=GrafanaConfig)
    skywalking: SkyWalkingConfig = Field(default_factory=SkyWalkingConfig)
    kafka: KafkaConfig = Field(default_factory=KafkaConfig)
    mysql: MySQLConfig = Field(default_factory=MySQLConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    vector_db: VectorDBConfig = Field(default_factory=VectorDBConfig)

    # Auto-create settings
    auto_create: AutoCreateConfig = Field(default_factory=AutoCreateConfig)

    # Direct environment variable overrides (convenience)
    prometheus_url: str = Field(default="", alias="PROMETHEUS_URL")
    mimir_url: str = Field(default="", alias="MIMIR_URL")
    loki_url: str = Field(default="", alias="LOKI_URL")
    grafana_url: str = Field(default="", alias="GRAFANA_URL")
    skywalking_url: str = Field(default="", alias="SKYWALKING_URL")
    kafka_servers: str = Field(default="", alias="KAFKA_BOOTSTRAP_SERVERS")
    mysql_host: str = Field(default="", alias="MYSQL_HOST")
    mysql_password: str = Field(default="", alias="MYSQL_PASSWORD")
    redis_url: str = Field(default="", alias="REDIS_URL")
    qdrant_url: str = Field(default="", alias="QDRANT_URL")
    milvus_host: str = Field(default="", alias="MILVUS_HOST")

    def model_post_init(self, __context: Any) -> None:
        """Apply direct environment variable overrides."""
        # Prometheus
        if self.prometheus_url:
            self.prometheus.url = self.prometheus_url
        if self.mimir_url:
            self.prometheus.mimir_url = self.mimir_url
            self.prometheus.use_mimir = True

        # Loki
        if self.loki_url:
            self.loki.url = self.loki_url

        # Grafana
        if self.grafana_url:
            self.grafana.url = self.grafana_url
            self.grafana.enabled = True

        # SkyWalking
        if self.skywalking_url:
            self.skywalking.oap_url = self.skywalking_url
            self.skywalking.enabled = True

        # Kafka
        if self.kafka_servers:
            self.kafka.bootstrap_servers = self.kafka_servers
            self.kafka.enabled = True

        # MySQL
        if self.mysql_host:
            self.mysql.host = self.mysql_host
            self.mysql.enabled = True
        if self.mysql_password:
            self.mysql.password = self.mysql_password

        # Redis
        if self.redis_url:
            self.redis.url = self.redis_url
            self.redis.enabled = True

        # Vector DB
        if self.qdrant_url:
            self.vector_db.qdrant_url = self.qdrant_url
            self.vector_db.provider = "qdrant"
        if self.milvus_host:
            self.vector_db.milvus_host = self.milvus_host
            self.vector_db.provider = "milvus"


# ============================================================
# Service Status Tracking
# ============================================================

@dataclass
class ServiceState:
    """Runtime state of a service."""
    service_type: ServiceType
    status: ServiceStatus = ServiceStatus.NOT_CONFIGURED
    url: str = ""
    error: str = ""
    auto_created: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# Infrastructure Manager
# ============================================================

class InfrastructureManager:
    """
    Manages infrastructure connections and auto-creation.

    Usage:
        manager = InfrastructureManager()
        await manager.initialize()

        # Get service URL
        prometheus_url = manager.get_url(ServiceType.PROMETHEUS)

        # Check status
        status = manager.get_status(ServiceType.PROMETHEUS)
    """

    def __init__(self, settings: Optional[InfrastructureSettings] = None):
        self.settings = settings or InfrastructureSettings()
        self._states: Dict[ServiceType, ServiceState] = {}
        self._initialized = False

        # Initialize states
        for svc_type in ServiceType:
            self._states[svc_type] = ServiceState(service_type=svc_type)

    async def initialize(self) -> Dict[ServiceType, ServiceState]:
        """
        Initialize all configured services.

        1. Check configured services
        2. Auto-create missing services if enabled
        3. Verify connectivity

        Returns:
            Dictionary of service states
        """
        logger.info("Initializing infrastructure manager...")

        # Check each service
        await self._check_prometheus()
        await self._check_loki()
        await self._check_grafana()
        await self._check_skywalking()
        await self._check_kafka()
        await self._check_mysql()
        await self._check_redis()
        await self._check_vector_db()

        # Auto-create missing services if enabled
        if self.settings.auto_create.enabled:
            await self._auto_create_missing_services()

        self._initialized = True

        # Log summary
        self._log_status_summary()

        return self._states

    def get_url(self, service_type: ServiceType) -> Optional[str]:
        """Get URL for a service."""
        state = self._states.get(service_type)
        if state and state.status == ServiceStatus.CONNECTED:
            return state.url
        return None

    def get_status(self, service_type: ServiceType) -> ServiceStatus:
        """Get status of a service."""
        state = self._states.get(service_type)
        return state.status if state else ServiceStatus.NOT_CONFIGURED

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all services."""
        return {
            svc_type.value: {
                "status": state.status.value,
                "url": state.url,
                "auto_created": state.auto_created,
                "error": state.error,
            }
            for svc_type, state in self._states.items()
        }

    def is_service_available(self, service_type: ServiceType) -> bool:
        """Check if a service is available."""
        state = self._states.get(service_type)
        return state is not None and state.status == ServiceStatus.CONNECTED

    # --------------------------------------------------------
    # Service Check Methods
    # --------------------------------------------------------

    async def _check_prometheus(self) -> None:
        """Check Prometheus/Mimir connectivity."""
        config = self.settings.prometheus
        state = self._states[ServiceType.PROMETHEUS]

        if not config.enabled:
            state.status = ServiceStatus.NOT_CONFIGURED
            return

        # Determine URL
        url = config.mimir_url if config.use_mimir else config.url
        if not url:
            state.status = ServiceStatus.NOT_CONFIGURED
            return

        state.url = url

        # Test connectivity
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                if config.use_mimir:
                    response = await client.get(f"{url}/ready")
                else:
                    response = await client.get(f"{url}/-/healthy")

                if response.status_code == 200:
                    state.status = ServiceStatus.CONNECTED
                    logger.info("Prometheus connected", url=url, mimir=config.use_mimir)
                else:
                    state.status = ServiceStatus.FAILED
                    state.error = f"HTTP {response.status_code}"
        except Exception as e:
            state.status = ServiceStatus.FAILED
            state.error = str(e)

    async def _check_loki(self) -> None:
        """Check Loki connectivity."""
        config = self.settings.loki
        state = self._states[ServiceType.LOKI]

        if not config.enabled or not config.url:
            state.status = ServiceStatus.NOT_CONFIGURED
            return

        state.url = config.url

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{config.url}/ready")
                if response.status_code == 200:
                    state.status = ServiceStatus.CONNECTED
                    logger.info("Loki connected", url=config.url)
                else:
                    state.status = ServiceStatus.FAILED
                    state.error = f"HTTP {response.status_code}"
        except Exception as e:
            state.status = ServiceStatus.FAILED
            state.error = str(e)

    async def _check_grafana(self) -> None:
        """Check Grafana connectivity."""
        config = self.settings.grafana
        state = self._states[ServiceType.GRAFANA]

        if not config.enabled or not config.url:
            state.status = ServiceStatus.NOT_CONFIGURED
            return

        state.url = config.url

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                headers = {}
                if config.api_key:
                    headers["Authorization"] = f"Bearer {config.api_key}"
                response = await client.get(f"{config.url}/api/health", headers=headers)
                if response.status_code == 200:
                    state.status = ServiceStatus.CONNECTED
                    logger.info("Grafana connected", url=config.url)
                else:
                    state.status = ServiceStatus.FAILED
                    state.error = f"HTTP {response.status_code}"
        except Exception as e:
            state.status = ServiceStatus.FAILED
            state.error = str(e)

    async def _check_skywalking(self) -> None:
        """Check SkyWalking connectivity."""
        config = self.settings.skywalking
        state = self._states[ServiceType.SKYWALKING]

        if not config.enabled or not config.oap_url:
            state.status = ServiceStatus.NOT_CONFIGURED
            return

        state.url = config.oap_url

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                # Check OAP health endpoint
                response = await client.get(f"{config.oap_url}/healthcheck")
                if response.status_code == 200:
                    state.status = ServiceStatus.CONNECTED
                    logger.info("SkyWalking connected", url=config.oap_url)
                else:
                    state.status = ServiceStatus.FAILED
                    state.error = f"HTTP {response.status_code}"
        except Exception as e:
            state.status = ServiceStatus.FAILED
            state.error = str(e)

    async def _check_kafka(self) -> None:
        """Check Kafka connectivity."""
        config = self.settings.kafka
        state = self._states[ServiceType.KAFKA]

        if not config.enabled or not config.bootstrap_servers:
            state.status = ServiceStatus.NOT_CONFIGURED
            return

        state.url = config.bootstrap_servers

        try:
            from kafka import KafkaAdminClient
            from kafka.errors import KafkaError

            admin = KafkaAdminClient(
                bootstrap_servers=config.bootstrap_servers.split(","),
                security_protocol=config.security_protocol,
                request_timeout_ms=5000,
            )
            admin.close()
            state.status = ServiceStatus.CONNECTED
            logger.info("Kafka connected", servers=config.bootstrap_servers)
        except ImportError:
            state.status = ServiceStatus.FAILED
            state.error = "kafka-python not installed"
        except Exception as e:
            state.status = ServiceStatus.FAILED
            state.error = str(e)

    async def _check_mysql(self) -> None:
        """Check MySQL connectivity."""
        config = self.settings.mysql
        state = self._states[ServiceType.MYSQL]

        if not config.enabled:
            state.status = ServiceStatus.NOT_CONFIGURED
            return

        if not config.host and not config.connection_string:
            state.status = ServiceStatus.NOT_CONFIGURED
            return

        state.url = config.connection_string or f"mysql://{config.host}:{config.port}/{config.database}"

        try:
            import aiomysql

            conn = await aiomysql.connect(
                host=config.host,
                port=config.port,
                user=config.username,
                password=config.password,
                db=config.database,
                connect_timeout=5,
            )
            await conn.ensure_closed()
            state.status = ServiceStatus.CONNECTED
            logger.info("MySQL connected", host=config.host)
        except ImportError:
            state.status = ServiceStatus.FAILED
            state.error = "aiomysql not installed"
        except Exception as e:
            state.status = ServiceStatus.FAILED
            state.error = str(e)

    async def _check_redis(self) -> None:
        """Check Redis connectivity."""
        config = self.settings.redis
        state = self._states[ServiceType.REDIS]

        if not config.enabled:
            state.status = ServiceStatus.NOT_CONFIGURED
            return

        url = config.url or (f"redis://{config.host}:{config.port}/{config.db}" if config.host else "")
        if not url:
            state.status = ServiceStatus.NOT_CONFIGURED
            return

        state.url = url

        try:
            import redis.asyncio as redis

            if config.cluster_mode:
                from redis.asyncio.cluster import RedisCluster
                client = RedisCluster.from_url(url)
            elif config.sentinel_mode:
                from redis.asyncio.sentinel import Sentinel
                sentinel = Sentinel(
                    [(n.split(":")[0], int(n.split(":")[1])) for n in config.sentinel_nodes],
                    socket_timeout=5,
                )
                client = sentinel.master_for(config.sentinel_master)
            else:
                client = redis.from_url(url)

            await client.ping()
            await client.close()
            state.status = ServiceStatus.CONNECTED
            logger.info("Redis connected", url=url)
        except ImportError:
            state.status = ServiceStatus.FAILED
            state.error = "redis not installed"
        except Exception as e:
            state.status = ServiceStatus.FAILED
            state.error = str(e)

    async def _check_vector_db(self) -> None:
        """Check Vector DB (Qdrant/Milvus) connectivity."""
        config = self.settings.vector_db
        state = self._states[ServiceType.QDRANT]  # Use QDRANT as default

        if not config.enabled:
            state.status = ServiceStatus.NOT_CONFIGURED
            return

        if config.provider == "qdrant":
            await self._check_qdrant(config, state)
        elif config.provider == "milvus":
            state = self._states[ServiceType.MILVUS]
            await self._check_milvus(config, state)

    async def _check_qdrant(self, config: VectorDBConfig, state: ServiceState) -> None:
        """Check Qdrant connectivity."""
        if not config.qdrant_url:
            state.status = ServiceStatus.NOT_CONFIGURED
            return

        state.url = config.qdrant_url

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{config.qdrant_url}/collections")
                if response.status_code == 200:
                    state.status = ServiceStatus.CONNECTED
                    logger.info("Qdrant connected", url=config.qdrant_url)
                else:
                    state.status = ServiceStatus.FAILED
                    state.error = f"HTTP {response.status_code}"
        except Exception as e:
            state.status = ServiceStatus.FAILED
            state.error = str(e)

    async def _check_milvus(self, config: VectorDBConfig, state: ServiceState) -> None:
        """Check Milvus connectivity."""
        if not config.milvus_host:
            state.status = ServiceStatus.NOT_CONFIGURED
            return

        state.url = f"{config.milvus_host}:{config.milvus_port}"

        try:
            from pymilvus import connections

            connections.connect(
                alias="default",
                host=config.milvus_host,
                port=config.milvus_port,
                user=config.milvus_username,
                password=config.milvus_password,
            )
            connections.disconnect("default")
            state.status = ServiceStatus.CONNECTED
            logger.info("Milvus connected", host=config.milvus_host)
        except ImportError:
            state.status = ServiceStatus.FAILED
            state.error = "pymilvus not installed"
        except Exception as e:
            state.status = ServiceStatus.FAILED
            state.error = str(e)

    # --------------------------------------------------------
    # Auto-Create Methods
    # --------------------------------------------------------

    async def _auto_create_missing_services(self) -> None:
        """Auto-create missing services using docker-compose."""
        services_to_create = []

        # Check which services need to be created
        service_mapping = {
            "prometheus": ServiceType.PROMETHEUS,
            "loki": ServiceType.LOKI,
            "grafana": ServiceType.GRAFANA,
            "qdrant": ServiceType.QDRANT,
            "redis": ServiceType.REDIS,
        }

        for service_name in self.settings.auto_create.services_to_create:
            service_type = service_mapping.get(service_name)
            if service_type:
                state = self._states.get(service_type)
                if state and state.status in (ServiceStatus.NOT_CONFIGURED, ServiceStatus.FAILED):
                    services_to_create.append(service_name)

        if not services_to_create:
            logger.info("No services need to be auto-created")
            return

        logger.info("Auto-creating services", services=services_to_create)

        # Run docker-compose up for the services
        compose_file = Path(self.settings.auto_create.docker_compose_file)
        if not compose_file.exists():
            logger.warning("Docker compose file not found", path=str(compose_file))
            return

        try:
            cmd = [
                "docker-compose",
                "-f", str(compose_file),
                "up", "-d",
            ] + services_to_create

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.settings.auto_create.timeout_seconds,
            )

            if process.returncode == 0:
                logger.info("Services created successfully", services=services_to_create)

                # Wait for services to be ready
                await asyncio.sleep(5)

                # Re-check connectivity and update URLs
                await self._update_auto_created_services(services_to_create)
            else:
                logger.error(
                    "Failed to create services",
                    stderr=stderr.decode() if stderr else "",
                )
        except asyncio.TimeoutError:
            logger.error("Timeout creating services")
        except FileNotFoundError:
            logger.warning("docker-compose not found, skipping auto-create")
        except Exception as e:
            logger.error("Error creating services", error=str(e))

    async def _update_auto_created_services(self, services: List[str]) -> None:
        """Update configuration for auto-created services."""
        # Default local URLs for auto-created services
        local_urls = {
            "prometheus": "http://localhost:9090",
            "loki": "http://localhost:3100",
            "grafana": "http://localhost:3000",
            "qdrant": "http://localhost:6333",
            "redis": "redis://localhost:6379",
        }

        for service_name in services:
            url = local_urls.get(service_name)
            if not url:
                continue

            # Update configuration
            if service_name == "prometheus":
                self.settings.prometheus.url = url
                await self._check_prometheus()
                if self._states[ServiceType.PROMETHEUS].status == ServiceStatus.CONNECTED:
                    self._states[ServiceType.PROMETHEUS].auto_created = True

            elif service_name == "loki":
                self.settings.loki.url = url
                await self._check_loki()
                if self._states[ServiceType.LOKI].status == ServiceStatus.CONNECTED:
                    self._states[ServiceType.LOKI].auto_created = True

            elif service_name == "grafana":
                self.settings.grafana.url = url
                self.settings.grafana.enabled = True
                await self._check_grafana()
                if self._states[ServiceType.GRAFANA].status == ServiceStatus.CONNECTED:
                    self._states[ServiceType.GRAFANA].auto_created = True

            elif service_name == "qdrant":
                self.settings.vector_db.qdrant_url = url
                await self._check_vector_db()
                if self._states[ServiceType.QDRANT].status == ServiceStatus.CONNECTED:
                    self._states[ServiceType.QDRANT].auto_created = True

            elif service_name == "redis":
                self.settings.redis.url = url
                self.settings.redis.enabled = True
                await self._check_redis()
                if self._states[ServiceType.REDIS].status == ServiceStatus.CONNECTED:
                    self._states[ServiceType.REDIS].auto_created = True

    def _log_status_summary(self) -> None:
        """Log status summary of all services."""
        connected = []
        failed = []
        not_configured = []
        auto_created = []

        for svc_type, state in self._states.items():
            if state.status == ServiceStatus.CONNECTED:
                if state.auto_created:
                    auto_created.append(svc_type.value)
                else:
                    connected.append(svc_type.value)
            elif state.status == ServiceStatus.FAILED:
                failed.append(f"{svc_type.value}({state.error})")
            else:
                not_configured.append(svc_type.value)

        logger.info(
            "Infrastructure status summary",
            connected=connected,
            auto_created=auto_created,
            failed=failed,
            not_configured=not_configured,
        )


# ============================================================
# Singleton Instance
# ============================================================

_infrastructure_manager: Optional[InfrastructureManager] = None


def get_infrastructure_manager() -> InfrastructureManager:
    """Get the singleton infrastructure manager."""
    global _infrastructure_manager
    if _infrastructure_manager is None:
        _infrastructure_manager = InfrastructureManager()
    return _infrastructure_manager


async def initialize_infrastructure() -> Dict[ServiceType, ServiceState]:
    """Initialize infrastructure and return status."""
    manager = get_infrastructure_manager()
    return await manager.initialize()
