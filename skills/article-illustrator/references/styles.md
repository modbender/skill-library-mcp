# Style Reference

## Style Gallery

| Style | Description | Best For |
|-------|-------------|----------|
| `notion` (Default) | Minimalist hand-drawn line art | Knowledge sharing, SaaS, productivity |
| `elegant` | Refined, sophisticated | Business, thought leadership |
| `warm` | Friendly, approachable | Personal growth, lifestyle, education |
| `minimal` | Ultra-clean, zen-like | Philosophy, minimalism, core concepts |
| `blueprint` | Technical schematics | Architecture, system design, engineering |
| `watercolor` | Soft artistic with natural warmth | Lifestyle, travel, creative |
| `editorial` | Magazine-style infographic | Tech explainers, journalism |
| `scientific` | Academic precise diagrams | Biology, chemistry, technical research |

Full specifications: `references/styles/<style>.md`

## Type × Style Compatibility Matrix

| | notion | warm | minimal | blueprint | watercolor | elegant | editorial | scientific |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| infographic | ✓✓ | ✓ | ✓✓ | ✓✓ | ✓ | ✓✓ | ✓✓ | ✓✓ |
| scene | ✓ | ✓✓ | ✓ | ✗ | ✓✓ | ✓ | ✓ | ✗ |
| flowchart | ✓✓ | ✓ | ✓ | ✓✓ | ✗ | ✓ | ✓✓ | ✓ |
| comparison | ✓✓ | ✓ | ✓✓ | ✓ | ✓ | ✓✓ | ✓✓ | ✓ |
| framework | ✓✓ | ✓ | ✓✓ | ✓✓ | ✗ | ✓✓ | ✓ | ✓✓ |
| timeline | ✓✓ | ✓ | ✓ | ✓ | ✓✓ | ✓✓ | ✓✓ | ✓ |

✓✓ = highly recommended | ✓ = compatible | ✗ = not recommended

## Auto Selection by Type

| Type | Primary Style | Secondary Styles |
|------|---------------|------------------|
| infographic | blueprint | notion, editorial, scientific |
| scene | warm | watercolor, elegant |
| flowchart | notion | blueprint, editorial |
| comparison | notion | elegant, editorial |
| framework | blueprint | notion, scientific |
| timeline | elegant | warm, editorial |

## Auto Selection by Content Signals

| Content Signals | Recommended Type | Recommended Style |
|-----------------|------------------|-------------------|
| API, metrics, data, comparison, numbers | infographic | blueprint, notion |
| Story, emotion, journey, experience, personal | scene | warm, watercolor |
| How-to, steps, workflow, process, tutorial | flowchart | notion, minimal |
| vs, pros/cons, before/after, alternatives | comparison | notion, elegant |
| Framework, model, architecture, principles | framework | blueprint, notion |
| History, timeline, progress, evolution | timeline | elegant, warm |
| Knowledge, concept, productivity, SaaS, tool | infographic | notion |
| Business, professional, strategy, corporate | framework | elegant |
| Biology, chemistry, medical, scientific | infographic | scientific |
| Explainer, journalism, magazine, investigation | infographic | editorial |

## Style Characteristics by Type

### infographic + blueprint
- Technical precision, schematic lines
- Grid-based layout, clear zones
- Monospace labels, data-focused
- Blue/white color scheme

### infographic + notion
- Hand-drawn feel, approachable
- Soft icons, rounded elements
- Neutral palette, clean backgrounds
- Perfect for SaaS/productivity

### scene + warm
- Golden hour lighting, cozy atmosphere
- Soft gradients, natural textures
- Inviting, personal feeling
- Great for storytelling

### scene + watercolor
- Artistic, painterly effect
- Soft edges, color bleeding
- Dreamy, creative mood
- Best for lifestyle/travel

### flowchart + notion
- Clear step indicators
- Simple arrow connections
- Minimal decoration
- Focus on process clarity

### flowchart + blueprint
- Technical precision
- Detailed connection points
- Engineering aesthetic
- For complex systems

### comparison + elegant
- Refined dividers
- Balanced typography
- Professional appearance
- Business comparisons

### framework + blueprint
- Precise node connections
- Hierarchical clarity
- System architecture feel
- Technical frameworks

### timeline + elegant
- Sophisticated markers
- Refined typography
- Historical gravitas
- Professional presentations

### timeline + warm
- Friendly progression
- Organic flow
- Personal journey feel
- Growth narratives
