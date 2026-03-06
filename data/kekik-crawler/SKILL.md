---
name: kekik-crawler
description: Scrapling-only, deterministic web crawler with clean SRP architecture, presets, checkpointing, and JSONL/report outputs.
---

# Kekik Crawler

Scrapling tabanlı, browser'sız crawler.

## Quick Start

```bash
pip install -r requirements.txt
python main.py --urls https://example.org
```

## Presets

```bash
python main.py --queries "Ömer Faruk Sancak" keyiflerolsun --preset person-research --out outputs/person.jsonl --report outputs/person-report.json
python main.py --queries "Ömer Faruk Sancak" keyiflerolsun --preset deep-research --out outputs/deep.jsonl --report outputs/deep-report.json
```

## Notes
- Output files are under `outputs/`
- Main entrypoint: `main.py`
- Orchestration: `core/crawl_runner.py`
