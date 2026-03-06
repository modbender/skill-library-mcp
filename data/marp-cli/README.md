# Marp CLI Skill

Convert Markdown to presentations via Marp CLI.

## Overview

[Marp CLI](https://github.com/marp-team/marp-cli) is a command-line interface that converts Markdown files into presentation formats. It supports HTML, PDF, PowerPoint (PPTX), PNG, and JPEG output.

**Key features:**
- Convert Markdown to multiple presentation formats
- Watch mode for live preview during editing
- Server mode for on-demand conversion
- Support for presenter notes
- Custom themes and styling
- Parallel conversion for multiple files

## Quick Example

```bash
marp presentation.md                    # HTML (default)
marp --pdf presentation.md              # PDF
marp --pptx presentation.md             # PowerPoint
marp --images png presentation.md       # PNG images

# Watch and preview
marp -w -p presentation.md

# Serve directory
marp -s ./presentations
```

## Documentation

| Document | Description |
|----------|-------------|
| [SKILL.md](SKILL.md) | Core CLI commands and options |
| [QUICKSTART.md](QUICKSTART.md) | Quick start guide |
| [EXAMPLES.md](EXAMPLES.md) | Detailed examples |

## Output Formats

### HTML
Native HTML/CSS slide deck with built-in navigation and features.

### PDF
High-quality PDF export (requires Chrome, Edge, or Firefox).

### PowerPoint (PPTX)
Standard PowerPoint format compatible with most presentation software.

### Images (PNG/JPEG)
Individual slide images, useful for social media, documentation, and thumbnails.

## Key Commands

| Command | Description |
|---------|-------------|
| `marp file.md` | Convert to HTML |
| `marp --pdf file.md` | Convert to PDF |
| `marp --pptx file.md` | Convert to PPTX |
| `marp --images png file.md` | Convert to PNG images |
| `marp -w file.md` | Watch mode (auto-convert) |
| `marp -p file.md` | Preview window |
| `marp -s ./dir` | Server mode |

## Usage Patterns

### Development
```bash
marp -w -p deck.md  # Watch with preview
```

### Export
```bash
marp --pdf deck.md
marp --pptx deck.md
marp --images png deck.md
```

### Serving
```bash
marp -s ./presentations
# Access: http://localhost:8080/
```

### Batch
```bash
marp --pdf *.md
marp -P 10 *.md  # Parallel processing
```

## Browser Requirement

**Important:** Conversions to PDF, PPTX, and images require a compatible browser:
- Google Chrome
- Microsoft Edge
- Mozilla Firefox

The browser is used for rendering and conversion. Marp CLI supports browser selection and configuration.

```bash
# Choose browser
marp --browser firefox deck.md -o deck.pdf

# Specify browser path
marp --browser-path /path/to/chrome deck.md
```

## Markdown Syntax

Marp uses standard Markdown with special frontmatter for configuration:

```markdown
---
marp: true
theme: gaia
paginate: true
---

# Presentation Title

## First Section

- Bullet point
- Another point

### Subsection

Content.
```

Built-in themes: `default`, `gaia`, `uncover`, `invert`

## Workflows

### Development Workflow
1. Write Markdown in your editor
2. Run `marp -w -p deck.md`
3. Browser preview auto-refreshes on save
4. Export when ready

### Batch Conversion
```bash
# Convert entire project
marp --pdf presentations/*.md
```

### Distribution
```bash
# Generate all formats
marp --pdf deck.md
marp --pptx deck.md
marp --images png deck.md
```

## Features

### Watch Mode
Automatically converts when files change.

### Server Mode
HTTP server with on-demand conversion. Access different formats via query strings:
- `?pdf` - PDF
- `?pptx` - PowerPoint
- `?images=png` - PNG images
- `?image=jpeg` - Single JPEG

### Preview Window
Immersive preview window with presentation controls.

### Presenter Notes
Export or embed presenter notes in slides.

### Parallel Processing
Convert multiple files concurrently for faster batch operations.

### Custom Theming
Use built-in themes or create custom CSS.

## Installation

This skill assumes `marp` is installed. Installation methods include:

- **npm**: `npm install -g @marp-team/marp-cli`
- **Homebrew** (macOS/Linux): `brew install marp-cli`
- **Scoop** (Windows): `scoop install marp`
- **Standalone binaries**: Download from GitHub releases

See https://github.com/marp-team/marp-cli for installation details.

## Limitations

- Browser-dependent conversions require compatible browser installed
- Editable PPTX is experimental and has limitations
- Complex themes may not render perfectly in all formats
- Large presentations may require increased timeout settings
- Local file access blocked by default (use `--allow-local-files` with caution)

## Common Use Cases

### 1. Conference Presentations
Create slides in Markdown, export to PDF for sharing or PPTX for editing.

### 2. Technical Documentation
Generate slide decks from documentation files for talks and workshops.

### 3. Classroom Teaching
Create educational materials with watch mode for real-time updates.

### 4. Social Media Content
Generate high-res images from slide content for sharing.

### 5. Corporate Reports
Convert report Markdown to professional PDF or PowerPoint.

### 6. Automated Documentation
Integrate with CI/CD to auto-generate presentations from documentation.

## Advanced Features

### Configuration Files
Use `.marprc` or `marp.config.js` for project-level settings.

### CSS Customization
Apply custom styles directly in Markdown frontmatter.

### External Theme Support
Use Marp themes from npm packages or custom CSS files.

### Plugin System
Extend functionality with Marp plugins.

### CLI Integrations
Works well with other text processing tools (Pandoc, etc.)

## Tips

1. **Start with watch mode**: `marp -w -p` during development
2. **Use server mode** for collaborative work and testing
3. **Choose appropriate format**: PDF for sharing, PPTX for editing, HTML for web
4. **Leverage parallelism** for batch conversions
5. **Optimize images** with `--image-scale` for quality/size balance
6. **Customize themes** to match brand/style guidelines

## Community & Resources

- **GitHub**: https://github.com/marp-team/marp-cli
- **Website**: https://marp.app/
- **Documentation**: https://github.com/marp-team/marp-cli#readme
- **Marpit Framework**: https://marpit.marp.app/
- **Marp Core**: https://github.com/marp-team/marp-core

## Integration Examples

### With Static Site Generators
Generate presentation assets for Jekyll, Hugo, Next.js sites.

### With Documentation Tools
Convert technical docs to presentations for conferences.

### With Automation
Run in CI/CD pipelines to auto-generate slides from markdown.

### With Note-taking
Convert Obsidian, Notion, or other markdown exports to presentations.

## License

Marp CLI is licensed under the MIT License.

---

**For usage:** Start with [SKILL.md](SKILL.md)
**For learning:** Check [QUICKSTART.md](QUICKSTART.md)
**For specifics:** See [EXAMPLES.md](EXAMPLES.md)
