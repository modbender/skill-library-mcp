---
name: gatecrash-forms
description: CLI-first form builder with BYOK philosophy. Generate beautiful HTML forms from JSON schemas, handle submissions via your own SMTP server, store responses locally. Kimi Claw native. We crash gates, we don't build new ones.
metadata:
  {
    "openclaw":
      {
        "emoji": "🚀",
        "requires": { "bins": ["gatecrash-forms", "node"] },
        "install":
          [
            {
              "id": "npm-global",
              "kind": "node",
              "package": "gatecrash-forms",
              "bins": ["gatecrash-forms"],
              "label": "Install GateCrash Forms globally (npm)",
            },
          ],
      },
  }
---

# GateCrash Forms Skill

**CLI-first form builder with BYOK (Bring Your Own Keys) philosophy**

Generate beautiful, secure HTML forms from JSON schemas. Email notifications via YOUR SMTP server, response storage on YOUR infrastructure. No external services, no gatekeeping.

## ✨ Kimi Claw Ready

**Perfect for Kimi's 24/7 cloud agents:**
- ✅ Works natively in Kimi.com browser tabs
- ✅ Installed via ClawHub's 5,000+ skill library
- ✅ 40GB cloud storage for form responses
- ✅ Agent-friendly email providers (agentmail.to, Resend)

Your AI assistant can now generate and manage forms for you!

## Quick Start

### Generate a Form

```bash
./scripts/generate.sh examples/feedback.json output.html
```

### Start Server

```bash
./scripts/serve.sh 3000
```

Visits http://localhost:3000 to see all forms.

### Initialize Project

```bash
./scripts/init.sh
```

Creates `forms/` and `responses/` directories with example forms.

## Features

- 🎨 **8+ Field Types:** text, email, textarea, select, radio, checkbox, scale/rating, date
- 🔒 **Security Hardened:** XSS prevention, CSRF tokens, honeypot spam protection, rate limiting
- 📧 **BYOK Email:** Use your own SMTP server (Zoho, Gmail, SendGrid, etc.)
- 💾 **Local Storage:** Responses saved as JSON or CSV
- 🎨 **Beautiful UI:** Gradient purple theme, responsive design
- 🚀 **Self-Hosted:** Deploy anywhere Node.js runs

## Configuration

Set up your SMTP credentials globally:

```bash
gatecrash-forms config smtp.host smtp.example.com
gatecrash-forms config smtp.port 465
gatecrash-forms config smtp.secure true
gatecrash-forms config smtp.auth.user your-email@example.com
gatecrash-forms config smtp.auth.pass your-password
```

Or configure per-form in the JSON schema.

## Example Form Schema

```json
{
  "title": "Customer Feedback",
  "description": "We'd love to hear from you!",
  "fields": [
    {
      "type": "scale",
      "name": "rating",
      "label": "Overall satisfaction",
      "min": 1,
      "max": 5,
      "required": true
    },
    {
      "type": "checkbox",
      "name": "topics",
      "label": "What interested you most?",
      "options": ["Product", "Service", "Price", "Experience"]
    },
    {
      "type": "textarea",
      "name": "comments",
      "label": "Additional comments",
      "maxLength": 500
    }
  ],
  "submit": {
    "email": "your-email@example.com",
    "storage": "responses/feedback.json"
  }
}
```

## Use Cases

- **Customer Feedback:** Collect product/service feedback
- **Contact Forms:** Simple contact forms for websites
- **Event Registration:** Sign up forms for workshops/events
- **Surveys:** Market research, user surveys
- **Lead Generation:** Capture leads without third-party services

## Philosophy: We Crash Gates

GateCrash Forms is **NOT** a service. It's a toolmaker.

- ✅ Your SMTP server (email notifications)
- ✅ Your storage (form responses)
- ✅ Your deployment (host anywhere)
- ✅ Your data (no external servers)

No GateCrash accounts. No GateCrash servers. No gatekeeping.

## Links

- **GitHub:** https://github.com/Phoenix2479/gatecrash-forms
- **npm:** https://www.npmjs.com/package/gatecrash-forms
- **Manifesto:** Read MANIFESTO.md in the project
- **Documentation:** Full docs in README.md

## Commands Reference

```bash
# Generate form from schema
gatecrash-forms generate schema.json output.html

# Start HTTP server
gatecrash-forms serve [port]

# Set global config
gatecrash-forms config <key> <value>

# Initialize project
gatecrash-forms init

# Show help
gatecrash-forms help
```

## License

MIT - Use it, fork it, sell it. Just don't gatekeep it.

---

*Made with 🔥 by Dinki & Molty*

**"We crash gates. We don't build new ones."**
