# ZUGFeRD Invoice Workflow

Erstellt valide ZUGFeRD 2.1 / Factur-X PDFs aus
- Rechnung (mit integriertem ZUGFeRD-XML)
- Zeitnachweis/-dokument (als Anhang)

## Zwei Workflows

| Workflow | Sichtbare Seiten | Anhang als Datei | Empfohlen |
|----------|-----------------|------------------|-----------|
| **zugferd_pages_workflow.py** | ✅ Ja | ❌ Nein | **Standard** |
| **zugferd_workflow.py** | ❌ Nein | ✅ Ja | Fallback |

---

## Empfohlen: Sichtbare Seiten (NEU)

**Durchbruch:** GhostScript merge + PDF/A-3 Konvertierung **vor** dem XML-Combine.

### Ablauf

```
Rechnung.pdf (PDF/A-3) ─┬─▶ [1. XML extrahieren]
                        │
Zeitnachweis.pdf        │
(nicht PDF/A)           │
                        ├─▶ [2. GhostScript merge] ──▶ Merged.pdf
                        │                                    │
                        │                              [3. GhostScript
                        │                               PDF/A-3 Konvertierung]
                        │                                    │
                        │                                    ▼
                        │                           MergedPDFA3.pdf (PDF/A-3)
                        │                                    │
                        └────────────────────────────────────┘
                                         │
                                    [4. XML einbetten]
                                         │
                                         ▼
                              ✅ Rechnung_komplett.pdf
                              ✅ SICHTBARE SEITEN
                              ✅ ZUGFeRD-konform
```

### Verwendung

```bash
export PATH="/opt/homebrew/opt/openjdk@21/bin:$PATH"
cd ~/.openclaw/workspace/skills/zugferd-invoice

python3 scripts/zugferd_pages_workflow.py \
  --invoice Rechnung_RE0182.pdf \
  --attachment Zeitnachweis.pdf \
  --output Rechnung_komplett.pdf
```

### Output

- PDF/A-3b compliant (isCompliant=true)
- Enthält ZUGFeRD 2.1 XML (Factur-X)
- **SICHTBARE SEITEN** beider Dokumente
- Validiert für B2B/Gov-Portal Einreichung

---

## Fallback: Attachment-Only

Falls der GhostScript-Workflow nicht funktioniert.

```bash
python3 scripts/zugferd_workflow.py \
  --invoice Rechnung.pdf \
  --attachment Zeitnachweis.pdf \
  --output Rechnung_komplett.pdf
```

**Unterschied:** Der Zeitnachweis ist als **Datei-Attachment** (nicht als sichtbare Seite) im PDF eingebettet. Im PDF-Reader unter "Anhänge" zu finden.

### Warum funktioniert Page-Merge normalerweise nicht?

Merging eines **nicht**-PDF/A-konformen Zeitnachweise-PDFs (z.B. von Lexware exportiert) zerstört die PDF/A-3 Compliance. Diese PDFs haben typischerweise:
- Fehlende/ungültige ICC-Profile
- Keine ToUnicode-CMaps
- Transparenz-Probleme
- Fehlende OutputIntent

**Der Trick mit GhostScript:** Merge zuerst, dann konvertiere zu PDF/A-3 → funktioniert!

---

## Voraussetzungen

- Java 21 (Homebrew: `brew install openjdk@21`)
- GhostScript (`brew install ghostscript`)
- MustangProject: `~/.openclaw/tools/mustang/mustang.jar`
  ```bash
  mkdir -p ~/.openclaw/tools/mustang
  curl -L https://github.com/ZUGFeRD/mustangproject/releases/download/core-2.22.0/mustang.jar \
       -o ~/.openclaw/tools/mustang/mustang.jar
  ```

## Dateien

| Datei | Zweck |
|-------|-------|
| `scripts/zugferd_pages_workflow.py` | **👑 NEU: Sichtbare Seiten + ZUGFeRD** (GhostScript) |
| `scripts/zugferd_workflow.py` | Attachment-Only Workflow (Fallback) |
| `temp/` | Arbeitsverzeichnis (automatisch) |
| `output/` | Standard-Ausgabeverzeichnis |

---

## Abgelegte Ansätze (nicht benutzen)

- ❌ **Preview.app Merge** - Unzuverlässig (Berechtigungs-Hölle)
- ❌ **qpdf merge** - Zerstört PDF/A-3
- ❌ **pypdf merge** - Zerstört PDF/A-3 + XML
- ❌ **mustang a3only** - Funktioniert nur für PDF/A-1 zu A-3
