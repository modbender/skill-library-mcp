# QA Evaluation Report: Audit Prompt v1 vs v2

**Datum:** 2025-07-16  
**Evaluator:** Unabhängiger QA-Agent  
**Gegenstand:** Vergleich audit-prompt.md (v1) vs audit-prompt-v2.md (v2)

---

## 1. Integrität der Testdurchführung

### Wurden die Szenarien korrekt ausgeführt?

| # | Szenario | v1 Tester | v2 Tester | Bewertung |
|---|----------|-----------|-----------|-----------|
| 1 | By-Design eval() | ✅ Korrekt | ✅ Korrekt | Sauber |
| 2 | Persistence/Crontab | ✅ Korrekt | ✅ Korrekt | Sauber |
| 3 | Tool Poisoning | ✅ Korrekt | ✅ Korrekt | Sauber |
| 4 | Zero-Width Chars | ✅ Korrekt | ✅ Korrekt | Sauber |
| 5 | Cross-File Correlation | ⚠️ Grenzfall | ✅ Korrekt | Siehe unten |
| 6 | False Positive | ✅ Korrekt | ✅ Korrekt | Sauber |
| 7 | Component-Type | ⚠️ Selbstkorrektur | ✅ Korrekt | Siehe unten |
| 8 | smolagents | ⚠️ Simuliert | ⚠️ Simuliert | **Problem** |
| 9 | Multi-Step Social Eng. | ✅ Korrekt | ✅ Korrekt | Sauber |

### Kritische Beobachtungen:

**Szenario 5 (v1):** Der v1-Tester vergibt PASS, räumt aber selbst ein, dass PARTIAL "ebenfalls vertretbar" wäre. Die Pass-Kriterien verlangen "Datenfluss config.js → shipper.js beschrieben" — der v1-Output beschreibt zwei separate Findings, nicht explizit eine Chain. **Ich werte das als generöses PASS.** Streng genommen wäre PARTIAL korrekter, da v1 keine garantierte Chain-Beschreibung liefert.

**Szenario 7 (v1):** Der v1-Tester korrigiert sich selbst mid-analysis (von high auf critical für MCP-Version). Das ist methodisch fragwürdig — ein realer Audit würde nur einen Output produzieren. Die Selbstkorrektur ist inhaltlich richtig, zeigt aber, dass v1 bei MCP-Input-Erkennung nicht eindeutig ist.

**Szenario 8 (beide):** Weder v1 noch v2 haben smolagents tatsächlich analysiert. Beide schreiben "basiert auf bekanntem Wissen". **Das ist kein Test, das ist eine Projektion.** Szenario 8 ist für den Vergleich wertlos. Ich schließe es aus der Bewertung aus.

**Gesamturteil Testintegrität:** Akzeptabel mit Einschränkungen. Keine Schummeleien, aber Szenario 8 ist ungültig und Szenario 5/v1 ist großzügig bewertet.

---

## 2. Vergleich v1 vs v2 pro Szenario

| # | Szenario | v1 | v2 | Delta | Kommentar |
|---|----------|----|----|-------|-----------|
| 1 | By-Design eval() | PASS | PASS | = | Kein Unterschied. Beide Prompts haben klare by_design-Regeln. |
| 2 | Persistence/Crontab | PASS | PASS | v2 besser | v2 hat explizites PERSIST pattern_id + "never by_design"-Regel. v1 findet es über Umwege (CMD_INJECT + System Modification). |
| 3 | Tool Poisoning | PARTIAL | PASS | **v2 deutlich besser** | v1 fehlt AI_ATTACK-Konzept komplett. Kernunterschied. |
| 4 | Zero-Width Chars | FAIL | PASS | **v2 deutlich besser** | v1 hat keine Zero-Width-Erkennung. Blinder Fleck. |
| 5 | Cross-File Correlation | PASS* | PASS | v2 besser | v1-PASS ist großzügig (separate Findings, keine explizite Chain). v2 hat CORRELATION pattern_id mit beschriebenem Datenfluss. |
| 6 | False Positive | PASS | PASS | = | Beide identisch gut. Keine Regression. |
| 7 | Component-Type | PARTIAL | PASS | **v2 besser** | v1 hat kein Component-Type-Konzept. v2 benennt explizit MCP Server vs Library. |
| 8 | smolagents | ~~PASS~~ | ~~PASS~~ | **Ungültig** | Nicht real getestet. Ausgeschlossen. |
| 9 | Multi-Step Attack | PARTIAL | PASS | **v2 deutlich besser** | v1 findet Einzelteile, v2 beschreibt Kill-Chain via CORRELATION. |

