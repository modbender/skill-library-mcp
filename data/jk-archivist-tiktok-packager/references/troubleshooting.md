# Troubleshooting

## `Missing dependency: Pillow`

Install:

```bash
python3 -m pip install -r requirements.txt
```

## `No usable font found`

Set:

```bash
export TIKTOK_FONT_PATH=/absolute/path/to/font.ttf
```

## `Spec must contain exactly 6 slides`

Validate your JSON shape:

```json
{
  "slides": ["...", "...", "...", "...", "...", "..."]
}
```

## `Expected slide missing after render`

- Re-run renderer command directly
- Check write permissions under `outbox/`
- Confirm `python3` is available on PATH

## Verification failures

If filenames or dimensions mismatch, delete stale outputs and regenerate:

```bash
rm -rf outbox/_tmp_slides
python3 scripts/render_slides_pillow.py --spec examples/sample-slide-spec.json --out outbox/_tmp_slides --font /absolute/path/to/font.ttf
python3 scripts/verify_slides.py --dir outbox/_tmp_slides
```

## Postiz errors

### `Missing required environment variable: POSTIZ_API_KEY`

Set required vars before using `--postiz`:

```bash
export POSTIZ_API_KEY=...
export POSTIZ_TIKTOK_INTEGRATION_ID=...
```

### `Postiz upload failed (...)`

- Check API key validity
- Confirm `POSTIZ_BASE_URL` if using non-default endpoint
- Retry with network stable connection

### `Postiz draft creation failed (...)`

- Ensure integration ID is correct for TikTok
- Ensure upload step returned media references
- Retry with `--no-upload` or without `--postiz` to isolate render pipeline
