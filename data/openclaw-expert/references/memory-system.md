# Memory-System — Deep Dive

## Architektur-Überblick

OpenClaw nutzt ein dateibasiertes Markdown-Memory-System mit optionaler semantischer Suche.
Kernprinzip: **Dateien sind die Quelle der Wahrheit** — der Agent behält nur, was auf Disk geschrieben wird.

```
Workspace/
├── MEMORY.md              # Langzeit (kuratiert, ~100 Zeilen, nur private Sessions)
└── memory/
    ├── 2026-02-15.md      # Tages-Log (append-only)
    ├── 2026-02-16.md
    └── ...
```

### Zwei Ebenen
1. **MEMORY.md** — Kuratierte, dauerhafte Fakten (Entscheidungen, Präferenzen). In jede private Session geladen.
2. **memory/YYYY-MM-DD.md** — Tagesnotizen, Running-Log. Über memorySearch abrufbar.

---

## Memory Flush (automatisch vor Compaction)

Wenn eine Session sich der Context-Window-Grenze nähert, triggert OpenClaw einen stillen Turn:
- Agent wird aufgefordert, wichtige Infos in `memory/YYYY-MM-DD.md` zu schreiben
- Standard-Antwort: `NO_REPLY` (User sieht nichts)

### Konfiguration
```json5
agents: {
  defaults: {
    compaction: {
      reserveTokensFloor: 20000,
      memoryFlush: {
        enabled: true,                 // Default: true
        softThresholdTokens: 4000,     // Wann der Flush triggert
        systemPrompt: "Session nearing compaction. Store durable memories now.",
        prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with NO_REPLY if nothing to store.",
      },
    },
  },
},
```

### Flush-Details
- Triggert wenn: `tokenEstimate > contextWindow - reserveTokensFloor - softThresholdTokens`
- Ein Flush pro Compaction-Zyklus (in sessions.json getrackt)
- Workspace muss schreibbar sein (`workspaceAccess: "ro"` oder `"none"` → Flush übersprungen)

---

## Session Compaction

Wenn das Context-Window voll ist, kompaktiert OpenClaw ältere Nachrichten:
- Zusammenfassung/Truncation älterer Messages
- **Risiko**: Wichtige Details gehen verloren wenn nicht in Memory geschrieben
- **memoryFlush** rettet Infos vor der Compaction

### Compaction-Modi
```json5
compaction: {
  mode: "safeguard",  // "safeguard" = Flush + Compaction
                       // "full" = Aggressivere Compaction
                       // "off" = Keine Compaction (Risiko: Token-Limit-Fehler)
}
```

---

## Semantic Memory Search (memorySearch)

Baut einen kleinen Vektor-Index über MEMORY.md und memory/*.md für semantische Abfragen.

### Konfiguration
```json5
agents: {
  defaults: {
    memorySearch: {
      enabled: true,              // Default: true
      provider: null,             // null = Auto-Detect
      // Auto-Detect-Reihenfolge:
      // 1. local (wenn modelPath existiert)
      // 2. openai (wenn Key vorhanden)
      // 3. gemini (wenn Key vorhanden)
      // 4. disabled
      local: {
        modelPath: null,          // Pfad zu GGUF-Embedding-Modell
      },
      extraPaths: [               // Zusätzliche Pfade indexieren
        "../team-docs",
        "/srv/shared-notes/overview.md",
      ],
    },
  },
},
```

### Funktionsweise
- Dateien werden in ~400-Token-Chunks mit 80-Token-Overlap aufgeteilt
- Vektor-Embeddings in SQLite gespeichert (sqlite-vec für Beschleunigung)
- Datei-Änderungen werden automatisch erkannt (File Watcher, debounced)
- **Erster Aufruf kann langsam sein**: QMD lädt ggf. GGUF-Modelle herunter

### Temporal Decay (Zeitverfall)
Memory-Ergebnisse werden nach Aktualität gewichtet:

| Alter | Decay-Faktor |
|---|---|
| Heute | 1.00 |
| 7 Tage | ~0.85 |
| 30 Tage | ~0.50 |
| 148 Tage | ~0.03 |

Score = `semantic_score × decay_factor`

→ Neuere Erinnerungen werden bevorzugt, auch wenn ältere semantisch besser passen.

### Datum-Quellen
- `memory/YYYY-MM-DD.md` → Datum aus Dateiname
- Session-Transkripte → Fallback auf mtime

---

## Session-Transkript-Indexierung

OpenClaw kann vergangene Konversationen automatisch speichern und indexieren:
- Session wird als timestamped Datei gespeichert (Slug per LLM generiert)
- Transkripte werden indexiert und über memorySearch durchsuchbar
- Erlaubt: "Was haben wir letzte Woche zu Thema X besprochen?"

---

## Bekannte Limitierungen

1. **Kein Relationship-Reasoning**: Memory findet ähnlichen Text, versteht aber keine Beziehungen
   (z.B. "Alice managt das Auth-Team" + "Wer kümmert sich um Permissions?" → keine automatische Verbindung)
2. **Cross-Projekt-Noise**: Bei mehreren Projekten können irrelevante Ergebnisse auftauchen
3. **Compaction-Verlust**: Was nicht in Memory geschrieben ist, geht bei Compaction verloren
4. **MEMORY.md im Context**: Wird in den Context geladen → kann selbst kompaktiert werden bei langen Sessions

---

## Verbesserungen / Community-Plugins

### Cognee Knowledge Graph
- Fügt eine Graph-Datenbank über Memory-Dateien
- Versteht Beziehungen zwischen Fakten
- `pip install cognee-mcp` + Config in openclaw.json

### Mem0 Persistent Memory
- Speichert Memory extern, außerhalb des Context-Windows
- Compaction kann Mem0-Memories nicht zerstören
- Long-Term + Short-Term Memory Scopes
- Config: `skills.entries["openclaw-mem0"].enabled: true`

---

## Tipps für effektives Memory

1. **Explizit schreiben lassen**: "Merke dir, dass ich Docker bevorzuge" → Agent schreibt in MEMORY.md/USER.md
2. **Regelmäßig aufräumen**: Veraltete memory/*.md Dateien archivieren
3. **MEMORY.md klein halten**: Max ~100 Zeilen, nur Dauerhaftes
4. **Präferenzen in USER.md**: Nicht in Memory, sondern dort wo sie jede Session geladen werden
5. **Memory-Review im Heartbeat**: HEARTBEAT.md-Aufgabe "Memory konsolidieren" hinzufügen
