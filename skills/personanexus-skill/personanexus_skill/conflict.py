"""Conflict resolution strategies for identity inheritance and mixin composition."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from personanexus_skill.types import (
    ConflictResolution,
    ListConflictStrategy,
    NumericConflictStrategy,
    ObjectConflictStrategy,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Merge tracing
# ---------------------------------------------------------------------------


@dataclass
class MergeTraceEntry:
    """Record of a single merge operation."""

    field_path: str
    source: str  # "archetype", "mixin:<name>", "own", "override", "default"
    strategy: str  # "last_wins", "highest", "lowest", "average", "deep_merge", etc.
    base_value: Any
    override_value: Any
    result_value: Any


@dataclass
class MergeTrace:
    """Complete trace of all merge operations during resolution."""

    entries: list[MergeTraceEntry] = field(default_factory=list)

    def add(
        self,
        field_path: str,
        source: str,
        strategy: str,
        base_value: Any,
        override_value: Any,
        result_value: Any,
    ) -> None:
        self.entries.append(
            MergeTraceEntry(
                field_path=field_path,
                source=source,
                strategy=strategy,
                base_value=base_value,
                override_value=override_value,
                result_value=result_value,
            )
        )

    def get_source(self, field_path: str) -> str | None:
        """Get the source of a specific field (last entry wins)."""
        for entry in reversed(self.entries):
            if entry.field_path == field_path:
                return entry.source
        return None

    def summary(self) -> dict[str, list[str]]:
        """Group fields by their source."""
        by_source: dict[str, list[str]] = {}
        for entry in self.entries:
            by_source.setdefault(entry.source, []).append(entry.field_path)
        return by_source

    def format_text(self) -> str:
        """Format trace as human-readable text."""
        if not self.entries:
            return "No merge operations recorded."

        lines: list[str] = []
        lines.append("Merge Trace")
        lines.append("=" * 60)

        # Summary section: group fields by source
        by_source = self.summary()
        lines.append("")
        lines.append("Fields by source:")
        for source, fields in by_source.items():
            unique_fields = sorted(set(fields))
            lines.append(f"  [{source}]")
            for f in unique_fields:
                lines.append(f"    - {f}")

        # Detailed operations
        lines.append("")
        lines.append("Detailed operations:")
        lines.append("-" * 60)
        for entry in self.entries:
            lines.append(f"  {entry.field_path}  src={entry.source}  strategy={entry.strategy}")
            lines.append(f"    base={_truncate_repr(entry.base_value)}")
            lines.append(f"    override={_truncate_repr(entry.override_value)}")
            lines.append(f"    result={_truncate_repr(entry.result_value)}")

        return "\n".join(lines)


def _truncate_repr(value: Any, max_len: int = 80) -> str:
    """Return a truncated repr of a value for trace display."""
    r = repr(value)
    if len(r) > max_len:
        return r[: max_len - 3] + "..."
    return r


class ConflictResolver:
    """Resolves conflicts when merging identity specs during inheritance/mixin composition."""

    def __init__(self, config: ConflictResolution | None = None):
        self.config = config or ConflictResolution()

    def merge(
        self,
        base: dict[str, Any],
        override: dict[str, Any],
        path: str = "",
        *,
        trace: MergeTrace | None = None,
        source: str = "",
    ) -> dict[str, Any]:
        """Deep-merge override into base using configured conflict resolution strategies.

        When *trace* is provided, each merge operation is recorded into it.
        *source* labels where the override came from (e.g. "archetype", "mixin:safety").
        """
        result = dict(base)

        for key, override_val in override.items():
            current_path = f"{path}.{key}" if path else key
            base_val = base.get(key)

            # Check for explicit per-field strategy
            explicit = self._get_explicit_strategy(current_path)

            if base_val is None:
                result[key] = override_val
                if trace is not None:
                    trace.add(current_path, source, "new_field", None, override_val, override_val)
            elif explicit:
                result[key] = self._apply_explicit(
                    base_val,
                    override_val,
                    explicit,
                    current_path,
                    trace=trace,
                    source=source,
                )
            elif isinstance(base_val, dict) and isinstance(override_val, dict):
                result[key] = self._merge_objects(
                    base_val,
                    override_val,
                    current_path,
                    trace=trace,
                    source=source,
                )
            elif isinstance(base_val, list) and isinstance(override_val, list):
                result[key] = self._merge_lists(
                    base_val,
                    override_val,
                    current_path,
                    trace=trace,
                    source=source,
                )
            elif isinstance(base_val, (int, float)) and isinstance(override_val, (int, float)):
                result[key] = self._merge_numeric(
                    base_val,
                    override_val,
                    current_path,
                    trace=trace,
                    source=source,
                )
            else:
                # String or other primitives: last wins
                result[key] = override_val
                if trace is not None:
                    trace.add(
                        current_path,
                        source,
                        "last_wins",
                        base_val,
                        override_val,
                        override_val,
                    )

        return result

    def _merge_numeric(
        self,
        base: float,
        override: float,
        path: str,
        *,
        trace: MergeTrace | None = None,
        source: str = "",
    ) -> float:
        strategy = self.config.numeric_traits
        if strategy == NumericConflictStrategy.LAST_WINS:
            result = override
        elif strategy == NumericConflictStrategy.HIGHEST:
            result = max(base, override)
        elif strategy == NumericConflictStrategy.LOWEST:
            result = min(base, override)
        elif strategy == NumericConflictStrategy.AVERAGE:
            result = (base + override) / 2
        else:
            result = override

        if trace is not None:
            trace.add(path, source, strategy.value, base, override, result)
        return result

    def _merge_lists(
        self,
        base: list[Any],
        override: list[Any],
        path: str,
        *,
        trace: MergeTrace | None = None,
        source: str = "",
    ) -> list[Any]:
        # Check for _merge_strategy in override (if it's a list of dicts with this key)
        strategy = self.config.list_fields

        # Special case: lists of dicts with 'id' keys get merged by id (override wins)
        # This applies to guardrails.hard, principles, expertise.domains, etc.
        if self._is_id_keyed_list(base, override):
            result = self._union_by_id(base, override)
            if trace is not None:
                trace.add(path, source, "union_by_id", base, override, result)
            return result

        # Warn if the list is partially id-keyed (some dicts have 'id', some don't),
        # as this likely indicates a data error rather than intentional design.
        all_items = base + override
        if all_items:
            dicts_with_id = sum(1 for item in all_items if isinstance(item, dict) and "id" in item)
            if 0 < dicts_with_id < len(all_items):
                logger.warning(
                    "List at '%s' is partially id-keyed (%d/%d items have 'id'). "
                    "Union-by-id merge was skipped; falling back to %s strategy.",
                    path,
                    dicts_with_id,
                    len(all_items),
                    strategy.value,
                )

        if strategy == ListConflictStrategy.REPLACE:
            result = override
        elif strategy == ListConflictStrategy.APPEND:
            result = base + override
        elif strategy == ListConflictStrategy.UNIQUE_APPEND:
            seen = set()
            result = []
            for item in base + override:
                key = self._list_item_key(item)
                if key not in seen:
                    seen.add(key)
                    result.append(item)
        else:
            result = override

        if trace is not None:
            trace.add(path, source, strategy.value, base, override, result)
        return result

    def _merge_objects(
        self,
        base: dict[str, Any],
        override: dict[str, Any],
        path: str,
        *,
        trace: MergeTrace | None = None,
        source: str = "",
    ) -> dict[str, Any]:
        strategy = self.config.object_fields
        if strategy == ObjectConflictStrategy.REPLACE:
            if trace is not None:
                trace.add(path, source, "replace", base, override, override)
            return override
        # deep_merge is the default — recurse into merge which will trace individual fields
        return self.merge(base, override, path, trace=trace, source=source)

    def _get_explicit_strategy(self, path: str) -> str | None:
        for resolution in self.config.explicit_resolutions:
            if resolution.field == path:
                return resolution.strategy
        return None

    def _apply_explicit(
        self,
        base: Any,
        override: Any,
        strategy: str,
        path: str = "",
        *,
        trace: MergeTrace | None = None,
        source: str = "",
    ) -> Any:
        if strategy == "union" and isinstance(base, list) and isinstance(override, list):
            result = self._union_by_id(base, override)
            if trace is not None:
                trace.add(path, source, "explicit:union", base, override, result)
            return result
        if (
            strategy == "highest"
            and isinstance(base, (int, float))
            and isinstance(override, (int, float))
        ):
            result = max(base, override)
            if trace is not None:
                trace.add(path, source, "explicit:highest", base, override, result)
            return result
        if (
            strategy == "lowest"
            and isinstance(base, (int, float))
            and isinstance(override, (int, float))
        ):
            result = min(base, override)
            if trace is not None:
                trace.add(path, source, "explicit:lowest", base, override, result)
            return result
        if (
            strategy == "average"
            and isinstance(base, (int, float))
            and isinstance(override, (int, float))
        ):
            result = (base + override) / 2
            if trace is not None:
                trace.add(path, source, "explicit:average", base, override, result)
            return result
        # Default: last wins
        if trace is not None:
            trace.add(path, source, "explicit:last_wins", base, override, override)
        return override

    def _is_id_keyed_list(self, base: list[Any], override: list[Any]) -> bool:
        """Check if both lists contain dicts with 'id' fields."""
        all_items = base + override
        if not all_items:
            return False
        return all(isinstance(item, dict) and "id" in item for item in all_items)

    def _union_by_id(self, base: list[Any], override: list[Any]) -> list[Any]:
        """Merge lists of dicts by 'id' field. Override wins for matching ids."""
        result_map: dict[str, Any] = {}
        for item in base:
            item_id = item.get("id") if isinstance(item, dict) else str(item)
            result_map[str(item_id)] = item
        for item in override:
            item_id = item.get("id") if isinstance(item, dict) else str(item)
            result_map[str(item_id)] = item  # override wins
        return list(result_map.values())

    def _list_item_key(self, item: Any) -> str:
        """Create a hashable key for list deduplication."""
        if isinstance(item, dict):
            return str(item.get("id", item))
        return str(item)
