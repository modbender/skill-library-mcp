---
name: my-tool
version: 1.0.0
description: A minimal example tool.
metadata:
  category: example
  capabilities:
    - hello
author:
  name: Your Name
---

# my-tool

A minimal example of the six-door pattern.

## When to Use This Skill

Use `hello` when you need to greet someone.

## API Reference

### hello(options)

```javascript
import { hello } from './core.mjs';
hello({ name: 'world' }); // "Hello, world!"
```
