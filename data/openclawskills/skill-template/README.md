# Skill Template

A template for creating OpenClaw-compatible skills.

## Skill Structure

```
my-skill/
├── skill.json          # Skill manifest
├── index.ts            # Main entry point
├── schema.json         # Configuration schema
├── README.md           # Documentation
└── tests/
    └── index.test.ts   # Tests
```

## Quick Start

1. Copy this template: `cp -r skill-template my-new-skill`
2. Update `skill.json` with your skill info
3. Implement your logic in `index.ts`
4. Test your skill

## Skill Manifest (skill.json)

```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "description": "What this skill does",
  "author": "Your Name",
  "entry": "index.ts",
  "config": {
    "schema": "schema.json"
  },
  "permissions": ["fs:read", "http:request"],
  "tools": [
    {
      "name": "doSomething",
      "description": "Does something useful"
    }
  ]
}
```
