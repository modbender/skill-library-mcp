"""
LangChain integration — automatic spend tracking for LLM calls.

Drop-in callback handler that records every LLM/chat call as a
financial transaction. Works with LangChain, LangGraph, and any
framework that emits BaseCallbackHandler events.

Usage::

    from langchain_openai import ChatOpenAI
    from agentfinobs.integrations.langchain import AgentFinObsHandler

    handler = AgentFinObsHandler(obs_stack=obs)
    llm = ChatOpenAI(callbacks=[handler])

    # Every LLM call is now automatically tracked
    llm.invoke("Hello world")

No LangChain dependency required at install time — this module
uses duck typing and will work with any compatible callback interface.
"""

from __future__ import annotations

import time
import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import AgentTx

logger = logging.getLogger("agentfinobs.integrations.langchain")


class AgentFinObsHandler:
    """
    LangChain callback handler that tracks LLM spending.

    Compatible with:
      - langchain.callbacks.base.BaseCallbackHandler
      - langchain_core.callbacks.BaseCallbackHandler

    Pricing is estimated from token counts using configurable rates.
    Override `estimate_cost()` for custom pricing logic.
    """

    def __init__(
        self,
        obs_stack: Any = None,
        tracker: Any = None,
        agent_id: str = "langchain",
        default_cost_per_1k_input: float = 0.003,
        default_cost_per_1k_output: float = 0.015,
        task_prefix: str = "llm",
    ):
        """
        Args:
            obs_stack: An ObservabilityStack instance (preferred).
            tracker: A SpendTracker instance (alternative to obs_stack).
            agent_id: Agent ID to tag transactions with.
            default_cost_per_1k_input: Default $/1k input tokens.
            default_cost_per_1k_output: Default $/1k output tokens.
            task_prefix: Prefix for auto-generated task IDs.
        """
        if obs_stack is not None:
            self._tracker = obs_stack.tracker
        elif tracker is not None:
            self._tracker = tracker
        else:
            raise ValueError("Provide either obs_stack or tracker")

        self._agent_id = agent_id
        self._cost_input = default_cost_per_1k_input
        self._cost_output = default_cost_per_1k_output
        self._task_prefix = task_prefix
        self._call_counter = 0

        # Track in-flight calls: run_id -> start_time
        self._inflight: dict[str, float] = {}

    # ── Cost estimation ───────────────────────────────────────────────

    # Model-specific pricing ($/1k tokens) — override or extend
    MODEL_PRICING: dict[str, tuple[float, float]] = {
        # (input_per_1k, output_per_1k)
        "gpt-4o": (0.0025, 0.01),
        "gpt-4o-mini": (0.00015, 0.0006),
        "gpt-4-turbo": (0.01, 0.03),
        "gpt-4": (0.03, 0.06),
        "gpt-3.5-turbo": (0.0005, 0.0015),
        "claude-3-opus": (0.015, 0.075),
        "claude-3-sonnet": (0.003, 0.015),
        "claude-3-haiku": (0.00025, 0.00125),
        "claude-sonnet-4": (0.003, 0.015),
        "claude-haiku-4": (0.0008, 0.004),
    }

    def estimate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Estimate the USD cost of an LLM call.
        Override this method for custom pricing logic.
        """
        # Try exact match, then prefix match
        pricing = self.MODEL_PRICING.get(model)
        if pricing is None:
            for key, val in self.MODEL_PRICING.items():
                if model.startswith(key):
                    pricing = val
                    break

        if pricing:
            cost_in, cost_out = pricing
        else:
            cost_in, cost_out = self._cost_input, self._cost_output

        return (input_tokens / 1000 * cost_in) + (output_tokens / 1000 * cost_out)

    # ── LangChain callback interface ──────────────────────────────────
    # These methods match BaseCallbackHandler's signature.
    # We don't inherit from it to avoid requiring langchain as a dependency.

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: Any = None,
        **kwargs: Any,
    ) -> None:
        """Called when an LLM call starts."""
        rid = str(run_id) if run_id else str(self._call_counter)
        self._inflight[rid] = time.time()

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[Any]],
        *,
        run_id: Any = None,
        **kwargs: Any,
    ) -> None:
        """Called when a chat model call starts."""
        rid = str(run_id) if run_id else str(self._call_counter)
        self._inflight[rid] = time.time()

    def on_llm_end(
        self,
        response: Any,
        *,
        run_id: Any = None,
        **kwargs: Any,
    ) -> None:
        """Called when an LLM call finishes. Records the transaction."""
        self._call_counter += 1
        rid = str(run_id) if run_id else str(self._call_counter)
        start_time = self._inflight.pop(rid, time.time())

        # Extract token usage from response
        input_tokens = 0
        output_tokens = 0
        model = "unknown"

        if hasattr(response, "llm_output") and response.llm_output:
            usage = response.llm_output.get("token_usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            model = response.llm_output.get("model_name", "unknown")

        cost = self.estimate_cost(model, input_tokens, output_tokens)

        task_id = f"{self._task_prefix}-{self._call_counter}"

        try:
            self._tracker.record(
                amount=cost,
                agent_id=self._agent_id,
                task_id=task_id,
                counterparty=model,
                description=f"LLM call: {input_tokens}in/{output_tokens}out tokens",
                tags={
                    "model": model,
                    "input_tokens": str(input_tokens),
                    "output_tokens": str(output_tokens),
                    "latency_ms": str(int((time.time() - start_time) * 1000)),
                },
            )
        except Exception as e:
            logger.warning(f"Failed to record LLM transaction: {e}")

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: Any = None,
        **kwargs: Any,
    ) -> None:
        """Called when an LLM call fails. Records as a zero-cost failed tx."""
        self._call_counter += 1
        rid = str(run_id) if run_id else str(self._call_counter)
        self._inflight.pop(rid, None)

        task_id = f"{self._task_prefix}-{self._call_counter}"
        try:
            from ..types import TxStatus
            tx = self._tracker.record(
                amount=0.0,
                agent_id=self._agent_id,
                task_id=task_id,
                description=f"LLM error: {type(error).__name__}: {error}",
                tags={"error": str(error)},
            )
            self._tracker.settle(tx.tx_id, revenue=0.0, status=TxStatus.FAILED)
        except Exception as e:
            logger.warning(f"Failed to record LLM error tx: {e}")

    # ── Convenience ───────────────────────────────────────────────────

    @property
    def call_count(self) -> int:
        return self._call_counter
