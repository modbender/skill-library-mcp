# AssemblyAI Transcriber 🎙️

> Audio-Transkription mit Speaker Diarization für OpenClaw

## Was macht dieser Skill?

Transkribiert Audio-Dateien und erkennt automatisch verschiedene Sprecher:

```
Speaker A [00:00]: Hallo, willkommen zum Meeting!
Speaker B [00:03]: Danke, freut mich dabei zu sein.
Speaker A [00:06]: Lass uns starten...
```

## Features

- 🎯 **Speaker Diarization** - Erkennt wer spricht
- 🌍 **100+ Sprachen** - Automatische Spracherkennung
- ⏱️ **Timestamps** - Zeitstempel pro Äusserung
- 📁 **Alle Formate** - MP3, WAV, M4A, FLAC, OGG, WEBM
- 💬 **Telegram Support** - Sprachnachrichten direkt transkribieren

## Setup

1. Account erstellen: https://www.assemblyai.com/
2. API Key holen (100 Min/Monat kostenlos!)
3. Config erstellen:

```json
{
  "api_key": "YOUR_API_KEY"
}
```

Speichern als `~/.assemblyai_config.json` oder im Workspace.

## Verwendung

```
Transkribiere /pfad/zur/aufnahme.mp3
Transkribiere diese Audio-Datei mit Speaker Labels
```

Oder einfach eine Telegram-Sprachnachricht senden!

## Kosten

- **Free**: 100 Min/Monat
- **Danach**: ~CHF 0.01/Minute

## Beispiel-Output

```markdown
## Transkript

*Sprache: DE*
*Dauer: 02:34*

**Speaker A** [00:00]: Guten Tag, herzlich willkommen.
**Speaker B** [00:04]: Vielen Dank für die Einladung.
**Speaker A** [00:08]: Ich freue mich, dass es geklappt hat...
```

---

*Made with 🦭 by xenofex7*
