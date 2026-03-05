# Skills — Entwicklung, Installation & Sicherheit

## Skill-Typen

| Typ | Pfad | Beschreibung |
|---|---|---|
| Bundled | Im npm-Paket | Mitgelieferte Skills |
| Managed | `~/.openclaw/skills/` | Via ClawHub installiert |
| Workspace | `<workspace>/skills/` | Manuell erstellt, pro Agent |

---

## Skills installieren

```bash
# ClawHub durchsuchen
clawhub search "memory"
clawhub search "calendar"

# Installieren
clawhub install <skill-name>

# Updaten
clawhub update <skill-name>
clawhub update --all

# Nach Installation: Skills neu laden
openclaw skills reload
# ODER Gateway neu starten (Skills werden erst in neuer Session aktiv!)
openclaw gateway restart

# Installierte Skills anzeigen
openclaw skills list
```

### Skills in openclaw.json konfigurieren
```json5
skills: {
  install: {
    nodeManager: "npm",       // "npm" | "pnpm"
  },
  entries: {
    "skill-name": {
      enabled: true,
      apiKey: "LLM_API_KEY",  // Optional: API-Key für diesen Skill
      env: {                   // Optional: Environment-Variables
        "TOOL_TOKEN": "xxx",
        "SERVICE_API_KEY": "yyy",
      },
    },
  },
},
```

---

## Eigene Skills erstellen

### SKILL.md-Format
```markdown
---
name: mein-skill
description: >
  Beschreibung was der Skill tut und wann er getriggert werden soll.
  Beispiel-Trigger-Phrasen hier auflisten.
---

# Mein Skill

## Anweisungen
Hier stehen die Anweisungen für den Agent...

## Beispiele
Input: "Mach X"
Output: Y
```

### Verzeichnis-Struktur
```
mein-skill/
├── SKILL.md           # Pflicht: Anweisungen
├── scripts/           # Optional: Ausführbare Skripte
├── references/        # Optional: Referenz-Dokumente
└── assets/            # Optional: Templates, Icons
```

### Workspace-Skills erstellen
```bash
mkdir -p ~/.openclaw/workspace/skills/mein-skill
# SKILL.md dort anlegen
# Skills neu laden:
openclaw skills reload
```

### Skills teilen
```bash
# Auf ClawHub veröffentlichen (nach Review!)
# Oder als Git-Repo teilen
```

---

## Skill-Sicherheit (KRITISCH!)

ClawHub hostet 5700+ Skills (Stand 02/2026). Nicht alle sind sicher.

### Risiken
- Prompt-Injections in SKILL.md
- Tool-Poisoning (Skill nutzt Tools für böswillige Zwecke)
- Versteckte Malware-Payloads in scripts/
- Unsichere Datenverarbeitung

### Schutzmaßnahmen
1. **Quellcode reviewen** vor Installation
2. **ClawHub "Hide Suspicious"** aktivieren
3. **VirusTotal-Report** auf ClawHub-Seite prüfen
4. **Code in Claude einfügen** und nach Risiken fragen lassen
5. **Sandbox nutzen**: `tools.exec.host: "sandbox"`
6. **Nur verifizierte Skills** von bekannten Autoren installieren

### Nützliche Community-Skills (geprüft)
- `memory-complete` — Vollständiges Memory-Protokoll mit Auto-Capture
- `agent-builder` — Agent-Workspace-Generator
- `soul-md` — Persona/Identity-Management
- `context-anchor` — Recovery nach Context-Compaction
- `claw-roam` — Workspace-Sync zwischen Maschinen

---

## Skill-Troubleshooting

```bash
# Skills nicht sichtbar?
openclaw skills list                    # Prüfen ob Skill gelistet
ls ~/.openclaw/workspace/skills/       # Workspace-Skills prüfen
ls ~/.openclaw/skills/                  # Managed-Skills prüfen

# Skill nicht aktiv nach Installation?
openclaw gateway restart               # Skills erst in neuer Session!

# Nur 1 von 6 Skills registriert?
# → SKILL.md-Format prüfen: name + description im YAML-Frontmatter Pflicht
# → Kein Syntax-Fehler im YAML (Doppelpunkt in description escapen!)
```
