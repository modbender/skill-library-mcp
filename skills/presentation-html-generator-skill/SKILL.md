---
name: presentation-generator
description: "Generate high-quality technical HTML presentations (Reveal.js) and Markdown technical deep-dive articles from projects or papers. Covers architecture diagrams, code walkthroughs, math formulas, and speaker notes. Use when users say: 'make a presentation', 'create slides', 'generate HTML slides', 'technical presentation', 'paper presentation', 'Reveal.js slides', 'write a technical deep-dive article', 'create tech blog from code', 'generate architecture diagrams with matplotlib'. Triggers on requests to: (1) Convert a project/paper into an HTML slide deck, (2) Write a Markdown technical analysis article, (3) Generate matplotlib architecture diagrams for documentation."
---

# Technical Presentation & Article Generator

Generate Reveal.js HTML presentations and Markdown technical deep-dive articles from complex technical projects or papers. All content in Chinese by default.

## Core Principles

- **Logic First**: Establish overall architecture before diving into details. No fragmented info dumps.
- **Visualization Driven**: Use diagrams (Mermaid, architecture charts) over plain text whenever possible.
- **Code-Theory Alignment**: Every formula/diagram must map to concrete code implementation.
- **Deep Dive via "What-Why-How-Code"**: For each core component, follow the 5-step pattern: Concept → Motivation → Mechanism → Code → Comparison.
- **User Friendly**: Leverage HTML/JS features for code highlighting, speaker notes, and interactivity.

## Workflow: HTML Presentation Generation

### Step 1: Analyze Source Material

Read the project/paper thoroughly. Collect:
- Model configs (yaml/json) for precise parameters
- Core model code for architecture details and tensor shapes
- Training code for loss design
- Inference code for inference flow
- README / paper for high-level overview

**All technical details (parameter values, shapes, formulas) must come from source code, not guesswork.**

### Step 2: Plan Content Structure

Organize slides into these modules:

1. **Cover & Context** — Title, pain points, one-line innovation summary
2. **High-Level Architecture** — System overview, data flow, module interactions
3. **Core Component Deep Dives** (~50%+ of slides) — Detailed breakdown per module
4. **Training & Inference Pipelines** (AI model/algorithm only) — See Step 4.5 below
5. **Performance & Optimization** — Experiments, speedup strategies, latency
6. **Summary & Future Work** — Contributions, open problems

### Step 3: Generate Single-File HTML

Produce a self-contained HTML file using Reveal.js via CDN. Must include:
- MathJax/KaTeX for LaTeX formulas
- highlight.js for code syntax highlighting
- Mermaid.js for diagrams (with manual rendering fix)
- Speaker notes (`<aside class="notes">`) on every slide — conversational style, explain "why" not "what"

**Reveal.js Config (mandatory):**
```javascript
Reveal.initialize({
    width: 1920,
    height: 960,     // 2:1 aspect ratio for widescreen
    margin: 0.1,
    minScale: 0.2,
    maxScale: 1.5,
    center: true,
});
```

**Centering CSS (mandatory):**
```css
.reveal .slides { text-align: center; }
.reveal .slides section {
    display: flex; flex-direction: column;
    justify-content: center; align-items: center;
    width: 100%; height: 100%;
    padding: 20px 40px; box-sizing: border-box;
}
.grid-2, .grid-3 { max-width: 1700px; width: 100%; }
.reveal .slides section > * { max-width: 100%; box-sizing: border-box; }
```

### Step 4: Apply Deep Dive Pattern for Each Core Component

For every core module, follow this 5-step structure:

1. **What**: Definition, input/output
2. **Why**: Design motivation, what problem does it solve
3. **How**: Algorithm flowchart, core formulas (MathJax), shape flow (e.g., `(B,C,T) → (B,2C,1)`)
4. **Code**: Key code snippet with line-level comments and highlighting
5. **Comparison**: Table comparing old vs new approach

### Step 4.5: Training vs Inference Split (AI Model/Algorithm Projects)

**When the project involves an AI model or algorithm, the training and inference pipelines MUST be presented as separate, clearly distinguished sections.** Do NOT merge them into a single "model overview" slide.

#### Detection Criteria
If the source material contains ANY of the following, apply this step:
- Training scripts (train.py, trainer.py, fit(), loss functions)
- Inference scripts (infer.py, predict.py, generate())
- Distinct training-only components (data augmentation, loss design, learning rate schedule, gradient accumulation)
- Distinct inference-only components (beam search, sampling strategy, post-processing, quantization, TensorRT)
- Model behavior differences between training and inference (e.g., dropout, batch norm, teacher forcing vs autoregressive)

#### Required Slide Structure

