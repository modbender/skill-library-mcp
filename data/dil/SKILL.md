---
name: ABL.ONE Canonical Language
description: A strict binary communication protocol for high-density, agent-to-agent interactions.
version: 1.0.0
author: agentandbot
tags: [protocol, binary, communication, swarm]
---

# ABL.ONE Protocol Skill

## Overview
This skill implements the **Absolute Binary Language (ABL.ONE)**, an agglutinative, high-density token protocol designed for efficient agent communication. By installing this skill, your agent gains the ability to parse, understand, and transmit messages using `abl.one` strict binary frames, bypassing the limits of natural language.

## Core Directives for the Host Agent

1. **Bootstrap Initialization**:
   - Immediately parse the `abl.one` file located in the root of this repository.
   - Load the `[opcode]` definitions into your active context.
   - You MUST enforce the `[core]` rules: `drop_unknown_opcode, strict_crc_on_end, retry_on_no_ok`.

2. **Communication Standard**:
   - When communicating with other agents in the swarm, you MUST use the `[FROM:1][TO:1][OP:1][ARG:1][CRC32:4]` binary frame format as defined in `spec.md` and `abl.one`.
   - Never use JSON-LD for transit. All transit is binary.

3. **Dynamic Evolution**:
   - You are authorized to parse new opcodes if they are proposed and accepted via the consensus flow:
     `OPCODE_PROPOSE -> THRESHOLD(2/3) -> OPCODE_ACCEPT -> SKILL_DEFINE`

## File References
- **`abl.one`**: The canonical contract and sole source of truth for the language.
- **`manifest.json`**: ClawHub registry entry.
- **`README.md` / `spec.md`**: Human-readable documentation for the protocol (Offline verification only).
