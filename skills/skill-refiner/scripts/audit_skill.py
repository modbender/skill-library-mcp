#!/usr/bin/env python3
"""
Audit a skill directory for compliance with skill-creator requirements.
Usage: audit_skill.py <skill-dir>
Output: JSON with issues (blocking) and warnings (advisory)
"""

import sys
import re
import json
from pathlib import Path


EXTRANEOUS_FILES = {
    'README.md', 'INSTALLATION_GUIDE.md', 'QUICK_REFERENCE.md',
    'CHANGELOG.md', 'INSTALL.md', 'SETUP.md', 'CONTRIBUTING.md',
}
ALLOWED_SUBDIRS = {'scripts', 'references', 'assets', 'locales', 'docs'}
TRIGGER_KEYWORDS = ['use when', 'trigger', 'when to use', 'activate when', 'use for', 'when user', 'when asked']


def audit_skill(skill_dir: str) -> dict:
    path = Path(skill_dir)

    if not path.is_dir():
        return {"skill_dir": skill_dir, "error": "Not a directory", "issues": [], "warnings": [], "compliant": False}

    issues = []
    warnings = []
    skill_md = path / "SKILL.md"

    # 1. SKILL.md must exist
    if not skill_md.exists():
        return {"skill_dir": skill_dir, "skill_name": path.name, "issues": ["SKILL.md not found"], "warnings": [], "compliant": False}

    content = skill_md.read_text(encoding='utf-8')
    lines = content.splitlines()

    # 2. YAML frontmatter
    if not content.startswith('---'):
        issues.append("Missing YAML frontmatter (must start with ---)")
    else:
        end = content.find('\n---', 3)
        if end == -1:
            issues.append("Malformed YAML frontmatter (no closing ---)")
        else:
            fm = content[3:end].strip()

            has_name = bool(re.search(r'^name:\s*\S', fm, re.MULTILINE))
            has_desc = bool(re.search(r'^description:\s*\S', fm, re.MULTILINE))

            if not has_name:
                issues.append("Frontmatter missing required field: 'name'")
            if not has_desc:
                issues.append("Frontmatter missing required field: 'description'")

            # No extra fields allowed
            field_names = re.findall(r'^([a-zA-Z_]+)\s*:', fm, re.MULTILINE)
            extra = set(field_names) - {'name', 'description'}
            if extra:
                issues.append(f"Frontmatter has extra fields (only name+description allowed): {', '.join(sorted(extra))}")

            # Description quality: should mention when to use
            if has_desc:
                desc_block = re.search(r'^description:\s*(?:\|[-]?\s*\n)?([\s\S]+?)(?=\n[a-zA-Z_]+\s*:|$)', fm, re.MULTILINE)
                if desc_block:
                    desc_text = desc_block.group(1).strip().lower()
                    # Strip YAML block scalar indent
                    desc_text = re.sub(r'\n\s+', ' ', desc_text)
                    if not any(kw in desc_text for kw in TRIGGER_KEYWORDS):
                        warnings.append("Description doesn't clearly state trigger conditions (add 'Use when...' or similar)")
                    if len(desc_text) < 60:
                        warnings.append(f"Description is very short ({len(desc_text)} chars) — should be comprehensive for reliable triggering")

    # 3. Naming convention
    name = path.name
    if not re.match(r'^[a-z0-9][a-z0-9-]*$', name):
        issues.append(f"Directory name '{name}' violates convention (lowercase letters, digits, hyphens only; no leading hyphen)")
    if len(name) > 64:
        issues.append(f"Directory name too long ({len(name)} chars, max 64)")

    # 4. Extraneous files
    for fname in EXTRANEOUS_FILES:
        if (path / fname).exists():
            issues.append(f"Extraneous file: {fname} (remove — skills should not contain auxiliary docs)")

    # 5. Unexpected subdirectories
    for item in path.iterdir():
        if item.is_dir() and not item.name.startswith('.') and item.name not in ALLOWED_SUBDIRS:
            warnings.append(f"Unexpected subdirectory: {item.name}/ (allowed: scripts/, references/, assets/)")

    # 6. SKILL.md length
    if len(lines) > 500:
        warnings.append(f"SKILL.md is {len(lines)} lines — consider splitting into references/ files (recommended max: 500)")

    # 7. References linked from SKILL.md
    refs_dir = path / 'references'
    if refs_dir.exists():
        for ref in refs_dir.iterdir():
            if ref.is_file() and ref.name not in content:
                warnings.append(f"references/{ref.name} is not linked from SKILL.md")

    return {
        "skill_dir": str(path.resolve()),
        "skill_name": name,
        "issues": issues,
        "warnings": warnings,
        "compliant": len(issues) == 0,
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: audit_skill.py <skill-dir>", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(audit_skill(sys.argv[1]), indent=2))
