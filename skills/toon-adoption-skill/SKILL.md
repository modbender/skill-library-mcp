---
name: toon-adoption
description: Optimize token usage by adopting the compact TOON format for data storage and context.
version: 1.0.0
author: Agent Zero Community
tags: [token-optimization, toon, format, efficiency]
---

# TOON Adoption Skill

## Description
Efficiently parse, generate, and store data using Token-Oriented Object Notation (TOON). TOON is designed for LLMs as a lossless, drop-in representation of JSON data that reduces token usage by approximately 40% through indentation, minimal quoting, and tabular layouts.

## TOON Syntax Rules

### 1. Indentation-based Nesting
- Use 2-space indentation to define hierarchy, similar to YAML.
- Avoid curly braces `{}` and square brackets `[]` for nesting unless defining a tabular schema.

### 2. Minimal Quoting
- Keys and values do not require quotes unless they contain commas or significant leading/trailing whitespace.

### 3. Explicit Array Lengths
- Declare the number of items in an array using the `[N]` notation (e.g., `friends[3]`).

### 4. Tabular Arrays (Arrays of Objects)
- For uniform arrays of objects, use the format: `key[N]{field1,field2,...}:`.
- List the field names once in the header, followed by rows of values separated by commas.

### 5. Encoding
- Always use UTF-8.

## Guidelines for Agent Use
1. **Storage**: Prioritize `.toon` files for logs, schedules, and long-term data tracking.
2. **Context Compression**: When summarizing history or notes, use TOON to fit more information into the context window.
3. **Parsing**: Interpret indentation as nested object levels and CSV rows as objects matching the header schema.

## Example Document
```toon
metadata:
  name: Sample Configuration
  format: TOON
  efficiency_gain: 0.4
goals[3]{id,title,category}:
  1,Lose weight,health
  2,Increase self-esteem,personal
  3,Get out of loneliness,social
```
