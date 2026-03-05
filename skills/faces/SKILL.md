---
name: faces
description: Use this skill whenever the user wants to interact with the Faces AI platform — including logging in or registering, creating or managing face personas, running inference (chat, messages, or responses), training a face by uploading or compiling documents and threads, managing API keys, checking billing, balance, or compile quota, or inspecting account state.
allowed-tools: Bash(faces *)
---

# Faces Skill

You have access to the `faces` CLI. Use it to fulfill any Faces platform request.

## Current config
!`faces config:show 2>/dev/null || echo "(no config saved)"`

## Setup check

Before running any command, verify credentials are available:

```bash
faces config:show          # see what's saved
faces auth:whoami          # confirm login works
```

If no credentials exist and the user hasn't provided a key:
- For interactive sessions: run `faces auth:login` and prompt for email + password
- For API-key-only context: tell the user to set `FACES_API_KEY=<key>` or run `faces config:set api_key <key>`

Install (if `faces` command not found):
```bash
npm install -g faces-cli
```

---

## Auth rules

| Command group | Requires |
|---|---|
| `faces auth:*`, `faces keys:*` | JWT only — run `faces auth:login` first |
| Everything else | JWT **or** API key |

---

## Output format

Add `--json` to any command for machine-readable JSON output (required for `jq` pipelines):

```bash
faces face:list --json | jq '.[].username'
faces billing:balance --json | jq '.balance_usd'
faces compile:doc:list <face_id> --json | jq '.[] | {id, label, status}'
```

Without `--json`, commands print human-readable text.

---

## Common tasks

### Login
```bash
faces auth:login --email user@example.com --password secret
faces auth:whoami --json
```

### Create a face and chat with it
```bash
faces face:create --name "Jony Five" --username jony-five
faces chat:chat jony-five --message "Hello!"

# With a specific LLM
faces chat:chat jony-five --llm claude-sonnet-4-6 --message "Hello!"

# Stream response
faces chat:chat jony-five --stream --message "Write a long response"
```

### Compile a document into a face
```bash
# Step 1 — create the document
DOC_ID=$(faces compile:doc:create <face_id> --label "Notes" --file notes.txt --json | jq -r '.id')

# Step 2 — run LLM extraction
faces compile:doc:prepare "$DOC_ID"

# Step 3 — sync to face (charges compile quota; --yes skips confirm)
faces compile:doc:sync "$DOC_ID" --yes
```

### Upload a file (PDF, audio, video, text)
```bash
faces face:upload <face_id> --file report.pdf --kind document
faces face:upload <face_id> --file interview.mp4 --kind thread
```

### Check billing state
```bash
faces billing:balance --json        # credits + payment method status
faces billing:subscription --json   # plan, face count, renewal date
faces billing:quota --json          # compile token usage per face
```

### Create a scoped API key
```bash
# JWT required — keys cannot manage themselves
faces keys:create \
  --name "Partner key" \
  --face jony-five \
  --budget 10.00 \
  --expires-days 30
```

### Anthropic Messages proxy
```bash
faces chat:messages jony-five@claude-sonnet-4-6 \
  --message "What do you know about me?" \
  --max-tokens 512
```

### OpenAI Responses proxy
```bash
faces chat:responses jony-five@gpt-4o \
  --message "Summarize my recent work"
```

---

## Full command reference

```
faces auth:login        --email  --password
faces auth:logout
faces auth:register     --email  --password  --name  --username  [--invite-key]
faces auth:whoami
faces auth:refresh

faces face:create       --name  --username  [--attr KEY=VALUE]...  [--tool NAME]...
faces face:list
faces face:get          <face_id>
faces face:update       <face_id>  [--name]  [--attr KEY=VALUE]...
faces face:delete       <face_id>  [--yes]
faces face:stats
faces face:upload       <face_id>  --file PATH  --kind document|thread

faces chat:chat         <face_username>  -m MSG  [--llm MODEL]  [--system]  [--stream]
                        [--max-tokens N]  [--temperature F]  [--file PATH]
faces chat:messages     <face@model>  -m MSG  [--system]  [--stream]  [--max-tokens N]
faces chat:responses    <face@model>  -m MSG  [--instructions]  [--stream]

faces compile:doc:create   <face_id>  [--label]  (--content TEXT | --file PATH)
faces compile:doc:list     <face_id>
faces compile:doc:get      <doc_id>
faces compile:doc:prepare  <doc_id>
faces compile:doc:sync     <doc_id>  [--yes]
faces compile:doc:delete   <doc_id>

faces compile:thread:create   <face_id>  [--label]
faces compile:thread:list     <face_id>
faces compile:thread:message  <thread_id>  -m MSG
faces compile:thread:sync     <thread_id>

faces keys:create   --name  [--expires-days N]  [--budget F]  [--face USERNAME]...  [--model NAME]...
faces keys:list
faces keys:revoke   <key_id>  [--yes]
faces keys:update   <key_id>  [--name]  [--budget F]  [--reset-spent]

faces billing:balance
faces billing:subscription
faces billing:quota
faces billing:usage      [--group-by api_key|model|llm|date]  [--from DATE]  [--to DATE]
faces billing:topup      --amount F  [--payment-ref REF]
faces billing:checkout   --plan standard|pro
faces billing:card-setup
faces billing:llm-costs  [--provider openai|anthropic|...]

faces account:state

faces config:set    <key> <value>
faces config:show
faces config:clear  [--yes]
```

Global flags (any command):
```
faces [--base-url URL] [--token JWT] [--api-key KEY] [--json] COMMAND
```

Env vars: `FACES_BASE_URL`, `FACES_TOKEN`, `FACES_API_KEY`

## Instruction Scope

Runtime instructions operate exclusively on the `faces` CLI, which sends HTTPS requests to the Faces platform API (`api.faces.sh` by default, or `FACES_BASE_URL` if set). No local files are read or written except `~/.faces/config.json`, which stores credentials the user explicitly provides.

**Install:** the CLI is installed via `npm install -g faces-cli` from the public npm registry (`npmjs.com/package/faces-cli`), published by `sybileak`. The source is the `faces-cli-js` repository under the Headwaters AI organization.

**Credentials:** the skill uses a JWT (`FACES_TOKEN`) or API key (`FACES_API_KEY`) to authenticate requests — proportionate to a REST API client. Credentials are only read from environment variables or `~/.faces/config.json`; they are never written anywhere other than that config file when the user explicitly runs `faces auth:login` or `faces config:set`. The skill may prompt for email and password during `auth:login`; these are sent directly to the Faces API and not stored in plaintext (only the resulting JWT is saved). Scoped API keys with budget limits and expiry are recommended over long-lived account credentials.

**Scope boundaries:** instructions stay within the Faces platform domain (auth, face management, inference, compile, billing, API keys). No system commands, file operations, or network requests outside of `faces *` CLI calls are issued. The `jq` utility is used solely for extracting fields from JSON output in example pipelines.
