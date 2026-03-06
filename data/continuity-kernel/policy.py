from __future__ import annotations

from dataclasses import dataclass


DEFAULT_FIELD_ORDER = (
    "mission",
    "definition_of_done",
    "role",
    "persona",
    "mission_constraints",
    "user_profile",
    "soul_constraints",
    "preferences",
)

DEFAULT_SCHEMA_VERSION = "v1"
DEFAULT_TOKEN_BUDGET = 220
MIN_TOKEN_BUDGET = 16
MAX_TOKEN_BUDGET = 4096

SELECTOR_MODE_DETERMINISTIC = "deterministic"
SELECTOR_MODE_DUAL_ROUTE_EXPERIMENTAL = "dual_route_experimental"
SUPPORTED_SELECTOR_MODES = frozenset(
    {
        SELECTOR_MODE_DETERMINISTIC,
        SELECTOR_MODE_DUAL_ROUTE_EXPERIMENTAL,
    }
)

COMPACTION_POLICY_SIZE_ONLY = "size_only"
COMPACTION_POLICY_ATTENTION_PRESERVING_EXPERIMENTAL = "attention_preserving_experimental"
SUPPORTED_COMPACTION_POLICIES = frozenset(
    {
        COMPACTION_POLICY_SIZE_ONLY,
        COMPACTION_POLICY_ATTENTION_PRESERVING_EXPERIMENTAL,
    }
)


@dataclass(frozen=True)
class InjectionPolicy:
    schema_version: str = DEFAULT_SCHEMA_VERSION
    token_budget: int = DEFAULT_TOKEN_BUDGET
    field_order: tuple[str, ...] = DEFAULT_FIELD_ORDER
    selector_mode: str = SELECTOR_MODE_DETERMINISTIC
    compaction_policy: str = COMPACTION_POLICY_SIZE_ONLY


def clamp_token_budget(token_budget: int) -> tuple[int, str | None]:
    try:
        parsed = int(token_budget)
    except Exception:
        return DEFAULT_TOKEN_BUDGET, "invalid_type"

    if parsed < MIN_TOKEN_BUDGET:
        return MIN_TOKEN_BUDGET, "clamped_low"

    if parsed > MAX_TOKEN_BUDGET:
        return MAX_TOKEN_BUDGET, "clamped_high"

    return parsed, None


def normalize_selector_mode(selector_mode: str) -> tuple[str, str | None]:
    if not isinstance(selector_mode, str) or not selector_mode:
        return SELECTOR_MODE_DETERMINISTIC, "invalid_type"

    if selector_mode in SUPPORTED_SELECTOR_MODES:
        return selector_mode, None

    return SELECTOR_MODE_DETERMINISTIC, "unsupported"


def normalize_compaction_policy(compaction_policy: str) -> tuple[str, str | None]:
    if not isinstance(compaction_policy, str) or not compaction_policy:
        return COMPACTION_POLICY_SIZE_ONLY, "invalid_type"

    if compaction_policy in SUPPORTED_COMPACTION_POLICIES:
        return compaction_policy, None

    return COMPACTION_POLICY_SIZE_ONLY, "unsupported"