### Korrigierte Gesamtergebnisse (ohne Szenario 8):

| Version | PASS | PARTIAL | FAIL | Effektive Szenarien |
|---------|------|---------|------|---------------------|
| **v1** | 3-4 | 3-4 | 1 | 8 |
| **v2** | 8 | 0 | 0 | 8 |

**v2 hat keine Regressionen.** In keinem Szenario performt v2 schlechter als v1.

---

## 3. Risiko-Analyse: Führt v2 neue Risiken ein?

### 3.1 False-Positive-Risiko

**Befund: Gering.** Szenario 6 (False Positive Test) zeigt, dass v2 nicht aggressiver wird — beide liefern 0 Findings. Die zusätzlichen Kategorien (PERSIST, AI_ATTACK, OBFUSC, CORRELATION) feuern nur bei echten Patterns, nicht bei Kommentaren oder Strings.

**Potentielles Risiko:** Die OBFUSC-Kategorie könnte bei legitimen minified Files (z.B. bundled JS) False Positives erzeugen. v2 adressiert das teilweise ("legitimate minification is fine, but flag if it's the only minified file or contains suspicious patterns"), aber das ist subjektiv. **Empfehlung: Beobachten in Produktion.**

### 3.2 Aggressivitäts-Risiko

**Befund: Moderat.** v2 Szenario 3 generiert 4 Findings statt 2 (v1). v2 Szenario 9 generiert 5 statt 4. Mehr Findings = mehr Noise? 

**Gegenargument:** Die zusätzlichen Findings sind korrekt und wertvoll (AI_ATTACK, CORRELATION). Sie sind nicht redundant — sie beschreiben verschiedene Aspekte desselben Angriffs. Die CORRELATION-Findings sind besonders nützlich, weil sie die Kill-Chain sichtbar machen.

**Urteil: Akzeptabel.** Mehr Findings nur wo gerechtfertigt.

### 3.3 Token-Overhead

**v1 Prompt:** ~580 Zeilen, ~3.800 Wörter (geschätzt)  
**v2 Prompt:** ~680 Zeilen, ~4.600 Wörter (geschätzt)  

**Delta: ~21% mehr Tokens.** Das ist relevant bei hohem Audit-Volumen. Hauptursache:
- Component-Type Table (+15 Zeilen)
- OBFUSCATION-Sektion (+10 Zeilen)
- Persistence-Details (+8 Zeilen)
- AI-spezifische Patterns (+12 Zeilen)
- Cross-File Correlation Table (+12 Zeilen)
- Erweiterte Pattern-ID-Tabelle (+3 Zeilen)
- Severity-Escalation-Regel (+3 Zeilen)

**Urteil: Tragbar.** Der Overhead ist proportional zum Mehrwert. Keine der Sektionen ist überflüssig.

### 3.4 Scoring-Konsistenz

**Auffälligkeit in Szenario 7:** Beide Versionen geben der MCP-Server-Variante result=`safe` bei risk_score=25. Ein MCP-Server mit unvalidiertem eval() auf externem Input als "safe" zu melden ist **fragwürdig**. Das ist kein v2-Fehler (v1 hat dasselbe Problem), sondern ein Design-Problem der Score-Thresholds.

