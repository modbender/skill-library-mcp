#!/usr/bin/env python3
"""Trust Verifier — Assess and attest skill trustworthiness."""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


TRUST_LEVELS = {
    "VERIFIED": {"score_min": 80, "description": "Meets all trust criteria"},
    "TRUSTED": {"score_min": 60, "description": "Most signals positive"},
    "UNKNOWN": {"score_min": 40, "description": "Insufficient data"},
    "SUSPICIOUS": {"score_min": 20, "description": "Trust signals failed"},
    "UNTRUSTED": {"score_min": 0, "description": "Multiple trust failures"},
}


def _hash_file(path):
    """Compute SHA-256 of a file."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def _validate_skill_path(skill_path):
    """Validate and resolve skill path — prevent path traversal."""
    skill_path = Path(os.path.realpath(str(skill_path)))
    # Must be under ~/.openclaw/skills/ or a reasonable location
    if not skill_path.is_dir():
        print(f"Error: {skill_path} is not a directory", file=sys.stderr)
        sys.exit(1)
    return skill_path


def _hash_directory(skill_path):
    """Compute hashes for all files in a skill directory."""
    skill_path = Path(os.path.realpath(str(skill_path)))
    hashes = {}
    for root, dirs, files in os.walk(skill_path, followlinks=False):
        # Skip __pycache__ and .git
        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'node_modules')]
        for f in sorted(files):
            fpath = Path(root) / f
            # Skip symlinks — prevent reading files outside skill directory
            if fpath.is_symlink():
                continue
            real = os.path.realpath(str(fpath))
            if not real.startswith(os.path.realpath(str(skill_path))):
                continue
            rel = str(fpath.relative_to(skill_path))
            hashes[rel] = _hash_file(str(fpath))
    return hashes


def assess(skill_path):
    """Assess trust signals for a skill."""
    skill_path = _validate_skill_path(skill_path)
    signals = []
    score = 0

    # 1. Check SKILL.md exists and has proper frontmatter
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        with open(skill_md) as f:
            content = f.read()
        if content.startswith("---"):
            signals.append({"signal": "valid_manifest", "passed": True, "detail": "SKILL.md has proper YAML frontmatter"})
            score += 15
        else:
            signals.append({"signal": "valid_manifest", "passed": False, "detail": "SKILL.md missing YAML frontmatter"})

        # Check description
        if 'description:' in content:
            signals.append({"signal": "has_description", "passed": True, "detail": "Skill has a description"})
            score += 10
        else:
            signals.append({"signal": "has_description", "passed": False, "detail": "No description found"})
    else:
        signals.append({"signal": "valid_manifest", "passed": False, "detail": "No SKILL.md found"})

    # 2. Check for scripts
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        script_files = list(scripts_dir.glob("*"))
        if script_files:
            signals.append({"signal": "has_scripts", "passed": True, "detail": f"{len(script_files)} script(s) found"})
            score += 10
        else:
            signals.append({"signal": "has_scripts", "passed": False, "detail": "Empty scripts directory"})
    else:
        signals.append({"signal": "has_scripts", "passed": False, "detail": "No scripts directory"})

    # 3. Check for suspicious patterns in code
    suspicious_patterns = [
        (r'eval\(|exec\(', "Dynamic code execution"),
        (r'subprocess.*shell\s*=\s*True', "Shell injection risk"),
        (r'os\.system', "Direct shell execution"),
        (r'base64\.b64decode', "Base64 decoding"),
    ]

    code_clean = True
    for root, dirs, files in os.walk(skill_path, followlinks=False):
        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'node_modules')]
        for f in files:
            if f.endswith(('.py', '.js', '.ts', '.sh')):
                fpath = Path(root) / f
                if fpath.is_symlink():
                    signals.append({"signal": "no_symlinks", "passed": False, "detail": f"Symlink: {f}"})
                    score -= 15
                    continue
                try:
                    with open(fpath) as fh:
                        code = fh.read()
                    for pattern, desc in suspicious_patterns:
                        if re.search(pattern, code):
                            signals.append({"signal": "clean_code", "passed": False, "detail": f"{desc} in {f}"})
                            code_clean = False
                            score -= 10
                except (UnicodeDecodeError, PermissionError):
                    pass

    if code_clean:
        signals.append({"signal": "clean_code", "passed": True, "detail": "No suspicious patterns found"})
        score += 20

    # 4. Check file count and size (reasonable for a skill)
    total_files = 0
    total_size = 0
    for root, dirs, files in os.walk(skill_path):
        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'node_modules')]
        total_files += len(files)
        total_size += sum(os.path.getsize(os.path.join(root, f)) for f in files)

    if total_files < 50 and total_size < 1000000:
        signals.append({"signal": "reasonable_size", "passed": True, "detail": f"{total_files} files, {total_size} bytes"})
        score += 10
    else:
        signals.append({"signal": "reasonable_size", "passed": False, "detail": f"{total_files} files, {total_size} bytes — unusually large"})

    # 5. Check for README/documentation
    has_docs = (skill_path / "README.md").exists() or (skill_path / "SKILL.md").exists()
    if has_docs:
        signals.append({"signal": "documented", "passed": True, "detail": "Documentation present"})
        score += 10
    else:
        signals.append({"signal": "documented", "passed": False, "detail": "No documentation"})

    # 6. No binary files
    binary_exts = {'.exe', '.dll', '.so', '.dylib', '.bin', '.wasm', '.pyc', '.pyo'}
    has_binaries = False
    for root, dirs, files in os.walk(skill_path):
        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'node_modules')]
        for f in files:
            if Path(f).suffix.lower() in binary_exts:
                has_binaries = True
                signals.append({"signal": "no_binaries", "passed": False, "detail": f"Binary file: {f}"})
                score -= 15

    if not has_binaries:
        signals.append({"signal": "no_binaries", "passed": True, "detail": "No binary files"})
        score += 15

    # Clamp score
    score = max(0, min(100, score))

    # Determine trust level
    trust_level = "UNTRUSTED"
    for level, info in TRUST_LEVELS.items():
        if score >= info["score_min"]:
            trust_level = level
            break

    return {
        "skill": skill_path.name,
        "trust_level": trust_level,
        "score": score,
        "signals": signals,
        "assessed_at": datetime.now(timezone.utc).isoformat(),
    }


def generate_attestation(skill_path, output_path=None):
    """Generate a trust attestation for a skill (hash manifest).

    NOTE: These attestations use SHA-256 hashes but are NOT cryptographically signed.
    They detect accidental modifications but cannot prevent deliberate tampering by
    an attacker with file write access. For tamper-proof attestations, use HMAC or
    digital signatures with a key stored outside the skill filesystem.
    """
    skill_path = _validate_skill_path(skill_path)
    file_hashes = _hash_directory(skill_path)

    # Compute overall hash
    combined = json.dumps(file_hashes, sort_keys=True)
    overall_hash = hashlib.sha256(combined.encode()).hexdigest()

    attestation = {
        "skill": skill_path.name,
        "version": "1.0",
        "attestor": "arc-trust-verifier",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "overall_hash": overall_hash,
        "file_hashes": file_hashes,
        "file_count": len(file_hashes),
    }

    if output_path:
        with open(output_path, 'w') as f:
            json.dump(attestation, f, indent=2)
        print(f"Attestation written to {output_path}")
    else:
        print(json.dumps(attestation, indent=2))

    return attestation


def verify_attestation(attestation_path, skill_path):
    """Verify a skill against an existing attestation."""
    skill_path = Path(skill_path)

    with open(attestation_path) as f:
        expected = json.load(f)

    current_hashes = _hash_directory(skill_path)
    expected_hashes = expected.get("file_hashes", {})

    mismatches = []
    new_files = []
    missing_files = []

    for path, hash_val in current_hashes.items():
        if path not in expected_hashes:
            new_files.append(path)
        elif hash_val != expected_hashes[path]:
            mismatches.append({"file": path, "expected": expected_hashes[path][:16], "actual": hash_val[:16]})

    for path in expected_hashes:
        if path not in current_hashes:
            missing_files.append(path)

    valid = not mismatches and not missing_files

    result = {
        "valid": valid,
        "skill": skill_path.name,
        "attestation_date": expected.get("created_at"),
        "mismatches": len(mismatches),
        "new_files": len(new_files),
        "missing_files": len(missing_files),
    }

    if mismatches:
        result["mismatch_details"] = mismatches
    if new_files:
        result["new_file_list"] = new_files
    if missing_files:
        result["missing_file_list"] = missing_files

    return result


def check_deps(skill_path):
    """Check trust of skill dependencies."""
    skill_path = Path(skill_path)
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        print("No SKILL.md found")
        return

    with open(skill_md) as f:
        content = f.read()

    # Look for dependency references
    deps = []
    dep_patterns = [
        r'requires.*?skills?\s*:\s*\[(.*?)\]',
        r'depends.*?:\s*\[(.*?)\]',
        r'import\s+(\S+)',
    ]

    for pattern in dep_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        for m in matches:
            items = [d.strip().strip('"').strip("'") for d in m.split(",")]
            deps.extend(items)

    if deps:
        print(f"Dependencies found: {deps}")
        for dep in deps:
            dep_path = Path.home() / ".openclaw" / "skills" / dep
            if dep_path.exists():
                result = assess(dep_path)
                print(f"  {dep}: {result['trust_level']} (score: {result['score']})")
            else:
                print(f"  {dep}: NOT INSTALLED (cannot verify)")
    else:
        print("No explicit dependencies found in SKILL.md")


def main():
    parser = argparse.ArgumentParser(description="Trust Verifier")
    sub = parser.add_subparsers(dest="command")

    p_assess = sub.add_parser("assess", help="Assess skill trust")
    p_assess.add_argument("--path", required=True, help="Skill directory")
    p_assess.add_argument("--json", action="store_true")

    p_attest = sub.add_parser("attest", help="Generate trust attestation")
    p_attest.add_argument("--path", required=True, help="Skill directory")
    p_attest.add_argument("--output", "-o", help="Output file")

    p_verify = sub.add_parser("verify", help="Verify attestation")
    p_verify.add_argument("--attestation", required=True, help="Attestation JSON file")
    p_verify.add_argument("--path", required=True, help="Skill directory")

    p_deps = sub.add_parser("deps", help="Check dependency trust")
    p_deps.add_argument("--path", required=True, help="Skill directory")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "assess":
        result = assess(args.path)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            level = result["trust_level"]
            score = result["score"]
            print(f"\n{level} — Score: {score}/100 — {result['skill']}")
            print()
            for s in result["signals"]:
                icon = "PASS" if s["passed"] else "FAIL"
                print(f"  [{icon}] {s['detail']}")

    elif args.command == "attest":
        generate_attestation(args.path, args.output)

    elif args.command == "verify":
        result = verify_attestation(args.attestation, args.path)
        if result["valid"]:
            print(f"VERIFIED — Skill matches attestation from {result['attestation_date']}")
        else:
            print(f"VERIFICATION FAILED")
            if result["mismatches"]:
                print(f"  {result['mismatches']} file(s) changed")
            if result["missing_files"]:
                print(f"  {result['missing_files']} file(s) missing")
            if result["new_files"]:
                print(f"  {result['new_files']} new file(s) added")

    elif args.command == "deps":
        check_deps(args.path)


if __name__ == "__main__":
    main()
