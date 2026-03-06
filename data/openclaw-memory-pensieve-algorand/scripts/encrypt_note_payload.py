#!/usr/bin/env python3
import argparse, base64, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

p = argparse.ArgumentParser()
p.add_argument('--key-file', required=True, help='Path to 32-byte key file')
p.add_argument('--payload', required=True, help='JSON payload string')
p.add_argument('--prefix', default='NXP1')
args = p.parse_args()

key = open(args.key_file, 'rb').read()
if len(key) != 32:
    raise SystemExit('Key must be 32 bytes for AES-256-GCM')
nonce = os.urandom(12)
ct = AESGCM(key).encrypt(nonce, args.payload.encode('utf-8'), None)
out = args.prefix.encode('utf-8') + nonce + ct
print(base64.b64encode(out).decode('ascii'))
