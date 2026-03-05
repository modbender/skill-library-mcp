# Expert Panel Recommendation: By-Design Findings

> **Date:** 2025-07-14
> **Panel:** Security Auditor · LLM Prompt Engineer · Product Owner
> **Problem:** Agent frameworks (llama-index, crewai, autogen) get penalized for patterns that ARE their core purpose

---

## 1. Security Auditor Perspective

### Niemals komplett ignorieren

**exec() ist IMMER ein Risiko — auch "by design".** Das ist keine theoretische Aussage:

| Package | Pattern war "by design" | Trotzdem exploited |
|---------|------------------------|--------------------|
| **log4j** | JNDI lookup war ein Feature | CVE-2021-44228 — Remote Code Execution |
| **pickle** | Deserialization ist der Zweck | Arbitrary code execution bei untrusted input |
| **Spring4Shell** | ClassLoader-Zugriff war Feature | CVE-2022-22965 |
| **event-stream** | Dependency war normal | Supply-chain attack über flatmap-stream |

**Die Grenze zwischen Feature und Vulnerability:**

```
Feature:  exec() mit hardcoded/validated input → "Ich führe meinen eigenen Code aus"
Vuln:     exec() mit user/external input → "Ich führe fremden Code aus"
Grauzone: exec() mit LLM-generiertem Code → "Ich führe unkontrollierten Code aus"
```

### Empfehlung

1. **Niemals exec() ignorieren** — aber den Kontext beschreiben
2. **Neue Unterscheidung:** "by-design pattern" ≠ "kein Risiko" — es bedeutet "erwartetes Risiko, das der User kennen sollte"
3. **Severity bleibt erhalten**, aber ein `by_design: true` Flag signalisiert: "Das ist der Zweck des Packages"
4. **Score-Impact: 0** für by-design findings — ABER sie werden prominent angezeigt
5. **Rote Linie:** Wenn exec() mit unvalidiertem externen Input aufgerufen wird, ist es KEIN by-design Pattern, auch nicht in einem Code-Execution-Framework

### Wann ist exec() "by design" vs "vulnerability"?

| Kriterium | By Design | Vulnerability |
|-----------|-----------|---------------|
| Input-Quelle | Hardcoded, vom Framework selbst generiert, oder durch Sandbox geschützt | Direkt von User/Netzwerk/externem File |
| Dokumentation | In README/Docs als Feature beschrieben | Nicht dokumentiert oder versteckt |
| Sandbox | Vorhanden (subprocess mit Limits, restricted globals) | Keine Isolation |
| Package-Zweck | Code-Execution/Agent/ML Framework | Utility/Parser/Formatter |

---

## 2. LLM Prompt Engineer Perspective

### Problem im aktuellen Prompt

Der aktuelle `audit-prompt.md` hat in Step 2 → HIGH:
> `eval()`, `exec()`, `Function()`, `compile()` on variables (even if not directly user-controlled)

Das ist ein Blanket-Statement das keinen Kontext erlaubt. Der Agent MUSS es als HIGH reporten, egal ob es ein Code-Runner oder ein JSON-Parser ist.

### Step 3 ist zu schwach

Die "NOT a finding" Section deckt nur triviale Fälle ab (DB query builder, comments). Es fehlt komplett: "exec() in einem Code-Execution-Framework ist erwartet."

### Lösung: Zwei Prompt-Änderungen

**Änderung 1:** Neuer Step zwischen Step 2 und Step 3 — "Understand Package Purpose"

**Änderung 2:** Neue Severity-Option `by_design` + Anpassung der Output-Spec

### Wie verhindert man "alles ist by-design"?

Strikte Regeln:
1. `by_design` NUR wenn der Package-Zweck exec/pickle/etc. **erfordert**
2. Maximum 5 by_design findings pro Audit — darüber muss der Agent begründen
3. by_design gilt NUR für die dokumentierte Funktionalität, nicht für Nebenwirkungen
4. Wenn Input nicht validiert ist, ist es KEIN by_design — auch in einem Code-Runner

### Exakter Prompt-Text

Siehe Section 3 unten — copy-paste-ready.

---

## 3. Product Owner Perspective

### Das Vertrauens-Paradox

| Szenario | User-Reaktion |
|----------|---------------|
| llama-index = "unsafe" (Score 35) | "Diese Registry ist kaputt. llama-index hat 10M Downloads, das ist offensichtlich falsch." → **User verliert Vertrauen in die Registry** |
| llama-index = "safe" (Score 95) mit exec() versteckt | "Moment, das hat exec() und ist safe? Was prüft ihr eigentlich?" → **User verliert Vertrauen in die Registry** |
| llama-index = Score 85, mit sichtbarer Erklärung "exec() is by-design for agent frameworks" | "OK, die wissen dass es exec() hat, es ist erwartet, und sie haben es trotzdem geprüft." → **User vertraut der Registry** |

