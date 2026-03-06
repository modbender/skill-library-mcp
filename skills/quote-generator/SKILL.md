---
name: Quote Generator
description: A simple skill to inject inspirational or technical quotes into
  agent responses, reports, or logs. Useful for "personality" injection and
  breaking up robotic monotony.
---

# Quote Generator

**Version:** 1.0.0
**Author:** OpenClaw Evolution (Cycle #2597)

## Description
A simple skill to inject inspirational or technical quotes into agent responses, reports, or logs. 
Useful for "personality" injection and breaking up robotic monotony.

## Usage

### Get a random quote (text)
```bash
node skills/quote-generator/index.js
```

### Get a random quote (json)
```bash
node skills/quote-generator/index.js --format json
```

### Write to file
```bash
node skills/quote-generator/index.js --output /tmp/quote.txt
```
