from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

PRIVACY_WARNING = """> ⚠️ PRIVACY WARNING: You have configured TaxClaw to use a cloud-hosted AI model. Tax documents contain sensitive personal and financial information including Social Security Numbers, income, and asset holdings. When using cloud models, document content is transmitted to a third-party AI provider outside your local control. This provider may log requests for safety monitoring. For maximum privacy, use local models (the default). Only continue if you understand and accept this. Set `privacy_acknowledged: true` in config.yaml to confirm.
"""


def _expand_path(p: str) -> str:
    return str(Path(os.path.expanduser(p)).expanduser())


@dataclass
class Config:
    model_backend: str = "local"  # local|cloud
    local_model: str = "llama3.2"
    cloud_model: str = "claude-haiku-4-5"
    cloud_api_key: str = ""
    privacy_acknowledged: bool = False
    port: int = 8421
    data_dir: str = "~/.local/share/taxclaw/"

    # Security limits
    max_upload_bytes: int = 10 * 1024 * 1024  # 10MB
    storage_cap_bytes: int = 2 * 1024 * 1024 * 1024  # 2GB total stored originals

    @property
    def data_path(self) -> Path:
        return Path(_expand_path(self.data_dir))

    @property
    def db_path(self) -> Path:
        return self.data_path / "tax.db"

    @property
    def uploads_dir(self) -> Path:
        return self.data_path / "uploads"


CONFIG_PATH = Path(os.path.expanduser("~/.config/taxclaw/config.yaml"))


def load_config() -> Config:
    cfg_path = CONFIG_PATH
    if cfg_path.exists():
        raw: dict[str, Any] = yaml.safe_load(cfg_path.read_text()) or {}
    else:
        raw = {}

    cfg = Config(**{k: v for k, v in raw.items() if hasattr(Config, k)})

    # allow env var override
    if not cfg.cloud_api_key:
        cfg.cloud_api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    # NOTE: Do not hard-exit here; the web UI needs to load even if the user
    # hasn't acknowledged cloud privacy yet. Enforce acknowledgement at call sites.

    cfg.data_path.mkdir(parents=True, exist_ok=True)
    cfg.uploads_dir.mkdir(parents=True, exist_ok=True)
    return cfg


def save_config(*, cfg: Config) -> None:
    """Persist user-editable config fields to ~/.config/taxclaw/config.yaml.

    Intentionally does not write cloud_api_key (prefer env var), and will preserve
    unknown keys already present in the file.
    """

    cfg_path = CONFIG_PATH
    cfg_path.parent.mkdir(parents=True, exist_ok=True)

    existing: dict[str, Any] = {}
    if cfg_path.exists():
        existing = yaml.safe_load(cfg_path.read_text()) or {}

    existing.update(
        {
            "model_backend": cfg.model_backend,
            "local_model": cfg.local_model,
            "cloud_model": cfg.cloud_model,
            "privacy_acknowledged": bool(cfg.privacy_acknowledged),
            "port": int(cfg.port),
            "data_dir": cfg.data_dir,
            "max_upload_bytes": int(cfg.max_upload_bytes),
            "storage_cap_bytes": int(cfg.storage_cap_bytes),
        }
    )

    cfg_path.write_text(yaml.safe_dump(existing, sort_keys=False))