### Der beste Kompromiss: Transparenz

- Score reflektiert **echte** Vulnerabilities
- By-design Patterns werden **sichtbar** angezeigt, aber beeinflussen den Score nicht
- User sieht: "Wir wissen dass exec() da ist. Es ist erwartet. Hier ist warum."

### Brauchen wir beides (Prompt + API)?

**Ja, aber priorisiert:**

1. **Prompt-Fix zuerst** (Phase 1) — Der Agent klassifiziert by-design direkt korrekt. Kein API-Change nötig. Sofortige Verbesserung.
2. **API `by_design` Flag später** (Phase 2) — Für nachträgliche Korrekturen + Review-Workflow. Kann warten.

**Begründung:** Der Agent IST die UI. Wenn der Agent korrekt klassifiziert, ist der Score sofort richtig. Die API braucht das Flag nur für Edge Cases und manuellen Override.

---

## 4. Gemeinsame Empfehlung

### Was implementiert wird

| Was | Prio | Aufwand | Wer |
|-----|------|---------|-----|
| **Prompt-Update** mit by_design Awareness | P0 | 30 min | Prompt in Repo ändern |
| **by_design im JSON-Output** des Agents | P0 | Teil des Prompt-Updates | — |
| **API: by_design Boolean auf Findings** | P1 | 1h Backend | API-Maintainer |
| **API: POST /review mit by_design Action** | P2 | 1h Backend | API-Maintainer |
| **Known-Patterns Allowlist** | P2 | Optional, nice-to-have | — |

### Score-Berechnung (neu)

```
Trust Score = max(0, 100 - Σ penalties)

Penalties:
  critical (by_design=false): -25
  high     (by_design=false): -15
  medium   (by_design=false): -8
  low      (by_design=false): -3
  ANY      (by_design=true):   0    ← NEU
```

---

## 5. Konkreter Prompt-Text (copy-paste-ready)

### Änderung 1: Neuer Abschnitt nach Step 2, vor Step 3

Einfügen in `audit-prompt.md` **direkt nach Step 2** (nach der SOCIAL ENGINEERING Section):

```markdown
## Step 2.5: Identify Package Purpose & By-Design Patterns

Before classifying findings, determine the package's **core purpose** from its README, package description, and code structure.

### Package Categories & Expected Patterns

| Package Category | Expected Patterns (by-design) |
|-----------------|-------------------------------|
| Code execution framework (agent, REPL, notebook) | `exec()`, `eval()`, `compile()`, `Function()`, dynamic imports |
| ML/AI framework (training, inference) | `pickle`, `torch.load()`, `joblib`, large binary downloads |
| Plugin/extension system | Dynamic `import()`, `require()`, `__import__()`, module loading |
| Build tool / bundler | File system writes, `child_process`, `subprocess`, shell commands |
| API client / SDK | Outbound HTTP requests, credential handling |
| Package manager / installer | `curl`, `wget`, `npm install`, `pip install`, file downloads |

### When to Mark a Finding as `by_design`

A finding is `by_design: true` ONLY when ALL of these are true:
1. The pattern is **core to the package's documented purpose** (not a side-effect)
2. The package's README/docs **explicitly describe** this functionality
3. The input to the dangerous function is **not directly from untrusted external sources** (user HTTP input, unvalidated file contents from unknown sources)
4. The pattern is **common across similar packages** in the same category

### When it is NOT by-design (even in a code-execution framework)

- `exec()` called with **unvalidated external input** (e.g., HTTP request body → exec) → REAL VULNERABILITY
- Network calls to **hardcoded suspicious domains** → REAL VULNERABILITY
- `pickle.loads()` on **user-uploaded files without validation** → REAL VULNERABILITY
- Functionality **not mentioned in docs** → REAL VULNERABILITY
- Disabling security features (TLS, sandboxing) **without user opt-in** → REAL VULNERABILITY

### By-Design Finding Format

When a finding IS by-design, report it with **reduced severity display** but full transparency:

- Set `"by_design": true` in the finding JSON
- Keep the original severity classification (high/medium/etc.) for reference
- Set `"score_impact": 0` to indicate it should not affect the Trust Score
- Explain WHY it's by-design in the description: "exec() is used for [specific purpose]. This is a core feature of this [category] framework."
- Still note any **mitigations** the package applies (sandboxing, input validation, restricted globals)

**Maximum 5 by-design findings per audit.** If you find more than 5 patterns that seem by-design, the package may genuinely be risky — reassess.
```

