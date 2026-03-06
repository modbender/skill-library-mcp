# document

> Manage Linear documents

## Usage

```text
linear document [subcommand]
```

Alias: `linear docs` can be used instead of `linear document`.

Documents can be attached to projects or issues, or exist at the workspace level.

## Subcommands

### list

List documents.

```bash
linear document list [options]
```

| Flag | Description |
|---|---|
| `--project <projectId>` | Filter by project |
| `--issue <issueId>` | Filter by issue (e.g. TC-123) |
| `--json` | Output as JSON |

**Examples:**

```bash
# List all documents
linear document list

# Filter by project
linear document list --project <projectId>

# Filter by issue
linear document list --issue TC-123

# JSON output
linear document list --json
```

### view

View a document.

```bash
linear document view <slug> [options]
```

| Flag | Description |
|---|---|
| `--raw` | Output raw markdown (for piping) |
| `--web` | Open in browser |
| `--json` | Output as JSON |

**Examples:**

```bash
# View rendered in terminal
linear document view my-document

# Get raw markdown
linear document view my-document --raw

# Open in browser
linear document view my-document --web

# JSON output for scripting
linear document view my-document --json
```

### create

Create a document.

```bash
linear document create [options]
```

| Flag | Description |
|---|---|
| `--title <title>` | Document title |
| `--content <content>` | Inline markdown content |
| `--content-file <path>` | Read content from a file |
| `--project <projectId>` | Attach to a project |
| `--issue <issueId>` | Attach to an issue (e.g. TC-123) |

Content can also be piped via stdin.

**Examples:**

```bash
# Create with inline content
linear document create --title "My Doc" --content "# Hello\n\nWorld"

# Create from file
linear document create --title "Design Spec" --content-file ./spec.md

# Attach to a project
linear document create --title "Project Notes" --content-file ./notes.md --project <projectId>

# Attach to an issue
linear document create --title "Investigation" --content "findings here" --issue TC-123

# Pipe from stdin
cat spec.md | linear document create --title "Spec"
```

### update

Update a document.

```bash
linear document update <slug> [options]
```

| Flag | Description |
|---|---|
| `--title <title>` | New title |
| `--content-file <path>` | New content from file |
| `--edit` | Open in $EDITOR |

**Examples:**

```bash
# Update title
linear document update my-doc --title "New Title"

# Update content from file
linear document update my-doc --content-file ./updated.md

# Open in editor
linear document update my-doc --edit
```

### delete

Delete a document.

```bash
linear document delete <slug> [options]
```

| Flag | Description |
|---|---|
| `--permanent` | Permanent delete (default is soft delete / move to trash) |
| `--bulk <slugs...>` | Bulk delete multiple documents |

**Examples:**

```bash
# Soft delete (move to trash)
linear document delete my-doc

# Permanent delete
linear document delete my-doc --permanent

# Bulk delete
linear document delete --bulk doc-1 doc-2 doc-3
```
