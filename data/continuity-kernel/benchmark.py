from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


BASELINE_SCHEMA_VERSION = "v1"
DETERMINISTIC_CONTRACT_VERSION = "v1"


@dataclass
class ContinuityRun:
    resumed_successfully: bool
    reprompted: bool
    off_goal_tool_call: bool
    duplicate_work: bool


@dataclass
class BaselineReport:
    schema_version: str
    generated_at: str
    total_runs: int
    resume_success_rate: float
    reprompt_rate: float
    off_goal_tool_call_rate: float
    duplicate_work_rate: float


class ContinuityBenchmarkHarness:
    """Phase-0 baseline benchmark harness (frozen v1 metrics)."""

    schema_version = BASELINE_SCHEMA_VERSION

    @staticmethod
    def _pct(numerator: int, denominator: int) -> float:
        if denominator == 0:
            return 0.0
        return round((numerator / denominator) * 100.0, 2)

    @staticmethod
    def _normalize_rate(value: float) -> float:
        try:
            numeric = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return 0.0

        if not numeric.is_finite():
            return 0.0

        clipped = min(max(numeric, Decimal("0")), Decimal("100"))
        return float(clipped.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @classmethod
    def deterministic_payload(cls, report: BaselineReport) -> dict[str, Any]:
        """Deterministic baseline payload (timestamp-free, normalized rates)."""

        return {
            "contract_version": DETERMINISTIC_CONTRACT_VERSION,
            "schema_version": report.schema_version,
            "total_runs": int(report.total_runs),
            "resume_success_rate": cls._normalize_rate(report.resume_success_rate),
            "reprompt_rate": cls._normalize_rate(report.reprompt_rate),
            "off_goal_tool_call_rate": cls._normalize_rate(report.off_goal_tool_call_rate),
            "duplicate_work_rate": cls._normalize_rate(report.duplicate_work_rate),
        }

    @classmethod
    def format_report_deterministic(cls, report: BaselineReport) -> str:
        """Deterministic formatter for stable snapshots/diffs.

        - Excludes dynamic timestamps (`generated_at`)
        - Normalizes/clamps rate values with decimal quantization
        - Uses canonical JSON formatting for stable hashes
        """

        payload = cls.deterministic_payload(report)
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

    @classmethod
    def deterministic_hash(cls, report: BaselineReport) -> str:
        encoded = cls.format_report_deterministic(report).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def evaluate(self, runs: Iterable[ContinuityRun]) -> BaselineReport:
        seq = list(runs)
        total = len(seq)
        resume_success = sum(1 for r in seq if r.resumed_successfully)
        reprompt = sum(1 for r in seq if r.reprompted)
        off_goal = sum(1 for r in seq if r.off_goal_tool_call)
        duplicate = sum(1 for r in seq if r.duplicate_work)

        return BaselineReport(
            schema_version=self.schema_version,
            generated_at=datetime.now(timezone.utc).isoformat(),
            total_runs=total,
            resume_success_rate=self._pct(resume_success, total),
            reprompt_rate=self._pct(reprompt, total),
            off_goal_tool_call_rate=self._pct(off_goal, total),
            duplicate_work_rate=self._pct(duplicate, total),
        )

    @classmethod
    def compare_trends_stub(cls, previous: BaselineReport, current: BaselineReport) -> dict[str, Any]:
        """Trend comparator stub for upcoming replay-fed trend analysis.

        Emits deterministic hash anchors so downstream tooling can verify that
        comparisons were computed from canonical snapshots.
        """

        prev_payload = cls.deterministic_payload(previous)
        cur_payload = cls.deterministic_payload(current)

        def delta(key: str) -> float:
            return round(float(cur_payload[key]) - float(prev_payload[key]), 2)

        return {
            "schema_version": BASELINE_SCHEMA_VERSION,
            "deterministic_contract_version": DETERMINISTIC_CONTRACT_VERSION,
            "status": "stub",
            "message": "Trend comparator stub: wire replay-series evaluator in next slice.",
            "previous_hash": cls.deterministic_hash(previous),
            "current_hash": cls.deterministic_hash(current),
            "deltas": {
                "resume_success_rate": delta("resume_success_rate"),
                "reprompt_rate": delta("reprompt_rate"),
                "off_goal_tool_call_rate": delta("off_goal_tool_call_rate"),
                "duplicate_work_rate": delta("duplicate_work_rate"),
            },
        }

    def write_report(self, report: BaselineReport, output_path: str | Path) -> str:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2) + "\n")
        return str(path)
