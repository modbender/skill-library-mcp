# Article Illustrator

Analyze articles, identify optimal illustration positions, and generate images using a Type x Style two-dimension consistency system. Supports infographics, scenes, flowcharts, comparisons, frameworks, and timelines across 20+ visual styles.

## What's Inside

- Two-dimension system: Type (information structure) x Style (visual aesthetics)
- Type selection guide (infographic, scene, flowchart, comparison, framework, timeline)
- Style selection guide (notion, elegant, warm, minimal, blueprint, watercolor, editorial, scientific, and more)
- Auto-selection by content signals
- Full workflow: pre-check, analyze, confirm settings, generate outline, generate images, finalize
- Prompt construction principles for effective illustrations
- Type x Style compatibility matrix
- Extension support via EXTEND.md for custom configurations
- 21 individual style specification files

## When to Use

- Adding illustrations to an article or blog post
- Generating visual aids for written content
- Triggered by: "illustrate article", "add images to article", "generate illustrations", "article images", or requests to visually enhance written content

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/writing/article-illustrator
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install article-illustrator
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/writing/article-illustrator .cursor/skills/article-illustrator
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/writing/article-illustrator ~/.cursor/skills/article-illustrator
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/writing/article-illustrator .claude/skills/article-illustrator
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/writing/article-illustrator ~/.claude/skills/article-illustrator
```

## Related Skills

- **clear-writing** — Write the article content before illustrating
- **mermaid-diagrams** — For technical diagrams that complement illustrations

---

Part of the [Writing](..) skill category.
