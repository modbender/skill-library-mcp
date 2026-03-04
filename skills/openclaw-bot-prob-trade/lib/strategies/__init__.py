"""
Auto-discovery of strategy modules.

Place your strategy file in this directory and set `strategy: <name>` in config.yaml.
The engine will find it automatically.
"""

import importlib
import os
import pkgutil
from typing import Dict, Type

from ..strategy_base import Strategy

_registry: Dict[str, Type[Strategy]] = {}


def _discover():
    """Scan this package for Strategy subclasses."""
    pkg_dir = os.path.dirname(__file__)
    for finder, module_name, _ in pkgutil.iter_modules([pkg_dir]):
        if module_name.startswith("_"):
            continue
        mod = importlib.import_module(f".{module_name}", package=__name__)
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, Strategy)
                and attr is not Strategy
            ):
                _registry[attr.name] = attr


def get_strategy(name: str) -> Strategy:
    """Get a strategy instance by name."""
    if not _registry:
        _discover()
    cls = _registry.get(name)
    if cls is None:
        available = ", ".join(sorted(_registry.keys())) or "(none)"
        raise ValueError(f"Strategy '{name}' not found. Available: {available}")
    return cls()


def list_strategies() -> list:
    """List all available strategy names."""
    if not _registry:
        _discover()
    return sorted(_registry.keys())
