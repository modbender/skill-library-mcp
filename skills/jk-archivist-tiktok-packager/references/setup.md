# Setup

## Requirements

- Node.js 20+
- Python 3.10+
- Pillow dependency

Install Python dependency:

```bash
python3 -m pip install -r requirements.txt
```

Optional env:

- `TIKTOK_FONT_PATH`: absolute `.ttf` font path
- `POSTIZ_BASE_URL`, `POSTIZ_API_KEY`, `POSTIZ_TIKTOK_INTEGRATION_ID` (reserved for future upload phases)

## Core command

```bash
node scripts/tiktok-intro-draft.mjs
```

Run from the skill directory root so `scripts/` can resolve local paths.

## Custom slide modes

Use your own spec:

```bash
node scripts/tiktok-intro-draft.mjs --spec /absolute/path/to/spec.json
```

Generate copy from a topic (deterministic template):

```bash
node scripts/tiktok-intro-draft.mjs --topic "your topic"
```

Choose template/style:

```bash
node scripts/tiktok-intro-draft.mjs --template educational --style clean
```

Audience and caption controls:

```bash
node scripts/tiktok-intro-draft.mjs --audience expert --cta-pack engagement-focused --hashtag-policy general
```

A/B test candidates:

```bash
node scripts/tiktok-intro-draft.mjs --ab-test caption-cta
```

Dry-run / verbose:

```bash
node scripts/tiktok-intro-draft.mjs --dry-run --verbose
```

## Optional Postiz mode

Set:

- `POSTIZ_API_KEY`
- `POSTIZ_TIKTOK_INTEGRATION_ID`
- `POSTIZ_BASE_URL` (optional, defaults to public v1)

Then run:

```bash
node scripts/tiktok-intro-draft.mjs --postiz
```

Resume partial uploads (if prior run failed mid-way):

```bash
node scripts/tiktok-intro-draft.mjs --postiz --resume-upload
```
