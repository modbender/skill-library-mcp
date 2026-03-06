#!/usr/bin/env python3
import argparse, base64, json, os
from datetime import datetime, timezone
from pathlib import Path

p = argparse.ArgumentParser(description='Rotate note encryption key with version registry')
p.add_argument('--keyring-dir', required=True, help='Directory where note keys are stored')
p.add_argument('--prefix', default='algorand-note-key')
args = p.parse_args()

kdir = Path(args.keyring_dir)
kdir.mkdir(parents=True, exist_ok=True)
registry = kdir / f'{args.prefix}-registry.json'

if registry.exists():
    meta = json.loads(registry.read_text(encoding='utf-8'))
else:
    meta = {'current_version': 0, 'keys': []}

new_version = int(meta.get('current_version', 0)) + 1
fname = f'{args.prefix}-v{new_version}.bin'
path = kdir / fname
key = os.urandom(32)
path.write_bytes(key)
os.chmod(path, 0o600)

entry = {
    'version': new_version,
    'file': fname,
    'created_at': datetime.now(timezone.utc).isoformat(),
    'fingerprint_b64': base64.b64encode(key[:8]).decode('ascii')
}
meta['current_version'] = new_version
meta['keys'] = meta.get('keys', []) + [entry]
registry.write_text(json.dumps(meta, indent=2), encoding='utf-8')
os.chmod(registry, 0o600)

print(json.dumps({'ok': True, 'current_version': new_version, 'key_file': str(path), 'registry': str(registry)}))
