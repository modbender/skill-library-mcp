---
name: ui-element-ops
description: Parse UI screenshots into structured element JSON (type, OCR text, bbox) and operate desktop UI from parsed elements. Use when a user asks to detect/locate UI elements, return coordinates, find elements by text/type, wait for element appearance or disappearance, click/type/press keys/hotkeys, take screenshots, or calibrate coordinates for multi-display/DPI/window offsets.
---

# UI Element Ops

Parse one or more screenshots into a machine-readable JSON schema with:

- `type` (normalized UI element type)
- `bbox_px` and `bbox_norm`
- `text` (OCR/caption content when available)
- `clickable` flag
- optional overlay image with labeled boxes
- desktop actions via `scripts/operate_ui.py` (click/type/key/hotkey/screenshot)
- element query and orchestration via `scripts/operate_ui.py` (`find`, `wait`)
- coordinate calibration profile for multi-display/DPI/window offset (`calibrate`)

## Quick Start

1. Prepare runtime once per machine:
```bash
skills/ui-element-ops/scripts/bootstrap_omniparser_env.sh "$PWD"
```

2. Parse one screenshot:
```bash
skills/ui-element-ops/scripts/run_parse_ui.sh /abs/path/to/1.jpeg
```

3. Read outputs:
- `<image>.elements.json`
- `<image>.overlay.png`

4. One-step capture + parse with randomized names:
```bash
skills/ui-element-ops/scripts/capture_and_parse.sh
```

## Workflow

1. Confirm screenshot path and desired output path.
2. Run `scripts/bootstrap_omniparser_env.sh` when `.venv` or OmniParser weights are missing.
3. Run `scripts/run_parse_ui.sh` for standard parsing.
4. Report absolute output paths and summary counts: `total`, `clickable`, `by_type`.
5. Call out obvious quality risks for tiny text or dense icon layouts.
6. Execute desktop actions when requested:
   - list elements: `python3 skills/ui-element-ops/scripts/operate_ui.py list --elements <json>`
   - find elements: `python3 skills/ui-element-ops/scripts/operate_ui.py find --elements <json> --type button --text-contains login`
   - wait for appear/disappear: `python3 skills/ui-element-ops/scripts/operate_ui.py wait --elements <json> --state appear --text-contains continue`
   - click by id: `python3 skills/ui-element-ops/scripts/operate_ui.py click --elements <json> --id e_0001`
   - screenshot: `python3 skills/ui-element-ops/scripts/operate_ui.py screenshot` (defaults to user tmp dir)
   - calibrate coordinates: `python3 skills/ui-element-ops/scripts/operate_ui.py calibrate --parsed-size <w> <h> --actual-size <w> <h>`

## Tunables

- Edit type mapping keywords in `references/type_rules.example.json`.
- Use advanced parser args via `scripts/parse_ui.py --help`.
- Use `--use-paddleocr` only when `paddleocr`/`paddlepaddle` are installed.

## Outputs

- Main JSON output:
  - `schema_version`, `pipeline`, `image`, `counts`, `elements`
  - each element has `id`, `type`, `bbox_px`, `bbox_norm`, `text`, `clickable`
- Overlay PNG output:
  - same screenshot with labeled detection boxes

## Failure Handling

- Missing dependencies or weights: run bootstrap script again.
- Permission/cache errors under `$HOME`: keep temporary caches under `/tmp` (handled by run script).
- CPU-only machine: expect slower inference.
- Performance note: parse/capture-and-parse commands are heavy; avoid very tight loops and reuse recent `elements.json` when possible.
- Headless environment limitation:
  - usable without GUI: parse/list/find/wait/calibrate on existing files.
  - requires GUI session: click/click-xy/type/key/hotkey/screenshot/screen-info.
