#!/usr/bin/env python3
"""LangChain callback integration without requiring LangChain at import time."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.api import GuardianScanner, ScanResult


class GuardianBlockedError(RuntimeError):
    """Raised when Guardian blocks model prompt content."""


class GuardianCallbackHandler:
    """Callback handler that scans prompts before model execution."""

    def __init__(
        self,
        scanner: Optional[GuardianScanner] = None,
        severity: str = "high",
        auto_block: bool = True,
        channel: str = "langchain",
    ) -> None:
        self.scanner = scanner or GuardianScanner(severity=severity, record_to_db=False)
        self.auto_block = auto_block
        self.channel = channel
        self.last_result: Optional[ScanResult] = None

    def _scan_prompts(self, prompts: List[str]) -> ScanResult:
        text = "\n".join(prompt for prompt in prompts if isinstance(prompt, str))
        result = self.scanner.scan(text, channel=self.channel)
        self.last_result = result
        if self.auto_block and result.blocked:
            raise GuardianBlockedError(result.summary)
        return result

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """LangChain callback hook for prompt scan."""
        del serialized, kwargs
        self._scan_prompts(prompts)

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
        """Fallback hook scanning all string inputs."""
        del serialized, kwargs
        prompts = [str(value) for value in inputs.values() if isinstance(value, (str, int, float))]
        self._scan_prompts(prompts)

    def close(self) -> None:
        """Close underlying scanner resources."""
        self.scanner.close()
