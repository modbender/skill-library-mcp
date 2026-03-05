"""
Pydantic Settings for SRE Agent configuration management.

Configuration is loaded from:
1. Environment variables (highest priority)
2. config/config.yaml file
3. Default values
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PrometheusSettings(BaseSettings):
    """Prometheus/Mimir configuration."""

    url: str = "http://localhost:9090"
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_delay_seconds: int = 1


class LokiSettings(BaseSettings):
    """Loki configuration."""

    url: str = "http://localhost:3100"
    timeout_seconds: int = 30
    retry_attempts: int = 3


class LLMSettings(BaseSettings):
    """LLM (Claude) configuration."""

    provider: str = "anthropic"
    model: str = "claude-sonnet-4-20250514"
    api_key: str = ""
    max_tokens: int = 4096
    temperature: float = 0.1

    model_config = SettingsConfigDict(env_prefix="LLM_")


class QdrantSettings(BaseSettings):
    """Qdrant vector database configuration."""

    url: str = "http://localhost:6333"
    collection_name: str = "sre_incidents"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    model_config = SettingsConfigDict(env_prefix="QDRANT_")


class BaselineSettings(BaseSettings):
    """Baseline learning configuration."""

    min_history_days: int = 7
    optimal_history_days: int = 30
    learning_interval_hours: int = 24
    stl_period: int = 1440  # minutes (24 hours)
    quantile_lower: float = 0.05
    quantile_upper: float = 0.95


class AnomalyDetectionSettings(BaseSettings):
    """Anomaly detection configuration."""

    check_interval_seconds: int = 60
    zscore_threshold: float = 3.0
    mad_threshold: float = 3.5
    min_anomaly_duration_minutes: int = 2
    ensemble_min_votes: int = 2
    algorithms: List[str] = Field(default_factory=lambda: ["zscore", "mad"])


class PredictionSettings(BaseSettings):
    """Trend prediction configuration."""

    enabled: bool = True
    horizons_hours: List[int] = Field(default_factory=lambda: [1, 3, 6])
    algorithms: List[str] = Field(default_factory=lambda: ["holt_winters"])


class RCASettings(BaseSettings):
    """Root cause analysis configuration."""

    enabled: bool = True
    lookback_minutes: int = 30
    correlation_threshold: float = 0.7
    granger_max_lag: int = 5
    use_llm: bool = True


class RiskWeights(BaseSettings):
    """Risk assessment weight configuration."""

    severity: float = 0.35
    urgency: float = 0.25
    impact: float = 0.25
    complexity: float = 0.15


class RiskThresholds(BaseSettings):
    """Risk threshold configuration."""

    auto: float = 0.4
    semi_auto: float = 0.6
    manual: float = 0.8


class RiskAssessmentSettings(BaseSettings):
    """Risk assessment configuration."""

    weights: RiskWeights = Field(default_factory=RiskWeights)
    thresholds: RiskThresholds = Field(default_factory=RiskThresholds)


class BlacklistSettings(BaseSettings):
    """Auto-remediation blacklist configuration."""

    namespaces: List[str] = Field(default_factory=lambda: ["kube-system"])
    labels: List[str] = Field(default_factory=lambda: ["do-not-remediate=true"])


class AutoRemediationSettings(BaseSettings):
    """Auto-remediation configuration."""

    enabled: bool = True
    dry_run: bool = False
    max_concurrent_actions: int = 3
    cooldown_minutes: int = 5
    blacklist: BlacklistSettings = Field(default_factory=BlacklistSettings)


class WebhookSettings(BaseSettings):
    """Webhook notification configuration."""

    url: str = ""
    timeout_seconds: int = 10
    retry_attempts: int = 3


class NotificationSettings(BaseSettings):
    """Notification configuration."""

    webhook: WebhookSettings = Field(default_factory=WebhookSettings)


class ApprovalSettings(BaseSettings):
    """Approval workflow configuration."""

    timeout_minutes: int = 30
    required_approvers_semi_auto: int = 1
    required_approvers_manual: int = 2


class AuditSettings(BaseSettings):
    """Audit logging configuration."""

    enabled: bool = True
    retention_days: int = 90
    log_file: str = "/var/log/sre-agent/audit.log"


class APISettings(BaseSettings):
    """API server configuration."""

    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])


class KubernetesSettings(BaseSettings):
    """Kubernetes configuration."""

    in_cluster: bool = False
    kubeconfig: str = "~/.kube/config"
    namespace: str = "default"

    model_config = SettingsConfigDict(env_prefix="K8S_")


class K8sClusterSettings(BaseSettings):
    """K8s cluster-level operation settings."""

    drain_timeout_seconds: int = 300
    drain_grace_period: int = 30
    ignore_daemonsets: bool = True
    delete_emptydir_data: bool = False
    force_drain: bool = False


class LarkSettings(BaseSettings):
    """Lark (Feishu) notification configuration."""

    enabled: bool = False
    app_id: str = ""
    app_secret: str = ""
    webhook_url: str = ""
    verification_token: str = ""
    encrypt_key: str = ""

    model_config = SettingsConfigDict(env_prefix="LARK_")


class AnsibleSettings(BaseSettings):
    """Ansible executor configuration."""

    enabled: bool = False
    playbooks_dir: str = "/etc/sre-agent/ansible/playbooks"
    roles_dir: str = "/etc/sre-agent/ansible/roles"
    inventory_file: str = ""
    timeout_seconds: int = 600
    forks: int = 5
    become: bool = False
    become_user: str = "root"
    extra_vars: Dict[str, Any] = Field(default_factory=dict)

    model_config = SettingsConfigDict(env_prefix="ANSIBLE_")


class LearningSettings(BaseSettings):
    """Learning engine configuration."""

    enabled: bool = True
    min_executions_for_learning: int = 3
    success_rate_threshold: float = 0.8
    auto_risk_adjustment: bool = True
    max_risk_reduction: float = 0.2


class Settings(BaseSettings):
    """Main settings class that aggregates all configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application settings
    app_name: str = "sre-agent"
    app_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"

    # Component settings
    prometheus: PrometheusSettings = Field(default_factory=PrometheusSettings)
    loki: LokiSettings = Field(default_factory=LokiSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    qdrant: QdrantSettings = Field(default_factory=QdrantSettings)
    baseline: BaselineSettings = Field(default_factory=BaselineSettings)
    anomaly_detection: AnomalyDetectionSettings = Field(default_factory=AnomalyDetectionSettings)
    prediction: PredictionSettings = Field(default_factory=PredictionSettings)
    rca: RCASettings = Field(default_factory=RCASettings)
    risk_assessment: RiskAssessmentSettings = Field(default_factory=RiskAssessmentSettings)
    auto_remediation: AutoRemediationSettings = Field(default_factory=AutoRemediationSettings)
    notification: NotificationSettings = Field(default_factory=NotificationSettings)
    approval: ApprovalSettings = Field(default_factory=ApprovalSettings)
    audit: AuditSettings = Field(default_factory=AuditSettings)
    api: APISettings = Field(default_factory=APISettings)
    kubernetes: KubernetesSettings = Field(default_factory=KubernetesSettings)
    k8s_cluster: K8sClusterSettings = Field(default_factory=K8sClusterSettings)
    lark: LarkSettings = Field(default_factory=LarkSettings)
    ansible: AnsibleSettings = Field(default_factory=AnsibleSettings)
    learning: LearningSettings = Field(default_factory=LearningSettings)

    # Direct environment variable overrides
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    prometheus_url: str = Field(default="", alias="PROMETHEUS_URL")
    loki_url: str = Field(default="", alias="LOKI_URL")
    qdrant_url: str = Field(default="", alias="QDRANT_URL")
    webhook_url: str = Field(default="", alias="WEBHOOK_URL")
    lark_webhook_url: str = Field(default="", alias="LARK_WEBHOOK_URL")
    lark_app_id: str = Field(default="", alias="LARK_APP_ID")
    lark_app_secret: str = Field(default="", alias="LARK_APP_SECRET")

    def model_post_init(self, __context: Any) -> None:
        """Apply environment variable overrides after initialization."""
        if self.anthropic_api_key:
            self.llm.api_key = self.anthropic_api_key
        if self.prometheus_url:
            self.prometheus.url = self.prometheus_url
        if self.loki_url:
            self.loki.url = self.loki_url
        if self.qdrant_url:
            self.qdrant.url = self.qdrant_url
        if self.webhook_url:
            self.notification.webhook.url = self.webhook_url
        if self.lark_webhook_url:
            self.lark.webhook_url = self.lark_webhook_url
        if self.lark_app_id:
            self.lark.app_id = self.lark_app_id
        if self.lark_app_secret:
            self.lark.app_secret = self.lark_app_secret

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper_v = v.upper()
        if upper_v not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return upper_v


def load_yaml_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"

    if not config_path.exists():
        return {}

    with open(config_path) as f:
        return yaml.safe_load(f) or {}


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Settings are loaded from environment variables and config file.
    Environment variables take precedence.
    """
    return Settings()


def reload_settings() -> Settings:
    """Force reload settings (clears cache)."""
    get_settings.cache_clear()
    return get_settings()
