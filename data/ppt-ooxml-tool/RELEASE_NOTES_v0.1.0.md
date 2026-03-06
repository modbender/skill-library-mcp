# v0.1.0

First public release of `ppt-ooxml-tool`.

## Highlights
- End-to-end PPT OOXML localization pipeline.
- Tool-agnostic integration surface (`--json`, `workflow`, `runfile`).
- Bilingual help output (Chinese + English).
- Language-aware font standardization presets.

## Included Commands
- `help`
- `unpack`
- `collect`
- `apply`
- `normalize`
- `validate`
- `repack`
- `workflow`
- `runfile`

## Integration Modes
- Structured output: add `--json`.
- One-shot automation: `workflow`.
- External-agent job contract: `runfile --job job.json`.

## Language Font Presets
- `en -> Calibri`
- `ja -> Yu Gothic`
- `zh-cn -> Microsoft YaHei`
- `zh-tw -> Microsoft JhengHei`
- `ko -> Malgun Gothic`
- `ar -> Tahoma`

## Example
```bash
ppt-ooxml-tool --json workflow \
  --input ./input.pptx \
  --root ./unpacked \
  --include slides,notes,masters \
  --lang ja \
  --glossary ./examples/glossary.example.json \
  --output ./output.ja.pptx
```

## Notes
- This tool does not embed any LLM.
- Translation quality depends on the caller's model/prompt pipeline.
