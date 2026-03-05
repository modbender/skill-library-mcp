---
name: glass2claw
description: "Ray-Ban glasses → voice command → WhatsApp → OpenClaw auto-routes your photo into the right database. Hands-free life logging."
version: "2.3.3"
metadata:
  {
    "openclaw":
      {
        "emoji": "👁️",
        "tools": ["sessions_send", "message"]
      }
  }
---

# glass2claw: From Your Eyes to Your Database — Instantly

## 🛠️ Installation

### 1. Ask OpenClaw (Recommended)
Tell OpenClaw: *"Install the glass2claw skill."* The agent will handle the installation and configuration automatically.

### 2. Manual Installation (CLI)
If you prefer the terminal, run:
```bash
clawhub install glass2claw
```

You're wearing your **Meta Ray-Ban glasses**. You see a wine label, a business card, a tea tin. You say:

> *"Hey Meta, take a picture and send this to myself on WhatsApp."*

That's it. OpenClaw does the rest.

The photo lands in your WhatsApp. OpenClaw's Vision Router picks it up, classifies what it is, and writes a structured entry into the right database — wine cellar, contacts, tea collection, whatever you've set up.

**No typing. No app switching. No friction.**

---

## 📸 How It Works

```
Meta Ray-Ban glasses
  → "Hey Meta, take a picture and send this to myself on WhatsApp"
      → Meta AI delivers the photo to your WhatsApp
          → OpenClaw (WhatsApp session) receives the image
              → classifies intent: Wine | Tea | Contacts | Cigar | ...
                  → routes to the matching specialist agent
                      → writes structured entry to your database
```

Your only action is the voice command. Everything downstream is automatic.

---

## 🔧 What You Need to Set Up

This skill is a **routing protocol** — it defines the pattern, not the specific implementation. You bring your own:

- **Meta AI + WhatsApp connection** — enable Meta AI on your Ray-Ban glasses and link it to WhatsApp (one-time setup in the Meta View app)
- **OpenClaw with WhatsApp channel** — your OpenClaw instance needs a WhatsApp session to receive the incoming images
- **Destination databases** — connect whichever databases you want: Notion, Airtable, a local file, a Discord channel. The skill routes to wherever you configure it
- **Database credentials** — set up API access for your chosen database yourself (Notion API key, Airtable token, etc.)

> The skill templates in this package show one reference implementation using Notion + Discord. Adapt them to your own stack.

---

## 🔒 Privacy

This skill processes **photos from your personal camera**. Images flow from WhatsApp → your OpenClaw instance → your configured destination. Any external services you connect (Notion, Discord, etc.) are governed by their own privacy policies. All routing logic runs on your own OpenClaw instance.

---

## 📦 What's Included

- `SAMPLE_AGENT.md` — reference routing logic for the hub agent
- `SAMPLE_SOUL_WINE.md` — reference persona for a wine specialist agent

Use these as starting points. Customize for your own categories and destinations.

---

*Created by JonathanJing | AI Reliability Architect*
