import json
from pathlib import Path
path = Path('earl_mind.json')
mind = json.loads(path.read_text(encoding='utf-8'))
mind['identity']['current_vibe'] = 'Text me on Telegram to add stuff.'
path.write_text(json.dumps(mind, indent=2, ensure_ascii=False), encoding='utf-8')
