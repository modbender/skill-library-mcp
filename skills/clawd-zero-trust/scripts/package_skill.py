#!/usr/bin/env python3
import os
import sys
import zipfile
import hashlib


def package(skill_dir: str, out_file: str) -> None:
    skill_dir = os.path.abspath(skill_dir)
    out_file = os.path.abspath(out_file)
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    root_name = os.path.basename(skill_dir)
    with zipfile.ZipFile(out_file, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for base, _, files in os.walk(skill_dir):
            for name in files:
                if name.endswith('.pyc'):
                    continue
                full = os.path.join(base, name)
                rel = os.path.relpath(full, skill_dir)
                arc = os.path.join(root_name, rel)
                zf.write(full, arc)
    
    # Calculate and output SHA256 checksum for integrity verification
    sha256_hash = hashlib.sha256()
    with open(out_file, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256_hash.update(chunk)
    
    return sha256_hash.hexdigest()


def main() -> int:
    if len(sys.argv) != 3:
        print('Usage: package_skill.py <skill_dir> <out_file>', file=sys.stderr)
        return 2
    checksum = package(sys.argv[1], sys.argv[2])
    print(f'packaged: {sys.argv[2]}')
    print(f'sha256: {checksum}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
