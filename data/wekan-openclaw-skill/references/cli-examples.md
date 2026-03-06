# WeKan CLI Reference

`wekancli` provides command-specific usage via `wekancli <action> -h` or
`wekancli <action> <type> -h`.

The environment variables `WEKAN_URL` and `WEKAN_TOKEN` are assumed to be set.

---

## Login

```bash
wekancli login          # prompts for username/password, prints token + user ID
```
*Does not require `WEKAN_TOKEN`. Use the returned token for subsequent calls.*

To get the user of the logged in session:

```bash
wekancli get user 
```

---

## List

`wekancli list <type> [args]`


| Type | Args | Example |
|------|------|---------|
| `users` | (none) | `wekancli list users` |
| `boards` | `[USER_ID]` | `wekancli list boards uId001` |
| `labels` | `BOARD_ID` | `wekancli list labels bId123` |
| `swimlanes` | `BOARD_ID` | `wekancli list swimlanes bId123` |
| `lists` | `BOARD_ID` | `wekancli list lists bId123` |
| `cards` | `BOARD_ID --list-id ID` or `--swimlane-id ID` | `wekancli list cards bId123 --list-id lId456` |
| `comments` | `CARD_ID` | `wekancli list comments cId789` |
| `checklists` | `CARD_ID` | `wekancli list checklists cId789` |

*Note: The list `users` command requires admin privileges.*

---

## Get

`wekancli get <type> <ids...>`

| Type | Args |
|------|------|
| `user` | (none) |
| `board` | `BOARD_ID` |
| `swimlane` | `BOARD_ID SWIMLANE_ID` |
| `list` | `BOARD_ID LIST_ID` |
| `card` | `CARD_ID` |
| `comment` | `CARD_ID COMMENT_ID` |
| `checklist` | `CARD_ID CHECKLIST_ID` |
| `checklist-item` | `CARD_ID CHECKLIST_ID ITEM_ID` |

```bash
wekancli get card cId789
wekancli get checklist cId789 clId012
```

---

## Create

`wekancli create <type> <required-args> [-f KEY=VALUE ...] [--json]`

Fields can be set with repeatable `-f` flags or by piping a JSON object when specifying `--json`.

| Type | Required Args | Example |
|------|---------------|---------|
| `board` | `TITLE OWNER_ID` | `wekancli create board "Sprint 1" uId001` |
| `label` | `BOARD_ID NAME COLOR` | `wekancli create label bId123 "Priority" "red"` |
| `swimlane` | `BOARD_ID TITLE` | `wekancli create swimlane bId123 "Default"` |
| `list` | `BOARD_ID TITLE` | `wekancli create list bId123 "To Do"` |
| `card` | `BOARD_ID LIST_ID TITLE AUTHOR_ID` | `wekancli create card bId123 lId456 "Fix bug" uId001` |
| `comment` | `CARD_ID AUTHOR_ID COMMENT` | `wekancli create comment cId789 uId001 "Looks good"` |
| `checklist` | `CARD_ID TITLE` | `wekancli create checklist cId789 "QA Steps"` |
| `checklist-item` | `CARD_ID CHECKLIST_ID TITLE` | `wekancli create checklist-item cId789 clId012 "Verify fix"` |

*A default swimlane is created when a board is created.*
  
Setting optional fields:

```bash
wekancli create card bId123 lId456 "Fix bug" uId001 -f description="Repro steps in issue #42" -f dueAt="2025-03-01"
```

Most fields get reasonable defaults or are updated automatically but if many values need to be set, it may be more convenient to use the `--json` flag and pipe in a json structure.

```bash
# Note Title and author are required positional arguments.
echo '{"description":"Card Description","color":"blue","assignees":["uId002"],"labelIds":["labelId201","labelId202"]}' | wekancli create card bId123 lId456 "Card Title" uId001 --json
```

---

## Edit

`wekancli edit <type> <ids...> -f KEY=VALUE [...]`

Only `card` and `checklist-item` support editing with the CLI

| Type | Required Args |
|------|---------------|
| `card` | `CARD_ID` |
| `checklist-item` | `CARD_ID CHECKLIST_ID ITEM_ID` |

```bash
wekancli edit card cId789 -f title="Updated title"
wekancli edit checklist-item cId789 clId012 iId345 -f isFinished=true
```

To move a card to a different list, edit its `listId`:

```bash
wekancli edit card cId789 -f listId="new_lId456"
```

---

## Archive

To archive a card

```bash
wekancli archive card cId789
```

To restore

```bash
wekancli archive --restore card cId789
```

---

## Delete

As a rule of thumb, archiving is preferred over deletion. Deletion is only appropriate when the data is truly no longer needed and cannot be recovered.

Specific deleting operations can be discovered by running `wekancli delete --help` or `wekancli delete <type> --help`.

---

## Schema Quick Reference

The full object schema is not documented here.  The most common fields are listed below. 
The --help options on each command shows a moderately more comprehensive listing of fields. 

### Board Fields

boardId, title, description, archived, labels [List of Label objects], color

*See `wekancli create board --help` for a listing of additional fields.*

### Label Fields

labelId, name, color

*See `wekancli create label --help` for a listing of additional fields.*

### Swimlane Fields

swimlaneId, title, archived, color

*See `wekancli create swimlane --help` for a listing of additional fields.*

### List Fields

listId, title, archived, swimlaneId

*See `wekancli create list --help` for a listing of additional fields.*

### Card Fields

cardId, title, description, listId, assignees [List of User IDs], assignedBy, dueAt, endAt, startAt, color

*A more comprehensive listing (but not exhaustive) can be found by running `wekancli create card --help`.*

### Checklist Fields

checklistId, title

*A more comprehensive listing (but not exhaustive) can be found by running `wekancli create checklist --help`.*

### Checklist Item Fields

checklistItemId, isFinished

*A more comprehensive listing (but not exhaustive) can be found by running `wekancli create checklist-item --help`.*

### Colors

 * Supported colors on cards, lists, and swimlanes: white, green, yellow, orange, red, purple, blue, sky, lime, pink, black, silver, peachpuff, crimson, plum, darkgreen, slateblue, magenta, gold, navy, gray, saddlebrown, paleturquoise, mistyrose, indigo

 * Supported colors (themes) on boards: belize, nephritis, pomegranate, pumpkin, wisteria, moderatepink, strongcyan, limegreen, midnight, dark, relax, corteza, clearblue, natural, modern, moderndark, exodark, cleandark, cleanlight

### Type Notes

Date/times use RFC 3339 UTC timestamp format (e.g., "2025-03-01T10:00:00Z")
List types accept multiple formats, including comma-separated values or [array of values].

---

## Output Format

By default, the CLI outputs JSON. 

```bash
# Example
wekancli list lists bId123
[{"listId": "listId1", "title": "Sometime"}, {"listId": "listId2", "title": "Triage"}, {"listId": "listId3", "title": "Ready"}, {"listId": "listId4", "title": "Doing"}, {"listId": "listId5", "title": "Done"}]
```

---

## Common Patterns

**Discover IDs top-down:** boards -> lists/swimlanes -> cards -> comments/checklists.

```bash
wekancli list boards                          # find BOARD_ID
wekancli list lists <BOARD_ID>                # find LIST_ID
wekancli list cards <BOARD_ID> --list-id <LIST_ID>  # find CARD_ID
wekancli get card <CARD_ID>                   # full card details
```
