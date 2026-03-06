---
name: TechPulse
description: "Мониторинг трендов: IoT, EV, Games, DIY, Tech."
---

# TechPulse

Мониторинг трендов: IoT, EV, Games, DIY, Tech.

## Установка

```bash
mkdir -p ~/.openclaw/skills/techpulse
unzip techpulse.zip -d ~/.openclaw/skills/
openclaw restart
```

## Использование

```
python3 main.py           # все категории
python3 main.py ev        # только EV
python3 main.py iot       # только IoT
python3 main.py games     # только Games
python3 main.py diy       # только DIY
python3 main.py tech      # только Tech
```

## Источники

Reddit (публичный API, без авторизации):
- r/homeautomation, r/IOT (IoT)
- r/electricvehicles, r/teslamotors (EV)
- r/gaming, r/gamedev (Games)
- r/arduino, r/raspberry_pi (DIY)
- r/technology, r/artificial (Tech)
