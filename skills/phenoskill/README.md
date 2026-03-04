# PhenoSkill

PhenoSkill is an OpenClaw skill for automated extraction of clinical phenotypes and medication entities from user-provided free text using the PhenoSnap engine.

## Features

- Detects phenotype and medication lists in free-text input
- Automatically bootstraps PhenoSnap (git clone or zip fallback)
- Auto-installs Python dependencies if missing
- Handles pip installation if pip is not present
- Produces timestamped JSON outputs
- Operates fully locally (no PHI upload)

## Requirements

- python3
- internet access (first-time bootstrap only)
- recommended: virtual environment

## Installation (via ClawHub)

```bash
clawhub install <your-slug>