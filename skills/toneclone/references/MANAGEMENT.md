# ToneClone Management Guide

Create, update, and manage personas, knowledge cards, and training data.

## Personas

### List Personas
```bash
toneclone personas list
toneclone personas list --format=json
toneclone personas list --filter="marketing"
```

### Get Persona Details
```bash
toneclone personas get <persona-id>
toneclone personas get <persona-id> --format=json
```

### Create Persona
```bash
toneclone personas create --name="Professional Writer"
toneclone personas create --name="Casual Blogger" --preset="blogger"
toneclone personas create --interactive  # Guided creation
```

### Update Persona
```bash
toneclone personas update <persona-id> --name="New Name"
```

### Delete Persona
```bash
toneclone personas delete <persona-id>
```

## Knowledge Cards

### List Knowledge Cards
```bash
toneclone knowledge list
toneclone knowledge list --format=json
toneclone knowledge list --filter="product"
```

### Get Knowledge Card Details
```bash
toneclone knowledge get "Card Name"
toneclone knowledge get "Card Name" --format=json
```

### Create Knowledge Card
```bash
toneclone knowledge create --name="Product Brief" \
  --instructions="Product details: [description]. Key features: [list]. Target audience: [description]."

toneclone knowledge create --interactive  # Guided creation
```

### Update Knowledge Card
```bash
toneclone knowledge update "Card Name" --name="New Name"
toneclone knowledge update "Card Name" --instructions="Updated instructions"
```

### Delete Knowledge Card
```bash
toneclone knowledge delete "Card Name"
```

### Associate/Disassociate with Personas
```bash
toneclone knowledge associate --knowledge="Product Brief" --persona="Marketing"
toneclone knowledge disassociate --knowledge="Product Brief" --persona="Marketing"
```

## Training Data

### List Training Files
```bash
toneclone training list
toneclone training list --format=json
```

### Add Training Data

From file:
```bash
toneclone training add --file=document.txt --persona="Professional"
```

From text:
```bash
toneclone training add --text="Sample content here" --persona="Casual" --filename="sample.txt"
```

From directory:
```bash
toneclone training add --directory=./my-writing --persona="Writer" --recursive
```

### Associate/Disassociate Files
```bash
toneclone training associate --file-id=<file-id> --persona="Writer"
toneclone training disassociate --file-id=<file-id> --persona="Writer"
```

### Remove Training Data
```bash
toneclone training remove --file-id=<file-id>
```

### Rate Limits

When uploading multiple samples quickly, you may hit rate limits. Solutions:
- Add 1-2 second delays between uploads
- Use `--directory` to batch upload (handles rate limiting internally)
- If rate limited mid-upload, wait a few seconds and use `training associate` to link the uploaded file

## StyleGuard

Auto-replace AI-sounding phrases and patterns in generated output.

### List Rules
```bash
toneclone personas style-guard list <persona>
```

### Add Rule
```bash
# AI mode - contextual rewrite
toneclone personas style-guard add <persona> --word "utilize" --mode AI

# CUSTOM mode - fixed replacement
toneclone personas style-guard add <persona> --word "in order to" --mode CUSTOM --replacement "to"

# Global rule (applies to all personas)
toneclone personas style-guard add --global --word "delve" --mode AI
```

### Apply Curated Bundle
```bash
# Preview bundle contents
toneclone personas style-guard bundle preview --type comprehensive

# Apply to persona (limited or comprehensive)
toneclone personas style-guard bundle apply --persona <persona> --type limited

# Check what's applied
toneclone personas style-guard bundle status --persona <persona>

# Remove bundle rules
toneclone personas style-guard bundle remove --persona <persona>
```

Bundle types:
- `limited` — Essential replacements (em-dashes, smart quotes, ellipsis) ~7 items
- `comprehensive` — Superset including common AI phrases ("delve", etc.) ~26 items

### Update/Delete Rules
```bash
toneclone personas style-guard update <rule-id> --word "new word" --mode CUSTOM --replacement "new replacement"
toneclone personas style-guard delete <rule-id>
```

## Typos (FingerPrint)

Add natural typo imperfections to make output feel more human.

### Get Settings
```bash
toneclone personas typos get <persona>
```

### Configure Typos
```bash
# Enable with preset intensity
toneclone personas typos set <persona> --enable --intensity subtle

# Disable
toneclone personas typos set <persona> --disable

# Custom rate with protections
toneclone personas typos set <persona> --rate 0.008 --max-per-chunk 5 --protected urls,emails,code
```

Intensity presets:
- `none` — 0% (disabled)
- `subtle` — 0.5%
- `noticeable` — 1.0%
- `high` — 2.0%

Protected contexts prevent typos in:
- `urls` — Web addresses
- `emails` — Email addresses
- `code` — Code blocks

## Knowledge Card Content Ideas

Good knowledge cards include:
- **Contact info**: Email, phone, address, timezone
- **Booking/scheduling**: Calendar links, booking URLs
- **Snippets**: Common phrases, taglines, signatures
- **URLs**: Website, social profiles, product links
- **Company info**: Mission, values, team bios
- **Product details**: Features, pricing, differentiators
- **Brand voice**: Tone guidelines, do's and don'ts
