"""
Strategy planner: selects multi-step search strategies based on intent
and depth. Maps intent categories to optimal SearXNG engines and builds
ordered search step plans.
"""

from __future__ import annotations
from .models import (
    SearchIntent, SearchStrategy, SearchStep, DorkQuery, Depth, IntentCategory
)
from .config import INTENT_ENGINE_MAP, STRATEGY_DEFINITIONS
from .dorks import DorkGenerator


class StrategyPlanner:
    """Build multi-step search strategies from parsed intents."""

    def __init__(self):
        self.dork_gen = DorkGenerator()

    def plan(self, intent: SearchIntent) -> SearchStrategy:
        """Create an optimal search strategy for the given intent."""
        depth = intent.depth
        category = intent.category.value

        # Select strategy type based on depth and category
        strategy_name = self._select_strategy_type(intent)
        strategy_def = STRATEGY_DEFINITIONS[strategy_name]

        # Generate all candidate dork queries
        all_dorks = self.dork_gen.generate(intent)

        # Get engine routing
        routing = INTENT_ENGINE_MAP.get(category, INTENT_ENGINE_MAP["general"])
        engines = routing["engines"]
        categories = routing["categories"]
        fallback_engines = routing.get("fallback_engines", [])

        # Limit dorks based on strategy
        max_queries = strategy_def["max_queries_per_step"] * strategy_def["max_steps"]
        dorks = all_dorks[:max_queries]

        # Build steps
        steps = self._build_steps(
            dorks=dorks,
            engines=engines,
            categories=categories,
            fallback_engines=fallback_engines,
            strategy_def=strategy_def,
            intent=intent,
        )

        return SearchStrategy(
            name=strategy_name,
            steps=steps,
            description=strategy_def["description"],
        )

    def select_engines(self, intent: SearchIntent) -> list[str]:
        """Get the best engines for this intent category."""
        routing = INTENT_ENGINE_MAP.get(
            intent.category.value, INTENT_ENGINE_MAP["general"]
        )
        return routing["engines"]

    def _select_strategy_type(self, intent: SearchIntent) -> str:
        """Choose the right strategy type based on intent + depth."""
        depth = intent.depth
        category = intent.category

        if depth == Depth.QUICK:
            return "quick"

        if depth == Depth.EXHAUSTIVE:
            if category == IntentCategory.OSINT:
                return "osint_chain"
            if category == IntentCategory.SECURITY:
                return "deep_dive"
            return "deep_dive"

        if depth == Depth.DEEP:
            if category in (IntentCategory.OSINT, IntentCategory.SECURITY):
                return "deep_dive"
            if category == IntentCategory.FILES:
                return "file_hunt"
            if category == IntentCategory.NEWS:
                return "temporal"
            return "multi_angle"

        # STANDARD depth
        if category == IntentCategory.OSINT:
            return "broad_to_narrow"
        if category == IntentCategory.SECURITY:
            return "multi_angle"
        if category == IntentCategory.NEWS:
            return "temporal"
        if category == IntentCategory.ACADEMIC:
            return "multi_angle"
        return "broad_to_narrow"

    def _build_steps(
        self,
        dorks: list[DorkQuery],
        engines: list[str],
        categories: list[str],
        fallback_engines: list[str],
        strategy_def: dict,
        intent: SearchIntent,
    ) -> list[SearchStep]:
        """Distribute dork queries across search steps."""
        max_steps = strategy_def["max_steps"]
        max_per_step = strategy_def["max_queries_per_step"]
        engines_per_step = strategy_def["engines_per_step"]

        steps: list[SearchStep] = []

        if not dorks:
            # Fallback: single step with keyword query
            keyword = " ".join(intent.keywords) if intent.keywords else "search"
            steps.append(SearchStep(
                queries=[DorkQuery(query=keyword, purpose="Fallback keyword search")],
                engines=engines[:engines_per_step],
                categories=categories,
                time_range=intent.time_range,
                description="Fallback search",
            ))
            return steps

        # Strategy-specific step building
        strategy_name = self._select_strategy_type(intent)

        if strategy_name == "quick":
            steps.append(SearchStep(
                queries=dorks[:2],
                engines=engines[:engines_per_step],
                categories=categories,
                time_range=intent.time_range,
                description="Quick search — best engines, top queries",
            ))

        elif strategy_name == "broad_to_narrow":
            # Step 1: Broad queries
            broad = [d for d in dorks if len(d.operators_used) <= 1][:max_per_step]
            if not broad:
                broad = dorks[:max_per_step]
            steps.append(SearchStep(
                queries=broad,
                engines=engines[:engines_per_step],
                categories=categories,
                time_range=intent.time_range,
                description="Broad initial search",
            ))
            # Step 2: Narrow queries with operators
            narrow = [d for d in dorks if len(d.operators_used) > 1][:max_per_step]
            if narrow:
                steps.append(SearchStep(
                    queries=narrow,
                    engines=engines[:engines_per_step],
                    categories=categories,
                    time_range=intent.time_range,
                    description="Narrowed search with operators",
                ))
            # Step 3: Fallback engines if available
            remaining = [d for d in dorks if d not in broad and d not in narrow]
            if remaining and fallback_engines:
                steps.append(SearchStep(
                    queries=remaining[:max_per_step],
                    engines=fallback_engines[:engines_per_step],
                    categories=categories,
                    time_range=intent.time_range,
                    description="Fallback engines — additional coverage",
                ))

        elif strategy_name == "multi_angle":
            # Split dorks into groups by operator type
            chunks = self._chunk_list(dorks, max_per_step)
            for i, chunk in enumerate(chunks[:max_steps]):
                eng = engines if i == 0 else (fallback_engines or engines)
                steps.append(SearchStep(
                    queries=chunk,
                    engines=eng[:engines_per_step],
                    categories=categories,
                    time_range=intent.time_range,
                    description=f"Search angle {i+1}",
                ))

        elif strategy_name in ("deep_dive", "osint_chain"):
            chunks = self._chunk_list(dorks, max_per_step)
            all_engines = engines + [e for e in fallback_engines if e not in engines]
            for i, chunk in enumerate(chunks[:max_steps]):
                # Rotate through engines
                start = (i * engines_per_step) % len(all_engines)
                step_engines = (all_engines * 2)[start:start + engines_per_step]
                steps.append(SearchStep(
                    queries=chunk,
                    engines=step_engines,
                    categories=categories,
                    time_range=intent.time_range,
                    description=f"Deep dive step {i+1}",
                ))

        elif strategy_name == "file_hunt":
            # All file-related dorks
            steps.append(SearchStep(
                queries=dorks[:max_per_step],
                engines=engines[:engines_per_step],
                categories=categories + ["files"],
                time_range="",
                description="Primary file search",
            ))
            if len(dorks) > max_per_step:
                steps.append(SearchStep(
                    queries=dorks[max_per_step:max_per_step*2],
                    engines=(fallback_engines or engines)[:engines_per_step],
                    categories=categories + ["files"],
                    time_range="",
                    description="Extended file search",
                ))

        elif strategy_name == "temporal":
            time_ranges = ["day", "week", "month", "year"]
            base_dorks = dorks[:max_per_step]
            for tr in time_ranges[:max_steps]:
                steps.append(SearchStep(
                    queries=base_dorks,
                    engines=engines[:engines_per_step],
                    categories=categories,
                    time_range=tr,
                    description=f"Temporal search — past {tr}",
                ))

        elif strategy_name == "verify":
            chunks = self._chunk_list(dorks, max_per_step)
            all_engines = engines + fallback_engines
            for i, chunk in enumerate(chunks[:max_steps]):
                step_engines = all_engines[i*2:(i*2)+engines_per_step] or engines[:engines_per_step]
                steps.append(SearchStep(
                    queries=chunk,
                    engines=step_engines,
                    categories=categories,
                    time_range=intent.time_range,
                    description=f"Verification step {i+1} — cross-reference",
                ))

        else:
            # Default
            steps.append(SearchStep(
                queries=dorks[:max_per_step],
                engines=engines[:engines_per_step],
                categories=categories,
                time_range=intent.time_range,
                description="Default search",
            ))

        return steps

    @staticmethod
    def _chunk_list(lst: list, size: int) -> list[list]:
        return [lst[i:i+size] for i in range(0, len(lst), size)]