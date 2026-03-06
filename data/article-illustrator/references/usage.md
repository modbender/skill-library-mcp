# Usage

## Command Syntax

```bash
# Auto-select type and style based on content
illustrate path/to/article.md

# Specify type
illustrate path/to/article.md --type infographic

# Specify style
illustrate path/to/article.md --style blueprint

# Combine type and style
illustrate path/to/article.md --type flowchart --style notion

# Specify density
illustrate path/to/article.md --density rich

# Direct content input (paste mode)
illustrate
[paste content]
```

## Options

| Option | Description |
|--------|-------------|
| `--type <name>` | Illustration type (see Type Gallery in SKILL.md) |
| `--style <name>` | Visual style (see references/styles.md) |
| `--density <level>` | Image count: minimal / balanced / rich |

## Input Modes

| Mode | Trigger | Output Directory |
|------|---------|------------------|
| File path | `path/to/article.md` | Use `default_output_dir` preference, or ask if not set |
| Paste content | No path argument | `illustrations/{topic-slug}/` |

## Output Directory Options

| Value | Path |
|-------|------|
| `same-dir` | `{article-dir}/` |
| `illustrations-subdir` | `{article-dir}/illustrations/` |
| `independent` | `illustrations/{topic-slug}/` |

Configure in EXTEND.md: `default_output_dir: illustrations-subdir`

## Examples

**Technical article with data**:
```bash
illustrate api-design.md --type infographic --style blueprint
```

**Personal story**:
```bash
illustrate journey.md --type scene --style warm
```

**Tutorial with steps**:
```bash
illustrate how-to-deploy.md --type flowchart --density rich
```
