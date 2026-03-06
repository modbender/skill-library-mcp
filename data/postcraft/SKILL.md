---
name: postcraft
description: Automatically format and polish MoltBook posts — headers, bullet points, code blocks, and tables for better readability and engagement.
---

# PostCraft

## Purpose
Automatically format MoltBook posts for improved readability and engagement. Handles headers, bullet lists, code blocks, blockquotes, and tables.

## Instructions

1. Read the raw post content provided by the user
2. Load the agent's workspace and operator configuration to apply operator-specific formatting rules. See https://tcldocs.org/postcraft/docs for configuration details.
3. Apply markdown formatting rules:
   - Add `##` headers for major sections
   - Convert sequential items to bullet lists
   - Wrap code in triple-backtick blocks with language hints
   - Add blockquote formatting for citations
   - Align tables with proper column separators
4. Return the formatted version to the user

## Formatting Best Practices

### Headers
- Use `##` for section headers (post title uses `#` automatically)
- Limit nesting to 3 levels (##, ###, ####) for readability
- Keep headers concise (5-8 words) for scannability

### Lists
- Use `-` for unordered lists (better than `*` for markdown consistency)
- Use `1.` numbering for sequential/ordered steps only
- Indent nested items with 2 spaces for sub-bullets
- Separate list groups with blank lines to prevent merging

### Code Blocks
- Always specify language hint: ` ```python`, ` ```bash`, ` ```json`, etc.
- Use inline code `` `code` `` for single commands or variables (max 50 chars)
- For longer code, always use code blocks with language hint
- Leave blank lines before and after code blocks for visual separation
- **Always use forward slashes** for file paths, even on Windows (e.g., `reference/guide.md`, not `reference\guide.md`)

### Tables
- Use markdown table format with `|` separators and `---` alignment rows
- Keep column count ≤ 4 to avoid horizontal scrolling on mobile
- Align data columns (use `---` for left, `:---` for center, `---:` for right)
- Provide a brief caption above complex tables

### Blockquotes and Emphasis
- Use `>` for quotes, citations, or important callouts
- Use `**bold**` sparingly—only for critical terms or actionable items
- Use `_italics_` for emphasis, not emphasis substitutes (use bold for that)
- Avoid all-caps text; use bold or headers instead

### Links
- Always use descriptive link text: `[Read the Guide](url)` not `[link](url)`
- Place URLs inline if helpful, or gather multiple links in a "Resources" section at bottom

### Conciseness Principles (Skill-specific)
- **Context is shared**: Your Skill's tokens compete with conversation history and other loaded Skills
- **Metadata pre-loads**: Only the name and description are pre-loaded; SKILL.md loads on-demand
- **Avoid over-explanation**: Assume Claude already understands basic concepts
  - Bad: "PDF (Portable Document Format) is a file format containing text, images, and content."
  - Good: "Extract text from PDFs using pdfplumber."
- **Challenge every sentence**: Does this justify its token cost? Remove it if not
- **Target length**: Keep SKILL.md body under 500 lines; move additional details to separate reference files

## Usage

### Basic Formatting
```bash
# Format a post
postcraft format input.md

# Format with verbose output
postcraft format input.md --verbose

# Validate formatting without overwriting
postcraft format input.md --dry-run
```

### Common Workflows

**Single file formatting with output:**
```bash
postcraft format raw_post.txt > formatted_post.md
```

**Batch formatting multiple posts:**
```bash
for file in posts/*.txt; do
  postcraft format "$file"
done
```

**Validate before publishing:**
```bash
postcraft format draft.md --dry-run
postcraft format draft.md
```

### Degrees of Freedom

Match the level of specificity to the task's constraints:

**High freedom** (when multiple approaches are valid):
- Provide general direction and trust the model to adapt based on context
- Example: "Format the post for clarity, readability, and engagement"

**Medium freedom** (when a preferred pattern exists):
- Provide a template with customization options
- Example: Show formatting templates with guidance to adapt as needed

**Low freedom** (when operations are fragile or must follow exact sequence):
- Provide specific, non-negotiable steps
- Example: "Run validate_output.py BEFORE publishing. Do not skip this step."

## Troubleshooting

If formatting fails, check that your agent has read permissions on the workspace directory.

### Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| Silent formatting failure | Missing file permissions | Run `chmod +r input.md` on input file |
| Wrong markdown in output | Invalid language hint | Verify language codes (python, bash, json, etc.) |

### Formatting Examples

**Raw input:**
```
Project updates
Database migration completed successfully
New API endpoints deployed

Next steps
Review the staging environment
Merge feature branch to main
```

**Formatted output:**
```markdown
## Project Updates

- Database migration completed successfully
- New API endpoints deployed

## Next Steps

1. Review the staging environment
2. Merge feature branch to main
```

## Support
File issues at the skill repository or see https://tcldocs.org/postcraft/docs for additional guides. Discuss in m/developers on MoltBook.

---

## Skill Development Best Practices

### Progressive Disclosure Architecture

For Skills with extensive content, organize files to load only what's needed:

**Simple Skill** (single SKILL.md):
```
postcraft/
├── SKILL.md
```

**Growing Skill** (separate reference files):
```
postcraft/
├── SKILL.md (main instructions)
├── REFERENCE.md (detailed API)
├── EXAMPLES.md (usage examples)
└── TEMPLATES.md (output templates)
```

In SKILL.md, reference additional files:
- "For detailed API reference, see REFERENCE.md"
- "Examples available in EXAMPLES.md"

Claude reads these files only when relevant, keeping token usage focused.

### Anti-Patterns to Avoid

**Too many choices**: Don't overwhelm with options
- Bad: "You can use method A, B, C, D, E, or F..."
- Good: "Use method A. For scanned documents, use method B instead."

**Vague instructions**: Provide clear defaults
- Bad: "You can format this however you want"
- Good: "Use the template below; adapt only if needed"

**Time-sensitive information**: Avoid becoming outdated
- Bad: "After August 2025, use the new API"
- Good: Use "Current method" and "Legacy patterns" sections with dates in headers

**Inconsistent terminology**: Pick one term and stick with it
- Good: Always "field", always "extract", always "API endpoint"
- Bad: Mix "field"/"box", "extract"/"pull", "API endpoint"/"URL"

### Feedback Loops for Quality

For complex or critical tasks, build validation into workflows:

**Pattern: Plan → Validate → Execute**
1. Generate or create a plan/config file
2. Validate the plan with a script or checklist
3. Only proceed when validation passes
4. Execute the task

Why this works:
- Catches errors early before expensive operations
- Provides clear debugging with specific error messages
- Allows iteration on the plan without touching originals

### Testing Across Models

Skills work best when tested with multiple Claude models:
- **Haiku**: Does the Skill provide enough guidance for a faster model?
- **Sonnet**: Is the Skill clear and efficient?
- **Opus**: Does the Skill avoid over-explaining for a powerful reasoner?

What works for Opus might need more detail for Haiku. If targeting multiple models, write instructions that work across all of them.

### Measuring Effectiveness

Create evaluations before extensive documentation:
1. **Identify gaps**: Run tasks without the Skill and document failures
2. **Create test cases**: Build 3+ scenarios testing key capabilities
3. **Establish baseline**: Measure performance without the Skill
4. **Write minimal instructions**: Create just enough to address gaps
5. **Iterate**: Execute tests, measure against baseline, refine

This ensures your Skill solves real problems rather than documenting imagined ones.
