---
name: Scientific Graphical Abstract Generator
description: Generate professional graphical abstracts for scientific papers
  using multiple AI models. This skill transforms research descriptions and data
  into publication-quality, editable SVG visualizations.
---

# Scientific Graphical Abstract Generator

> **AI-Powered Scientific Visualization Tool** - Generate editable graphical abstracts for research papers

## Description

Generate professional graphical abstracts for scientific papers using multiple AI models. This skill transforms research descriptions and data into publication-quality, editable SVG visualizations.

## Features

- **Multiple AI Models**: Support for Claude, GPT-4o, DeepSeek, and other multimodal models
- **Editable SVG Output**: Generate vector graphics that can be edited in Inkscape, Illustrator, or any SVG editor
- **Multiple Chart Types**: Bar charts, line charts, pie charts, scatter plots, flowcharts, diagrams
- **Data-Driven Visuals**: Automatically create charts from CSV/JSON data
- **Customizable Styles**: Adjust colors, fonts, layouts to match journal requirements
- **Publication Ready**: High-quality output suitable for scientific journals

## Usage

```
/graphical-abstract Generate a graphical abstract showing the research workflow for a CRISPR gene editing study
/graphical-abstract Create a bar chart comparing the performance of three different machine learning models from this data: [data]
/graphical-abstract Design a flowchart illustrating the mechanism of action of the proposed drug
/graphical-abstract Generate a line chart showing temperature changes over time from the following CSV data
```

## Examples

### Generate Research Workflow Diagram

```
/graphical-abstract Create a graphical abstract showing the workflow: Sample preparation → RNA extraction → Sequencing → Data analysis → Results visualization. Use a clean, professional style with blue color scheme.
```

### Create Data Visualization

```
/graphical-abstract Generate a bar chart with the following data:
Model A: 85% accuracy
Model B: 92% accuracy
Model C: 78% accuracy

Title: Model Performance Comparison
Y-axis: Accuracy (%)
Color scheme: Professional blue gradient
```

### Generate Mechanism Diagram

```
/graphical-abstract Design a schematic diagram showing how the proposed inhibitor binds to the active site of the enzyme, blocking substrate access. Include labels for key components.
```

## Command Reference

### generate

Generate a graphical abstract.

| Option | Description |
|--------|-------------|
| `--prompt` | Description of what to visualize |
| `--data` | Data file (CSV/JSON) for charts |
| `--type` | Chart type: bar, line, pie, scatter, flowchart, diagram |
| `--model` | AI model: claude, gpt4o, deepseek (default: claude) |
| `--style` | Style: minimal, professional, colorful, journal |
| `--output` | Output SVG file path |
| `--width` | Canvas width (default: 800) |
| `--height` | Canvas height (default: 600) |

### template

Use predefined templates for common visualizations.

| Option | Description |
|--------|-------------|
| `--type` | Template type: workflow, mechanism, comparison, timeline |
| `--prompt` | Specific requirements |

## Supported Models

### Claude (Recommended)
- Best for: Complex diagrams, scientific illustrations
- Vision capabilities: Excellent
- API: Anthropic Claude API

### GPT-4o
- Best for: Charts, data visualization
- Vision capabilities: Very good
- API: OpenAI API

### DeepSeek
- Best for: Technical diagrams, cost-effective
- Vision capabilities: Good
- API: DeepSeek API

## Output Format

All outputs are in **SVG format** which offers:
- **Editable**: Open in Inkscape, Adobe Illustrator, or any text editor
- **Scalable**: Infinite resolution without quality loss
- **Web-ready**: Can be embedded directly in websites
- **Publication quality**: Meets most journal requirements

Example SVG structure:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <!-- Editable elements with clear structure -->
  <g id="chart-area">...</g>
  <g id="labels">...</g>
  <g id="legend">...</g>
</svg>
```

## Notes

- For complex visualizations, provide detailed descriptions
- Data files should be in CSV or JSON format
- SVG files can be edited after generation
- Different models may produce different styles
- Journal-specific requirements can be specified in the prompt

## Related Skills

- [sci-data-extractor](../sci-data-extractor/) - Extract data from scientific papers
- [semanticscholar-search-skill](../semanticscholar-search-skill/) - Search academic papers
- [pubmed-search-skill](../pubmed-search-skill/) - Search biomedical literature
