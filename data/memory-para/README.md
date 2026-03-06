# Memory Management (PARA) for OpenClaw

A streamlined memory distillation skill for OpenClaw agents based on the **Root + PARA** hybrid architecture. This skill transforms raw conversation logs into structured, high-signal knowledge.

## Overview

OpenClaw generates raw daily logs (`memory/YYYY-MM-DD.md`) through its context compaction mechanism. While useful, these logs can become noisy. **Memory-Para** provides a systematic SOP for agents to "metabolize" these raw logs into a curated knowledge base, ensuring long-term recall and high-precision retrieval.

## Features

- **Root + PARA Architecture**: Splits memory into a "Hot" Root layer (Identity/Rules) and a "Warm" PARA layer (Projects/Areas/Resources).
- **Automated SOP**: Provides clear step-by-step instructions for agents to analyze, route, and merge new information.
- **High-Signal Retrieval**: Implements a tiered retrieval protocol (Hot -> Warm -> Cold -> Archive).
- **Markdown-Native**: Optimizes for LLM readability using precise naming, semantic enrichment, and structured encoding.

## Installation

1. Copy the `memory-para` folder to your OpenClaw workspace:
   ```bash
   cp -r memory-para ~/.openclaw/workspace/skills/
   ```
2. Integrate into your `HEARTBEAT.md` for automated nightly distillation.

## Usage

This skill is designed to be triggered by OpenClaw's internal maintenance tasks or manual user prompts like:
- "Perform memory maintenance"
- "Distill today's logs"

When active, the agent will scan the `memory/` directory, extract valuable insights (preferences, decisions, SOPs), and merge them into your Master files following the "Read-Before-Write" principle.

## File Structure

- `SKILL.md`: Core metadata and the Distillation SOP.
- `README.md`: This documentation.

---
Developed for the OpenClaw community. 🎩
