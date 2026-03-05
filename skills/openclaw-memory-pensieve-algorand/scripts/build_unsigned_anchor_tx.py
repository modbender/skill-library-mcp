#!/usr/bin/env python3
import argparse, json, os
from algosdk.v2client import algod
from algosdk.transaction import PaymentTxn
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from algosdk import encoding

p = argparse.ArgumentParser(description='Build unsigned 0-ALGO self-transfer anchor tx with encrypted note (for external signing)')
p.add_argument('--algod-url', required=True)
p.add_argument('--algod-token', default='')
p.add_argument('--address', required=True, help='Sender/receiver address (self-transfer)')
p.add_argument('--payload-file', required=True, help='JSON payload file')
p.add_argument('--note-key-file', required=True, help='32-byte AES key')
p.add_argument('--prefix', default='NXP1')
args = p.parse_args()

payload_obj = json.loads(open(args.payload_file,'r',encoding='utf-8').read())
payload_json = json.dumps(payload_obj, ensure_ascii=False, separators=(',', ':'))
key = open(args.note_key_file,'rb').read()
if len(key) != 32:
    raise SystemExit('note key must be 32 bytes')
nonce = os.urandom(12)
ct = AESGCM(key).encrypt(nonce, payload_json.encode('utf-8'), None)
note = args.prefix.encode('utf-8') + nonce + ct

client = algod.AlgodClient(args.algod_token, args.algod_url)
sp = client.suggested_params()
txn = PaymentTxn(sender=args.address, sp=sp, receiver=args.address, amt=0, note=note)
unsigned_b64 = encoding.msgpack_encode(txn)

print(json.dumps({
  'ok': True,
  'address': args.address,
  'note_bytes': len(note),
  'unsigned_txn_msgpack_b64': unsigned_b64,
  'instruction': 'Sign this unsigned transaction in an external wallet/signer, then submit with algorand_anchor_tx.py --signed-tx-b64 <...>'
}))
