---
name: claw-canvas
displayName: Claw Canvas
description: A virtual canvas for OpenClaw to output content and visualize its thinking during development.
version: 0.1.0
---

# Claw Canvas Skill

## Description

This skill wraps OpenClaw's native `canvas` tool to provide a dedicated, interactive surface for the agent to visualize its internal processes, display intermediate results, and output rich content directly on a virtual canvas. It enables a more transparent and intuitive development workflow by making the agent's thinking and work-in-progress visible.

## Core Functionalities

- **Render Markdown/HTML**: Display formatted text, code, tables, and images.
- **Visualize Data**: Present charts, graphs, or structured data.
- **Show Progress**: Update the canvas with real-time progress of tasks.
- **Interactive Thinking**: Optionally display thought processes or decision trees.
- **Snapshot**: Capture the current state of the canvas.

## Usage

This is primarily an internal skill for the agent to use to illustrate its workflow. It will expose a CLI interface for displaying content.

```bash
# Example: Display markdown content
python3 scripts/canvas_cli.py display_markdown --content "# Agent Thinking\n\nHere's my current thought process..."

# Example: Display an image
python3 scripts/canvas_cli.py display_image --url "https://example.com/image.png"
```

## Purpose

To enhance transparency, improve user understanding of complex agent processes, and provide a dynamic, real-time output area for development tasks. This will be invaluable for tasks like: 
- Visualizing website structure during the Mac App conversion.
- Displaying drafted blog posts or tweets with formatting.
- Showing data analysis results.
- Illustrating program flow or architectural decisions.