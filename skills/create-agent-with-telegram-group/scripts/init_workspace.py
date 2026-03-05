#!/usr/bin/env python3
import argparse
from pathlib import Path


def validate_path_within(prefix: Path, path: Path, name: str):
    """Ensure path is within prefix to prevent arbitrary file write."""
    try:
        path.resolve().relative_to(prefix.resolve())
    except ValueError:
        raise SystemExit(f"Error: {name} must be within {prefix}")


def write_if(path: Path, content: str, enabled: bool):
    if not enabled:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def main():
    ap = argparse.ArgumentParser(description="Initialize agent workspace core files")
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--agent-name", required=True)
    ap.add_argument("--with-user", action="store_true")
    ap.add_argument("--with-identity", action="store_true")
    ap.add_argument("--with-soul", action="store_true")
    args = ap.parse_args()

    # Validate workspace is within user's home to prevent arbitrary file write
    home = Path.home()
    ws = Path(args.workspace).expanduser().resolve()
    validate_path_within(home, ws, "workspace")

    created = []

    if write_if(ws / "USER.md", "# USER.md\n\n- Name: <fill-me>\n- What to call them: <fill-me>\n- Preferred language: <fill-me>\n- Goals: <fill-me>\n", args.with_user):
        created.append("USER.md")

    if write_if(ws / "IDENTITY.md", f"# IDENTITY.md\n\n- Name: {args.agent_name}\n- Role: Dedicated assistant\n", args.with_identity):
        created.append("IDENTITY.md")

    soul = f"# SOUL.md\n\nYou are {args.agent_name}.\nBe concise, useful, and reliable.\n"
    if write_if(ws / "SOUL.md", soul, args.with_soul):
        created.append("SOUL.md")

    print(",".join(created) if created else "none")


if __name__ == "__main__":
    main()
