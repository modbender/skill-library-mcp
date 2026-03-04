"""
Local runtime config store for SociClaw onboarding.

This captures stable user defaults used by local commands and future agent flows.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


@dataclass
class RuntimeConfig:
    provider: str = "telegram"
    provider_user_id: str = ""
    user_niche: str = ""
    posting_frequency: str = "2/day"
    content_language: str = "en"
    brand_logo_url: str = ""
    has_brand_document: bool = False
    brand_document_path: str = ""
    use_trello: bool = False
    use_notion: bool = False
    timezone: str = "UTC"


def default_runtime_config_path() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / ".sociclaw" / "runtime_config.json"


class RuntimeConfigStore:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or default_runtime_config_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> RuntimeConfig:
        if not self.path.exists():
            return RuntimeConfig()
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return RuntimeConfig(
            provider=str(data.get("provider", "telegram")),
            provider_user_id=str(data.get("provider_user_id", "")),
            user_niche=str(data.get("user_niche", "")),
            posting_frequency=str(data.get("posting_frequency", "2/day")),
            content_language=str(data.get("content_language", "en")),
            brand_logo_url=str(data.get("brand_logo_url", "")),
            has_brand_document=bool(data.get("has_brand_document", False)),
            brand_document_path=str(data.get("brand_document_path", "")),
            use_trello=bool(data.get("use_trello", False)),
            use_notion=bool(data.get("use_notion", False)),
            timezone=str(data.get("timezone", "UTC")),
        )

    def save(self, config: RuntimeConfig) -> Path:
        payload = asdict(config)
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return self.path
