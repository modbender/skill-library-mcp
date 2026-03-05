#!/usr/bin/env python3
import argparse, base64, json
from algosdk.v2client import algod
from algosdk import encoding

p = argparse.ArgumentParser(description='Submit pre-signed Algorand tx for memory anchor (no private keys handled)')
p.add_argument('--algod-url', required=True)
p.add_argument('--algod-token', default='')
p.add_argument('--signed-tx-b64', required=True, help='Signed tx bytes (base64), produced by external wallet/signer')
args = p.parse_args()

stx_bytes = base64.b64decode(args.signed_tx_b64)
client = algod.AlgodClient(args.algod_token, args.algod_url)
txid = client.send_raw_transaction(stx_bytes)
print(json.dumps({'ok': True, 'txid': txid, 'signed_tx_bytes': len(stx_bytes)}))
