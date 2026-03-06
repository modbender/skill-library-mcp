"""
Memori + Zhipu API - OpenClaw Skill Integration

Provides simplified API for OpenClaw integration using the Memori Python library.
"""
from .memori_extension import (
    get_memori,
    get_interceptor,
    get_zhipu_client,
    search,
    augment,
    intercept_llm,
    enhance_with_memori,
    intercept_llm_call,
    MemoriWrapper,
    LLMInterceptor,
    ZhipuClient,
    Message
)

# Import core classes from Memori library
from memori import Memori, Memory, AugmentedContext


__all__ = [
    # From Memori library
    "Memori",
    "Memory",
    "AugmentedContext",
    # Skill wrapper classes
    "MemoriWrapper",
    "LLMInterceptor",
    "ZhipuClient",
    "Message",
    # Global instances
    "get_memori",
    "get_interceptor",
    "get_zhipu_client",
    # Convenience API
    "search",
    "augment",
    "intercept_llm",
    # Compatibility API
    "enhance_with_memori",
    "intercept_llm_call"
]
