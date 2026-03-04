import json
from pathlib import Path

TARGET = "Coffee machine TLC"
path = Path('earl_mind.json')
data = json.loads(path.read_text(encoding='utf-8'))
takes = data.get('earl_unplugged', [])
match = None
for idx, take in enumerate(takes):
    if take.get('topic') == TARGET:
        match = idx
        break
if match is not None:
    takes.insert(0, takes.pop(match))
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Moved '{TARGET}' to top")
else:
    print(f"Take '{TARGET}' not found")
