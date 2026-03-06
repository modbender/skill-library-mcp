#!/usr/bin/env python3
"""Check that all modules in a package can be imported.

Usage:
    python import_check.py <package_name> [--exclude dir1,dir2] [--json]

Example:
    python import_check.py castle --exclude aot,sam,dinov2,dinov3
"""
from __future__ import annotations

import argparse
import importlib
import json
import logging
import pkgutil
import re
import sys
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

# Configure logging to stderr (not stdout, which is for output)
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Hardware/environment-specific libraries that are typically optional
OPTIONAL_DEPENDENCY_PATTERNS: list[str] = [
    r"cuml",
    r"triton",
    r"tensorrt",
    r"cuda",
    r"nccl",
    r"apex",
    r"flash_attn",
    r"xformers",
    r"bitsandbytes",
    r"deepspeed",
    r"horovod",
    r"mpi4py",
]

# Paths that indicate optional/auxiliary code
OPTIONAL_PATH_PATTERNS: list[str] = [
    r"examples?/",
    r"scripts?/",
    r"tools?/",
    r"benchmarks?/",
    r"demos?/",
    r"notebooks?/",
    r"_test\.py$",
    r"test_.*\.py$",
    r"conftest\.py$",
    r"tests?/",
]

# Paths that indicate critical/core code
CRITICAL_PATH_PATTERNS: list[str] = [
    r"__init__\.py$",
    r"__main__\.py$",
    r"main\.py$",
    r"app\.py$",
    r"cli\.py$",
    r"core/",
    r"src/",
    r"lib/",
]


@dataclass
class ImportFailure:
    """Record of a failed import."""

    module: str
    error: str
    error_type: str
    is_critical: bool = True

    def to_dict(self) -> dict:
        return {
            "module": self.module,
            "error": self.error,
            "type": self.error_type,
            "critical": self.is_critical,
        }


@dataclass
class ImportResults:
    """Results of an import check run."""

    total: int = 0
    passed: int = 0
    failed: list[ImportFailure] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    duration_s: float = 0.0

    @property
    def critical_failures(self) -> list[ImportFailure]:
        return [f for f in self.failed if f.is_critical]

    @property
    def optional_failures(self) -> list[ImportFailure]:
        return [f for f in self.failed if not f.is_critical]

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": [f.to_dict() for f in self.failed],
            "critical_failed": len(self.critical_failures),
            "optional_failed": len(self.optional_failures),
            "skipped": self.skipped,
            "duration_s": self.duration_s,
        }


def is_optional_failure(module_name: str, error_msg: str) -> bool:
    """Determine if an import failure is for an optional dependency.

    Uses heuristics based on:
    1. Module path patterns (tests, examples, scripts)
    2. Error message content (missing hardware libs)
    """
    # Check if module path suggests optional code
    for pattern in OPTIONAL_PATH_PATTERNS:
        if re.search(pattern, module_name):
            return True

    # Check if error mentions optional dependencies
    error_lower = error_msg.lower()
    for pattern in OPTIONAL_DEPENDENCY_PATTERNS:
        if re.search(pattern, error_lower):
            return True

    # Check for common environment-specific errors
    env_errors = [
        "no module named",
        "cannot import name",
        "shared object file",
        "library not loaded",
        "dll load failed",
    ]
    if any(err in error_lower for err in env_errors):
        # But only if it's not a core module
        for pattern in CRITICAL_PATH_PATTERNS:
            if re.search(pattern, module_name):
                return False
        return True

    return False


def walk_package_modules(
    package_name: str, exclude: list[str]
) -> Iterator[tuple[str, bool]]:
    """Yield (module_name, is_pkg) for all modules in a package."""
    try:
        pkg = importlib.import_module(package_name)
    except ImportError as e:
        logger.error(f"Cannot import base package {package_name}: {e}")
        return

    pkg_path = getattr(pkg, "__path__", None)
    if pkg_path is None:
        yield package_name, False
        return

    for _importer, modname, ispkg in pkgutil.walk_packages(
        pkg_path, prefix=f"{package_name}."
    ):
        # Check exclusions
        skip = False
        for ex in exclude:
            if f"{package_name}.{ex}." in modname or modname == f"{package_name}.{ex}":
                skip = True
                break
        if not skip:
            yield modname, ispkg


