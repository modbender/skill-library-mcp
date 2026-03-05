# gog Setup, Auth, and Usage Guide

> Practical guide for this Mac + Clawdbot environment. English-only version for sharing.

---

## 1. What is `gog`?

`gog` is a Google Workspace CLI. It lets you control Google services from the terminal:

- **Gmail** – search, send mail, drafts, replies
- **Calendar** – create / list / update events
- **Drive** – search files, inspect metadata
- **Docs** – export document content
- **Sheets** – read and update spreadsheets
- **Contacts** – list contacts

In this setup, the bot uses `gog` behind the scenes to:

- Create calendar events for you
- Check today’s schedule
- Send email (later)
- Look up recent Drive files and open them in the browser

---

## 2. Install `gog`

> You already have this installed; these steps are for reference or new machines.

### 2.1 Install via Homebrew

```bash
brew install steipete/tap/gogcli
```

Verify:

```bash
gog --version
```

---

## 3. Prepare OAuth credentials (one-time)

`gog` needs a Google OAuth client to access Gmail, Calendar, Drive, etc.

### 3.1 Create OAuth client in Google Cloud Console

1. Go to: <https://console.cloud.google.com/apis/credentials>
2. Select or create a GCP project.
3. Click **"Create credentials → OAuth client ID"**.
4. Application type: **Desktop app**.
5. After creation, download the JSON file (name similar to
   `client_secret_XXXXXXXXXXXX-xxxxx.apps.googleusercontent.com.json`).

### 3.2 Put JSON where `gog` expects it

On this Mac we use:

```bash
/Users/user/Library/Application Support/gogcli/credentials.json
```

Commands:

```bash
mkdir -p "/Users/user/Library/Application Support/gogcli"
mv ~/Downloads/client_secret_*.json \
  "/Users/user/Library/Application Support/gogcli/credentials.json"
```

### 3.3 Tell `gog` to use this file

```bash
gog auth credentials "/Users/user/Library/Application Support/gogcli/credentials.json"
```

---

## 4. Authorize each Google account (auth add)

In this environment you have three accounts wired up:

- `aiagentg888@gmail.com`
- `jackychen0615@gmail.com`
- `step1nework016@gmail.com`

### 4.1 Base command

General pattern:

```bash
gog auth add <email> --services gmail,calendar,drive,docs,sheets
```

Example:

```bash
gog auth add aiagentg888@gmail.com --services gmail,calendar,drive,docs,sheets
```

After running this, `gog` will:

1. Print an OAuth URL.
2. Open your browser.
3. You choose the given account in the browser and click **Allow**.

Verify with:

```bash
gog auth list
```

You should see the account with services:

```text
calendar,docs,drive,gmail,sheets
```

---

## 5. Calendar: creating and listing events

### 5.1 Create an event

Basic pattern:

```bash
gog calendar create <calendarId> \
  --summary "Title" \
  --from "START_ISO" \
  --to   "END_ISO" \
  --account <email>
```

In your environment we normally do:

```bash
cd /Users/user/clawd

gog calendar create primary \
  --summary "Meeting with mentor (LINE call)" \
  --from "2026-02-01T21:00:00+08:00" \
  --to   "2026-02-01T22:00:00+08:00" \
  --location "LINE online" \
  --account aiagentg888@gmail.com
```

Notes:

- `primary` = the main calendar for that account
- `--account` = which Google account you are using

### 5.2 List events for a day

```bash
cd /Users/user/clawd

gog calendar events primary \
  --from "2026-02-01T00:00:00+08:00" \
  --to   "2026-02-01T23:59:59+08:00" \
  --account aiagentg888@gmail.com
```

This is essentially what the bot uses for the "9am daily schedule summary" job.

---

## 6. Gmail: sending email

### 6.1 Simple plain-text email

```bash
cd /Users/user/clawd

gog gmail send \
  --account jackychen0615@gmail.com \
  --to someone@example.com \
  --subject "Test email" \
  --body "This is a test email."
```

### 6.2 Multi-line email via stdin

