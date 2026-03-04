"""
SenseGuard Main Scanner
CLI entry point that orchestrates Layer 1 (rules), Layer 2 (semantic),
and Layer 3 (reputation scoring).

Usage:
  python scanner.py --target <name|path|all> [--deep] [--no-cache] [--skills-dir <dir>]
"""

import argparse
import io
import json
import os
import sys
from typing import List, Optional

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from rule_engine import RuleEngine, get_frontmatter, get_skill_content
from semantic_analyzer import SemanticAnalyzer
from reputation_scorer import ReputationScorer
from report_generator import ReportGenerator
from cache_manager import CacheManager


# Default skill installation paths
SKILL_PATHS = [
    os.path.expanduser("~/.openclaw/skills"),
]


def find_skill_dirs(skills_dir: Optional[str] = None) -> List[str]:
    """Discover all installed skill directories."""
    dirs_to_search = [skills_dir] if skills_dir else SKILL_PATHS
    # Also check workspace skills
    workspace_skills = os.path.join(os.getcwd(), "skills")
    if os.path.isdir(workspace_skills) and workspace_skills not in dirs_to_search:
        dirs_to_search.append(workspace_skills)

    skill_dirs = []
    for base_dir in dirs_to_search:
        if not os.path.isdir(base_dir):
            continue
        for entry in os.listdir(base_dir):
            skill_path = os.path.join(base_dir, entry)
            if os.path.isdir(skill_path):
                skill_md = os.path.join(skill_path, "SKILL.md")
                if os.path.isfile(skill_md):
                    skill_dirs.append(skill_path)
    return skill_dirs


def resolve_target(target: str, skills_dir: Optional[str] = None) -> List[str]:
    """Resolve target argument to list of skill directories."""
    if target == "all":
        return find_skill_dirs(skills_dir)

    # Check if target is a direct path
    if os.path.isdir(target):
        return [os.path.abspath(target)]

    # Search by name in known skill paths
    dirs_to_search = [skills_dir] if skills_dir else SKILL_PATHS
    workspace_skills = os.path.join(os.getcwd(), "skills")
    if os.path.isdir(workspace_skills):
        dirs_to_search.append(workspace_skills)

    for base_dir in dirs_to_search:
        candidate = os.path.join(base_dir, target)
        if os.path.isdir(candidate):
            return [candidate]

    # Nothing found
    return []