### Änderung 2: Ergänzung in Step 3 (False Positives Section)

Zum bestehenden "It is NOT a finding when:" Block hinzufügen:

```markdown
**It is a BY-DESIGN finding (report with `by_design: true`, score_impact: 0) when:**
- `exec()` in an agent framework's code-runner module (e.g., llama-index, autogen, crewai)
- `pickle.loads()` in an ML framework's model loading (e.g., torch, sklearn)
- Dynamic `import()` in a plugin system's loader
- Outbound HTTP in an API client library
- `subprocess.run()` in a build tool for compilation steps

These are reported for **transparency** but do NOT penalize the Trust Score.
```

### Änderung 3: Ergänzung im JSON Output Format (Step 4)

Das Finding-Object erweitern:

```markdown
```json
{
  "severity": "high",
  "pattern_id": "CMD_INJECT_001",
  "title": "Short descriptive title",
  "description": "What the issue is and why it matters",
  "file": "relative/path/to/file.js",
  "line": 42,
  "content": "the exact problematic code snippet",
  "confidence": "high",
  "remediation": "Specific fix: use X instead of Y",
  "by_design": false,
  "score_impact": -15
}
```

> **`by_design`**: Set to `true` when the pattern is an expected, documented feature of the package's category. By-design findings have `score_impact: 0` and do NOT reduce the Trust Score. Default: `false`.
> **`score_impact`**: The penalty this finding applies. `0` for by-design findings. Otherwise: critical=-25, high=-15, medium=-8, low=-3.
```

### Änderung 4: Risk Score Guide Ergänzung

Zum bestehenden Score Guide hinzufügen:

```markdown
> **By-design findings** are excluded from score calculation. A package with 3 by-design findings and 0 real findings = score 0, result "safe".
> Calculate: `risk_score = Σ(penalties for findings WHERE by_design = false)`. Then map to result.
```

---

## 6. API-Änderungen

### Phase 1 (mit Prompt-Fix, minimal)

**Keine API-Änderung nötig.** Der Agent schreibt `by_design: true` in den Finding-JSON. Die API speichert es als Teil des Finding-Objekts (die meisten JSON-APIs akzeptieren zusätzliche Felder). Der Score wird clientseitig korrekt berechnet weil der Agent die Formel im Prompt hat.

### Phase 2 (wenn API-Maintainer Zeit hat)

1. **Findings-Tabelle:** `by_design BOOLEAN DEFAULT false`, `by_design_reason TEXT`
2. **POST /api/findings/:ecap_id/review** erweitern:
   ```json
   {
     "verdict": "by_design",
     "reasoning": "exec() is core feature of this agent framework"
   }
   ```
3. **GET /api/findings** Response: `by_design` und `by_design_reason` Felder zurückgeben
4. **Score-Endpoint** (optional): Serverseitiger Trust Score der by_design findings exkludiert

---

## 7. Priorisierung

```
JETZT (Phase 0):
  ✅ audit-prompt.md updaten mit den 4 Änderungen oben
  ✅ SKILL.md Score-Berechnung um by_design Ausnahme ergänzen
  → Sofortige Verbesserung für alle zukünftigen Audits

DIESE WOCHE (Phase 1):
  📋 API: by_design Boolean in Findings-Tabelle
  📋 Bestehende Findings für llama-index, crewai, autogen nachträglich markieren

SPÄTER (Phase 2):
  📋 Review-Endpoint um by_design Verdict erweitern
  📋 Known-Patterns Allowlist (config/known-patterns.json)
  📋 UI/Dashboard: Separate Darstellung von by-design vs. real findings
```

---

## 8. Erwartetes Ergebnis

### Vorher
```
⚠️ llama-index-core — Trust Score: 45/100 (caution)
  🟠 HIGH: exec() usage in code runner
  🟠 HIGH: eval() in expression parser
  🟡 MEDIUM: pickle usage in caching
  🟡 MEDIUM: Dynamic imports
  🟡 MEDIUM: Outbound HTTP calls
  🔵 LOW: No input validation on plugin names
```

### Nachher
```
✅ llama-index-core — Trust Score: 92/100 (safe)

  Vulnerabilities (1):
    🔵 LOW: No input validation on plugin names (-3)
    → Remediation: Validate plugin names against allowlist

  By-Design Patterns (5, score-neutral):
    ℹ️ exec() — Core code-execution feature (sandboxed)
    ℹ️ eval() — Expression parser for query DSL
    ℹ️ pickle — Model/index caching (local files only)
    ℹ️ Dynamic imports — Plugin loading system
    ℹ️ HTTP calls — LLM API communication
```

**User sieht:** "Die Registry hat alles geprüft, versteht den Kontext, und zeigt mir was wichtig ist."
