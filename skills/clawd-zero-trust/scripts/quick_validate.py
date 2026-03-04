#!/usr/bin/env python3
import os
import sys

REQUIRED = [
    'SKILL.md',
    'scripts/egress-filter.sh',
    'scripts/audit.sh',
    'scripts/harden.sh',
    'scripts/release-gate.sh',
    'references/false-positives.md',
    'references/zero-trust-principles.md',
]


def main() -> int:
    if len(sys.argv) != 2:
      print('Usage: quick_validate.py <skill_dir>', file=sys.stderr)
      return 2
    skill_dir = os.path.abspath(sys.argv[1])
    missing = []
    for rel in REQUIRED:
        path = os.path.join(skill_dir, rel)
        if not os.path.exists(path):
            missing.append(rel)
    if missing:
        print('Missing required files:', file=sys.stderr)
        for m in missing:
            print(f' - {m}', file=sys.stderr)
        return 1
    print(f'quick_validate: OK ({skill_dir})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
