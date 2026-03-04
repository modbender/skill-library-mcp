# Example: CSV Upload and Roster Creation

## Typical Flow

### 1. Upload CSV

The user sends a CSV file from Google Forms to the bot. The CSV contains availability with dates in the column headers.

**Example CSV:**

```csv
Timestamp,"Administrative Arbeit [Mo., 16.02.]",Name,"[Mo., 16.02.]","[Di., 17.02.]","[Mi., 18.02.]","[Do., 19.02.]","[Fr., 20.02.]","[Sa., 21.02.]",An welchen Tagen kannst du dein Auto einsetzen?,Kommentar
2026/02/13 10:44:22,,,Alex🟦🟪🚗,ab 15:00,ab 14:30,ab 14:30,ab 14:30,ab 14:00,9:00-12:00,"Mo., Di., Mi., Do., Fr., Sa.",
2026/02/13 11:02:15,,,Jordan🟦🟪,ab 14:00,ab 14:00,ab 15:30,ab 14:00,ab 14:00,nicht möglich,nicht möglich,
2026/02/13 11:30:00,,,Kim🟥,ab 15:00,nicht möglich,"ab 15:00, bis 18:00",ab 15:00,ab 15:00,nicht möglich,nicht möglich,
2026/02/13 12:00:00,,,Sam🟥🚗,ab 16:00,ab 15:00,ab 15:00,ab 15:00,"ab 15:30",nicht möglich,"Mi., Do., Fr.",Donnerstag hab ich nur bis 17:30 Zeit
```

### 2. Bot Response (automatic)

The bot:
1. Loads `employees.json` from GitHub (Step 0)
2. Detects KW 08/2026 from the date columns
3. Parses CSV availability and status emojis
4. Creates the roster with validation
5. Shows a formatted preview:

```
Mitarbeiterdaten geladen. Untrained: Sam (Trainer: Alex/Jordan), Kim (Trainer: Alex/Jordan, minderjährig). Erstelle jetzt den Plan...

Ich habe die Verfügbarkeiten für KW 08/2026 (Mo. 16.02 - Sa. 21.02) erkannt.

(Roster preview with emojis and formatting)

Soll ich den Plan hochladen?
```

### 3. Confirmation and Upload

**User:** "PDF bitte"

**Bot:**
1. Pushes JSON to GitHub via `push-to-github.sh`
2. Triggers PDF build via `trigger-build.sh` with chat ID
3. Responds: "Die PDF wird gerade gebaut und wird dir in ca. 3-5 Minuten hier im Chat als Dokument zugeschickt."

## Key Planning Rules (Examples)

### Departure Rule

- Shift starts at 15:00, Sam has "ab 16:00" on Monday
- Sam is NOT scheduled on Monday (misses the departure)

### Trainer Assignment

- Kim is `untrained` with `trainerPriority: ["alex", "jordan"]`
- Kim is ALWAYS grouped with Alex (when available), Jordan only as fallback

### Car Capacity

- Max. 5 people per car (including driver)
- With 7 available employees + 1 driver: Second car needed

### End Time Rule

- Kim has "ab 15:00, bis 18:00" on Wednesday
- Shift ends at 18:30 -> Kim is NOT scheduled (hard end before shift end)
