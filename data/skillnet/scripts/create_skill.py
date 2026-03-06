#!/usr/bin/env python3
"""create_skill.py — Create a new skill from various sources and auto-evaluate.

Usage:
  # From GitHub repo
  python create_skill.py --github https://github.com/owner/repo

  # From a natural-language description
  python create_skill.py --prompt "A skill for managing Docker Compose stacks"

  # From an office document
  python create_skill.py --office report.pdf

  # From an execution trajectory
  python create_skill.py --trajectory trace.txt

Requires: pip install skillnet-ai
          Environment variable: API_KEY
"""
import argparse
import os
import sys

DEFAULT_OUTPUT = os.path.expanduser("~/.openclaw/workspace/skills")


def main():
    parser = argparse.ArgumentParser(description="Create a skill from various sources via SkillNet.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--github", metavar="URL", help="GitHub repository URL")
    group.add_argument("--prompt", metavar="TEXT", help="Natural-language skill description")
    group.add_argument("--office", metavar="FILE", help="Path to PDF/PPT/DOCX file")
    group.add_argument("--trajectory", metavar="FILE", help="Path to execution trajectory/log file")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help=f"Output directory (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--model", default="gpt-4o", help="LLM model to use (default: gpt-4o)")
    parser.add_argument("--max-files", type=int, default=20, help="Max files to analyze (GitHub mode)")
    parser.add_argument("--no-evaluate", action="store_true", help="Skip auto-evaluation after creation")
    args = parser.parse_args()

    try:
        from skillnet_ai import SkillNetClient
    except ImportError:
        print("ERROR: skillnet-ai not installed. Run: pip install skillnet-ai", file=sys.stderr)
        sys.exit(1)

    api_key = os.getenv("API_KEY")
    if not api_key:
        print("ERROR: API_KEY environment variable is required for skill creation.", file=sys.stderr)
        print("Set it via: export API_KEY=sk-... (Linux/macOS) or $env:API_KEY='sk-...' (PowerShell)", file=sys.stderr)
        sys.exit(1)

    client = SkillNetClient(
        api_key=api_key,
        base_url=os.getenv("BASE_URL"),
        github_token=os.getenv("GITHUB_TOKEN"),
    )
    os.makedirs(args.output, exist_ok=True)

    # --- Determine input ---
    create_kwargs = {"output_dir": args.output, "model": args.model}

    if args.github:
        print(f"🔧 Creating skill from GitHub: {args.github}")
        create_kwargs["github_url"] = args.github
        create_kwargs["max_files"] = args.max_files
    elif args.prompt:
        print(f"🔧 Creating skill from prompt")
        create_kwargs["prompt"] = args.prompt
    elif args.office:
        print(f"🔧 Creating skill from document: {args.office}")
        create_kwargs["office_file"] = args.office
    elif args.trajectory:
        print(f"🔧 Creating skill from trajectory: {args.trajectory}")
        with open(args.trajectory, "r", encoding="utf-8") as f:
            create_kwargs["trajectory_content"] = f.read()

    # --- Create ---
    try:
        paths = client.create(**create_kwargs)
    except Exception as e:
        print(f"❌ Creation failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not paths:
        print("⚠️  No skills were generated.")
        sys.exit(0)

    print(f"\n✅ Created {len(paths)} skill(s):")
    for p in paths:
        print(f"   📁 {p}")

    # --- Auto-evaluate ---
    if not args.no_evaluate:
        print("\n📊 Running quality evaluation...")
        for skill_path in paths:
            try:
                report = client.evaluate(target=skill_path, model=args.model)
                print(f"\n   Evaluation for: {os.path.basename(skill_path)}")
                dimensions = ["safety", "completeness", "executability", "maintainability", "cost_awareness"]
                for dim in dimensions:
                    if dim in report:
                        level = report[dim].get("level", "N/A") if isinstance(report[dim], dict) else report[dim]
                        print(f"     {dim.replace('_', ' ').title():20s}: {level}")
                # Warn on Poor scores
                poors = [d for d in dimensions if isinstance(report.get(d), dict) and report[d].get("level") == "Poor"]
                if poors:
                    print(f"   ⚠️  Poor scores on: {', '.join(poors)} — review before using")
            except Exception as e:
                print(f"   ⚠️  Evaluation failed for {skill_path}: {e}")

    print("\n🎉 Done. Skills are ready in:", args.output)


if __name__ == "__main__":
    main()
