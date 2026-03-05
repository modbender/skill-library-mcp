#!/usr/bin/env python3
import argparse, json
from algosdk.v2client import algod

p = argparse.ArgumentParser(description='Check wallet funding for anchoring operations')
p.add_argument('--algod-url', required=True)
p.add_argument('--algod-token', default='')
p.add_argument('--address', required=True)
p.add_argument('--required-microalgos', type=int, default=200000)
args = p.parse_args()

client = algod.AlgodClient(args.algod_token, args.algod_url)
info = client.account_info(args.address)
amount = info.get('amount', 0)
min_bal = info.get('min-balance', 0)
spendable = max(0, amount - min_bal)

print(json.dumps({
    'ok': True,
    'address': args.address,
    'amount_microalgos': amount,
    'min_balance_microalgos': min_bal,
    'spendable_microalgos': spendable,
    'required_microalgos': args.required_microalgos,
    'funded_for_ops': spendable >= args.required_microalgos
}))
