# SKILL.md

name: Local Portfolio Auditor
slug: local-portfolio-auditor
summary: Monitors cryptocurrency addresses and stock tickers from a local file using public APIs.
description: |-
  This skill provides a privacy-focused way to audit your financial portfolio. It reads a list of cryptocurrency addresses and stock symbols from a local configuration file (e.g., `portfolio.json`) and fetches their current values using public, read-only APIs. No private keys are ever requested or stored, ensuring maximum security. The skill then presents a summary of your holdings.
author: Manus AI
version: 0.1.0
trigger:
  - "audit my portfolio"
  - "check my crypto holdings"
  - "what's my stock value"
commands:
  - name: audit
    description: Audits the user's portfolio based on the local configuration file.
    usage: "audit"
    script: python3 main.py
