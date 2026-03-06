---
name: claw-todolist
description: A structured, conversational task management system based on GTD and Eisenhower (V3.2 Protocol). This skill strictly confines persistence to its own skill directory and supports aliases (a, x, ls, e) and structured formatting (Priority Groups, Weight ⭐, DUE dates). Includes 'REVIEW' command for weekly structural analysis.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": [] },
        "install": []
      }
  }
---

# claw-todolist Skill

This skill implements the **Todo List Management Protocol V3.2**, enabling structured task management via conversational commands.

## Core Protocol (Commands)
This skill understands aliases: **a** (ADD), **x** (DONE), **ls** (SHOW), **e** (EDIT).
It also understands the **REVIEW** command for automated structural analysis.

## Features & Output Style
- **Structure:** Tasks are persisted locally using defined rules (V3.2).
- **Visuals:** Full list output (`ls`) defaults to **Text Format** with **Priority Group Headers** and **Weight ⭐** placed after the task text.
- **Review:** Command `REVIEW` triggers an automated analysis based on predefined thresholds (P1 Ratio, Overdue, Aging, Strategic Neglect).

## Persistence
All state, rules, and display configs are bundled within the skill folder for deterministic installation.
