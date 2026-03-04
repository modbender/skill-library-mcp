

# ppt-ooxml-tool

Tool-agnostic CLI for PPTX OOXML localization workflows.

ppt-ooxml-translator is an AI-agent Skill that standardizes and automates PPTX (OOXML) localization workflows. It provides an end-to-end pipeline from unpacking, text extraction, translation apply-back, terminology normalization, and font standardization to final repacking, with structured JSON outputs for integration across clients and orchestration systems. The Skill is model-agnostic; translation model choice is delegated to the caller.

## What It Does
- Unpack `.pptx` into OOXML files
- Extract all `a:t` text runs into TSV
- Apply translated TSV back to XML by stable IDs
- Normalize terminology and font by language preset
- Validate XML parse + font consistency
- Repack OOXML back into `.pptx`

This project is model-agnostic. It does not bundle any LLM. Any client can call this CLI and use its own model for translation.

## Install

```bash
python3 -m pip install .
```

Or editable mode for development:

```bash
python3 -m pip install -e .
```

## Quick Start

### 1) Print bilingual help

```bash
ppt-ooxml-tool help --lang both
```

### 2) End-to-end one command

```bash
ppt-ooxml-tool --json workflow \
  --input ./input.pptx \
  --root ./unpacked \
  --include slides,notes,masters \
  --lang ja \
  --glossary ./examples/glossary.example.json \
  --output ./output.ja.pptx
```

### 3) Job file mode (recommended for external agents)

```bash
ppt-ooxml-tool --json runfile --job ./examples/job.example.json
```

## Command Surface
- `help`
- `unpack`
- `collect`
- `apply`
- `normalize`
- `validate`
- `repack`
- `workflow`
- `runfile`

All commands support `--json` for machine-readable output.

## Language -> Font Preset
- `en` -> `Calibri`
- `ja` -> `Yu Gothic`
- `zh-cn` -> `Microsoft YaHei`
- `zh-tw` -> `Microsoft JhengHei`
- `ko` -> `Malgun Gothic`
- `ar` -> `Tahoma`

You can override with `--font`.

## Input / Output Expectations
- Packed input: pass `.pptx` path via `--input`
- Unpacked input: folder must contain `[Content_Types].xml` and `ppt/`
- Default TSV path pattern: `<unpacked_root>/translation.<lang>.tsv`
- Default repack path pattern: `<unpacked_root>.out.pptx` (or explicit `--output`)

## Integration Notes
- External tools only need shell command execution + JSON parsing.
- Translation generation should write the TSV `target` column without changing row count/order.
- Keep placeholders and numeric tokens intact.

## License
MIT. See `LICENSE`.
