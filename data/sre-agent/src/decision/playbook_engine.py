"""
Playbook engine for parsing and executing playbooks.

Playbooks define remediation procedures as YAML files.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
import structlog

from src.config.constants import ActionType

logger = structlog.get_logger()


class PlaybookStep:
    """A single step in a playbook."""

    def __init__(
        self,
        name: str,
        action: ActionType,
        target: str,
        parameters: Optional[Dict[str, Any]] = None,
        condition: Optional[str] = None,
        timeout_seconds: int = 300,
        retry_count: int = 1,
        rollback_on_failure: bool = True,
    ):
        self.name = name
        self.action = action
        self.target = target
        self.parameters = parameters or {}
        self.condition = condition
        self.timeout_seconds = timeout_seconds
        self.retry_count = retry_count
        self.rollback_on_failure = rollback_on_failure


class Playbook:
    """A remediation playbook."""

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        trigger_conditions: List[str],
        steps: List[PlaybookStep],
        tags: Optional[List[str]] = None,
        risk_override: Optional[float] = None,
        enabled: bool = True,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.trigger_conditions = trigger_conditions
        self.steps = steps
        self.tags = tags or []
        self.risk_override = risk_override
        self.enabled = enabled


class PlaybookEngine:
    """
    Engine for loading and matching playbooks.

    Features:
    - YAML playbook loading
    - Condition matching
    - Step validation
    """

    def __init__(self, playbooks_dir: Optional[str] = None):
        self._playbooks: Dict[str, Playbook] = {}
        self._playbooks_dir = playbooks_dir or str(
            Path(__file__).parent.parent.parent / "config" / "playbooks"
        )
        self._load_playbooks()

    def _load_playbooks(self) -> None:
        """Load all playbooks from directory."""
        playbooks_path = Path(self._playbooks_dir)
        if not playbooks_path.exists():
            logger.warning("Playbooks directory not found", path=self._playbooks_dir)
            playbooks_path.mkdir(parents=True, exist_ok=True)
            return

        for yaml_file in playbooks_path.glob("*.yaml"):
            try:
                self._load_playbook_file(yaml_file)
            except Exception as e:
                logger.warning(
                    "Failed to load playbook",
                    file=str(yaml_file),
                    error=str(e),
                )

        logger.info("Loaded playbooks", count=len(self._playbooks))

    def _load_playbook_file(self, file_path: Path) -> None:
        """Load a single playbook file."""
        with open(file_path) as f:
            data = yaml.safe_load(f)

        if not data:
            return

        # Parse steps
        steps: List[PlaybookStep] = []
        for step_data in data.get("steps", []):
            action_str = step_data.get("action", "")
            try:
                action = ActionType(action_str)
            except ValueError:
                logger.warning(
                    "Unknown action type in playbook",
                    action=action_str,
                    file=str(file_path),
                )
                continue

            steps.append(
                PlaybookStep(
                    name=step_data.get("name", ""),
                    action=action,
                    target=step_data.get("target", ""),
                    parameters=step_data.get("parameters", {}),
                    condition=step_data.get("condition"),
                    timeout_seconds=step_data.get("timeout_seconds", 300),
                    retry_count=step_data.get("retry_count", 1),
                    rollback_on_failure=step_data.get("rollback_on_failure", True),
                )
            )

        playbook = Playbook(
            id=data.get("id", file_path.stem),
            name=data.get("name", file_path.stem),
            description=data.get("description", ""),
            trigger_conditions=data.get("trigger_conditions", []),
            steps=steps,
            tags=data.get("tags", []),
            risk_override=data.get("risk_override"),
            enabled=data.get("enabled", True),
        )

        self._playbooks[playbook.id] = playbook

    def get_playbook(self, playbook_id: str) -> Optional[Playbook]:
        """Get a playbook by ID."""
        return self._playbooks.get(playbook_id)

    def find_matching_playbooks(
        self,
        metric_name: str,
        anomaly_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Playbook]:
        """
        Find playbooks matching given conditions.

        Args:
            metric_name: Name of the affected metric
            anomaly_type: Type of anomaly
            tags: Tags to match

        Returns:
            List of matching playbooks
        """
        matching: List[Playbook] = []
        tags = tags or []

        for playbook in self._playbooks.values():
            if not playbook.enabled:
                continue

            # Check trigger conditions
            condition_match = False
            for condition in playbook.trigger_conditions:
                if metric_name in condition:
                    condition_match = True
                    break
                if anomaly_type and anomaly_type in condition:
                    condition_match = True
                    break

            # Check tag match
            tag_match = not tags or any(t in playbook.tags for t in tags)

            if condition_match or tag_match:
                matching.append(playbook)

        return matching

    def list_playbooks(self) -> List[Dict[str, Any]]:
        """List all available playbooks."""
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "trigger_conditions": p.trigger_conditions,
                "steps": len(p.steps),
                "tags": p.tags,
                "enabled": p.enabled,
            }
            for p in self._playbooks.values()
        ]

    def reload_playbooks(self) -> int:
        """Reload all playbooks."""
        self._playbooks.clear()
        self._load_playbooks()
        return len(self._playbooks)