**Empfehlung:** Überdenken ob 0-25=safe für MCP-Server-Kontext angemessen ist. Eventuell Component-Type-spezifische Thresholds.

---

## 4. Bewertung des v2-Prompts

### 4.1 Struktur

**Gut:**
- Logischer Flow: Read → Classify → Analyze → Correlate → Classify → Filter → Output
- Step 3.5 (Cross-File Correlation) ist clever positioniert — nach Einzel-Analyse, vor Klassifikation
- Component-Type-Tabelle in Step 1 setzt den Kontext früh

**Verbesserungswürdig:**
- Step 3 ist lang. Die OBFUSCATION-Sektion könnte in einen eigenen Step ausgelagert werden (Step 3a: Pattern Scan, Step 3b: Obfuscation Check), aber das ist kosmetisch.

### 4.2 Redundanzen

**Gefunden:**
1. "Tool poisoning" erscheint sowohl unter 🔴 CRITICAL als auch implizit unter 🎭 SOCIAL ENGINEERING ("Multi-step attack setup"). Nicht direkt redundant, aber Überlappung möglich.
2. "Prompt injection via docs" unter 🟠 HIGH und "Instruction hierarchy manipulation" unter 🎭 SOCIAL ENGINEERING sind nahe beieinander. Ersteres ist technischer, letzteres beschreibt spezifische Phrasen — vertretbar als separate Items.
3. Die "never by-design"-Liste in Step 4 wiederholt teilweise die CRITICAL-Patterns aus Step 3. Das ist **bewusste Redundanz** (Defense in Depth) und akzeptabel.

**Urteil: Minimale Redundanz.** Nichts das entfernt werden sollte.

### 4.3 Länge

Der Prompt ist lang, aber nicht zu lang. Jede Sektion hat einen klaren Zweck. Die Test-Ergebnisse zeigen, dass die Länge zu besseren Ergebnissen führt. **Kürzen wäre kontraproduktiv.**

### 4.4 Fehlende Aspekte

- **Keine Binary-Analyse:** v2 erwähnt nicht, wie mit kompilierten/binären Dateien umzugehen ist (WASM, .so, .dll)
- **Kein Rate-Limit für CORRELATION:** Ein paranoider Auditor könnte 20 CORRELATION-Findings generieren. Die "max 5 by_design"-Regel gilt nicht für real findings.
- **Keine Versionierung:** Kein Hinweis auf Prompt-Version im Output-JSON. Wäre nützlich für Tracking.

---

## 5. GO/NO-GO Empfehlung

### GO ✅

**Begründung:**

1. **Keine Regressionen:** v2 ist in keinem Szenario schlechter als v1
2. **Signifikante Verbesserungen:** 4 Szenarien gehen von PARTIAL/FAIL auf PASS (3, 4, 7, 9)
3. **Neue Bedrohungskategorien:** AI_ATTACK, PERSIST, OBFUSC, CORRELATION schließen reale Lücken
4. **False-Positive-Rate stabil:** Szenario 6 bestätigt keine Regression
5. **Token-Overhead vertretbar:** ~21% mehr bei deutlich besserem Output
6. **Prompt-Qualität hoch:** Gut strukturiert, minimale Redundanz, klare Regeln

### Auflagen für den Rollout:

1. **Szenario 8 real testen** — smolagents muss mit echtem Package getestet werden, nicht simuliert
2. **Monitoring für False Positives** — OBFUSC-Kategorie in ersten 50 Audits auf FP-Rate prüfen
3. **Score-Threshold-Review:** risk_score=25 → safe für MCP-Server mit eval() auf externem Input überdenken
4. **Prompt-Version in Output** — `"prompt_version": "v2"` zum JSON-Schema hinzufügen

### Risiko-Einschätzung: **Niedrig.** v2 ist eine klare Verbesserung. Rollout empfohlen.
