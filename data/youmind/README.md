# Youmind Skill (API-First)

Use this skill to operate Youmind from local CLI/agents without manual browser workflows.

中文文档: [README.zh-CN.md](./README.zh-CN.md)

- List / find / create boards
- Add links and upload files to boards
- Start chats and continue existing chats
- Trigger image and slides generation via chat
- Extract generated artifacts (image/slides/doc) from chat payloads

## Who This Is For

This skill is for local AI agents and developers with shell access (Codex, Claude Code, OpenClaw, etc.).

## Runtime Model

- Business operations are API-only.
- Browser is used only for authentication bootstrap/refresh.
- Auth/session data is stored locally under `data/`.

## Requirements

- Python `3.10+`
- Shell access
- Network access to `youmind.com`

`scripts/run.py` auto-creates `.venv` and installs dependencies on first run.

## Install

### Claude Code / Codex

```bash
mkdir -p ~/.claude/skills
cd ~/.claude/skills
git clone https://github.com/p697/youmind-skill.git
cd youmind-skill
```

### OpenClaw

```bash
mkdir -p ~/.openclaw/workspace/skills
cd ~/.openclaw/workspace/skills
git clone https://github.com/p697/youmind-skill.git
cd youmind-skill
```

## Quick Start (CLI)

### 1. Authenticate once

```bash
python scripts/run.py auth_manager.py setup
python scripts/run.py auth_manager.py validate
```

### 2. List and create boards

```bash
python scripts/run.py board_manager.py list
python scripts/run.py board_manager.py create --name "Demo Board"
python scripts/run.py board_manager.py find --query "demo"
```

### 3. Add materials

```bash
python scripts/run.py material_manager.py add-link --board-id <board-id> --url "https://example.com"
python scripts/run.py material_manager.py upload-file --board-id <board-id> --file /path/to/file.pdf
```

### 4. Chat and generate

```bash
python scripts/run.py chat_manager.py create --board-id <board-id> --message "Summarize key points"
python scripts/run.py chat_manager.py generate-image --board-id <board-id> --prompt "Minimal product poster"
python scripts/run.py chat_manager.py generate-slides --board-id <board-id> --prompt "6-slide project update"
```

### 5. Extract artifacts from chat

```bash
python scripts/run.py artifact_manager.py extract --chat-id <chat-id>
python scripts/run.py artifact_manager.py extract-latest --board-id <board-id>
python scripts/run.py artifact_manager.py extract --chat-id <chat-id> --include-raw-content
```

## Capabilities

### Boards

- `list`: list all boards
- `find`: search boards by keyword
- `get`: board detail by id
- `create`: create a new board

```bash
python scripts/run.py board_manager.py list
python scripts/run.py board_manager.py find --query "roadmap"
python scripts/run.py board_manager.py get --id <board-id>
python scripts/run.py board_manager.py create --name "My Board" --prompt "Initialize this board"
```

### Materials

- Add URL to a board
- Upload file to a board
- Query snips by ids
- List board picks

```bash
python scripts/run.py material_manager.py add-link --board-id <board-id> --url "https://example.com"
python scripts/run.py material_manager.py add-link --board-url "https://youmind.com/boards/<id>" --url "https://example.com"
python scripts/run.py material_manager.py upload-file --board-id <board-id> --file /path/to/file.pdf
python scripts/run.py material_manager.py get-snips --ids "<snip-id-1>,<snip-id-2>"
python scripts/run.py material_manager.py list-picks --board-id <board-id>
```

### Chat

- Create chat and send follow-up messages
- List history and fetch details
- Mark chat as read
- Generate image/slides via prompt

```bash
python scripts/run.py chat_manager.py create --board-id <board-id> --message "Summarize this board"
python scripts/run.py chat_manager.py send --board-id <board-id> --chat-id <chat-id> --message "Give next steps"
python scripts/run.py chat_manager.py history --board-id <board-id>
python scripts/run.py chat_manager.py detail --chat-id <chat-id>
python scripts/run.py chat_manager.py mark-read --chat-id <chat-id>
python scripts/run.py chat_manager.py generate-image --board-id <board-id> --prompt "Blue AI poster"
python scripts/run.py chat_manager.py generate-slides --board-id <board-id> --prompt "Project review deck"
```

### Artifacts

`artifact_manager.py` parses assistant tool blocks from chat details:

- `image_generate` -> image URLs + media ids
- `slides_generate` -> per-slide image URLs + media ids
- `write` -> document page id + content preview (+ raw content if requested)

## Agent Usage Examples

You can ask your agent:

- "List all my Youmind boards"
- "Find board named roadmap"
- "Create a board called GTM Plan"
- "Add this link to board <id>: https://example.com"
- "Generate an image in board <id>: minimalist launch poster"
- "Generate slides in board <id>: quarterly product update"
- "Extract the latest generated artifact in board <id>"

## Project Structure

```text
SKILL.md
scripts/
  run.py
  auth_manager.py
  api_client.py
  board_manager.py
  material_manager.py
  chat_manager.py
  artifact_manager.py
  ask_question.py
  cleanup_manager.py
  setup_environment.py
references/
  api_reference.md
  integration_api_discovery.md
  integration_plan_from_live_product.md
  troubleshooting.md
data/ (generated locally)
```

## Limitations

- API surface may change as Youmind updates backend contracts
- Session may expire and require `auth_manager.py reauth`
- Slide generation currently exposes slide image assets, not direct `.pptx` download URL

## Troubleshooting

```bash
python scripts/run.py auth_manager.py status
python scripts/run.py auth_manager.py validate
python scripts/run.py auth_manager.py reauth
```

References:

- `references/api_reference.md`
- `references/troubleshooting.md`

## Security

- `data/` contains session/auth information and should never be committed
- Use a dedicated account if your org requires separation for automation

## License

MIT (`LICENSE`)