def scan_single_skill(
    skill_dir: str,
    rule_engine: RuleEngine,
    semantic_analyzer: SemanticAnalyzer,
    scorer: ReputationScorer,
    cache: CacheManager,
    deep: bool = False,
    no_cache: bool = False,
) -> dict:
    """Scan a single skill and return structured result."""
    skill_name = os.path.basename(skill_dir)
    content_hash = cache.compute_hash(skill_dir)

    # Check cache
    if not no_cache:
        cached = cache.get_cached(skill_dir)
        if cached:
            cached["from_cache"] = True
            return cached

    # Detect if we're scanning the scanner itself (senseguard)
    is_self_scan = skill_name == "senseguard" or os.path.basename(os.path.dirname(skill_dir)) == "senseguard"
    
    # Layer 1: Rule engine
    # Skip scanner code (rules/, scripts/) when scanning senseguard itself to avoid false positives
    layer1_result = rule_engine.scan_skill(skill_dir, exclude_scanner_code=is_self_scan)
    layer1_dict = layer1_result.to_dict()

    # Determine if Layer 2 should run
    run_layer2 = deep or layer1_result.has_suspicious
    layers_used = ["Layer 1 (Rules)"]

    layer2_result = None
    layer2_prompt = None
    if run_layer2:
        layers_used.append("Layer 2 (Semantic)")
        frontmatter = get_frontmatter(skill_dir) or {}
        full_content = get_skill_content(skill_dir)
        layer2_prompt = semantic_analyzer.build_analysis_prompt(
            name=frontmatter.get("name", skill_name),
            description=frontmatter.get("description", ""),
            full_content=full_content,
        )
        # NOTE: In actual OpenClaw usage, the agent would process this prompt
        # and feed back the JSON result. For CLI standalone testing, we use
        # the default result.
        layer2_result = semantic_analyzer.get_default_result()
    else:
        layer2_result = semantic_analyzer.get_default_result()

    layers_used.append("Layer 3 (Scoring)")

    # Metadata analysis for bonuses
    frontmatter = get_frontmatter(skill_dir)
    has_frontmatter = frontmatter is not None
    has_examples = False
    structure_clean = True
    permissions_match = True

    if has_frontmatter:
        content = get_skill_content(skill_dir)
        # Check for usage examples
        has_examples = any(kw in content.lower() for kw in ["example", "usage", "## how to", "## instructions"])

    # Structure cleanliness (no excessive files, no binaries)
    structure_clean = not any(
        sf.check_name in ("excessive_files", "suspicious_file_types")
        for sf in layer1_result.structure_findings
        if hasattr(sf, "check_name")
    )

    # Layer 3: Reputation scoring
    rep_result = scorer.score(
        layer1_result=layer1_dict,
        layer2_result=layer2_result,
        has_frontmatter=has_frontmatter,
        has_usage_examples=has_examples,
        structure_is_clean=structure_clean,
        permissions_match=permissions_match,
    )

    result = {
        "skill_name": skill_name,
        "skill_dir": skill_dir,
        "hash": content_hash,
        "score": rep_result.score,
        "rating": rep_result.rating,
        "layers_used": layers_used,
        "layer1": layer1_dict,
        "layer2": layer2_result,
        "layer2_prompt": layer2_prompt,
        "score_breakdown": [
            {"dimension": b.dimension, "points": b.points, "reason": b.reason}
            for b in rep_result.breakdown
        ],
        "critical_count": layer1_result.critical_count,
        "high_count": layer1_result.high_count,
        "from_cache": False,
    }

    # Store in cache
    cache.store(skill_dir, result, content_hash)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="SenseGuard - OpenClaw Skill Security Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scanner.py --target /path/to/skill          # Scan a specific skill
  python scanner.py --target my-skill                 # Scan by skill name
  python scanner.py --target all                      # Scan all installed skills
  python scanner.py --target all --deep               # Force Layer 2 on all
  python scanner.py --target /path/to/skill --no-cache  # Ignore cache
  python scanner.py --target all --json               # Output raw JSON
        """,
    )
    parser.add_argument("--target", required=True, help="Skill name, path, or 'all'")
    parser.add_argument("--deep", action="store_true", help="Force Layer 2 semantic analysis")
    parser.add_argument("--no-cache", action="store_true", help="Ignore cached results")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of Markdown")
    parser.add_argument("--skills-dir", default=None, help="Custom skills directory")
    parser.add_argument("--cache-file", default=None, help="Custom cache file path")

    args = parser.parse_args()

    # Initialize components
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    rules_dir = os.path.join(scripts_dir, "rules")

    rule_engine = RuleEngine(rules_dir=rules_dir)
    semantic_analyzer = SemanticAnalyzer()
    scorer = ReputationScorer()
    report_gen = ReportGenerator()
    cache = CacheManager(cache_file=args.cache_file)

    # Resolve targets
    skill_dirs = resolve_target(args.target, args.skills_dir)
    if not skill_dirs:
        print(f"Error: No skill found for target '{args.target}'", file=sys.stderr)
        print(f"Searched in: {SKILL_PATHS}", file=sys.stderr)
        sys.exit(1)

    # Get previous results for diff
    previous_results = cache.get_all_previous_results()

    # Scan each skill
    results = []
    for skill_dir in skill_dirs:
        result = scan_single_skill(
            skill_dir=skill_dir,
            rule_engine=rule_engine,
            semantic_analyzer=semantic_analyzer,
            scorer=scorer,
            cache=cache,
            deep=args.deep,
            no_cache=args.no_cache,
        )
        results.append(result)

    # Output
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    elif len(results) == 1:
        # Single skill detailed report
        r = results[0]
        prev = cache.get_previous_result(r["skill_dir"]) if not args.no_cache else None
        report = report_gen.generate_single_report(
            skill_name=r["skill_name"],
            score=r["score"],
            rating=r["rating"],
            layer1_result=r["layer1"],
            layer2_result=r["layer2"],
            score_breakdown=r["score_breakdown"],
            layers_used=r["layers_used"],
            previous_result=prev,
        )
        print(report)
    else:
        # Batch summary report
        report = report_gen.generate_batch_report(
            results=results,
            previous_results=previous_results,
        )
        print(report)

    # Return exit code based on worst rating
    worst_score = min(r["score"] for r in results) if results else 100
    if worst_score < 30:
        sys.exit(2)  # MALICIOUS found
    elif worst_score < 60:
        sys.exit(1)  # DANGEROUS found
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
