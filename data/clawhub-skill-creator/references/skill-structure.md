# Skill Structure Patterns

## Minimal Skill

For simple, focused tasks:

```
minimal-skill/
├── SKILL.md          # Everything inline
├── _meta.json        # Registry metadata
└── LICENSE.txt       # Apache-2.0 or MIT
```

**When to use:** Single-purpose skills, <100 lines of instructions.

## Standard Skill

For most use cases:

```
standard-skill/
├── SKILL.md
├── _meta.json
├── LICENSE.txt
└── references/
    └── advanced.md   # Detailed docs
```

**When to use:** Multi-step workflows, need examples or edge cases.

## Complex Skill

For domain-heavy or multi-variant skills:

```
complex-skill/
├── SKILL.md              # Overview + navigation
├── _meta.json
├── LICENSE.txt
├── references/
│   ├── quickstart.md     # Fast path
│   ├── domain-a.md       # Variant A details
│   ├── domain-b.md       # Variant B details
│   └── examples.md       # Use cases
└── assets/
    └── template.txt      # Reusable template
```

**When to use:** Multiple domains, frameworks, or complex configurations.

## Directory Purposes

### references/

Documentation loaded on demand:
- Detailed guides
- API documentation
- Configuration schemas
- Examples and patterns

### scripts/

**Avoid if possible.** If needed:
- Must be cross-platform (Python preferred)
- No external dependencies
- Clear input/output contract
- Document in SKILL.md, not inline

### assets/

Files used in output:
- Templates
- Boilerplate code
- Configuration files
- Static resources

## File Naming

| File | Convention |
|------|------------|
| SKILL.md | Exactly this name |
| _meta.json | Exactly this name |
| references/ | snake_case.md |
| scripts/ | snake_case.py (or .sh if unavoidable) |
| assets/ | descriptive-name.ext |

## What NOT to Include

❌ **Never:**
- README.md
- CHANGELOG.md
- INSTALL.md
- .gitignore (clawhub handles this)
- Test files
- Build artifacts

**Why:** Clutter increases token usage without value.