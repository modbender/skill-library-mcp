# Detect File Type - Local

[![CI](https://github.com/pgeraghty/openclaw-detect-file-type-local/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/pgeraghty/openclaw-detect-file-type-local/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/github/license/pgeraghty/openclaw-detect-file-type-local)](LICENSE)
![PyPI](https://img.shields.io/pypi/v/detect-file-type-local)
![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)
![Inference: Local/Offline](https://img.shields.io/badge/inference-local%20%7C%20offline-success)
![API Keys](https://img.shields.io/badge/api_keys-none-success)

An [OpenClaw](https://openclaw.org) skill for AI-powered local file type detection.

Wraps [Google Magika](https://github.com/google/magika) to provide ML-based file type identification that runs entirely offline. No API keys, no network calls — just local inference on an embedded ONNX model.

## Features

- **214 file types** detected by content, not extension
- **Fully offline** — no network access required
- **Fast** — only reads the bytes needed for classification
- **Batch support** — process multiple files or entire directories
- **Multiple output formats** — JSON, human-readable, bare MIME type
- **Security-focused triage** — detect extension/content mismatch and suspicious polyglot content
- **Stdin support** — default mode spools and classifies like file-path mode

## Security Use Cases

- Catch extension masquerading (`invoice.pdf.exe`, `report.xlsx.lnk`) before execution or ingestion.
- Detect content/extension mismatch in upload and download pipelines.
- Flag suspicious polyglot payloads where one file can be parsed as multiple formats (for example PDF/ZIP or PDF/HTA-style delivery chains).
- Keep all analysis local for sensitive data workflows.

Related references:
- [MITRE ATT&CK: Masquerading](https://attack.mitre.org/techniques/T1036/)
- [Proofpoint: Call It What You Want, Threat Actor Delivers Highly Targeted Multistage Polyglot](https://www.proofpoint.com/us/blog/threat-insight/call-it-what-you-want-threat-actor-delivers-highly-targeted-multistage-polyglot)

## Quick Start

```bash
pip install detect-file-type-local

# Detect a single file
detect_file_type document.pdf

# Batch detect
detect_file_type --human *.pdf *.png

# Recursive directory scan
detect_file_type -r ./uploads/

# Pipe from stdin
cat mystery_file | detect_file_type -

# Stdin fast path (best effort): read only first 1 MB
cat mystery_file | detect_file_type --stdin-mode head --stdin-max-bytes 1048576 -
```

## Output Formats

**JSON (default):**
```json
{
  "path": "photo.jpg",
  "label": "jpeg",
  "mime_type": "image/jpeg",
  "score": 0.99,
  "group": "image",
  "description": "JPEG image",
  "is_text": false
}
```

**Human-readable:**
```
photo.jpg: JPEG image (image/jpeg) [score: 0.99]
```

**MIME-only:**
```
image/jpeg
```

## OpenClaw Skill

See [SKILL.md](SKILL.md) for the OpenClaw skill definition, including structured output schemas and usage guidance for LLM integration.

OpenClaw skill metadata now auto-installs from PyPI package `detect-file-type-local`.

Stdin note: default `--stdin-mode spool` writes stdin to a temporary file and uses Magika path-based detection so begin/end file features are handled consistently with normal file input. `--stdin-mode head` is available as an explicit speed tradeoff.

## Development

```bash
pip install -e '.[dev]'
pytest tests/ -v
ruff check .
```

## Release

PyPI publishing is automated via GitHub Actions (`Publish Python Package` workflow):

1. Create a GitHub release with a tag matching package version (for example, `v0.2.0`)
2. Workflow builds and validates artifacts
3. Workflow publishes to PyPI via trusted publishing

After PyPI release, update and republish the ClawHub skill metadata to enable auto-install from `detect-file-type-local`.

## License

MIT — see [LICENSE](LICENSE).

This project uses [Google Magika](https://github.com/google/magika) (Apache-2.0). See [NOTICE](NOTICE) and [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
