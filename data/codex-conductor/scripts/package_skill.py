#!/usr/bin/env python3
import argparse
import zipfile
from pathlib import Path


def validate(skill_dir: Path):
    required = [
        skill_dir / "SKILL.md",
        skill_dir / "scripts" / "init_project_docs.py",
        skill_dir / "references" / "planning-questionnaire.md",
        skill_dir / "references" / "testing-matrix.md",
        skill_dir / "scripts" / "run_gate.py",
        skill_dir / "scripts" / "gate_status.py",
        skill_dir / "scripts" / "agent_exec.py",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise SystemExit("Missing required files:\n" + "\n".join(missing))


def package(skill_dir: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    skill_name = skill_dir.name
    out_file = out_dir / f"{skill_name}.skill"

    with zipfile.ZipFile(out_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in skill_dir.rglob("*"):
            if path.is_file():
                arcname = f"{skill_name}/{path.relative_to(skill_dir)}"
                zf.write(path, arcname)

    return out_file


def main():
    parser = argparse.ArgumentParser(description="Package codex-orchestrator skill without external deps")
    parser.add_argument("--skill-dir", default=".", help="Skill directory")
    parser.add_argument("--out", default="dist", help="Output directory")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    out_dir = Path(args.out).resolve()

    validate(skill_dir)
    out_file = package(skill_dir, out_dir)
    print(f"Packaged: {out_file}")


if __name__ == "__main__":
    main()
