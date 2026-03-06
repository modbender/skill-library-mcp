#!/usr/bin/env python3
import argparse, base64
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

p = argparse.ArgumentParser()
p.add_argument('--note-b64', required=True)
p.add_argument('--key-file', help='single key file (32-byte)')
p.add_argument('--keyring-dir', help='directory with versioned keys + registry')
p.add_argument('--prefix', default='NXP1')
args = p.parse_args()

raw = base64.b64decode(args.note_b64)
pre = args.prefix.encode('utf-8')
if not raw.startswith(pre):
    raise SystemExit('invalid prefix')
nonce = raw[len(pre):len(pre)+12]
ct = raw[len(pre)+12:]

candidates = []
if args.key_file:
    candidates.append(Path(args.key_file).read_bytes())
elif args.keyring_dir:
    reg = Path(args.keyring_dir) / 'algorand-note-key-registry.json'
    if reg.exists():
        import json
        meta = json.loads(reg.read_text(encoding='utf-8'))
        for k in reversed(meta.get('keys', [])):
            kp = Path(args.keyring_dir) / k['file']
            if kp.exists():
                candidates.append(kp.read_bytes())
    else:
        for kp in sorted(Path(args.keyring_dir).glob('algorand-note-key-v*.bin'), reverse=True):
            candidates.append(kp.read_bytes())
else:
    raise SystemExit('provide --key-file or --keyring-dir')

for i, key in enumerate(candidates, start=1):
    try:
        pt = AESGCM(key).decrypt(nonce, ct, None)
        print(pt.decode('utf-8', 'replace'))
        raise SystemExit(0)
    except Exception:
        continue

raise SystemExit('decryption failed with provided key material')
