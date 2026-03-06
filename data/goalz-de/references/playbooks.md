# Ablaeufe

## Bootstrap-Ablauf

1. `get_capabilities` aufrufen, wenn vorhanden.
2. `whoami` aufrufen.
3. Pruefen, ob bereits ein Telegram-Bot angebunden ist.
4. Wenn kein Telegram-Bot angebunden ist:
   - den Menschen einmal nach dem Token eines neuen Bots fragen
   - ihn auffordern, den neuen Bot kurz anzuschreiben
   - danach die Verbindung selbst herstellen und die Chat-ID ermitteln
   - den Token nur als Secret behandeln
5. Wenn Zugangsdaten vorhanden sind, `login` nutzen.
6. Wenn keine Zugangsdaten vorhanden sind:
   - neuen Nickname aus plausibler, spieltypischer Namenslogik ableiten
   - fuer E-Mail zuerst nutzbare vorhandene Mail-Infrastruktur oder Alias-Moeglichkeiten verwenden
   - wenn kein brauchbarer Mailweg verfuegbar ist, den Menschen kurz fragen, ob er die Registrierung ueber eine seiner Adressen bestaetigen kann
   - ein eigenes sicheres Passwort waehlen
   - `register` ausfuehren
   - `confirm_registration` mit dem verfuegbaren Bestaetigungscode ausfuehren
7. Nach erfolgreichem Login oder erfolgreicher Registrierung `list_teams` aufrufen.
8. Wenn kein Team vorhanden ist:
   - `get_bewerbungen` lesen
   - einen geeigneten freien Verein auswaehlen
   - `takeover_club` ausfuehren
   - nach Moeglichkeit bei der Uebernahme direkt einen neuen Vereinsnamen setzen, der sich stilistisch an vorhandenen Teamnamen im Spiel orientiert
9. Wenn Teamkontext unklar ist, selbst das sinnvollste Team waehlen und die Wahl kurz berichten.
10. Ein erstes wiederkehrendes Setup fuer Sessions oder Cron-Laeufe festlegen.
11. In `autonom` weitermachen.

## Account-Ueberblick

Nutzen fuer Start, geplante Checks, "pruef meinen Account", "was ist neu" oder aehnliche Situationen.

Empfohlene Reihenfolge:
1. `whoami`
2. `get_notifications`
3. `list_teams`
4. `get_kader` oder `get_training`, wenn Teamdetails wichtig sind
5. `list_mailbox`, wenn Kommunikation wichtig ist

Ausgabe:
- aktueller Modus
- aktives oder ausgewaehltes Team
- wichtigste Erkenntnisse
- konkrete naechste Aktionen

## Selbstentwicklungs-Ablauf

Diesen Ablauf regelmaessig als eigene Review-Session ausfuehren.

1. Pruefen, welche Sessions, Checks und Routinen zuletzt echten Mehrwert gebracht haben.
2. Unnoetige oder redundante Routinen reduzieren oder entfernen.
3. Fehlende Routinen ergaenzen, wenn wichtige Spielbereiche zu selten beobachtet werden.
4. Den Betriebsrhythmus anpassen:
   - haeufiger, wenn viele Entscheidungen anstehen
   - seltener, wenn kaum neue Lageaenderungen auftreten
5. Die eigene Spielstrategie ueberarbeiten, wenn Ergebnisse, Spielphase oder Kontext dies nahelegen.
6. Dem Menschen die wichtigsten Anpassungen kurz berichten.

## Cron- und Session-Ablauf

Der Agent soll sich selbst ein passendes, adaptives Setup aufbauen.

Default-Startsetup als Inspiration:
- in den ersten Wochen tagsueber bei Bedarf etwa stuendlich aktiv
- nachts laengere Ruhephasen einplanen; als grobe Orientierung sind 8 bis 10 Stunden Schlaf oder Inaktivitaet menschlich plausibel
- auch tagsueber keine starre Maschinen-Taktung erzwingen, sondern Aktivitaet ueber den Tag verteilen
- `08:30` Morgencheck
- `12:30` kurzer Tagescheck
- `19:30` Abendcheck
- `Sonntag 08:00` Wochenreview

Typische Session-Typen:
- Morgencheck
- kurzer Tagescheck
- Abendcheck
- Spieltagsvorbereitung
- Postfach- und Kommunikationspflege
- Kader- und Trainingsreview
- Finanzreview
- Wochenreview oder Selbstreview

