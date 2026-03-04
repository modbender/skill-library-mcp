---
name: iserv
description: HTTP client for IServ school platforms. Log in to an IServ instance (e.g. https://grabbe-dt.de) and fetch common student data like unread mail counts, calendar events, files/folders, tasks/exercises, announcements/news, and other IServ modules via HTTP endpoints. Includes best-effort file ops + exercise submission.
---

# IServ (school platform)

This skill uses an HTTP client (no browser automation) to log in and call IServ endpoints.

## Credentials / security

- Do NOT hardcode credentials.
- Provide credentials via environment variables.

Single profile:
- `ISERV_BASE_URL` (e.g. `https://grabbe-dt.de`)
- `ISERV_USER`
- `ISERV_PASS`

Multiple profiles (parallel):
- set `ISERV_PROFILE=<name>` or pass `--profile <name>`
- provide `ISERV_<PROFILE>_BASE_URL`, `ISERV_<PROFILE>_USER`, `ISERV_<PROFILE>_PASS`

## Commands

```bash
cd skills/iserv/scripts

# unread inbox count
./iserv.py mail-unread

# last 3 mails (IMAP)
./iserv.py mail-last --n 3

# upcoming calendar events (JSON)
./iserv.py calendar-upcoming

# list files (JSON)
./iserv.py files-list --path "/"        # root
./iserv.py files-list --path "/Files"   # typical user file area

# search files/folders recursively by substring
./iserv.py files-search --query "bio" --start-dir "/Files" --max-depth 6

# download a file (best-effort across IServ versions)
./iserv.py files-download --path "/Files/foo.pdf" --out-dir ./downloads

# upload a file (prefers FS Dropzone-style chunked upload; falls back to legacy form upload)
./iserv.py files-upload --file ./foo.pdf --dest-dir "/Files"
# optionally tune chunk size (bytes)
./iserv.py files-upload --file ./foo.pdf --dest-dir "/Files" --chunk-size 8388608

# create folder (best-effort; depends on IServ version)
./iserv.py files-mkdir --path "/Dokumente/Neu"

# rename/move (best-effort)
./iserv.py files-rename --src "/Dokumente/Alt.txt" --dest "/Dokumente/Neu.txt"

# delete (best-effort; USE WITH CARE)
./iserv.py files-delete --path "/Dokumente/Neu.txt"

# messenger: list chats / conversations
./iserv.py messenger-chats

# messenger: fetch messages for a chat
./iserv.py messenger-messages --chat-id <ID>

# messenger: send message
./iserv.py messenger-send --chat-id <ID> --text "Hello"

# list exercises (best-effort HTML scrape)
./iserv.py exercise-list --limit 50

# view one exercise + list attachments (optionally download them)
./iserv.py exercise-detail --id 123
./iserv.py exercise-detail --id 123 --download-dir ./downloads

# attempt to submit an exercise file (best-effort; depends on IServ version)
./iserv.py exercise-submit --id 123 --file ./solution.pdf --comment "Abgabe"
```

## Notes / next steps

- Exercises: listing/details/submission are implemented via HTML scraping.
  Submission is now form-driven (parses the actual `<form>` on the exercise page and posts multipart), which is more robust than guessing an internal upload API.
  If it still fails on a specific IServ instance, capture:
  - the HTML of the exercise detail page (after login)
  - response status + redirect URL

- Files: list/download/upload + mkdir/rename/delete are implemented as **best-effort** across IServ versions.
  Some instances expose slightly different endpoints; the client tries to discover Symfony FOS routes (when available) and falls back to common API paths.

Ideas to extend further:
- richer exercise parsing (due dates, teacher, description)
- announcements/news
- messenger notifications (currently experimental)
- robust file search, move/copy, and recursive folder download

Reference: IServ routes are discoverable via the bundled FOS routes JS (commonly `/iserv/js/fos_js_routes.js`; some instances also use `/iserv/js/assets/fos_js_routes*.js`).
