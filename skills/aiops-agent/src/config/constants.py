"""
Constants and enumerations for SRE Agent.
"""

from enum import Enum


class AnomalyType(str, Enum):
    """Types of anomalies that can be detected."""

    POINT = "point"  # Single point anomaly
    TREND = "trend"  # Trend deviation
    PERIODIC = "periodic"  # Periodic pattern anomaly
    CORRELATION = "correlation"  # Multi-metric correlation anomaly
    THRESHOLD = "threshold"  # Static threshold breach


class AnomalySeverity(str, Enum):
    """Severity levels for anomalies."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    """Risk levels for remediation actions."""

    AUTO = "auto"  # < 0.4 - Automatic execution
    SEMI_AUTO = "semi_auto"  # 0.4-0.6 - Single approval required
    MANUAL = "manual"  # 0.6-0.8 - Multiple approvals required
    CRITICAL = "critical"  # >= 0.8 - Diagnosis only, no auto action


class ActionStatus(str, Enum):
    """Status of remediation actions."""

    PENDING = "pending"
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ActionType(str, Enum):
    """Types of remediation actions."""

    # Pod-level actions
    POD_RESTART = "pod_restart"
    HPA_SCALE = "hpa_scale"
    DEPLOYMENT_ROLLBACK = "deployment_rollback"
    CONFIG_ROLLBACK = "config_rollback"
    CIRCUIT_BREAKER = "circuit_breaker"
    TRAFFIC_SHIFT = "traffic_shift"
    DATABASE_FAILOVER = "database_failover"
    CACHE_FLUSH = "cache_flush"
    CUSTOM_WEBHOOK = "custom_webhook"

    # Ansible actions
    ANSIBLE_PLAYBOOK = "ansible_playbook"
    ANSIBLE_ROLE = "ansible_role"

    # K8s cluster-level actions
    NODE_CORDON = "node_cordon"
    NODE_DRAIN = "node_drain"
    NODE_UNCORDON = "node_uncordon"
    PVC_EXPAND = "pvc_expand"
    PVC_SNAPSHOT = "pvc_snapshot"
    NETWORK_POLICY_APPLY = "network_policy_apply"
    NETWORK_POLICY_REMOVE = "network_policy_remove"


class MetricCategory(str, Enum):
    """Categories of metrics."""

    TRADING = "trading"
    MATCHING = "matching"
    RISK = "risk"
    WALLET = "wallet"
    API = "api"
    INFRASTRUCTURE = "infrastructure"
    DATABASE = "database"
    QUEUE = "queue"
    BUSINESS = "business"


class LogLevel(str, Enum):
    """Log severity levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventType(str, Enum):
    """Types of Kubernetes events."""

    NORMAL = "Normal"
    WARNING = "Warning"


# Time constants (in seconds)
MINUTE = 60
HOUR = 3600
DAY = 86400
WEEK = 604800

# Default thresholds
DEFAULT_ZSCORE_THRESHOLD = 3.0
DEFAULT_MAD_THRESHOLD = 3.5
DEFAULT_ISOLATION_FOREST_CONTAMINATION = 0.1

# Correlation thresholds
STRONG_CORRELATION = 0.8
MODERATE_CORRELATION = 0.6
WEAK_CORRELATION = 0.4

# Cache TTLs (in seconds)
BASELINE_CACHE_TTL = 3600  # 1 hour
METRICS_CACHE_TTL = 60  # 1 minute
RAG_CACHE_TTL = 300  # 5 minutes

# API rate limits
MAX_REQUESTS_PER_MINUTE = 60
MAX_CONCURRENT_CONNECTIONS = 100

# Kubernetes constants
K8S_RESTART_GRACE_PERIOD = 30
K8S_SCALE_TIMEOUT = 300
K8S_ROLLBACK_TIMEOUT = 600

# Notification templates
ANOMALY_TEMPLATE = "anomaly"
PREDICTION_TEMPLATE = "prediction"
REMEDIATION_TEMPLATE = "remediation"
APPROVAL_TEMPLATE = "approval"
