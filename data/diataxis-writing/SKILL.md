---
name: diataxis-writing
description: Diataxis documentation framework practice guide. Provides diagnosis, classification, templates, and quality assessment for four documentation types (Tutorial/How-to/Reference/Explanation).
---

# Diátaxis Documentation Framework Practice

## Quick Start

When creating or refactoring documentation:

### Pre-Writing Questions (Must Ask)

**Before starting, ask the user:**

1. **Language Preference**: "What language should this document be written in?"
   - English / 中文 / Other

2. **Output Method**: "After completion, how would you like to output this document?"
   - Chat message (default)
   - Feishu document (via MCP/mcporter)
   - Local Markdown file
   - GitHub repository
   - Other platforms

### Tool Availability Check (After User Selection)

**After user selects output method, automatically check tool availability:**

```bash
# Run auto-detection (script is in ./scripts/ relative to this skill)
python3 scripts/output-handler.py --detect
```

**Check results:**
- ✅ Tool available → Proceed with selected output method
- ⚠️ Tool not available → Inform user and suggest alternatives

**For Feishu output via MCP:**
- Check if mcporter is installed
- Check if MCP feishu server is configured (typically in `/root/config/mcporter.json` or `~/.mcporter/mcporter.json`)
- Test connection to Feishu MCP server

**If tool not available:**
1. Inform user: "Selected output method [X] is not available"
2. Suggest alternatives: "Available options: [list]"
3. Ask user to confirm alternative or configure tool

### Writing Workflow

After confirming language, output preference, and tool availability:

1. **Identify User Needs** - Use the [Diataxis Compass](references/compass.md) to determine document type
2. **Select Template** - Choose the corresponding template from [templates/](templates/)
3. **Apply Checklist** - Use the corresponding [checklist](references/) during writing
4. **Quality Assessment** - Use the [quality framework](references/quality-framework.md) to evaluate the final draft
5. **Execute Output** - Output using the user's chosen method and language

## Four Documentation Types

Diataxis identifies four fundamentally different documentation types, corresponding to four user needs:

| Type | User Need | Document Purpose | Key Characteristics |
|------|-----------|------------------|---------------------|
| **Tutorial** | Acquire skills (study) | Provide learning experience | Practice-oriented, minimize explanation, concrete steps |
| **How-to Guide** | Apply skills (work) | Help complete tasks | Goal-oriented, assume competence, handle real scenarios |
| **Reference** | Apply skills (work) | Describe technical facts | Neutral description, accurate and complete, structured |
| **Explanation** | Acquire skills (study) | Provide understanding context | Discursive, allows opinions, provides context |

### Type Details