def check_imports(package_name: str, exclude: list[str] | None = None) -> ImportResults:
    """Check all modules in a package can be imported.

    Args:
        package_name: The package to check
        exclude: List of submodule names to skip

    Returns:
        ImportResults with pass/fail counts and details
    """
    exclude = exclude or []
    results = ImportResults()

    # Try to import the base package first
    try:
        importlib.import_module(package_name)
    except ImportError as e:
        results.failed.append(
            ImportFailure(
                module=package_name,
                error=str(e),
                error_type=type(e).__name__,
                is_critical=True,
            )
        )
        return results

    for modname, _ispkg in walk_package_modules(package_name, exclude):
        # Check if excluded
        if any(
            f"{package_name}.{ex}." in modname or modname == f"{package_name}.{ex}"
            for ex in exclude
        ):
            results.skipped.append(modname)
            continue

        results.total += 1
        try:
            importlib.import_module(modname)
            results.passed += 1
        except KeyboardInterrupt:
            # Always re-raise keyboard interrupt
            raise
        except SystemExit as e:
            # Treat SystemExit as a failure but don't exit
            error_msg = f"Module called sys.exit({e.code})"
            results.failed.append(
                ImportFailure(
                    module=modname,
                    error=error_msg,
                    error_type="SystemExit",
                    is_critical=not is_optional_failure(modname, error_msg),
                )
            )
        except (ImportError, ModuleNotFoundError) as e:
            # Specific import errors
            error_msg = str(e)
            results.failed.append(
                ImportFailure(
                    module=modname,
                    error=error_msg,
                    error_type=type(e).__name__,
                    is_critical=not is_optional_failure(modname, error_msg),
                )
            )
        except (AttributeError, TypeError, ValueError, RuntimeError) as e:
            # Common errors during import (e.g., missing config, bad initialization)
            error_msg = str(e)
            results.failed.append(
                ImportFailure(
                    module=modname,
                    error=error_msg,
                    error_type=type(e).__name__,
                    is_critical=not is_optional_failure(modname, error_msg),
                )
            )
        except OSError as e:
            # File/resource access errors
            error_msg = str(e)
            results.failed.append(
                ImportFailure(
                    module=modname,
                    error=error_msg,
                    error_type=type(e).__name__,
                    is_critical=False,  # Usually environment-specific
                )
            )
        except Exception as e:
            # Catch-all for any other exceptions (custom exceptions, etc.)
            # This prevents the entire check from crashing on unexpected errors
            error_msg = str(e)
            results.failed.append(
                ImportFailure(
                    module=modname,
                    error=error_msg,
                    error_type=type(e).__name__,
                    is_critical=not is_optional_failure(modname, error_msg),
                )
            )

    return results


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Import check for Python packages")
    parser.add_argument("package", help="Package name to check")
    parser.add_argument(
        "--exclude", default="", help="Comma-separated dirs to exclude"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    exclude = [x.strip() for x in args.exclude.split(",") if x.strip()]

    t0 = time.time()
    results = check_imports(args.package, exclude)
    results.duration_s = round(time.time() - t0, 2)

    if args.json:
        # JSON goes to stdout
        print(json.dumps(results.to_dict(), indent=2))
    else:
        # Human-readable output to stderr
        logger.info(f"Import Check: {args.package}")
        logger.info(f"  Total:   {results.total}")
        logger.info(f"  Passed:  {results.passed}")
        logger.info(f"  Failed:  {len(results.failed)}")
        logger.info(f"    Critical: {len(results.critical_failures)}")
        logger.info(f"    Optional: {len(results.optional_failures)}")
        logger.info(f"  Skipped: {len(results.skipped)}")

        if results.critical_failures:
            logger.info("\n❌ Critical Failures:")
            for f in results.critical_failures:
                logger.info(f"  {f.module}: {f.error}")

        if results.optional_failures:
            logger.info("\n⚠️  Optional Failures:")
            for f in results.optional_failures:
                logger.info(f"  {f.module}: {f.error}")

        logger.info(f"\nDuration: {results.duration_s}s")

    # Exit code: 1 if any critical failures
    sys.exit(1 if results.critical_failures else 0)


if __name__ == "__main__":
    main()
