# Spec Schema

`--spec` accepts a JSON object:

```json
{
  "slides": ["line1", "line2", "line3", "line4", "line5", "line6"],
  "caption": "Optional caption override",
  "template": "intro",
  "audience": "operator",
  "ctaPack": "follow-focused",
  "hashtagPolicy": "tcg-default",
  "hashtagOverrides": ["#customtag"],
  "locale": "en",
  "ab_test": { "strategy": "caption-cta" },
  "style": {
    "preset": "default"
  }
}
```

## Fields

- `slides` (required): exactly 6 non-empty strings.
- `caption` (optional): overrides default caption output.
- `template` (optional): metadata label for source tracking.
- `audience` (optional): `beginner|operator|expert`.
- `ctaPack` (optional): `follow-focused|link-focused|engagement-focused`.
- `hashtagPolicy` (optional): `tcg-default|general`.
- `hashtagOverrides` (optional): additional hashtags.
- `locale` (optional): `en|es|fr` (currently used for CTA localization).
- `ab_test.strategy` (optional): `caption-cta|style|template`.
- `style.preset` (optional): one of:
  - `default`
  - `high-contrast`
  - `clean`
  - `midnight`

## CLI precedence

1. `--spec` (highest)
2. `--topic`
3. `--template`
4. default JK preset

## Runtime flags (non-spec)

- `--dry-run`
- `--postiz-only`
- `--no-upload`
- `--resume-upload`
- `--max-retries <n>`
- `--timeout-ms <n>`
