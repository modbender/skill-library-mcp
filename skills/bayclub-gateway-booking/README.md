# Bay Club Court Manager OpenClaw Bot

Never miss a court slot again. This bot handles tennis and pickleball bookings at Bay Club Connect automatically - you can even text it from WhatsApp.

## What It Does

- 🎾 Check and book tennis courts
- 🏓 Check and book pickleball courts
- 🤖 Runs browser automation via Stagehand
- 📅 Works with "today", "tomorrow", or specific weekdays
- 💬 WhatsApp interface - just text to book
- 📆 Auto-adds bookings to Google Calendar

## The Story

I started building this by SSHing into my DigitalOcean droplet in VSCode, writing the initial automation code. But then I realized I could just... chat with OpenClaw via WhatsApp to finish it.

So I did. The rest of the development - debugging XPath selectors, adding calendar integration, cleaning up files, writing docs, pushing to GitHub - all happened through WhatsApp messages. No more switching between terminal windows.

## Setup

### Option 1: DigitalOcean (Easiest)

1. Go to the [OpenClaw marketplace page](https://marketplace.digitalocean.com/apps/openclaw)
2. Click "Create OpenClaw Droplet"
3. Pick the $21/month plan
4. Wait ~2 minutes for it to boot

Full guide: [How to Run OpenClaw on DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-run-openclaw)

### Option 2: Local Install

If you already have OpenClaw running locally, skip to "Install the Bot" below.

## Connect WhatsApp

After your droplet starts:

1. SSH in: `ssh root@your-droplet-ip`
2. OpenClaw will show a QR code in the terminal
3. Open WhatsApp → Settings → Linked Devices → Link a Device
4. Scan it
5. Done!

You can now text your droplet like it's a person. Wild.

## Install the Bot

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/elizabethsiegle/bayclub-pb-tennis-openclaw-bot.git bayclub_manager
cd bayclub_manager
npm install
```

### Add Your Bay Club Credentials

Either add them to OpenClaw's config:

```bash
openclaw gateway config.patch
```

```json
{
  "env": {
    "BAYCLUB_USERNAME": "your-username",
    "BAYCLUB_PASSWORD": "your-password"
  }
}
```

Or just export them:

```bash
export BAYCLUB_USERNAME="your-username"
export BAYCLUB_PASSWORD="your-password"
```

### Google Calendar (Optional)

If you want bookings to auto-appear in your calendar:

**1. Create a service account**

- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Make a project (or use an existing one)
- Enable the Calendar API
- Create a service account under Credentials
- Generate a JSON key and download it

**2. Share your calendar**

- Open [Google Calendar](https://calendar.google.com)
- Find your calendar (or make one called "Court Bookings")
- Settings → Share with specific people
- Add the service account email (it's in the JSON: `client_email`)
- Give it "Make changes to events" permission

**3. Add credentials**

Copy the JSON to the bot directory:

```bash
cp ~/Downloads/your-key.json ~/.openclaw/workspace/skills/bayclub_manager/google-calendar-credentials.json
```

Set your calendar ID:

```bash
echo 'export GOOGLE_CALENDAR_ID="your-email@gmail.com"' >> ~/.bashrc
source ~/.bashrc
```

That's it. Future bookings will show up in your calendar automatically.

## Usage

### Via WhatsApp (Natural Language)

Just text your OpenClaw agent:

- "Check tennis courts for Sunday"
- "Book pickleball Saturday at 10am"
- "What's available tomorrow?"

### Via Command Line

```bash
# Check what's open
NODE_ENV=development STAGEHAND_ENV=LOCAL HEADLESS=true npx ts-node cli.ts check tennis saturday

# Book a slot
NODE_ENV=development STAGEHAND_ENV=LOCAL HEADLESS=true npx ts-node cli.ts book pickleball sunday "10:00 AM - 11:00 AM"
```

## How It Works

1. Logs into Bay Club Connect
2. Navigates to the booking page using Stagehand
3. Selects sport + duration
4. Finds available time slots
5. Books the court
6. Adds it to your Google Calendar

Pretty straightforward automation. The interesting part is that you can control it entirely through text messages.

## Files

- `cli.ts` - command-line interface
- `bayclub_skills.ts` - OpenClaw skill exports
- `BayClubBot.ts` - browser automation logic
- `GoogleCalendarService.js` - calendar integration
- `SKILL.md` - skill definition
- `package.json` - dependencies

## Why OpenClaw?

Normal workflow: Write code → SSH into server → Test → Debug → Deploy

OpenClaw workflow: Text "build this" → Done

It's legitimately different. You're having a conversation with something that can read files, write code, run tests, and push to GitHub. I built this entire bot without opening a terminal once.

Links:
- [Docs](https://docs.openclaw.ai)
- [GitHub](https://github.com/openclaw/openclaw)
- [DigitalOcean Marketplace](https://marketplace.digitalocean.com/apps/openclaw)
- [Discord Community](https://discord.gg/openclaw)

## Troubleshooting

**"Invalid username or password"**  
Check your Bay Club credentials in the environment variables.

**"Timeout waiting for element"**  
Bay Club might've changed their website. The XPath selectors in `BayClubBot.ts` may need updating.

**Browser won't launch**  
Install Playwright's browser locally:
```bash
npx playwright install chromium
```

In production, Stagehand uses Browserbase's cloud browsers automatically.

## Todo

- Auto-book weekly recurring slots
- Notify when new slots open
- Support other Bay Club locations
- Maybe add SMS notifications
