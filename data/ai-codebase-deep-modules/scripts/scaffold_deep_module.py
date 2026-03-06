#!/usr/bin/env python3
"""
Scaffold a "deep module" folder with a small public interface.

This is optional helper tooling for the ai-codebase-deep-modules skill.
It aims to create the *shape* of a module quickly so you can iterate on the
public interface and contract tests first.

Usage examples:
  python scripts/scaffold_deep_module.py --name auth --lang ts
  python scripts/scaffold_deep_module.py --name billing --lang py --base-dir src
  python scripts/scaffold_deep_module.py --name video-editor --lang ts --base-dir packages
  python scripts/scaffold_deep_module.py --name video-editor --lang py   # becomes video_editor/

Notes:
- This script does not enforce boundaries; use lint/arch rules for that.
- It is intentionally minimal and dependency-free.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        # Don't clobber existing work.
        return
    path.write_text(content, encoding="utf-8")


def scaffold_ts(module_dir: Path, name: str) -> list[Path]:
    created: list[Path] = []

    index_ts = module_dir / "index.ts"
    types_ts = module_dir / "types.ts"
    public_api_ts = module_dir / "internal" / "public-api.ts"
    test_ts = module_dir / "__tests__" / f"{name}.contract.test.ts"

    _write(
        types_ts,
        f"""// Public types for the `{name}` module.

export type {to_pascal(name)}Error =
  | {{ type: "not-implemented" }};
""",
    )
    created.append(types_ts)

    _write(
        public_api_ts,
        f"""import type {{ {to_pascal(name)}Error }} from "../types";

export type Result<T, E> =
  | {{ ok: true; value: T }}
  | {{ ok: false; error: E }};

export function notImplementedYet(): Result<never, {to_pascal(name)}Error> {{
  return {{ ok: false, error: {{ type: "not-implemented" }} }};
}}
""",
    )
    created.append(public_api_ts)

    _write(
        index_ts,
        f"""// Public entrypoint for the `{name}` module.
// External code should import from here only.

export type {{ {to_pascal(name)}Error }} from "./types";
export type {{ Result }} from "./internal/public-api";
export {{ notImplementedYet }} from "./internal/public-api";
""",
    )
    created.append(index_ts)

    _write(
        test_ts,
        f"""import {{ notImplementedYet }} from "../index";

test("notImplementedYet returns a structured error", () => {{
  const result = notImplementedYet();
  expect(result.ok).toBe(false);
  if (!result.ok) {{
    expect(result.error.type).toBe("not-implemented");
  }}
}});
""",
    )
    created.append(test_ts)

    return created


def scaffold_py(module_dir: Path, package_name: str, display_name: str) -> list[Path]:
    created: list[Path] = []

    init_py = module_dir / "__init__.py"
    types_py = module_dir / "types.py"
    public_api_py = module_dir / "internal" / "public_api.py"
    test_py = module_dir / "tests" / f"test_{package_name}_contract.py"

    type_name = to_pascal(display_name) + "Error"

    _write(
        types_py,
        f"""\"\"\"Public types for the `{display_name}` module.\"\"\"

from __future__ import annotations

from typing import Literal, TypedDict, Union


class NotImplementedErrorType(TypedDict):
    type: Literal["not-implemented"]


{type_name} = Union[NotImplementedErrorType]
""",
    )
    created.append(types_py)

    _write(
        public_api_py,
        f"""from __future__ import annotations

from typing import Literal, TypedDict

from ..types import {type_name}


class Result(TypedDict):
    ok: Literal[False]
    error: {type_name}


def not_implemented_yet() -> Result:
    return {{"ok": False, "error": {{"type": "not-implemented"}}}}
""",
    )
    created.append(public_api_py)

    _write(
        init_py,
        f"""\"\"\"Public entrypoint for the `{display_name}` module.\"\"\"

from .types import {type_name}
from .internal.public_api import not_implemented_yet

__all__ = [
    "{type_name}",
    "not_implemented_yet",
]
""",
    )
    created.append(init_py)

    _write(
        test_py,
        f"""from {package_name} import not_implemented_yet


def test_not_implemented_yet_returns_structured_error():
    result = not_implemented_yet()
    assert result["ok"] is False
    assert result["error"]["type"] == "not-implemented"
""",
    )
    created.append(test_py)

    return created


def to_pascal(s: str) -> str:
    return "".join(part.capitalize() for part in s.replace("_", "-").split("-") if part)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Module name (kebab-case recommended).")
    parser.add_argument("--lang", choices=["ts", "py"], required=True, help="Language template to use.")
    parser.add_argument("--base-dir", default="src", help="Base directory inside repo (default: src).")
    parser.add_argument("--root", default=".", help="Repo root (default: current directory).")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    base_dir = root / args.base_dir

    if args.lang == "py":
        # Python packages must be valid identifiers; normalise kebab-case to snake_case.
        package_name = args.name.replace("-", "_")
        module_dir = base_dir / package_name
        created = scaffold_py(module_dir, package_name=package_name, display_name=args.name)
    else:
        module_dir = base_dir / args.name
        created = scaffold_ts(module_dir, args.name)

    print(f"Scaffolded module at: {module_dir}")
    for p in created:
        if p.exists():
            print(f"  - {p.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
