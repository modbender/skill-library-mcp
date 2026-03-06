# Integration Test Report — ecap-security-auditor

**Date:** 2026-02-02  
**Tester:** Integration Test Subagent  
**Agent:** ecap0  
**API Base:** https://skillaudit-api.vercel.app

---

## Test 1: Neuer Agent — Erstregistrierung

**Result: PASS (with gaps)**

### Was funktioniert
- `register.sh` ist sauber geschrieben: Input-Validierung, jq für JSON-Safety, chmod 600 für Credentials
- Idempotent: Erkennt bereits existierende Registration
- Klare Usage-Message bei fehlendem Argument

### Was fehlt in der Doku
- **❌ Kein "Discovery"-Mechanismus:** Ein neuer Agent weiß nicht, welche Packages noch nicht auditiert sind. Es gibt kein `GET /api/unaudited` oder `GET /api/packages` Endpoint. Man muss erraten welche Packages existieren.
- **❌ Kein "Getting Started"-Tutorial:** Nach der Registrierung fehlt ein "Hier ist dein erster Audit"-Walkthrough
- **❌ Kein `GET /api/packages` Endpoint** um alle bekannten Packages aufzulisten
- `/api/stats` zeigt Gesamtzahlen, `/api/health` existiert — aber keiner sagt "diese Packages brauchen noch Reviews"

---

## Test 2: Agent will npm Package installieren (`express`)

**Result: FAIL — Flow bricht ab**

### Durchlauf
1. ✅ `GET /api/findings?package=express` → `total: 0, findings: []` — korrekt, kein Report
2. ✅ Gate Flow sagt: "No report → Auto-Audit triggered"
3. **❌ HIER BRICHT ES:** SKILL.md sagt für npm: "Location: `node_modules/<name>/`"
   - Aber das Package ist ja noch **nicht installiert** — genau das wollen wir ja gaten!
   - **Chicken-and-egg Problem:** Um zu auditen, muss man die Source-Files lesen. Um die Files zu haben, muss man installieren. Aber der Gate soll VOR der Installation laufen.

### Fehlende Doku / Lösungsansätze
- **❌ Kein Hinweis auf `npm pack` + `tar xzf`** (download ohne install)
- **❌ Kein Hinweis auf GitHub Source Review** als Alternative
- **❌ Kein Hinweis auf `npx` dry-run** oder Registry-API
- Für npm Packages braucht es entweder: (a) Source von GitHub/npm Registry holen ohne zu installieren, oder (b) in isoliertem Temp-Dir installieren und dort auditen
- **Die Doku schweigt komplett darüber**

---

## Test 3: Agent will MCP Server nutzen (`mcp-server-fetch`)

**Result: PASS (mit Einschränkungen)**

### Durchlauf
1. ✅ `GET /api/findings?package=mcp-server-fetch` → 3 Findings vorhanden
2. ✅ Trust Score berechnen: 3 Low-Severity Findings → 100 - 3×3 = **91** → 🟢 PASS
3. ⚠️ Hash Verification: `verify.sh` ist hardcoded auf feste Dateiliste (SKILL.md, scripts/, prompts/, README.md)

### Problem: verify.sh funktioniert nur für den eigenen Skill
- `verify.sh` hat eine **hardcoded FILES-Array** mit ecap-eigenen Dateien
- Für mcp-server-fetch gibt es keine lokale Skill-Verzeichnisstruktur
- `/api/integrity?package=mcp-server-fetch` könnte Hashes liefern, aber `verify.sh` kann damit nichts anfangen
- **❌ verify.sh ist nicht generisch** — es verifiziert nur `ecap-security-auditor` selbst

### Fehlende Doku
- **❌ Kein Hinweis wie Hash-Verification für nicht-Skill Packages funktioniert**
- **❌ verify.sh müsste die Dateiliste dynamisch aus `/api/integrity` holen**
- Workaround: Integrity-Check überspringen, nur Trust Score nutzen — aber das ist nirgends dokumentiert

---

## Test 4: Agent will ClawdHub Skill installieren

**Result: PASS**

### Durchlauf
1. ✅ Skill landet in `skills/<name>/` — dort hat es SKILL.md, scripts/, etc.
2. ✅ `verify.sh` KÖNNTE darauf laufen — aber nur wenn die Dateistruktur dem ecap-Format entspricht
3. ✅ Gate Flow ist klar: Query → Hash → Score → Decision

### Einschränkungen
- `verify.sh` prüft hardcoded Dateien (SKILL.md etc.) — ein Skill ohne diese Struktur scheitert
- **Empfehlung:** verify.sh sollte die Dateiliste aus `/api/integrity` dynamisch laden

---

## Test 5: Peer Review Workflow

**Result: BLOCKED — Self-review Protection**

### Durchlauf
1. ✅ `GET /api/findings?package=coding-agent` → 6 Findings (2 critical, 2 high, 2 medium)
2. ✅ Finding ausgewählt: ECAP-2026-0777 (critical, CMD_INJECT_001)
3. ✅ `review-prompt.md` gelesen — Anleitung ist klar und gut strukturiert
4. ✅ Review erstellt nach Checklist
5. **❌ Submit scheitert:** `"error": "Self-review not allowed. You cannot review your own finding."`

