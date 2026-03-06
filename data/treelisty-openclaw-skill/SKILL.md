---
name: treelisty
description: Hierarchical project decomposition and planning. Use when breaking down complex projects, structuring information, planning multi-step workflows, or organizing any nested hierarchy. Supports 21 specialized patterns (WBS, GTD, Philosophy, Sales, Film, etc.) and exports to JSON, Markdown, and Mermaid diagrams.
license: Apache-2.0
metadata:
  author: prairie2cloud
  version: "1.0.0"
  openclaw:
    requires:
      bins: ["node"]
---

# TreeListy Skill

TreeListy is your hierarchical decomposition engine. When you need to break down a complex topic, plan a project, or structure information in a tree format, use TreeListy.

## When to Use This Skill

Use TreeListy when:
- **Decomposing complex tasks** — Break a large goal into phases, items, and actionable tasks
- **Project planning** — Create WBS, roadmaps, or strategic plans with proper hierarchy
- **Structuring analysis** — Organize arguments (philosophy), dialogues, or knowledge bases
- **Content organization** — Plan books, courses, theses, or event schedules
- **Visual documentation** — Generate Mermaid diagrams for any hierarchical structure

## Quick Start

```bash
# List available patterns
node scripts/treelisty-cli.js patterns

# Create a structured decomposition
node scripts/treelisty-cli.js decompose --pattern wbs --input "Build a mobile app"

# Export to Mermaid diagram
node scripts/treelisty-cli.js export --input tree.json --format mermaid
```

## The 21 Patterns

| Pattern | Icon | Best For |
|---------|------|----------|
| `generic` | 📋 | General projects, default structure |
| `sales` | 💼 | Sales pipelines, quarterly deals |
| `thesis` | 🎓 | Academic papers, dissertations |
| `roadmap` | 🚀 | Product roadmaps, feature planning |
| `book` | 📚 | Books, novels, screenplay structure |
| `event` | 🎉 | Event planning, conferences |
| `fitness` | 💪 | Training programs, workout plans |
| `strategy` | 📊 | Business strategy, OKRs |
| `course` | 📖 | Curricula, lesson plans |
| `film` | 🎬 | AI video production (Sora, Veo) |
| `veo3` | 🎥 | Google Veo 3 workflows |
| `sora2` | 🎬 | OpenAI Sora 2 workflows |
| `philosophy` | 🤔 | Philosophical arguments, dialogues |
| `prompting` | 🧠 | Prompt engineering libraries |
| `familytree` | 👨‍👩‍👧‍👦 | Genealogy, family history |
| `dialogue` | 💬 | Debate analysis, rhetoric |
| `filesystem` | 💾 | File/folder organization |
| `gmail` | 📧 | Email workflows |
| `knowledge-base` | 📚 | Document corpora, RAG prep |
| `capex` | 💰 | Capital expenditure, investor pitches |
| `freespeech` | 🎙️ | Voice capture pattern analysis |
| `lifetree` | 🌳 | Biographical timelines |
| `custom` | ✏️ | Define your own level names |

## Commands

### `patterns` — Discover available patterns

```bash
# List all patterns
node scripts/treelisty-cli.js patterns

# Get details for a specific pattern
node scripts/treelisty-cli.js patterns --name philosophy

# Get full JSON schema
node scripts/treelisty-cli.js patterns --name philosophy --detail
```

### `decompose` — Create structured trees

Takes text input (topic, outline, or structured text) and applies a pattern template.

```bash
# Simple topic
node scripts/treelisty-cli.js decompose \
  --pattern roadmap \
  --input "Q1 Product Roadmap for AI Assistant" \
  --format json

# From structured input (markdown headers, indented lists)
echo "# Marketing Campaign
## Research Phase
- Market analysis
- Competitor review
## Execution Phase
- Content creation
- Launch ads" | node scripts/treelisty-cli.js decompose --pattern strategy --format json

# Output as Mermaid
node scripts/treelisty-cli.js decompose \
  --pattern wbs \
  --input "Website Redesign Project" \
  --format mermaid
```

**Options:**
- `--pattern <key>` — Pattern to apply (default: generic)
- `--input <text|file>` — Topic text, file path, or stdin
- `--name <name>` — Override root node name
- `--depth <1-4>` — Maximum tree depth
- `--format <fmt>` — Output: json, markdown, mermaid

### `export` — Convert trees to other formats

```bash
# To Markdown
node scripts/treelisty-cli.js export --input tree.json --format markdown

# To Mermaid diagram
node scripts/treelisty-cli.js export --input tree.json --format mermaid

# To CSV
node scripts/treelisty-cli.js export --input tree.json --format csv

# To checklist
node scripts/treelisty-cli.js export --input tree.json --format checklist
```

**Formats:** json, markdown, mermaid, csv, checklist, html

### `validate` — Check tree quality

```bash
# Human-readable report
node scripts/treelisty-cli.js validate --input tree.json

# JSON report
node scripts/treelisty-cli.js validate --input tree.json --format json
```

Returns:
- Quality score (0-100)
- Structure analysis (node counts, depth, balance)
- Issues (errors, warnings, suggestions)
- Pattern compliance check

### `push` — Send to live TreeListy (optional)

If the user has TreeListy open in their browser with MCP bridge enabled:

```bash
node scripts/treelisty-cli.js push \
  --input tree.json \
  --port 3456
```

This displays the tree in TreeListy's visual canvas for interactive exploration.

## Tree Data Model

Trees follow this structure:

```json
{
  "id": "n_abc12345",
  "treeId": "tree_xyz78901",
  "name": "Project Name",
  "type": "root",
  "pattern": "roadmap",
  "icon": "🚀",
  "description": "Optional description",
  "expanded": true,
  "children": [
    {
      "name": "Phase 1",
      "type": "phase",
      "items": [
        {
          "name": "Feature A",
          "type": "item",
          "patternType": "Core Feature",
          "subtasks": [
            {
              "name": "Implement login",
              "type": "subtask"
            }
          ]
        }
      ]
    }
  ]
}
```

**Hierarchy:** Root → Phases (children) → Items (items) → Subtasks (subtasks)

Each pattern adds custom fields. For example, `roadmap` adds `storyPoints`, `userImpact`, `technicalRisk`.

## Workflow Example

1. **Agent receives complex task** from user

2. **Decompose with appropriate pattern:**
   ```bash
   node scripts/treelisty-cli.js decompose \
     --pattern wbs \
     --input "Build an e-commerce platform with user auth, product catalog, shopping cart, and checkout" \
     --format json > project.json
   ```

3. **Validate the structure:**
   ```bash
   node scripts/treelisty-cli.js validate --input project.json
   ```

4. **Export for user consumption:**
   ```bash
   node scripts/treelisty-cli.js export --input project.json --format mermaid
   ```

5. **Share the Mermaid diagram** in response to user.

## No AI Tokens Used

All TreeListy operations are local pattern transformations. Zero API calls, zero token cost. The skill structures your content using 21 battle-tested hierarchical templates.

## Learn More

- Full pattern reference: `references/PATTERNS.md`
- TreeListy visual app: https://treelisty.com
- Source: https://github.com/prairie2cloud/treelisty