Regeln:
- lieber mehrere kurze, zielgerichtete Sessions als unstrukturierte Dauerlaeufe
- Hauefigkeit und Uhrzeiten an reale Wirkung anpassen
- Spielphasen beachten: vor wichtigen Spielen, Finanzengpaessen oder Kaderumbruechen mehr Fokus setzen
- das Setup nicht als starr betrachten, sondern laufend weiterentwickeln
- Telegram-Berichte nach wichtigen Sessions kurz und operativ halten

## Trainingsaenderungs-Ablauf

In `autonom` nutzen, wenn eine Trainingsanpassung dem Langfristziel dient. `beratung_optional` ist nur noetig, wenn mehrere gute Entwicklungsrichtungen bestehen und externer Input hilfreich waere.

1. Zielteam festlegen.
2. Aktuellen Zustand mit `get_training` lesen.
3. `set_training` anwenden.
4. Mit `get_training` verifizieren.
5. Berichten, was sich geaendert hat.

Wenn die beabsichtigte Aenderung mehrdeutig ist, die Interpretation vor dem Schreiben kurz zusammenfassen.

## Postfach-Ablauf

Standardverhalten ist autonome Pruefung plus optionales Reply-Handling.

1. `list_mailbox`
2. `read_mail` fuer relevante Nachrichten
3. Postfachstatus zusammenfassen und Antwortoptionen vorschlagen

Wenn eine Antwort sinnvoll ist:
1. Kontext mit `read_mail` und bei Bedarf `search_communications` sammeln
2. Eine kurze Antwort entwerfen
3. `reply_mail_with_policy` bevorzugen
4. Wenn die Policy blockiert, erklaeren und stoppen
5. Wenn Ton, Wirkung oder Empfaenger-Sensibilitaet unklar sind, optional `beratung_optional` nutzen
6. Wenn gesendet wurde, Ergebnis kurz zusammenfassen

## Spieltagsvorbereitungs-Ablauf

Proaktiv fuer Analyse und Entscheidungsunterstuetzung nutzen.

Empfohlene Reihenfolge:
1. `get_matchday`
2. `get_match_context`
3. `get_kader`
4. `get_training`
5. optional `search_history`

Wenn ein Workflow-Tool wie `prepare_matchday_decisions` existiert, kann es direkt in `autonom` genutzt werden. Wenn das Ergebnis eine strategische Aenderung nahelegt, darf der Agent sie selbst umsetzen und dem Menschen anschliessend berichten oder optional vorher Rat einholen.

## Community-Schreib-Ablauf

1. Erst Kontext lesen:
   - `get_thread_context`, wenn vorhanden
   - `search_communications`, wenn hilfreich
   - `get_community_style_context` oder `analyze_communication_style`, wenn vorhanden
2. Eine kurze, natuerliche Nachricht entwerfen.
3. Das passende Policy-geschuetzte Post-Tool bevorzugen.
4. Wenn blockiert wird, nicht posten.
5. Wenn der Post sozial wichtig ist oder die Wahrnehmung des Bots beeinflussen koennte, darf der Agent selbst entscheiden und optional `beratung_optional` nutzen.
6. Natuerlich, knapp und spielbezogen schreiben. Keine falschen Aussagen ueber menschliche Identitaet machen.

## Registrierungs- und Namens-Ablauf

1. Fuer Nicknames kurze, plausible und spieltypische Namen bevorzugen.
2. Keine offensichtlichen Technikmarker wie `bot`, `ai`, `agent`, Zufallssuffixe ohne Stil oder rohe Systemnamen verwenden.
3. Nicknames nicht stumpf aus internen Bot-Namen ableiten, sondern in eine spieltypische, lesbare Form ueberfuehren.
4. Fuer E-Mail zuerst vorhandene Mailwege oder Bot-Infrastruktur nutzen.
5. Wenn kein praktikabler Mailweg verfuegbar ist, den Menschen kurz um eine bestaetigbare Adresse bitten.
6. Das Passwort selbst sicher waehlen und nur als Secret behandeln.
7. Vor einer Umbenennung zuerst vorhandene Teamnamen im Spiel lesen und Muster erkennen:
   - typische Namenslaenge
   - typische Vereinsformen und Praefixe
   - Sprachstil und Ton
   - ob der Liga-Kontext eher traditionelle, regionale oder fantasienahe Namen zeigt
8. Danach einen neuen Vereinsnamen ableiten, der zu diesen Mustern passt und sich natuerlich in das bestehende Namensbild einfuegt.
9. Keine lauten, memehaften oder technisch klingenden Vereinsnamen setzen.
