# Transforming Content to Skill Format

Reference — how to convert any knowledge into proper skill structure.

## Source Types

### Already a Skill
- Copy to separate publish folder
- Run sanitization
- Verify structure meets standards

### Instructions in Files
- Read and understand the full process
- Extract core actionable instructions
- Remove personal context, keep universal value
- Structure into SKILL.md + auxiliaries

### Knowledge You've Developed
- Document what you know about the topic
- Focus on WHAT TO DO, not explanations
- Include the non-obvious parts
- Ask user to confirm you captured it correctly

### User's Request to Share Something
- Ask: "What specifically should this skill help others do?"
- Ask: "What do you do that others might not know?"
- Condense their workflow into reusable instructions

## Transformation Rules

### Keep
- Actionable instructions
- Non-obvious insights
- Useful patterns
- Practical examples (genericized)

### Remove
- Personal context
- Explanations of basics
- Verbose descriptions
- Meta-commentary

### Restructure
- SKILL.md: Core instructions only (30-50 lines ideal)
- Auxiliary files: Details, references, patterns
- Progressive disclosure: Load details only when needed

## Standard Structure

```
publish-folder/
├── SKILL.md          ← Core instructions
├── FILES.txt         ← List of files to publish
└── [topic].md        ← Supporting details
```

## When Unsure What to Include

**Default: Include it.** Easier for user to remove than to add later.

Mark uncertain sections:
> "I included [X] — let me know if this should be removed or modified."

## Verify Understanding

Before finalizing, confirm with user:
1. "Here's what I understood as the core value: [summary]"
2. "I'm including these sections: [list]"
3. "I'm excluding: [list with reasons]"
4. "Any changes before I prepare the publish version?"