- **Tutorial**: [references/four-types.md#Tutorial](references/four-types.md)
- **How-to Guide**: [references/four-types.md#How-to Guide](references/four-types.md)
- **Reference**: [references/four-types.md#Reference](references/four-types.md)
- **Explanation**: [references/four-types.md#Explanation](references/four-types.md)

## Using the Diataxis Compass

When unsure about document type, use the compass tool: [references/compass.md](references/compass.md)

Ask two questions:
1. **Content Type**: Is it action guidance (action) or cognitive knowledge (cognition)?
2. **User State**: Is the user acquiring skills (acquisition/study) or applying skills (application/work)?

## Common Use Cases

### Use Case 1: Troubleshooting Records → How-to Guide or Explanation

Troubleshooting records typically belong to:
- **How-to Guide**: If it's step-by-step guidance on "how to solve X problem"
- **Explanation**: If it's principle analysis on "why X problem occurred"

Template: [templates/template-troubleshooting.md](templates/template-troubleshooting.md)

### Use Case 2: Experience Summary → How-to Guide or Explanation

- **Best Practices**: How-to Guide (guidance on how to do things correctly)
- **Lessons Learned**: Explanation (explaining why certain approaches are wrong)

Template: [templates/template-best-practices.md](templates/template-best-practices.md)

### Use Case 3: Learning Notes → Tutorial or Explanation

- **Learning Notes**: Tutorial (if containing practical steps)
- **Theory Summary**: Explanation (if conceptual understanding)

Template: [templates/template-learning-notes.md](templates/template-learning-notes.md)

### Use Case 4: Exploratory Sharing → Explanation

Technical exploration, experiment records, and comparative analysis typically belong to Explanation.

Template: [templates/template-exploration.md](templates/template-exploration.md)

## Checklists

Use checklists during and after writing:

- Tutorial: [checklist/checklist-tutorial.md](checklist/checklist-tutorial.md)
- How-to: [checklist/checklist-how-to.md](checklist/checklist-how-to.md)
- Reference: [checklist/checklist-reference.md](checklist/checklist-reference.md)
- Explanation: [checklist/checklist-explanation.md](checklist/checklist-explanation.md)

## Quality Assessment

Use the Functional Quality and Deep Quality framework: [references/quality-framework.md](references/quality-framework.md)

### Functional Quality
- Accuracy, completeness, consistency, usability, precision

### Deep Quality
- Flow, fitting human needs, beauty, anticipating user needs

## Common Mistakes

Avoid the following error patterns: [references/common-mistakes.md](references/common-mistakes.md)

1. **Type Conflation** - Mixing Reference content into Tutorial
2. **Misplacement** - Writing Explanation as Tutorial
3. **Boundary Blur** - Mixing too much explanation into How-to
4. **Structural Misalignment** - Reference not reflecting product architecture

## Language Style

Four types use different language styles: [references/writing-language.md](references/writing-language.md)

- **Tutorial**: "We will...", "Notice...", "Now do X..."
- **How-to**: "If you want X, do Y", "Refer to X documentation for complete options"
- **Reference**: "X inherits Y", "Subcommands: a, b, c", "Must use X"
- **Explanation**: "The reason for X is...", "W is better than Z because..."

## Output Methods

After completing the document, output using the user's chosen method:

### Available Output Methods

1. **Chat Message** - Display directly in conversation (default)
2. **Feishu Document** - Create/update Feishu document via **MCP/mcporter** (requires MCP feishu server)
3. **Local Markdown** - Save as .md file (built-in support)
4. **GitHub Repo** - Commit to code repository (requires MCP github or git)
5. **Other Platforms** - User provides platform and MCP capabilities

**Important:** For Feishu output, always use MCP/mcporter method, NOT channel tools.

### Detect Available Tools

Use [scripts/output-handler.py](scripts/output-handler.py) to auto-detect (script is in `./scripts/` relative to this skill file):

```bash
python3 scripts/output-handler.py --detect
```

### Tool Availability Check

**After user selects output method, check if tool is available:**

1. Run `output-handler.py --detect`
2. Check if selected tool is configured and available
3. If not available:
   - Inform user: "Selected output method [X] is not available"
   - Suggest alternatives from available tools list
   - Ask user to confirm alternative

### Choose Output Method

**Must ask user:** "Document completed, how would you like to output?"

Based on user selection:
- **Chat** → Reply directly
- **Feishu (MCP)** → Use mcporter to call Feishu MCP server
  ```bash
  node /path/to/mcporter/dist/cli.js call feishu doc.create '{"title":"...", "content":"..."}'
  # Note: mcporter path varies by installation, common paths:
  # - ~/.npm/_npx/*/node_modules/mcporter/dist/cli.js
  # - Or use: npx mcporter call feishu doc.create ...
  ```
- **Local** → Call `write` tool or `output-handler.py --output local`
- **GitHub** → Call `output-handler.py --output github`
- **Other** → Ask user to provide MCP server information

### Language Considerations

Output in the user's chosen language:
- If English → Output in English
- If Chinese (中文) → Output in Chinese
- If other → Confirm translation capabilities

### Output Platform Details

Complete platform list and configuration methods: [references/output-platforms.md](references/output-platforms.md)

| Platform | Required Tools | Configuration Difficulty | Use Case |
|----------|---------------|-------------------------|----------|
| Chat | None | - | Quick reply |
| Feishu (MCP) | MCP feishu server | Medium | Team collaboration |
| Local MD | write | Low | Personal knowledge |
| GitHub | MCP github/git | Medium | Tech blog |
| Notion | MCP notion | Medium | Knowledge base |
| Google Docs | MCP google | High | Google ecosystem |

## Theoretical Framework

Complete Diataxis theory:

- **Map Model**: [references/map.md](references/map.md)
- **Theoretical Foundations**: [references/four-types.md](references/four-types.md)
- **Quality Theory**: [references/quality-framework.md](references/quality-framework.md)

## Using Scripts (Optional)

Use the diagnosis script to automatically identify document types (script is in `./scripts/` relative to this skill):

```bash
python3 scripts/diagnose.py <document content or file path>
```

---

**Skill Version**: 1.0  
**Theory Source**: https://diataxis.fr  
**Author**: Zhua Zhua (Created for Master)
