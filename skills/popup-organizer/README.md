# ClawHub Skill — PopUp Organizer

This directory contains the ClawHub skill definition for the PopUp organizer API — searching vendors, managing events, sending booking inquiries, and tracking invoices.

**Scope:** Full organizer API access — vendor search, event CRUD, inquiry management, invoices, saved vendors, profile management. Does not include referral program features (see `clawhub-skill/` for that).

## Publishing

### 1. Authenticate (one-time)

```bash
npx clawhub@latest auth login --token "clh_..." --no-browser --registry "https://www.clawhub.ai/"
```

Replace `clh_...` with your actual CLI token.

### 2. Publish

```bash
npx clawhub@latest publish ./clawhub-organizer \
  --slug popup-organizer \
  --name "PopUp Organizer" \
  --version 1.0.0 \
  --changelog "Initial release: vendor search, event management, inquiries, invoices, saved vendors, profile" \
  --tags "events,vendors,food-trucks,marketplace,booking,invoicing,organizer"
```

### 3. Verify

```bash
npx clawhub@latest info popup-organizer
```

## Updating

```bash
npx clawhub@latest publish ./clawhub-organizer \
  --slug popup-organizer \
  --name "PopUp Organizer" \
  --version 1.1.0 \
  --changelog "Description of changes" \
  --tags "events,vendors,food-trucks,marketplace,booking,invoicing,organizer"
```
