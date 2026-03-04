#!/usr/bin/env python3
"""
genome_manager.py - Real implementation of genome management for GEP

Usage:
  python3 genome_manager.py create --task-type research --name my-genome
  python3 genome_manager.py list
  python3 genome_manager.py get <genome-id>
  python3 genome_manager.py mutate <genome-id> --type evolution
"""

import json
import uuid
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

GENOMES_DIR = Path.home() / ".openclaw" / "genomes"


def ensure_dir():
    """Ensure genomes directory exists"""
    GENOMES_DIR.mkdir(parents=True, exist_ok=True)


def create_genome(args):
    """Create a new genome"""
    ensure_dir()
    
    genome = {
        "genome_id": str(uuid.uuid4()),
        "name": args.name,
        "task_type": args.task_type,
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "approach": {
            "steps": args.steps.split(",") if args.steps else [],
            "tools": args.tools.split(",") if args.tools else [],
            "prompts": args.prompts.split(",") if args.prompts else [],
            "config": {}
        },
        "outcome": {
            "success_rate": args.success_rate or 0.0,
            "avg_duration_seconds": args.duration or 0,
            "user_satisfaction": args.satisfaction or 0.0,
            "sample_size": args.sample_size or 0
        },
        "lineage": {
            "parent_id": args.parent or None,
            "generation": 1,
            "mutations": []
        },
        "tags": args.tags.split(",") if args.tags else []
    }
    
    filepath = GENOMES_DIR / f"{args.name}.json"
    with open(filepath, 'w') as f:
        json.dump(genome, f, indent=2)
    
    print(f"✅ Created genome: {args.name}")
    print(f"   ID: {genome['genome_id']}")
    print(f"   Location: {filepath}")
    return genome


def list_genomes(args):
    """List all genomes"""
    ensure_dir()
    
    genomes = []
    for filepath in GENOMES_DIR.glob("*.json"):
        with open(filepath) as f:
            genome = json.load(f)
            genomes.append({
                "name": genome.get("name", filepath.stem),
                "task_type": genome.get("task_type", "unknown"),
                "success_rate": genome.get("outcome", {}).get("success_rate", 0),
                "version": genome.get("version", "unknown")
            })
    
    if not genomes:
        print("No genomes found.")
        return
    
    print(f"\n📚 Genomes in {GENOMES_DIR}:")
    print("-" * 60)
    print(f"{'Name':<30} {'Type':<15} {'Success':<10} {'Version'}")
    print("-" * 60)
    for g in genomes:
        print(f"{g['name']:<30} {g['task_type']:<15} {g['success_rate']:<10.2f} {g['version']}")


def get_genome(args):
    """Get a specific genome"""
    filepath = GENOMES_DIR / f"{args.name}.json"
    
    if not filepath.exists():
        print(f"❌ Genome not found: {args.name}")
        return None
    
    with open(filepath) as f:
        genome = json.load(f)
    
    print(json.dumps(genome, indent=2))
    return genome


def mutate_genome(args):
    """Create a mutated copy of a genome"""
    filepath = GENOMES_DIR / f"{args.name}.json"
    
    if not filepath.exists():
        print(f"❌ Genome not found: {args.name}")
        return None
    
    with open(filepath) as f:
        parent = json.load(f)
    
    # Create child genome
    child = parent.copy()
    child["genome_id"] = str(uuid.uuid4())
    child["name"] = f"{parent['name']}-mutated"
    child["version"] = bump_version(parent["version"])
    child["created_at"] = datetime.now().isoformat()
    child["lineage"]["parent_id"] = parent["genome_id"]
    child["lineage"]["generation"] = parent["lineage"]["generation"] + 1
    child["lineage"]["mutations"].append({
        "type": args.mutation_type,
        "timestamp": datetime.now().isoformat(),
        "changes": args.changes or "automated mutation"
    })
    
    filepath = GENOMES_DIR / f"{child['name']}.json"
    with open(filepath, 'w') as f:
        json.dump(child, f, indent=2)
    
    print(f"✅ Created mutated genome: {child['name']}")
    print(f"   Parent: {parent['name']}")
    print(f"   Mutation: {args.mutation_type}")
    return child


def bump_version(version):
    """Bump patch version"""
    parts = version.split(".")
    parts[2] = str(int(parts[2]) + 1)
    return ".".join(parts)


def validate_genome(args):
    """Validate a genome meets quality standards"""
    filepath = GENOMES_DIR / f"{args.name}.json"
    
    if not filepath.exists():
        print(f"❌ Genome not found: {args.name}")
        return False
    
    with open(filepath) as f:
        genome = json.load(f)
    
    outcome = genome.get("outcome", {})
    checks = [
        ("Success rate >= 0.8", outcome.get("success_rate", 0) >= 0.8),
        ("Sample size >= 3", outcome.get("sample_size", 0) >= 3),
        ("Has task type", bool(genome.get("task_type"))),
        ("Has approach steps", len(genome.get("approach", {}).get("steps", [])) > 0),
    ]
    
    print(f"\n✅ Validation for {args.name}:")
    for check, passed in checks:
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")
    
    all_passed = all(p for _, p in checks)
    if all_passed:
        print("\n✅ Genome is valid and ready for sharing")
    else:
        print("\n⚠️  Genome needs improvement before sharing")
    
    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Genome Manager - GEP genome lifecycle management")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new genome")
    create_parser.add_argument("--name", required=True, help="Genome name")
    create_parser.add_argument("--task-type", required=True, help="Task type (research, debug, etc.)")
    create_parser.add_argument("--steps", help="Comma-separated steps")
    create_parser.add_argument("--tools", help="Comma-separated tools")
    create_parser.add_argument("--prompts", help="Comma-separated prompts")
    create_parser.add_argument("--success-rate", type=float, help="Success rate (0-1)")
    create_parser.add_argument("--duration", type=int, help="Average duration in seconds")
    create_parser.add_argument("--satisfaction", type=float, help="User satisfaction (0-1)")
    create_parser.add_argument("--sample-size", type=int, help="Sample size")
    create_parser.add_argument("--parent", help="Parent genome ID")
    create_parser.add_argument("--tags", help="Comma-separated tags")
    
    # List command
    subparsers.add_parser("list", help="List all genomes")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get a specific genome")
    get_parser.add_argument("name", help="Genome name")
    
    # Mutate command
    mutate_parser = subparsers.add_parser("mutate", help="Create a mutated copy")
    mutate_parser.add_argument("name", help="Parent genome name")
    mutate_parser.add_argument("--type", dest="mutation_type", default="evolution",
                               choices=["evolution", "adaptation", "specialization"],
                               help="Mutation type")
    mutate_parser.add_argument("--changes", help="Description of changes")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate genome quality")
    validate_parser.add_argument("name", help="Genome name")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_genome(args)
    elif args.command == "list":
        list_genomes(args)
    elif args.command == "get":
        get_genome(args)
    elif args.command == "mutate":
        mutate_genome(args)
    elif args.command == "validate":
        validate_genome(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
