#!/usr/bin/env python3
import argparse, base64, json, urllib.parse, urllib.request

p = argparse.ArgumentParser(description='Fetch tx note from Algorand indexer by txid')
p.add_argument('--indexer-url', required=True, help='e.g. https://mainnet-idx.algonode.cloud')
p.add_argument('--txid', required=True)
args = p.parse_args()

url = args.indexer_url.rstrip('/') + '/v2/transactions/' + urllib.parse.quote(args.txid)
with urllib.request.urlopen(url, timeout=20) as r:
    obj = json.load(r)

tx = obj.get('transaction', {})
note_b64 = tx.get('note', '')
out = {
    'ok': True,
    'txid': tx.get('id', args.txid),
    'sender': tx.get('sender'),
    'round_time': tx.get('round-time'),
    'note_b64': note_b64,
    'note_bytes': len(base64.b64decode(note_b64)) if note_b64 else 0
}
print(json.dumps(out))
