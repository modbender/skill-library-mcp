# Agent-First Design

**Key insight:** Skills are used by AI agents, not humans.

## Human vs Agent Usage

| Aspect | Human Skill | Agent Skill |
|--------|-------------|-------------|
| Navigation | Click, scroll | Read, parse, decide |
| Input | Interactive prompts | Command templates |
| Context | Can skim, skip | Must read linearly |
| Platform | One at a time | Must detect and adapt |
| Attention | Can be long | Limited by token budget |

## Design Implications

### 1. No Interactive Scripts

❌ **Bad for agent:**
```bash
#!/bin/bash
read -p "Enter filename: " filename
read -p "Enter option [y/n]: " option
```

✅ **Good for agent:**
```markdown
## Usage

```bash
# Template: process.sh <input> <option>
process.sh data.txt y
```
```

Agent fills template based on context, no interaction needed.

### 2. Platform Detection, Not Assumption

❌ **Bad:**
```bash
#!/bin/bash  # Linux only
```

✅ **Good:**
```markdown
## Commands

**Linux/Mac:**
```bash
protoc --cpp_out=. message.proto
```

**Windows CMD:**
```cmd
protoc --cpp_out=. message.proto
```

**PowerShell:**
```powershell
protoc --cpp_out=. (Get-ChildItem *.proto)
```
```

Agent detects platform and chooses appropriate command.

### 3. Explicit Navigation

❌ **Bad:**
```markdown
See advanced guide for details.
```

✅ **Good:**
```markdown
## Advanced Topics

- Batch processing → [BATCH.md](references/BATCH.md)
- Error handling → [ERRORS.md](references/ERRORS.md)
- Performance tuning → [PERFORMANCE.md](references/PERFORMANCE.md)
```

Agent knows exactly what to load and when.

### 4. Token-Efficient Structure

Agent reads linearly. Structure for scanability:

```markdown
## Quick Command
```bash
easy-to-copy command
```

## When to Use
- Case 1: trigger
- Case 2: trigger

## Resources
- [DETAILS.md](references/DETAILS.md)
```

Frontload what agent needs most.

### 5. Imperative Voice

❌ **Passive (verbose):**
> "The file should be opened by using the OpenFile tool before any operations can be performed."

✅ **Imperative (concise):**
> "Open the file with OpenFile tool."

Saves tokens, clearer for agent parsing.

### 6. Examples Over Explanations

❌ **Theory-heavy:**
> "PDF rotation is a complex operation that involves transforming the coordinate system..."

✅ **Example-driven:**
> ```bash
> # Rotate PDF 90 degrees
> scripts/rotate.py input.pdf 90 output.pdf
> ```

Agent learns from patterns, not descriptions.

## Testing with Agents

Before publishing:

1. **Trigger test:** Does skill activate for intended queries?
2. **Workflow test:** Can agent follow steps without clarification?
3. **Resource test:** Are references loaded at right time?
4. **Edge case test:** How does agent handle errors?

## Red Flags

Watch for these anti-patterns:

- [ ] "See documentation for details" (without link)
- [ ] "Run setup script first" (interactive)
- [ ] "For advanced users..." (vague condition)
- [ ] "It depends on your environment..." (not actionable)

Fix: Make explicit, conditional, with clear navigation.