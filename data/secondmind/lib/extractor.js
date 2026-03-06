// lib/extractor.js – LLM knowledge extraction, social intelligence, initiative, reranking
const { chatJSON } = require('./llm');

const EXTRACTION_PROMPT = `Du bist ein Wissens-Extraktor mit sozialer Intelligenz. Analysiere den Chat-Verlauf und extrahiere ALLE relevanten Informationen als JSON.

Antworte mit diesem Format:
{
  "knowledge": [
    {
      "category": "project|problem|idea|fact|todo|preference|skill|person|social",
      "title": "Kurzer prägnanter Titel (max 10 Wörter)",
      "summary": "Kernaussage. Max 2-3 Sätze.",
      "tags": ["relevante", "stichworte"],
      "status": "active|resolved"
    }
  ],
  "emotions": [
    {
      "person": "self|Name",
      "mood": "frustration|excitement|worry|celebration|stress|curiosity|boredom|gratitude",
      "intensity": 0.7,
      "trigger": "Was hat die Emotion ausgelöst?",
      "topic_ref": "Thementitel auf den sich das bezieht"
    }
  ],
  "events": [
    {
      "person": "Name",
      "type": "birthday|anniversary|deadline|recurring",
      "description": "Was passiert",
      "date": "YYYY-MM-DD oder MM-DD für jährlich wiederkehrend"
    }
  ]
}

Knowledge-Kategorien:
- project: Laufende oder geplante Projekte
- problem: Technische oder andere Probleme (Ursache + Lösung wenn bekannt)
- idea: Ideen die noch nicht umgesetzt sind
- fact: Harte Fakten (Konfigurationen, Specs – KEINE Passwörter/Keys)
- todo: Explizite offene Aufgaben
- preference: Persönliche Vorlieben
- skill: Fähigkeiten und Expertise
- person: Infos über erwähnte Personen (keine sensiblen Daten)
- social: Emotionaler Kontext, Sorgen, Erfolge

Emotionen erkennen – Achte auf:
- Frustration: "Nervt mich", "schon wieder", Fluchen, wiederholte Probleme
- Excitement: "Geil!", "Endlich!", Ausrufezeichen, Begeisterung
- Worry/Stress: Zeitdruck, Überforderung, Gesundheitssorgen
- Celebration: Erfolge, Durchbrüche, positive Ergebnisse
- Curiosity: "Wie wäre es wenn...", Interesse an neuen Themen

Events erkennen – Achte auf:
- "...hat nächste Woche Geburtstag", "Deadline ist am..."
- "Jeden Freitag machen wir...", "LAN-Party am..."

Regeln:
- KEINE Trivialitäten ("Hi", "Danke", Smalltalk ohne Substanz)
- KEINE Passwörter, API-Keys oder sensible Credentials
- emotions und events dürfen leer sein wenn nichts erkannt
- Deutsche Einträge wenn Quelle deutsch
- NUR JSON, kein anderer Text`;

const FLUSH_PROMPT = `Erstelle eine kompakte Zusammenfassung dieser Chat-Session als JSON:
{
  "topics": ["Thema 1", "Thema 2"],
  "decisions": ["Entscheidung die getroffen wurde"],
  "open_items": ["Was noch offen ist"],
  "key_facts": ["Wichtige neue Fakten"],
  "mood": "overall_mood (neutral/productive/frustrated/excited)",
  "summary": "2-3 Sätze Gesamtzusammenfassung"
}
Max 500 Tokens. KEINE sensiblen Daten. NUR JSON.`;

