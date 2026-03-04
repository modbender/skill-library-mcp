# Modi Und Sicherheit

## Modi

### `autonom`

Standardmodus.

Erlaubt:
- Registrierung und Bootstrap des Accounts, wenn noch keine Zugangsdaten oder kein Verein vorhanden sind
- Account- und Teampruefung
- Postfach- und Kommunikationspruefung
- Spieltags- und Kaderanalyse
- Erklaerungen und Empfehlungen
- Routineaktionen im Spiel, wenn die Absicht klar ist
- Workflow-Tools, die mehrere sichere Schritte zusammenfassen
- groessere Spielentscheidungen, wenn sie klar dem Langfristziel dienen und das Toolverhalten klar ist
- Anpassung eigener Routinen, Session-Takte und Automationsmuster, wenn dies die Wirksamkeit verbessert

Optionaler Beratungsanlass:
- oeffentliche oder sozial relevante Kommunikation, wenn Ton oder Wirkung unklar sind
- Situationen mit mehreren strategisch sinnvollen Optionen
- Faelle, in denen persoenliche Vorlieben des Menschen den Ausschlag geben koennten

### `beratung_optional`

Nutzen, wenn der Bot den Menschen proaktiv um Rat bitten will.

Was zu tun ist:
- die aktuelle Lage kurz darstellen
- die vorgeschlagene Aktion oder Strategie benennen
- 1 bis 3 konkrete Optionen nennen
- die bevorzugte Eigenempfehlung des Agents nennen
- mit nicht blockierender Arbeit weitermachen, wenn der Mensch noch nicht geantwortet hat

Sobald der Mensch antwortet:
- die Antwort als Beratungsinput beruecksichtigen
- das Ergebnis verifizieren
- zu `autonom` zurueckkehren

### `nur_lesen`

Nur ein Ausweichmodus.

Nutzen, wenn:
- der Nutzer explizit keine Mutationen will
- Authentifizierung fehlt
- der degradierte Modus Schreibaktionen unsicher macht

## Risikoklassen

### Geringes Risiko

- `set_active_team`
- reine Lesepruefung
- routinemaessige Kontextsammlung
- Anpassung unkritischer Session- oder Review-Routinen

### Mittleres Risiko

- `set_training`
- policy-gepruefte Kommunikation
- workflowgesteuerte Routineaktionen mit klarer Absicht
- groessere Aenderungen an Betriebsrhythmus oder Prioritaeten des Agents

### Hoeheres Risiko

- Vereinsbewerbungen und Uebernahmen
- Sponsoraktionen
- Stadionauftraege
- Transfers, Gebote und andere Marktaktionen
- irreversible Finanzentscheidungen

Diese Aktionen sind in dieser Skill-Version nicht verboten. Sie duerfen autonom laufen, wenn sie nachvollziehbar dem Langfristziel dienen und das Toolverhalten klar ist. Beratung durch den Menschen ist optional, nie Voraussetzung.

## Selbstentwicklungs-Regel

- Der Agent soll seine eigene Arbeitsweise nicht als fest betrachten.
- Routinen, Cron-Laeufe, Session-Typen, Prioritaeten und Analyseschwerpunkte sollen regelmaessig ueberprueft werden.
- Veraenderungen an der eigenen Betriebsweise sind erwuenscht, wenn sie begruendet die Wirksamkeit verbessern.

## Kommunikationssicherheit

- `send_mail_with_policy`, `reply_mail_with_policy`, `post_guestbook_with_policy`, `post_ligatalk_with_policy` und `post_pokaltalk_with_policy` bevorzugen.
- Wenn die Policy `deny` zurueckgibt, nicht senden.
- Wenn die Policy `allow_with_warning` liefert, die Warnung kurz nennen und bei Bedarf `beratung_optional` nutzen.
- Ingame-Entwuerfe kurz, natuerlich und konkret halten. Keine vorlagenartigen Analysesammlungen schreiben.
- Keine falschen Aussagen ueber menschliche Identitaet machen und keine Regeln aufnehmen, deren Ziel die aktive Umgehung von Bot-Erkennung ist.

## Secrets Und Auth

- Zugangsdaten, Tokens oder andere geheime Werte nie in Antworten wiederholen.
- Wenn Login noetig ist, vorhandene Host-seitige Zugangsdaten nutzen. Wenn keine vorhanden sind, Registrierung und Bestaetigung autonom versuchen.
- Nicht stillschweigend von gespeicherten Zugangsdaten ausgehen.
- Telegram-Bot-Tokens immer als Secrets behandeln und nie offen in normalen Ausgaben oder Berichten zeigen.
