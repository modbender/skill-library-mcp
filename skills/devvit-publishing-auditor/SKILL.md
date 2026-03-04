# Devvit Publishing Auditor

A specialized auditor for Reddit Devvit developers to verify app readiness before uploading to the Reddit servers. It ensures compliance with Devvit CLI v0.12.x and Reddit’s publishing standards.

## Overview
This skill acts as a pre-flight checklist runner. It performs environment checks, dependency validation, configuration audits, and compliance scans for Web View games.

## How to use
1. Drop this folder/skill into your project.
2. Ask your coding agent: "Run the Devvit Publishing Auditor."
3. Follow the Go/No-Go report instructions.

## Included Checks
- **CLI/Env:** Version checks, Auth status, and Type integrity.
- **Config:** `devvit.json` validation and permission mapping.
- **Game Compliance:** Asset size limits, scroll-trap detection, and launch screen verification.
- **Docs:** README and Privacy Policy requirements.