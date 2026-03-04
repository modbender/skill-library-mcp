#!/usr/bin/env python3
import json
from pathlib import Path
import requests

URL = 'https://api.yuboto.com/swagger/v1/swagger.json'
OUT = Path(__file__).resolve().parents[1] / 'references' / 'swagger_v1.json'

r = requests.get(URL, timeout=30)
r.raise_for_status()
obj = r.json()
OUT.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'[OK] saved {OUT}')
print(f"[INFO] paths={len(obj.get('paths', {}))}")
