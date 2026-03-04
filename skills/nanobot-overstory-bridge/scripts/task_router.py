#!/usr/bin/env python3
"""
Task routing from nanobot to overstory.
Classifies tasks, maps to overstory capabilities, and translates formats.
"""

import json
import logging
import os
import re
import sys
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=os.environ.get("BRIDGE_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("task_router")


CAPABILITY_PATTERNS: List[Dict[str, Any]] = [
    {
        "capability": "researcher",
        "patterns": [
            r"\bresearch\b", r"\btrend", r"\banalyz", r"\banalys",
            r"\bstudy\b", r"\binvestigat", r"\bcompare\b", r"\bsurvey\b",
            r"\bpaper", r"\bdata\s+(?:analysis|mining)", r"\binsight",
        ],
        "priority": 10,
    },
    {
        "capability": "social-media-manager",
        "patterns": [
            r"\btweet", r"\bpost(?:ing)?\b", r"\bsocial\s*media",
            r"\btwitter\b", r"\bx\.com\b", r"\binstagram\b",
            r"\blinkedin\b", r"\bschedul.*post", r"\bthread\b",
        ],
        "priority": 10,
    },
    {
        "capability": "blogger",
        "patterns": [
            r"\bblog\b", r"\barticle\b", r"\bcontent\b", r"\bwrite.*post",
            r"\bpublish\b", r"\beditor", r"\bcopywriting", r"\bessay\b",
            r"\bnewsletter\b",
        ],
        "priority": 8,
    },
    {
        "capability": "builder",
        "patterns": [
            r"\bcode\b", r"\bbuild\b", r"\bimplement", r"\bfix\b",
            r"\brefactor", r"\bdebug\b", r"\bdeploy\b", r"\btest\b",
            r"\bapi\b", r"\bscript\b", r"\bfeature\b", r"\bbug\b",
            r"\bpull\s*request", r"\bpr\b", r"\bcreate.*(?:app|service|endpoint)",
        ],
        "priority": 5,
    },
    {
        "capability": "scout",
        "patterns": [
            r"\bexplore\b", r"\bfind\b", r"\bsearch\b", r"\bdiscover",
            r"\blook\s*(?:up|for|into)", r"\bscan\b", r"\bcheck\s+(?:if|whether)",
            r"\blist\b.*(?:files|repos|projects)",
        ],
        "priority": 6,
    },
    {
        "capability": "scribe",
        "patterns": [
            r"\blog\b", r"\bmemory\b", r"\bnote", r"\bdocument",
            r"\brecord\b", r"\bsummar", r"\btranscri", r"\bjournal",
            r"\bminutes\b", r"\bchangelog\b",
        ],
        "priority": 7,
    },
    {
        "capability": "reviewer",
        "patterns": [
            r"\breview\b", r"\bmerge\b", r"\baudit\b", r"\bapprove\b",
            r"\bcode\s*review", r"\bpr\s*review", r"\bfeedback\b",
        ],
        "priority": 9,
    },
]


@dataclass
class RoutedTask:
    task_id: str
    capability: str
    name: str
    description: str
    confidence: float
    original_task: str
    context: Optional[Dict[str, Any]] = field(default_factory=dict)


class TaskRouter:
    """Routes nanobot tasks to the appropriate overstory capability."""

    def __init__(self, overstory_client=None):
        self.client = overstory_client
        self.patterns = CAPABILITY_PATTERNS

    def determine_capability(self, task: str) -> Dict[str, Any]:
        """Map a task description to an overstory capability using pattern matching."""
        task_lower = task.lower()
        scores: Dict[str, float] = {}

        for entry in self.patterns:
            cap = entry["capability"]
            priority = entry["priority"]
            match_count = 0
            for pattern in entry["patterns"]:
                if re.search(pattern, task_lower):
                    match_count += 1
            if match_count > 0:
                scores[cap] = match_count * priority

        if not scores:
            return {"capability": "builder", "confidence": 0.3}

        best = max(scores, key=scores.get)
        total = sum(scores.values())
        confidence = min(scores[best] / max(total, 1), 1.0)

        return {"capability": best, "confidence": round(confidence, 3)}

    def translate_to_overstory(self, nanobot_task: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a nanobot task format to overstory sling parameters."""
        description = nanobot_task.get("description", nanobot_task.get("task", ""))
        cap_info = self.determine_capability(description)

        task_id = nanobot_task.get("id", str(uuid.uuid4())[:8])
        capability = nanobot_task.get("capability_override", cap_info["capability"])
        name = nanobot_task.get("name", f"{capability}-{task_id}")

        return {
            "task_id": task_id,
            "capability": capability,
            "name": name,
            "description": description,
            "confidence": cap_info["confidence"],
        }

    def translate_from_overstory(self, overstory_result: Dict[str, Any]) -> Dict[str, Any]:
        """Convert overstory results back to nanobot format."""
        return {
            "status": overstory_result.get("status", "unknown"),
            "agent_name": overstory_result.get("name", overstory_result.get("agent")),
            "output": overstory_result.get("output", overstory_result.get("raw", "")),
            "error": overstory_result.get("error"),
            "metadata": {
                k: v for k, v in overstory_result.items()
                if k not in ("status", "name", "agent", "output", "raw", "error")
            },
        }

    def route_task(
        self, task_description: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Full routing pipeline: classify, translate, and optionally spawn.
        Returns a RoutedTask as a dict.
        """
        nanobot_task = {
            "description": task_description,
            "id": str(uuid.uuid4())[:8],
            "context": context or {},
        }

        overstory_params = self.translate_to_overstory(nanobot_task)

        routed = RoutedTask(
            task_id=overstory_params["task_id"],
            capability=overstory_params["capability"],
            name=overstory_params["name"],
            description=task_description,
            confidence=overstory_params["confidence"],
            original_task=task_description,
            context=context or {},
        )

        result = asdict(routed)

        if self.client:
            try:
                worker_caps = {"builder", "scout", "reviewer"}
                if routed.capability in worker_caps:
                    # Coordinator can only spawn "lead" directly; spawn lead first, then worker with --parent
                    lead_name = f"lead-{routed.task_id[:8]}"
                    self.client.sling(
                        task_id=routed.task_id,
                        capability="lead",
                        name=lead_name,
                        description=routed.description,
                    )
                    time.sleep(1)  # give overstory a moment to register the lead
                    spawn_result = self.client.sling(
                        task_id=routed.task_id,
                        capability=routed.capability,
                        name=routed.name,
                        description=routed.description,
                        parent=lead_name,
                    )
                else:
                    spawn_result = self.client.sling(
                        task_id=routed.task_id,
                        capability=routed.capability,
                        name=routed.name,
                        description=routed.description,
                    )
                result["spawn_result"] = spawn_result
                result["spawned"] = True
                log.info("Spawned agent %s via overstory", routed.name)
            except Exception as exc:
                result["spawn_error"] = str(exc)
                result["spawned"] = False
                log.error("Failed to spawn agent: %s", exc)
        else:
            result["spawned"] = False
            result["spawn_note"] = "No overstory client provided; dry-run only"

        return result


# ── CLI interface ───────────────────────────────────────────────

def _cli():
    import argparse

    parser = argparse.ArgumentParser(
        description="Route nanobot tasks to overstory capabilities",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_route = sub.add_parser("route", help="Route a task to overstory")
    p_route.add_argument("--task", required=True, help="Task description")
    p_route.add_argument("--context", default=None, help="JSON context string")
    p_route.add_argument("--json", action="store_true", help="JSON output")
    p_route.add_argument("--spawn", action="store_true", help="Actually spawn via overstory")

    p_classify = sub.add_parser("classify", help="Classify task capability only")
    p_classify.add_argument("--task", required=True)
    p_classify.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "route":
        ctx = json.loads(args.context) if args.context else None
        client = None
        if args.spawn:
            from overstory_client import OverstoryClient
            client = OverstoryClient()
        router = TaskRouter(overstory_client=client)
        result = router.route_task(args.task, context=ctx)
        print(json.dumps(result, indent=2))

    elif args.command == "classify":
        router = TaskRouter()
        result = router.determine_capability(args.task)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _cli()
