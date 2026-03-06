#!/usr/bin/env python3
import argparse
import re
import shutil
from pathlib import Path


def detect_prefix(src: Path) -> str:
    p = str(src)
    if p.startswith('/mnt/c/Users/'):
        return 'c-'
    # Treat everything else as WSL/Linux path
    return 'wsl-'


def safe_name(src: Path) -> str:
    p = str(src)
    p = p.lstrip('/')
    p = p.replace('\\', '/')
    p = p.replace('/', '-')
    p = p.lower()
    # keep a-z0-9._-
    p = re.sub(r'[^a-z0-9._-]+', '-', p)
    p = re.sub(r'-{2,}', '-', p).strip('-')

    prefix = detect_prefix(src)
    if not p.startswith(prefix):
        p = prefix + p
    return p


def copy_one(src: Path, dest_dir: Path) -> Path:
    if not src.exists():
        raise FileNotFoundError(str(src))
    if src.is_dir():
        raise IsADirectoryError(str(src))

    dest_dir.mkdir(parents=True, exist_ok=True)
    out = dest_dir / safe_name(src)

    # Avoid overwrite by suffixing if needed
    if out.exists():
        stem = out.stem
        suf = out.suffix
        i = 2
        while True:
            cand = out.with_name(f"{stem}--{i}{suf}")
            if not cand.exists():
                out = cand
                break
            i += 1

    shutil.copy2(src, out)
    return out


def read_env_file(path: Path) -> dict:
    """Very small dotenv-style parser for KEY=VALUE lines."""
    out: dict = {}
    if not path.exists():
        return out

    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            continue
        k, v = line.split('=', 1)
        k = k.strip()
        v = v.strip()
        # strip optional quotes
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        out[k] = v
    return out


def default_config_path() -> Path:
    # ~/.openclaw/skills/onedrive-integration/config.env
    return Path(__file__).resolve().parent.parent / 'config.env'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default=None, help='Path to config.env (defaults to skill-local config.env)')
    ap.add_argument('--onedrive-root', default=None)
    ap.add_argument('--subdir', default=None, help='Destination folder within OneDrive (default: openclaw)')
    ap.add_argument('paths', nargs='+')
    args = ap.parse_args()

    cfg_path = Path(args.config).expanduser() if args.config else default_config_path()
    cfg = read_env_file(cfg_path)

    onedrive_root = args.onedrive_root or cfg.get('ONEDRIVE_ROOT')
    if not onedrive_root:
        raise SystemExit(
            'ONEDRIVE_ROOT is not set. Provide --onedrive-root or create config.env next to the skill.'
        )

    subdir = args.subdir or cfg.get('ONEDRIVE_SUBDIR') or 'openclaw'

    onedrive_root_p = Path(onedrive_root).expanduser()
    dest_dir = onedrive_root_p / subdir

    outs = []
    for p in args.paths:
        src = Path(p)
        outs.append(copy_one(src, dest_dir))

    for o in outs:
        print(str(o))


if __name__ == '__main__':
    main()
