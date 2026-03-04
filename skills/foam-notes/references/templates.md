# Templates in Foam

Source: https://foamnotes.com/user/features/templates

Foam supports note templates which let you customize the starting content of your notes instead of always starting from an empty note.

## Quickstart

### Getting Starter Templates

The foam-notes skill includes official Foam starter templates:

```bash
python3 scripts/init_templates.py
```

This copies these templates to your workspace's `.foam/templates/`:

- **new-note.md** — Default template for new notes
- **daily-note.md** — Daily notes template (saves to journal/)
- **your-first-template.md** — Example demonstrating VS Code snippet syntax

See `init_templates.py --list` for details on each template.

### Creating Templates Manually

For simple templates:
- Run the "Foam: Create New Template" command from the command palette
- OR manually create a regular .md file in the `.foam/templates` directory

For smart templates:
- Create a .js file in the `.foam/templates` directory (see JavaScript Templates section)

### Using Templates

To create a note from a template:
- Run the "Foam: Create New Note From Template" command and follow the instructions. Don't worry if you've not created a template yet! You'll be prompted to create a new simple template if none exist.
- OR run the "Foam: Create New Note" command, which uses the special default template (`.foam/templates/new-note.md` or `.foam/templates/new-note.js`, if it exists)

## Special templates

### Default template

The default template is used by the "Foam: Create New Note" command. Foam will look for these templates in order:

- `.foam/templates/new-note.js` (JavaScript template)
- `.foam/templates/new-note.md` (Markdown template)

Customize this template to contain content that you want included every time you create a note.

### Default daily note template

The daily note template is used when creating daily notes (e.g. by using "Foam: Open Daily Note"). Foam will look for these templates in order:

- `.foam/templates/daily-note.js` (JavaScript template)
- `.foam/templates/daily-note.md` (Markdown template)

For a simple markdown template, it is recommended to define the YAML Front-Matter similar to the following:

```yaml
---
type: daily-note
---
```

## Markdown Templates

### Variables

Markdown templates can use all VS Code Snippet variables plus Foam-specific ones:

| Variable | Description |
|----------|-------------|
| `FOAM_SELECTED_TEXT` | Text selected when creating note (replaced with wikilink) |
| `FOAM_TITLE` | Note title (prompts if used) |
| `FOAM_TITLE_SAFE` | File-safe title |
| `FOAM_SLUG` | Sluggified title |
| `FOAM_CURRENT_DIR` | Current editor's directory |

### FOAM_DATE_* Variables

Prefer these over VS Code's datetime variables:

| Variable | Description |
|----------|-------------|
| `FOAM_DATE_YEAR` | 4-digit year (e.g., 2025) |
| `FOAM_DATE_MONTH` | 2-digit month (e.g., 09) |
| `FOAM_DATE_WEEK` | ISO 8601 week number |
| `FOAM_DATE_WEEK_YEAR` | Year of ISO week |
| `FOAM_DATE_DAY_ISO` | ISO weekday (1=Monday, 7=Sunday) |
| `FOAM_DATE_DATE` | Day of month (e.g., 15) |
| `FOAM_DATE_DAY_NAME` | Full weekday name |
| `FOAM_DATE_DAY_NAME_SHORT` | Short weekday name |
| `FOAM_DATE_HOUR`, `MINUTE`, `SECOND` | Time components |
| `FOAM_DATE_SECONDS_UNIX` | Unix timestamp |

### Template Metadata

Add metadata in YAML frontmatter:

```markdown
---
foam_template:
  name: My Note Template
  description: This is my note template
  filepath: 'journal/$FOAM_TITLE.md'
---
```

**filepath patterns:**
- `$FOAM_CURRENT_DIR/$FOAM_SLUG.md` - Current directory
- `/$FOAM_SLUG.md` - Workspace root
- `$FOAM_CURRENT_DIR/meetings/$FOAM_SLUG.md` - Subdirectory

## JavaScript Templates

JavaScript templates create smart, context-aware notes.

### When to Use

- Create different structures based on date/time
- Adapt based on creation context
- Automatically find and link related notes
- Generate content based on workspace structure
- Implement complex logic

### Basic Structure

```javascript
async function createNote({ trigger, foam, resolver, foamDate }) {
  const today = dayjs();
  const formattedDay = today.format('YYYY-MM-DD');

  let content = `# Daily Note - ${formattedDay}

## Today's focus
-

## Notes
-
`;

  return {
    content,
    filepath: `/daily-notes/${formattedDay}.md`,
  };
}

module.exports = createNote;
```

### Result Format

```javascript
return {
  content: '# My Note\n\nContent here...',  // Required
  filepath: 'custom-folder/my-note.md',       // Required
};
```

### Security

- ✅ Can only run from trusted VS Code workspaces
- ✅ Can access Foam workspace and utilities
- ✅ Can use standard JavaScript features
- ✅ Have a 30-second execution timeout
- ❌ Cannot access file system directly
- ❌ Cannot make network requests
- ❌ Cannot access Node.js modules

### Example: Smart Meeting Notes

```javascript
async function createNote({ trigger, foam, resolver }) {
  const title = (await resolver.resolveFromName('FOAM_TITLE')) || 'Meeting';
  const today = dayjs();
  const isStandup = title.toLowerCase().includes('standup');
  const isReview = title.toLowerCase().includes('review');

  let template = `# ${title} - ${today.format('YYYY-MM-DD')}\n\n`;

  if (isStandup) {
    template += `## What I did yesterday\n-\n\n## What I'm doing today\n-\n\n## Blockers\n-\n`;
  } else if (isReview) {
    template += `## What went well\n-\n\n## What could be improved\n-\n\n## Action items\n- [ ]\n`;
  } else {
    template += `## Agenda\n-\n\n## Notes\n-\n\n## Action items\n- [ ]\n`;
  }

  return {
    content: template,
    filepath: `/meetings/${title}.md`,
  };
}
```

## Related

- daily-notes.md - Daily note templates
