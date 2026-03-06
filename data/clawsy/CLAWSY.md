# CLAWSY — Kontext-Zugriff

## clawsy-service Session direkt lesen

Session-ID ermitteln:
```bash
cat /home/claw/.openclaw/agents/main/sessions/sessions.json | python3 -c "
import json,sys; d=json.load(sys.stdin)
s = d.get('agent:main:clawsy-service',{})
print(s.get('sessionFile',''))
"
```

Aktuelle Datei: `/home/claw/.openclaw/agents/main/sessions/669223f5-3bb7-45ed-99f8-a5cf60d3d8be.jsonl`

Letzten Inhalt lesen:
```bash
tail -50 <sessionFile> | python3 -c "
import json,sys,base64
for line in sys.stdin:
    try:
        obj = json.loads(line.strip())
        msg = obj.get('message',{})
        if msg.get('role') == 'user':
            for c in msg.get('content',[]):
                if c.get('type') == 'text': print('TEXT:', c['text'][:300])
                if c.get('type') == 'image':
                    open('/home/claw/.openclaw/workspace/clawsy_screenshot.jpg','wb').write(base64.b64decode(c['data']))
                    print('IMAGE: gespeichert')
    except: pass
"
```

Screenshot analysieren: `image(image='/home/claw/.openclaw/workspace/clawsy_screenshot.jpg')`
