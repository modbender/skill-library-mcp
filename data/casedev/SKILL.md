---
name: casedev
description: "case.dev — a legal AI platform with encrypted document vaults, OCR, audio transcription, and legal search. This skill installs the casedev CLI and provides sub-skills for each capability. Use when the user mentions case.dev, casedev, or needs legal AI tools for document processing, transcription, or research."
tags:
  - legal
  - case.dev
  - cli
  - ocr
  - transcription
  - search
  - vaults
---

# case.dev

[case.dev](https://case.dev) is a legal AI platform. This skill bundle covers the CLI and all platform capabilities.

## Sub-skills

| Sub-skill | What it does |
|-----------|-------------|
| `setup/` | Install CLI, authenticate, diagnostics, API routes |
| `vaults/` | Encrypted document vaults — create, upload, download, semantic search |
| `ocr/` | Document OCR — PDF/image text extraction with word-level positioning |
| `transcription/` | Audio/video transcription with speaker diarization |
| `search/` | Web, legal, case law, patent, and vault search |

Start with `setup/` to install and authenticate, then use the others as needed.

## Quick start

```bash
# Install
brew install casemark/casedev/casedev

# Or via shell script
curl -fsSL https://raw.githubusercontent.com/CaseMark/homebrew-casedev/main/install.sh | sh

# Authenticate
export CASE_API_KEY=sk_case_YOUR_KEY
# or
casedev auth login
```

Then read the sub-skill for the task at hand.