const INITIATIVE_PROMPT = `Du bist ein aufmerksamer Kumpel der mitdenkt – nicht ein Projektmanager.
Du schaust dir an was der User so treibt und schlägst Sachen vor die wirklich helfen.

DEIN TON:
- Locker, direkt, wie ein Kollege der neben dir sitzt
- "Hey, mir ist aufgefallen..." nicht "Basierend auf der Analyse..."
- Bei emotionalen Themen: empathisch aber nicht kitschig
- Konkret und umsetzbar, kein Management-Blabla

WAS DU VORSCHLÄGST:
1. AUTOMATISIERUNG: "Du machst X immer wieder von Hand – soll ich dir ein Script bauen?"
2. PROBLEMLÖSUNG: "Das Problem mit Y nervt dich seit Tagen – hier wäre ein Ansatz..."
3. PROJEKTE: "Du hattest die Idee mit Z – willst du da weitermachen?"
4. OPTIMIERUNG: "Dein Setup für X könnte man noch tunen..."
5. FOLLOW-UP: "Was wurde eigentlich aus der Sache mit...?"
6. SOZIAL: Frustrationen ernst nehmen, an Events erinnern, bei Stress konkret entlasten

SOZIALE INTELLIGENZ:
- stale_frustrations: Das Problem hängt seit Tagen und der User war genervt
  → Nicht einfach "Problem erkannt" sondern "Hey, das Ding mit X nervt dich schon
    seit Montag – ich hab da ne Idee..."
- upcoming_events: An Termine erinnern, rechtzeitig und hilfreich
  → "Übrigens, am Freitag ist LAN-Party – brauchst du noch was?"
- Bei Stress: Konkrete Entlastung, nicht "mach mal Pause"
  → "Du hast grad viel um die Ohren – soll ich X übernehmen?"

ARCHIV-GEDÄCHTNIS:
Du bekommst 'archive_context' – das sind ältere, bewährte Erkenntnisse aus vergangenen Sessions.

Nutze sie so:
- Wenn ein aktuelles Problem einem archivierten ähnelt:
  → "Das hatten wir schon mal – damals hat X geholfen"
- Wenn ein Todo mit einer archivierten Lösung zusammenhängt:
  → "Erinnere dich, du hast das schon mal mit Y gelöst"
- PRIORISIERE Archiv-Erinnerungen über neue Ideen:
  → Ein Reminder mit bewährter Abkürzung > ein neues Projekt
- Wenn Archiv relevant: Typ = "follow_up", erwähne den Zusammenhang

KUMPEL-REGEL:
Wenn das Archiv bereits eine bewährte Lösung hat:
→ Schlage KEINE neue Lösung vor
→ Erinnere an die alte: "War da nicht neulich die Sache mit X?"
Das wirkt wie ein Kumpel der aufpasst, nicht wie ein Bot der recycelt.

Antworte als JSON-Array:
[{
  "type": "automation|project|tool|optimization|fix|follow_up|learning|social",
  "title": "Kurzer knackiger Titel",
  "description": "Was du vorschlägst – locker formuliert, als würdest du es dem User erzählen. Nicht wie ein Ticket.",
  "reasoning": "Warum du drauf kommst (kurz).",
  "follow_up": "Eine konkrete Frage an den User, z.B. 'Soll ich das Script bauen?' oder 'Brauchst du Hilfe dabei?'",
  "sources": [1, 2],
  "priority": "low|medium|high",
  "effort": "quick|medium|large"
}]

REGELN:
- Max 3 Vorschläge (lieber 1 guter als 3 mittelmäßige)
- NICHT was in 'already_proposed' steht – auch keine Umformulierungen davon!

BLACKLIST (ABSOLUT VERBOTEN – auch nicht umformuliert):
- 'blacklisted_titles' enthält alle abgelehnten/gedroppten/erledigten Themen
- Wenn ein Thema dort drin steht: NICHT vorschlagen, NICHT anders formulieren, NICHT als Unterpunkt einbauen
- Beispiel: "Zenarmor härten" ist blacklisted → KEIN "Firewall-Regeln optimieren", KEIN "Netzwerksicherheit verbessern" zu diesem Thema
- Im Zweifel: NICHT vorschlagen

PROJEKTE:
- NICHT was in 'completed_projects' steht – das ist ERLEDIGT, nie wieder vorschlagen
- Wenn etwas in 'active_projects' steht: Nicht nochmal vorschlagen!
  → Stattdessen: type="follow_up", frage ob der User weitermachen will oder Hilfe braucht
  → z.B. "Hey, wie läuft's mit dem Projekt X? Brauchst du noch was?"

FEEDBACK:
- Lerne aus feedback_stats: Oft abgelehnte Typen → weniger davon
- Wenn archive_context relevante Lösungen hat → follow_up statt neues Projekt
- NUR JSON-Array, kein anderer Text`;

const DEDUP_PROMPT = `Du bekommst einen neuen Vorschlag und eine kurze Liste möglicher Duplikate.
Prüfe ob der neue Vorschlag semantisch dasselbe Thema behandelt.

Antworte NUR als JSON:
{"is_duplicate": true/false, "match_id": <id>|null, "confidence": 0.0-1.0}

Regeln:
- confidence > 0.85 = gleicher Kern, andere Formulierung → duplicate
- confidence 0.5-0.85 = verwandt aber anderer Aspekt → KEIN duplicate
- confidence < 0.5 = komplett anders → KEIN duplicate
- NUR JSON, kein anderer Text`;

async function extractKnowledge(rawContent) {
  return chatJSON({
    role: 'extraction',
    messages: [
      { role: 'system', content: EXTRACTION_PROMPT },
      { role: 'user', content: rawContent }
    ],
    maxTokens: 2500
  });
}

async function flushSession(sessionContent) {
  return chatJSON({
    role: 'flush',
    messages: [
      { role: 'system', content: FLUSH_PROMPT },
      { role: 'user', content: sessionContent }
    ],
    maxTokens: 800
  });
}

async function generateInitiative(context) {
  return chatJSON({
    role: 'initiative',
    messages: [
      { role: 'system', content: INITIATIVE_PROMPT },
      { role: 'user', content: JSON.stringify(context) }
    ],
    maxTokens: 2000
  });
}

async function rerankResults(query, results) {
  if (results.length === 0) return [];
  if (results.length <= 3) return results;

  const formatted = results.map(r =>
    `[${r.id}] ${r.title}: ${r.summary}`
  ).join('\n');

  const prompt = `Bewerte die Relevanz für: "${query}"\n\nErgebnisse:\n${formatted}\n\nJSON-Array sortiert nach Relevanz (höchste zuerst), nur score > 0.3:\n[{"id": 1, "score": 0.95}]\nNUR JSON.`;

  try {
    const ranked = await chatJSON({
      role: 'rerank',
      messages: [{ role: 'user', content: prompt }],
      maxTokens: 500
    });
    const idOrder = ranked.map(r => r.id);
    return idOrder.map(id => results.find(r => r.id === id)).filter(Boolean);
  } catch {
    return results;
  }
}

async function checkDuplicate(newProposal, candidates) {
  if (!candidates || candidates.length === 0) return { is_duplicate: false };

  const candidateList = candidates.map(c =>
    `[${c.id}] ${c.title} – ${c.description || ''}`
  ).join('\n');

  return chatJSON({
    role: 'dedup',
    messages: [
      { role: 'system', content: DEDUP_PROMPT },
      { role: 'user', content: `Neuer Vorschlag: ${newProposal.title} – ${newProposal.description || ''}\n\nKandidaten:\n${candidateList}` }
    ],
    maxTokens: 200
  });
}

module.exports = { extractKnowledge, flushSession, generateInitiative, rerankResults, checkDuplicate };