```bash
cd /Users/user/clawd

gog gmail send \
  --account step1nework016@gmail.com \
  --to someone@example.com \
  --subject "Meeting notes" \
  --body-file - << 'EOF'
Hi,

Here are the key points from todays meeting:

1. ...
2. ...

Thanks,
Your Name
EOF
```

---

## 7. Drive / Docs / Sheets: finding and opening files

### 7.1 List the 5 most recent files

```bash
cd /Users/user/clawd

gog drive search "*" --max 5 --account aiagentg888@gmail.com
```

Example output:

```text
ID                                            NAME
1eMQUXRcn9-wELa8cLoK6kXrdnEnkZoMyMzAtCH1Bmes  seo-article
...
1LFAI18uyzl1Zh0WKJrmhT4InrM7wYAl             Lens platform + AI voice assistant quote.docx
```

### 7.2 Get metadata + webViewLink

```bash
cd /Users/user/clawd

gog drive get 1LFAI18uyzl1Zh0WKJrmhT4InrM7wYAl \
  --json \
  --account aiagentg888@gmail.com
```

You will see something like:

```json
{
  "file": {
    "id": "1LFAI18uyzl1Zh0WKJrmhT4InrM7wYAl",
    "name": "Lens platform + AI voice assistant quote.docx",
    "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "webViewLink": "https://docs.google.com/document/d/1LFAI18uyzl1Zh0WKJrmhT4InrM7wYAl/edit?..."
  }
}
```

### 7.3 Open the file in your browser

```bash
open "https://docs.google.com/document/d/1LFAI18uyzl1Zh0WKJrmhT4InrM7wYAl/edit?usp=drivesdk&rtpof=true&sd=true"
```

This is exactly what the bot used earlier to "open the quote document".

> **Current limitation:** this version of `gog` does not have a built-in "download file to local disk" command. It can search, show metadata, and give you a link; the final "Download" click still has to happen in the browser.

---

## 8. Multi-account strategy

You now have three fully authorized accounts:

- `aiagentg888@gmail.com`
- `jackychen0615@gmail.com`
- `step1nework016@gmail.com`

Practical usage pattern:

- **Personal / AI experiments** → use `aiagentg888` calendar & mail
- **Main personal / work** → use `jackychen0615`
- **Testing / automation sandbox** → use `step1nework016`

Every `gog` command should explicitly specify which account to use:

```bash
--account <email>
```

The bot will also always ask you: **"Which account?"** before creating events or sending email, and then set `--account` accordingly.

---

## 9. Common errors & fixes

### 9.1 `missing --account`

Message:

```text
missing --account (or set GOG_ACCOUNT ...)
```

Cause: multiple accounts are configured; `gog` needs to know which one to use.

Fix:

- Add `--account some@gmail.com` to the command, **or**
- Set a default account:

```bash
export GOG_ACCOUNT=some@gmail.com
```

### 9.2 `OAuth client credentials missing`

Message:

```text
OAuth client credentials missing (OAuth client ID JSON)
```

Cause: `credentials.json` is missing or not in the expected location.

Fix:

1. Make sure the file exists at:

   `/Users/user/Library/Application Support/gogcli/credentials.json`

2. Re-run:

```bash
gog auth credentials "/Users/user/Library/Application Support/gogcli/credentials.json"
```

### 9.3 `Google Calendar API has not been used / disabled`

Message:

```text
Google Calendar API has not been used in project ... or it is disabled.
```

Cause: The GCP project has Calendar API disabled.

Fix:

1. Open the URL shown in the error (Calendar API page).
2. Click **Enable**.
3. Wait a minute or two, then retry the `gog` command.

---

## 10. How the bot uses `gog` for you

Whenever you say things like "help me schedule this" or "send an email":

1. The bot asks:
   - Which Google account?
   - Do you need a video link (Google Meet)?
   - Do you want to invite / email the other person?
2. The bot builds and runs the correct `gog` command on your Mac.
3. On success, it reports back with a standard format, for example for calendar events:

   - Title, time range, account
   - Location, video link (yes/no)
   - Who (if anyone) was invited or notified
4. If something fails (OAuth, missing API, etc.), the bot first tries to fix it, then only asks you for the **minimal** manual step (like clicking "Enable API" in GCP or approving OAuth once).
