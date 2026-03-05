#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import inspect
import pkgutil
from pathlib import Path

from common import configure_vnstock_api_key, ensure_outdir, timestamp, write_json


def is_public_method(name: str, member) -> bool:
    return callable(member) and not name.startswith("_")


def add_module_classes(module, bag):
    for name in dir(module):
        if name.startswith("_"):
            continue
        obj = getattr(module, name)
        if inspect.isclass(obj):
            methods = []
            for mname in dir(obj):
                member = getattr(obj, mname)
                if is_public_method(mname, member):
                    try:
                        sig = str(inspect.signature(member))
                    except Exception:
                        sig = "(signature unavailable)"
                    methods.append({"method": mname, "signature": sig})
            if methods:
                full = f"{obj.__module__}.{obj.__name__}"
                bag[full] = sorted(methods, key=lambda x: x["method"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Catalog available vnstock classes and public methods")
    parser.add_argument("--outdir", default="./outputs", help="Output directory")
    parser.add_argument("--deep", action="store_true", help="Scan vnstock submodules in addition to top-level exports")
    parser.add_argument("--api-key", default="", help="Optional VNStock API key override")
    args = parser.parse_args()

    configure_vnstock_api_key(args.api_key or None)
    import vnstock

    outdir = ensure_outdir(args.outdir)
    ts = timestamp()

    exported_classes = {}
    add_module_classes(vnstock, exported_classes)

    scanned_modules = ["vnstock"]
    if args.deep and hasattr(vnstock, "__path__"):
        for m in pkgutil.walk_packages(vnstock.__path__, prefix="vnstock."):
            mod_name = m.name
            try:
                mod = importlib.import_module(mod_name)
                add_module_classes(mod, exported_classes)
                scanned_modules.append(mod_name)
            except Exception:
                # Skip problematic internal modules; catalog should stay best-effort.
                continue

    payload = {
        "generated_at": ts,
        "vnstock_version": getattr(vnstock, "__version__", "unknown"),
        "deep_scan": args.deep,
        "scanned_modules_count": len(scanned_modules),
        "classes": exported_classes,
    }

    json_path = Path(outdir) / f"vnstock_catalog_{ts}.json"
    md_path = Path(outdir) / f"vnstock_catalog_{ts}.md"
    write_json(json_path, payload)

    lines = [
        f"# VNStock Catalog ({ts})",
        "",
        f"- Version: `{payload['vnstock_version']}`",
        f"- Class count: `{len(exported_classes)}`",
        "",
        "## Classes",
    ]

    for cls, methods in sorted(exported_classes.items()):
        lines.append(f"### {cls}")
        for m in methods:
            lines.append(f"- `{m['method']}{m['signature']}`")
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    (Path(outdir) / "vnstock_catalog_latest.json").write_text(str(json_path), encoding="utf-8")
    (Path(outdir) / "vnstock_catalog_latest.md").write_text(str(md_path), encoding="utf-8")

    print(f"Saved: {json_path}")
    print(f"Saved: {md_path}")


if __name__ == "__main__":
    main()
