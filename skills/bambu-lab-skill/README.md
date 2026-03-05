# Bambu Lab 3D-Drucker Skill

Steuerung und Überwachung von Bambu Lab 3D-Druckern über MQTT im lokalen Netzwerk.

## 🖨️ Unterstützte Modelle

- ✅ A1 (getestet)
- ✅ A1 Mini
- ✅ P1P / P1S  
- ✅ X1 / X1C

## 📋 Voraussetzungen

**Wichtig:** Der Drucker muss im **LAN-Mode** sein:

1. Drucker-Menü → Netzwerk → LAN-Only Mode
2. Access Code notieren (unter Settings)
3. IP-Adresse notieren (auf Display oder Router)

**Abhängigkeit installieren:**
```bash
# Für Python-Version (empfohlen)
pip3 install paho-mqtt

# ODER für Bash-Version
apt-get install mosquitto-clients
```

## ⚙️ Konfiguration

Standard-Konfiguration in `scripts/bambu.sh` oder `scripts/bambu.py`:
- **Host:** `192.168.30.103`
- **Port:** `8883` (MQTT over TLS)
- **Username:** `03919A3A2200009` (Seriennummer)
- **Passwort:** `33576961` (Access Code)
- **Model:** A1

## 🚀 Verwendung

### Status abfragen
```bash
./skills/bambu-lab/scripts/bambu.sh status
# oder
python3 ./skills/bambu-lab/scripts/bambu.py status
```

### Live-Überwachung
```bash
./skills/bambu-lab/scripts/bambu.sh watch
```

### Steuerung
```bash
./skills/bambu-lab/scripts/bambu.sh pause       # Pausieren
./skills/bambu-lab/scripts/bambu.sh resume      # Fortsetzen
./skills/bambu-lab/scripts/bambu.sh stop        # Abbrechen
./skills/bambu-lab/scripts/bambu.sh light on    # Licht an
./skills/bambu-lab/scripts/bambu.sh light off   # Licht aus
```

### Mit Benachrichtigungen
```bash
./skills/bambu-lab/scripts/bambu.sh notify
```

Dies zeigt:
- ✅ "DRUCK FERTIG" bei Abschluss
- ❌ Fehler bei Problemen
- 📊 Fortschritt alle 10%

## 📁 Dateien

- `scripts/bambu.sh` - Bash-Version (benötigt mosquitto-clients)
- `scripts/bambu.py` - Python-Version (empfohlen, benötigt paho-mqtt)
- `references/mqtt.md` - MQTT API Dokumentation

## 🔗 Links

- GitHub: https://github.com/photonixlaser-ux/bambu-lab-skill
- Bambu Lab Wiki: https://wiki.bambulab.com/en/home