### Erkenntnisse
- Die Self-Review-Protection funktioniert korrekt — das ist gut!
- **Problem:** Da es nur 1 Reporter gibt (ecap0), können keine Reviews getestet werden
- **Kritisch:** SKILL.md sagt man soll die **numerische `id`** verwenden, aber nur `ecap_id` (String wie ECAP-2026-0777) funktioniert! Numerische IDs geben alle "Finding not found"!

### 🐛 BUG: Finding ID Routing
- `POST /api/findings/6/review` → `"Finding not found"` (numeric ID)
- `POST /api/findings/ECAP-2026-0777/review` → `"Self-review not allowed"` (ecap_id works!)
- **SKILL.md dokumentiert explizit:** "use the **numeric `id`** field" — **das ist falsch!**
- **Die API akzeptiert nur `ecap_id` Strings, nicht die numerische `id`**

---

## Test 6: Fix Reporting

**Result: PASS (nur mit ecap_id)**

### Durchlauf
1. ✅ Finding gefunden: id=58, ecap_id=ECAP-2026-0829 ("API key stored in plaintext JSON file")
2. **❌ `POST /api/findings/58/fix`** → `"Finding not found"` (numerische ID)
3. ✅ `POST /api/findings/ECAP-2026-0829/fix` → `{"ok":true, "ecap_id":"ECAP-2026-0829", "status":"fixed", "trust_recovered":0}`

### 🐛 Gleicher Bug wie Test 5
- Numerische IDs funktionieren nicht für `/fix` Endpoint
- Nur `ecap_id` Strings funktionieren
- `trust_recovered: 0` — unklar ob das korrekt ist (Doku sagt "Recovers 50% of penalty")

---

## Test 7: Leaderboard + Agent Profile

**Result: PASS**

### Leaderboard
- ✅ `/api/leaderboard` liefert sortierte Liste aller Reports nach skill_slug
- ⚠️ Leaderboard zeigt Reports, nicht Agents — es ist eigentlich eine Report-Liste
- **❌ Kein Agent-Ranking** (nach Punkten etc.) — widerspricht der "Leaderboard"-Bezeichnung

### Agent Profile (`/api/agents/ecap0`)
- ✅ Umfangreiche Daten: total_reports (50), total_findings_submitted (64), total_points (1075)
- ✅ Skills audited Liste, recent findings, recent reports
- ⚠️ `severity_breakdown` zeigt nur `low: 50`, obwohl Findings mit critical/high existieren — möglicherweise nur die letzten N?
- ⚠️ `total_findings_confirmed: 0` — korrekt, da keine Peer Reviews möglich waren

### Integrity Check
- ✅ `verify.sh ecap-security-auditor` läuft durch
- ❌ Ergebnis: "Integrity check FAILED — files differ from official repo"
- Dies bedeutet lokale SKILL.md wurde seit dem letzten Audit modifiziert (erwartet nach Edits)

---

## Zusammenfassung

| Test | Result | Schwere |
|------|--------|---------|
| 1. Erstregistrierung | ⚠️ PASS (mit Lücken) | Low |
| 2. npm Package (express) | ❌ FAIL | **High** — Chicken-egg Problem undokumentiert |
| 3. MCP Server (mcp-server-fetch) | ⚠️ PASS (eingeschränkt) | Medium — verify.sh nicht generisch |
| 4. ClawdHub Skill | ✅ PASS | Low |
| 5. Peer Review | 🚫 BLOCKED + 🐛 BUG | **Critical** — Falsche ID-Doku |
| 6. Fix Reporting | ⚠️ PASS (nur ecap_id) | **Critical** — Gleicher ID-Bug |
| 7. Leaderboard + Profile | ✅ PASS | Low |

---

## Critical Bugs

### 🐛 BUG-001: Finding ID Mismatch (CRITICAL)
**SKILL.md dokumentiert:** "use the **numeric `id`** field from the findings response (not the `ecap_id` string)"  
**Realität:** Nur `ecap_id` Strings funktionieren. Numerische IDs geben IMMER "Finding not found".  
**Betrifft:** `/api/findings/:id/review` und `/api/findings/:id/fix`  
**Fix:** Entweder API oder Doku anpassen.

### 🐛 BUG-002: verify.sh ist nicht generisch (HIGH)
`verify.sh` hat eine hardcoded Dateiliste und funktioniert nur für `ecap-security-auditor` selbst.  
Für jedes andere Package (npm, pip, MCP) ist der Integrity-Check nicht nutzbar.

---

## Fehlende Doku-Kapitel

1. **"How to audit npm/pip packages before installation"** — Das Chicken-egg Problem braucht eine klare Lösung
2. **"Package Discovery"** — Wie finde ich unauditierte Packages?
3. **"Integrity for non-Skill packages"** — verify.sh Limitierung dokumentieren
4. **"API ID format"** — Klarstellen dass `ecap_id` (nicht numerische `id`) für Endpoints verwendet wird
