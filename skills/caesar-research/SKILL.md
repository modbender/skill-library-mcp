---
name: caesar-research
description: Deep research using the Caesar API — run queries, follow up with chat, brainstorm, and manage collections.
homepage: https://www.caesar.org/
metadata: { "openclaw": { "emoji": "🔬", "requires": { "bins": ["caesar"], "env": ["CAESAR_API_KEY"] } } }
---

# Caesar Research

CLI for [Caesar](https://www.caesar.org/) deep research. Runs multi-source research jobs with citations, follow-up chat, and brainstorming.

## Setup

```bash
go install github.com/alexrudloff/caesar-cli@latest
export CAESAR_API_KEY=your_key_here
```

## Research

Run a query (waits for completion by default, prints events as they happen):

```bash
caesar research create "What are the latest advances in mRNA vaccines?"
```

Returns JSON with `content` (synthesized answer with `[n]` citations) and a `results` array of sources.

Fire-and-forget:

```bash
caesar research create "query" --no-wait
# Returns: { "id": "uuid", "status": "queued" }
```

Then check on it:

```bash
caesar research get <job-id>
caesar research watch <job-id>
caesar research events <job-id>
```

### Research Options

| Flag | Description |
|------|-------------|
| `--no-wait` | Return immediately with job ID |
| `--model <name>` | `gpt-5.2`, `gemini-3-pro`, `gemini-3-flash`, `claude-opus-4.5` |
| `--loops N` | Max reasoning loops (default 1, higher = deeper research) |
| `--reasoning` | Enable advanced reasoning mode |
| `--auto` | Let Caesar auto-configure based on query |
| `--exclude-social` | Skip social media sources |
| `--exclude-domain x.com` | Exclude specific domains (repeatable) |
| `--system-prompt "..."` | Custom synthesis prompt |
| `--brainstorm <id>` | Use a brainstorm session for context |

### Status Lifecycle

`queued` → `searching` → `summarizing` → `analyzing` → `researching` → `completed` or `failed`

## Chat (Follow-Up Questions)

Ask follow-up questions about a completed research job:

```bash
caesar chat send <job-id> "How does this compare to traditional vaccines?"
```

Waits for the response by default. The answer includes inline `[n]` citations referencing the original research sources.

```bash
caesar chat send <job-id> "question" --wait=false
caesar chat history <job-id>
```

## Brainstorm

Get clarifying questions before research to improve results:

```bash
caesar brainstorm "How does CRISPR gene editing work?"
# Prints questions with multiple-choice options and a session ID
```

Then use the session ID:

```bash
caesar research create --brainstorm <session-id> "How does CRISPR gene editing work?"
```

## Collections

Group files for research context:

```bash
caesar collections create "Dataset Name" --description "Optional description"
```

## Tips

- For broad topics, use `--auto` to let Caesar pick optimal settings.
- Use `--loops 3` or higher for complex multi-faceted questions.
- Use `--reasoning` for questions requiring deep analysis.
- Pipe output through `jq` to extract specific fields: `caesar research get <id> | jq '.content'`
- Chain brainstorm → research for best results on ambiguous queries.
