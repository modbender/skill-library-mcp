# Daily Notes in Foam

Source: https://foamnotes.com/user/features/daily-notes

Daily notes allow you to quickly create and access a note file for each day.

## Creating Daily Notes

- **Command**: Ctrl+Shift+P → "Foam: Open Daily Note"
- **Shortcut**: Alt+D
- **Snippets**: Type /today, /yesterday, /tomorrow in any note

## Automatic Daily Notes

Open daily note automatically on VS Code startup:

```json
{
  "foam.openDailyNote.onStartup": true
}
```

## Daily Note Templates

Create `.foam/templates/daily-note.md` to customize the structure:

```markdown
---
type: daily-note
---

# Daily Note - $FOAM_DATE_YEAR-$FOAM_DATE_MONTH-$FOAM_DATE_DATE

## Tasks

- [ ]

## Notes

```

## Date Snippets

Create links to recent daily notes using snippets:

| Snippet    | Date           |
|------------|----------------|
| /today     | today          |
| /tomorrow  | tomorrow       |
| /yesterday | yesterday      |
| /monday    | next Monday    |
| /+1d       | tomorrow       |
| /-3d       | 3 days ago     |
| /+1w       | in a week      |
| /-1m       | one month ago  |
| /+1y       | in one year    |

## Configuration

By default, daily notes are created as `yyyy-mm-dd.md` in the workspace's journals folder.

To customize your daily note location and format, create a `.foam/templates/daily-note.md` template. See templates.md for more information.

**Note**: Some settings for customizing daily notes behavior are deprecated and will be removed. Use the daily-note.md template instead.

## Related

- templates.md - Customizing note templates