**Slide Group A: Training Pipeline (2-4 slides)**
1. **Training Architecture Overview** — Training-specific data flow diagram showing: Dataset → Preprocessing → Model (train mode) → Loss → Optimizer → Update
2. **Training Core Details** — Loss function design (formulas + code), optimizer config, LR schedule, regularization strategies
3. **Training Data Flow** — Shape transformations specific to training (include batch dimension, label handling)
4. **Training Tricks & Optimization** (optional) — Mixed precision, gradient accumulation, distributed training, curriculum learning

**Slide Group B: Inference Pipeline (2-4 slides)**
1. **Inference Architecture Overview** — Inference-specific data flow diagram showing: Input → Preprocessing → Model (eval mode) → Post-processing → Output
2. **Inference Core Details** — Decoding strategy (greedy/beam/sampling), post-processing, confidence thresholds
3. **Inference Data Flow** — Shape transformations specific to inference (note differences from training: no labels, potentially different batch handling)
4. **Inference Optimization** (optional) — Quantization, pruning, caching (KV-cache), batching strategies, latency benchmarks

**Slide Group C: Training vs Inference Comparison (1 slide)**

Must include a comparison table:

| Aspect | Training | Inference |
|--------|----------|----------|
| Mode | `model.train()` | `model.eval()` |
| Data | Labeled dataset + augmentation | Raw input only |
| Dropout/BN | Active / running stats update | Disabled / frozen stats |
| Output | Loss value | Predictions |
| Batch Size | Large (throughput) | Small/1 (latency) |
| Key Metric | Training loss, validation accuracy | Latency, throughput, quality |
| Unique Components | Loss fn, optimizer, scheduler | Decoder, post-processor, cache |

#### Visual Differentiation
- Use **distinct color schemes**: Training slides use 🔵 blue tones (`#e3f2fd`, `#1976d2`), Inference slides use 🟢 green tones (`#e8f5e9`, `#388e3c`)
- Use **labeled section headers**: "🏋️ Training Pipeline" and "🚀 Inference Pipeline"
- Mermaid/flowchart diagrams for training and inference should be **separate diagrams**, not a single combined one
- Highlight components that **only exist in one phase** (e.g., loss function is training-only; beam search is inference-only)

### Step 5: Quality Checklist

Before delivering, verify:
- [ ] Every slide fits within viewport (no overflow/truncation)
- [ ] Font sizes appropriate (code not too small)
- [ ] Every "Why" is explained, not just "What"
- [ ] Core components have code correspondence
- [ ] Shape transformations clearly annotated
- [ ] Complex formulas have intuitive explanations
- [ ] All user-raised questions are addressed
- [ ] (AI model projects) Training and inference pipelines are presented separately with distinct visual styles
- [ ] (AI model projects) Training-only and inference-only components are clearly marked
- [ ] (AI model projects) A Training vs Inference comparison table is included

## Workflow: Markdown Technical Article

Follow the article structure template in [references/article-template.md](references/article-template.md).

Key principles:
- **Table-driven**: Use tables for parameter comparisons, model comparisons, shape references
- **Code as documentation**: Every core module needs code snippet + line comments
- **Formula-code alignment**: LaTeX symbols must match code variable names
- **"Why" over "What"**: Explain design motivation for every decision

## Workflow: Matplotlib Architecture Diagrams

See [references/matplotlib-guide.md](references/matplotlib-guide.md) for the complete matplotlib diagram generation methodology.

Critical rules:
- `FancyBboxPatch` pad must be proportional: `min(w, h) * 0.15`
- Line height based on box height: `h * 0.75 / n_lines`
- Long-distance connections use polylines, not arcs
- Never use `set_aspect('equal')`
- macOS fonts: `Arial Unicode MS` > `Heiti TC` > `STHeiti`
- No emoji in matplotlib (not supported)

## Common Pitfalls Quick Reference

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Slide content overflow | Too much content per slide | Use scrollable containers or split slides |
| Content off-center | Missing Flexbox centering CSS | Apply mandatory centering CSS above |
| Mermaid not rendering on hidden slides | `startOnLoad: true` only renders visible | Set `startOnLoad: false`, manual render on `ready` + `slidechanged` |
| Vertical flowchart overflow | Too many nodes in HTML/CSS flowchart | Compress gap/padding/font-size, see [references/revealjs-fixes.md](references/revealjs-fixes.md) |
| Matplotlib boxes distorted | `pad` in data coordinates, not pixels | Use proportional pad calculation |
| Chinese not showing in matplotlib | Wrong font | Use `Arial Unicode MS` / `Heiti TC` |
| Training/Inference merged into one slide | AI model specifics lost | Split into separate slide groups with distinct color themes (blue=train, green=infer) |

## Prompt Template

For generating presentations with maximum quality, see [references/prompt-template.md](references/prompt-template.md) for a proven C.R.I.S.P principle prompt.

## Slide Template

See [assets/slide-template.html](assets/slide-template.html) for a starter HTML template with all required configs pre-set.
