"""
Main orchestrator: the SearchSkill class that ties together intent parsing,
dork generation, strategy planning, SearXNG searching, result analysis,
and query refinement into a single clean interface for AI agents.
"""

from __future__ import annotations
import time
import logging
from typing import Any
from .models import (
    SearchIntent, SearchReport, SearchResult, SearchStrategy,
    DorkQuery, Depth
)
from .client import SearXNGClient
from .intent import IntentParser
from .dorks import DorkGenerator
from .strategies import StrategyPlanner
from .analyzer import ResultAnalyzer

logger = logging.getLogger(__name__)


class SearchSkill:
    """
    Advanced AI-powered search skill using SearXNG.

    Provides intelligent search with:
    - Natural language intent parsing
    - Multi-engine dork generation (Google, Bing, Yandex, etc.)
    - Adaptive multi-step search strategies
    - Result scoring, deduplication, and analysis
    - Automatic query refinement
    - Zero API keys — all searches flow through your SearXNG instance

    Usage:
        skill = SearchSkill(searxng_url="http://localhost:8888")
        report = skill.search("find exposed .env files on example.com")
        print(report.to_context())
    """

    def __init__(
        self,
        searxng_url: str = "http://localhost:8888",
        timeout: float = 30.0,
        max_retries: int = 2,
        rate_limit: float = 0.5,
        verify_ssl: bool = True,
        auto_refine: bool = True,
        max_refine_rounds: int = 1,
    ):
        self.client = SearXNGClient(
            base_url=searxng_url,
            timeout=timeout,
            max_retries=max_retries,
            rate_limit_delay=rate_limit,
            verify_ssl=verify_ssl,
        )
        self.intent_parser = IntentParser()
        self.dork_generator = DorkGenerator()
        self.strategy_planner = StrategyPlanner()
        self.analyzer = ResultAnalyzer()
        self.auto_refine = auto_refine
        self.max_refine_rounds = max_refine_rounds

    # ─── Main search interface ────────────────────────────────────────────

    def search(
        self,
        query: str,
        depth: str | Depth = Depth.STANDARD,
        engines: list[str] | None = None,
        categories: list[str] | None = None,
        language: str = "auto",
        time_range: str = "",
        max_results: int = 50,
    ) -> SearchReport:
        """
        Execute an intelligent search from a natural language query.

        Args:
            query: Natural language search query
            depth: "quick", "standard", "deep", or "exhaustive"
            engines: Override engine selection (optional)
            categories: Override category selection (optional)
            language: Language code or "auto"
            time_range: "day", "week", "month", "year", or ""
            max_results: Maximum results to return

        Returns:
            SearchReport with scored, deduplicated results and metadata
        """
        start_time = time.time()

        # 1. Parse intent
        if isinstance(depth, str):
            depth = Depth(depth)
        intent = self.intent_parser.parse(query, depth)

        if time_range:
            intent.time_range = time_range

        logger.info(
            f"Intent: {intent.category.value}/{intent.subcategory} "
            f"(confidence={intent.confidence:.2f}) — entities: {intent.entities}"
        )

        # 2. Plan strategy
        strategy = self.strategy_planner.plan(intent)
        logger.info(f"Strategy: {strategy.name} — {len(strategy.steps)} steps")

        # 3. Execute search steps
        all_results: list[SearchResult] = []
        all_suggestions: list[str] = []
        engines_used: set[str] = set()
        errors: list[str] = []

        for step_idx, step in enumerate(strategy.steps):
            logger.debug(f"Executing step {step_idx+1}: {step.description}")

            # Override engines/categories if provided
            step_engines = engines or step.engines
            step_categories = categories or step.categories
            step_time = step.time_range or intent.time_range

            for dork in step.queries:
                try:
                    raw = self.client.search(
                        query=dork.query,
                        engines=step_engines,
                        categories=step_categories,
                        language=language,
                        time_range=step_time,
                    )

                    results = self.client.parse_results(raw)
                    all_results.extend(results)

                    suggestions = self.client.get_suggestions(raw)
                    all_suggestions.extend(suggestions)

                    unresponsive = self.client.get_unresponsive(raw)
                    if unresponsive:
                        logger.debug(f"Unresponsive engines: {unresponsive}")

                    # Track which engines actually returned results
                    for r in results:
                        engines_used.update(r.engines)

                    if raw.get("_error"):
                        errors.append(f"Query '{dork.query}': {raw['_error']}")

                except Exception as e:
                    logger.error(f"Error executing dork '{dork.query}': {e}")
                    errors.append(f"Query '{dork.query}': {str(e)}")

        # 4. Analyze results
        analyzed = self.analyzer.analyze(all_results, intent)

        # 5. Auto-refine if enabled and results are poor
        refined_queries: list[str] = []
        if self.auto_refine and len(analyzed) < 5:
            for _ in range(self.max_refine_rounds):
                refinements = self.analyzer.generate_refinements(analyzed, intent)
                refined_queries.extend(refinements)

                if refinements:
                    logger.info(f"Refining with {len(refinements)} new queries")
                    for ref_query in refinements[:3]:  # Limit refinement queries
                        try:
                            raw = self.client.search(
                                query=ref_query,
                                engines=engines or strategy.steps[0].engines if strategy.steps else None,
                                categories=categories or (strategy.steps[0].categories if strategy.steps else None),
                                language=language,
                            )
                            new_results = self.client.parse_results(raw)
                            all_results.extend(new_results)
                        except Exception as e:
                            logger.debug(f"Refinement query failed: {e}")

                    # Re-analyze with new results
                    analyzed = self.analyzer.analyze(all_results, intent)

                if len(analyzed) >= 5:
                    break

        # 6. Trim to max_results
        analyzed = analyzed[:max_results]

        # 7. Build report
        elapsed = time.time() - start_time
        total_found = len(all_results)  # before dedup

        # Merge SearXNG suggestions with analyzer refinements
        all_suggestions = list(dict.fromkeys(all_suggestions + refined_queries))

        report = SearchReport(
            query=query,
            intent=intent,
            strategy=strategy,
            results=analyzed,
            total_found=total_found,
            suggestions=all_suggestions[:10],
            refined_queries=refined_queries,
            errors=errors,
            timing_seconds=elapsed,
            engines_used=sorted(engines_used),
        )

        logger.info(
            f"Search complete: {len(analyzed)} results, "
            f"{elapsed:.2f}s, {len(engines_used)} engines"
        )

        return report

    # ─── Direct dork search ───────────────────────────────────────────────

    def search_dork(
        self,
        dork_query: str,
        engines: list[str] | None = None,
        categories: list[str] | None = None,
        time_range: str = "",
        language: str = "auto",
    ) -> SearchReport:
        """
        Execute a raw dork query directly (no intent parsing).
        For users who want full control over the search operators.
        """
        start_time = time.time()

        intent = SearchIntent(
            category="general",
            subcategory="direct_dork",
            keywords=dork_query.split(),
            depth=Depth.QUICK,
            confidence=1.0,
        )

        try:
            raw = self.client.search(
                query=dork_query,
                engines=engines,
                categories=categories,
                time_range=time_range,
                language=language,
            )
            results = self.client.parse_results(raw)
            suggestions = self.client.get_suggestions(raw)
            error = raw.get("_error")
        except Exception as e:
            results = []
            suggestions = []
            error = str(e)

        analyzed = self.analyzer.analyze(results, intent)
        elapsed = time.time() - start_time

        engines_used = set()
        for r in analyzed:
            engines_used.update(r.engines)

        strategy = SearchStrategy(
            name="direct_dork",
            steps=[],
            description="Direct dork query execution",
        )

        return SearchReport(
            query=dork_query,
            intent=intent,
            strategy=strategy,
            results=analyzed,
            total_found=len(results),
            suggestions=suggestions,
            errors=[error] if error else [],
            timing_seconds=elapsed,
            engines_used=sorted(engines_used),
        )

    # ─── Suggest optimized queries ────────────────────────────────────────

    def suggest_queries(self, query: str, depth: str = "standard") -> list[DorkQuery]:
        """
        Generate optimized dork queries for a natural language query
        WITHOUT executing them. Useful for preview/confirmation workflows.
        """
        intent = self.intent_parser.parse(query, depth)
        return self.dork_generator.generate(intent)

    # ─── Build custom dork ────────────────────────────────────────────────

    def build_dork(
        self,
        keyword: str,
        domain: str = "",
        filetype: str = "",
        intitle: str = "",
        inurl: str = "",
        exclude: list[str] | None = None,
        exact_match: bool = False,
        extra_operators: dict[str, str] | None = None,
    ) -> DorkQuery:
        """Build a custom dork query from explicit parameters."""
        return self.dork_generator.generate_custom(
            keyword=keyword,
            domain=domain,
            filetype=filetype,
            intitle=intitle,
            inurl=inurl,
            exclude=exclude,
            exact_match=exact_match,
            extra_operators=extra_operators,
        )

    # ─── Execute a named strategy directly ────────────────────────────────

    def execute_strategy(
        self,
        strategy_name: str,
        query: str = "",
        target: str = "",
        depth: str = "deep",
        **kwargs,
    ) -> SearchReport:
        """
        Execute a named strategy (e.g., "osint_chain", "deep_dive")
        against a target.
        """
        # Build a synthetic query from strategy + target
        if not query:
            if strategy_name == "osint_chain":
                query = f"OSINT investigation on {target}"
            elif strategy_name == "deep_dive":
                query = f"deep security analysis of {target}"
            elif strategy_name == "file_hunt":
                query = f"find files on {target}"
            else:
                query = f"{strategy_name} search for {target}"

        return self.search(query, depth=depth, **kwargs)

    # ─── Multi-query batch search ─────────────────────────────────────────

    def search_batch(
        self,
        queries: list[str],
        depth: str = "quick",
        engines: list[str] | None = None,
    ) -> list[SearchReport]:
        """Execute multiple searches and return individual reports."""
        return [
            self.search(q, depth=depth, engines=engines)
            for q in queries
        ]

    # ─── Utilities ────────────────────────────────────────────────────────

    def health_check(self) -> bool:
        """Check if the SearXNG instance is reachable."""
        return self.client.health_check()

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        return f"SearchSkill(searxng={self.client.base_url})"