# Example: Commands

## /mitarbeiter

Shows the current employee list from GitHub.

**User:** `/mitarbeiter`

**Bot response (Telegram format):**

```
Mitarbeiterliste

Alex - Supervisor (kann einschulen)
Hauptfahrer, kann einschulen

Jordan - Geschult (kann einschulen)

Taylor - Geschult

Kim - In Einschulung (Trainer: Alex, Jordan)
Minderjährig, nicht alleine einteilen

Sam - In Einschulung (Trainer: Alex, Jordan)
Hat Auto

Gesamt: 5 Mitarbeiter (3 geschult, 2 in Einschulung)
```

## /hilfe

Shows available commands.

**User:** `/hilfe`

**Bot response:**

```
Verfügbare Befehle:
- /dienstplan - Neuen Dienstplan erstellen (CSV hochladen)
- /mitarbeiter - Aktuelle Mitarbeiterliste anzeigen
- /hilfe - Diese Hilfe anzeigen

So erstellst du einen Dienstplan:
1. Lade die CSV-Datei aus Google Forms hoch
2. Ich erkenne automatisch die Kalenderwoche
3. Du bekommst eine Vorschau
4. Nach Bestätigung wird der Plan zu GitHub hochgeladen
```

## Updating Employee Status

**User:** "Sam ist jetzt eingeschult"

**Bot:**
1. Loads `employees.json` from GitHub
2. Changes `status: ["untrained"]` to `status: ["trained"]`
3. Clears `trainerPriority: []`
4. Adds info: `"[16.02.2026] Eingeschult (trained)."`
5. Pushes to GitHub
6. Confirms: "Ich habe Sams Status auf 'geschult' aktualisiert."

## Detecting a New Employee

When an unknown name appears in the CSV:

**Bot:** "Ich habe einen neuen Mitarbeiter erkannt: **Chris**. Bitte gib mir seine E-Mail-Adresse und sag mir ob er minderjährig ist."

**User:** "chris@example.com, nicht minderjährig"

**Bot:**
1. Adds Chris with default values to `employees.json`
2. Pushes to GitHub
3. Confirms and continues with roster creation
