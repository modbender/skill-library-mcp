# Foam Documentation Overview

Source: https://foamnotes.com

## What is Foam?

Foam is a personal knowledge management system built on Visual Studio Code and GitHub. It helps you organize research, create discoverable notes, and publish your knowledge.

## Key Features

- **Wikilinks** - Connect thoughts with [[double bracket]] syntax
- **Embeds** - Include content from other notes with ![[note]] syntax
- **Backlinks** - Automatically discover connections between notes
- **Graph visualization** - See your knowledge network visually
- **Daily notes** - Capture timestamped thoughts
- **Templates** - Standardize note creation
- **Tags** - Organize and filter content

## Why Choose Foam?

- **Free and open source** - No subscriptions or vendor lock-in
- **Own your data** - Notes stored as standard Markdown files
- **VS Code integration** - Leverage powerful editing and extensions
- **Git-based** - Version control and collaboration built-in

## Core Philosophy

Foam is like a bathtub: What you get out of it depends on what you put into it.

## What's in a Foam?

Foam combines existing tools:

- **VS Code** - Enhanced with recommended extensions optimized for knowledge management
- **GitHub** - Version control, backup, and collaboration
- **Static site generators** - Publish to GitHub Pages, Netlify, or Vercel

## Getting Started

Requirements: GitHub account and Visual Studio Code

1. **Create repository** - Use the foam-template to generate a new repository
2. **Clone and open** - Clone locally and open the folder in VS Code
3. **Install extensions** - Click "Install all" when prompted for recommended extensions
4. **Configure** - Edit .vscode/settings.json for your preferences

## Foam File Structure

```
foam-workspace/
├── .vscode/
│   ├── extensions.json    # Recommended extensions
│   └── settings.json      # VS Code settings
├── .foam/
│   └── templates/         # Note templates
├── journals/              # Daily notes (optional)
├── attachments/           # Images and files
└── *.md                   # Your notes
```

## Recommended Extensions (Core)

- **Foam for VSCode** - Core Foam functionality
- **Markdown All In One** - Enhanced markdown editing
- **Prettier** - Code formatting

## Additional Recommended Extensions

- **Emojisense** - Emoji autocomplete
- **Markdown Emoji** - :smile: syntax support
- **Mermaid diagrams Support** - Diagram rendering
- **Excalidraw** - Whiteboard integration
- **VSCode PDF Viewing** - PDF viewing
- **Project Manager** - Workspace switching
- **Markdown Extended** - Extended syntax
- **GitDoc** - Automatic git commits
- **Markdown Footnotes** - Footnote support
- **Todo Tree** - TODO scanning

## Foam vs Obsidian

Similarities:
- Same wikilink syntax [[note]]
- Same embed syntax ![[note]]
- Same markdown base

Differences:
- Foam uses VS Code instead of dedicated app
- Foam has fewer plugins but more robust core
- Foam is Git-native from the start
- Foam uses standard markdown files
- Foam's configuration is in .vscode/settings.json

## Inspiration

Foam was inspired by Roam Research and Zettelkasten methodology.

Foam builds on Visual Studio Code, GitHub, and recommended extensions.

License: MIT
