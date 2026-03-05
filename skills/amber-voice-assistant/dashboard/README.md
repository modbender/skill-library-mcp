# Amber Voice Assistant Call Log Dashboard

A beautiful web dashboard for viewing and managing call logs from the Amber Voice Assistant (Twilio/OpenAI SIP Bridge).

## Features

- 📞 Timeline view of all calls (inbound/outbound)
- 📝 Full transcript display with captured messages
- 📊 Statistics and filtering
- 🔍 Search by name, number, or transcript content
- 🔔 Follow-up tracking with localStorage persistence
- ⚡ Auto-refresh when data changes (every 30s)

## Setup

### 1. Environment Variables

The dashboard uses environment variables for configuration. Set these before running:

```bash
# Required for direction detection
export TWILIO_CALLER_ID="+16473709139"

# Optional - customize names
export ASSISTANT_NAME="Amber"
export OPERATOR_NAME="Abe"

# Optional - customize paths (defaults work for standard setup)
export LOGS_DIR="$HOME/clawd/skills/amber-voice-assistant/runtime/logs"
export OUTPUT_DIR="$HOME/clawd/skills/amber-voice-assistant/dashboard/data"

# Optional - contact name resolution
export CONTACTS_FILE="$HOME/clawd/skills/amber-voice-assistant/dashboard/contacts.json"
```

**Environment variable defaults:**
- `TWILIO_CALLER_ID`: *(required, no default)*
- `ASSISTANT_NAME`: `"Assistant"`
- `OPERATOR_NAME`: `"the operator"`
- `LOGS_DIR`: `../runtime/logs` (relative to dashboard directory)
- `OUTPUT_DIR`: `./data` (relative to dashboard directory)
- `CONTACTS_FILE`: `./contacts.json` (relative to dashboard directory)

### 2. Contact Resolution (Optional)

To resolve phone numbers to names, create a `contacts.json` file:

```bash
cp contacts.example.json contacts.json
# Edit contacts.json with your actual contacts
```

**Format:**
```json
{
  "+14165551234": "John Doe",
  "+16475559876": "Jane Smith"
}
```

Phone numbers should be in E.164 format (with `+` and country code).

### 3. Processing Logs

Run the log processor to generate dashboard data:

```bash
# Using environment variables
node process_logs.js

# Or specify paths directly
node process_logs.js --logs /path/to/logs --out /path/to/data

# Help
node process_logs.js --help
```

The processor reads call logs from the `LOGS_DIR` (or `../runtime/logs` by default) and generates:
- `data/calls.json` - processed call data
- `data/calls.js` - same data as window.CALL_LOG_CALLS for file:// usage
- `data/meta.json` - metadata about the processing run
- `data/meta.js` - metadata as window.CALL_LOG_META

**Quick update script:**
```bash
./update_data.sh
```

### 4. Viewing the Dashboard

**Option 1: Local HTTP Server (Recommended)**

```bash
node scripts/serve.js
# Open http://127.0.0.1:8787/

# Or custom port/host
node scripts/serve.js --port 8080 --host 0.0.0.0
```

**Option 2: File Protocol**

Open `index.html` directly in your browser. The dashboard works with `file://` URLs.

### 5. Auto-Update (Optional)

To automatically reprocess logs when files change:

```bash
node scripts/watch.js
# Watches logs directory and regenerates data on changes (every 1.5s)

# Or specify custom paths
node scripts/watch.js --logs /path/to/logs --out /path/to/data --interval-ms 2000
```

## Usage

### Dashboard Interface

- **Stats Cards:** Click to filter by type (inbound, outbound, messages, etc.)
- **Search:** Filter by name, number, transcript content, or Call SID
- **Follow-ups:** Click 🔔 icon on any call to mark for follow-up
- **Refresh:** Click ↻ button or wait for auto-refresh (30s)
- **Transcript:** Click "Transcript" to expand full conversation

### Command-Line Options

**process_logs.js:**
```
--logs <dir>       Path to logs directory
--out <dir>        Path to output directory
--no-sample        Skip generating sample data
-h, --help         Show help
```

**watch.js:**
```
--logs <dir>       Path to logs directory
--out <dir>        Path to output directory
--interval-ms <n>  Polling interval in milliseconds (default: 1500)
-h, --help         Show help
```

**serve.js:**
```
--host <ip>        Bind address (default: 127.0.0.1)
--port <n>         Port number (default: 8787)
-h, --help         Show help
```

## File Structure

```
dashboard/
├── index.html           # Main dashboard HTML
├── process_logs.js      # Log processor (generalized)
├── update_data.sh       # Quick update script
├── contacts.json        # Your contacts (not tracked in git)
├── contacts.example.json # Example contacts file
├── README.md            # This file
├── scripts/
│   ├── serve.js         # Local HTTP server
│   └── watch.js         # Auto-update watcher
└── data/                # Generated data (git-ignored)
    ├── calls.json
    ├── calls.js
    ├── meta.json
    └── meta.js
```

## Integration with Amber Voice Assistant

This dashboard is designed to work standalone but integrates seamlessly with the Amber Voice Assistant skill:

1. The skill writes logs to `../runtime/logs/` (relative to dashboard)
2. Run `process_logs.js` to generate dashboard data
3. View the dashboard via HTTP server or file://
4. Optionally run `watch.js` for continuous updates

## Customization

**Change dashboard title:**
Edit the `<title>` and `<h1>` tags in `index.html`.

**Adjust auto-refresh interval:**
Edit the `setInterval` call at the bottom of `index.html` (default: 30000ms).

**Modify log processing logic:**
Edit `process_logs.js` - all hardcoded values are now configurable via environment variables.

## Troubleshooting

**No calls showing up:**
- Check that `LOGS_DIR` points to the correct directory
- Ensure logs exist (incoming_*.json and rtc_*.txt files)
- Run `process_logs.js` manually to see any errors

**Direction not detected correctly:**
- Set `TWILIO_CALLER_ID` to your Twilio phone number
- The script detects outbound calls by matching the From header

**Names not resolving:**
- Create `contacts.json` with your phone numbers in E.164 format
- Verify `CONTACTS_FILE` path is correct
- Check console for "Loaded N contacts" message

**Auto-refresh not working:**
- Ensure you're using the HTTP server (not file://)
- Check browser console for fetch errors
- Verify `data/meta.json` is being updated

## License

Part of the Amber Voice Assistant skill. See parent directory for license information.
