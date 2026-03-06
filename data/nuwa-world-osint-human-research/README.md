# Nuwa World API Skill

A Cursor Agent Skill that teaches the AI how to use the **Nuwa World API** for face search and deep research over the open web.

## What this skill does

Based on `SKILL.md`, the skill exposes two core capabilities backed by `https://gateway.nuwa.world/api/v1`:

- **Face Search** – upload a face image and get matching URLs across the internet (async, 2‑step flow)
- **Deep Research** – send a natural‑language query and get a structured summary with facts and sources

The agent will use this skill when the conversation mentions Nuwa, the Nuwa World API, face search, or deep research / open‑web investigation.

## API overview

- **Base URL**: `https://gateway.nuwa.world/api/v1`
- **Auth header**: `X-API-Key: $NUWA_API_KEY`
- **Get an API key**: `https://platform.nuwa.world`
- **Env required by the skill**: `NUWA_API_KEY` (see `metadata.openclaw.requires.env` in `SKILL.md`)

### Face Search

Two‑step async flow: **upload → poll**.

1. **Upload (cost: 10 credits)**  
   `POST /face-search` with multipart form data:

   ```bash
   curl -X POST https://gateway.nuwa.world/api/v1/face-search \
     -H "X-API-Key: $NUWA_API_KEY" \
     -F "image=@photo.jpg"
   ```

   Returns `202 Accepted` with a `search_id`.

2. **Poll (cost: 0 credits)**  
   `GET /face-search/{search_id}` every 3–5 seconds:

   ```bash
   curl https://gateway.nuwa.world/api/v1/face-search/abc123 \
     -H "X-API-Key: $NUWA_API_KEY"
   ```

   - While processing: `status: "processing"`, empty `results`
   - When complete: `status: "completed"` plus an array of `{ index, score, url }`
   - Typical latency: 15–30 seconds
   - Results expire ~2 hours after completion

### Deep Research

Single synchronous call (cost: 20 credits).

```bash
curl -X POST https://gateway.nuwa.world/api/v1/deep-research \
  -H "X-API-Key: $NUWA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "0xajc on X"}'
```

- Response includes a `summary`, a `facts` list, and `sources` with titles and URLs.
- Typical latency: 10–60 seconds.
- `query` max length: 2000 characters.

### Errors and credits

All errors share a consistent shape:

```json
{ "error": { "code": "ERROR_CODE", "message": "Human-readable description" } }
```

Common error codes: `INVALID_API_KEY`, `RATE_LIMITED`, `INSUFFICIENT_CREDITS`, `UPLOAD_FAILED`, `NOT_FOUND`, `RESEARCH_FAILED`.

Credit costs (also summarized in `SKILL.md`):

| Endpoint             | Credits |
|----------------------|---------|
| Face Search (upload) | 10      |
| Face Search (poll)   | 0       |
| Deep Research        | 20      |

Free tier: 30 credits / month. Higher‑tier plans are listed at `https://platform.nuwa.world`.

## How to install this skill

You can install the skill either per‑project or for your entire user account.

### Project-level (recommended)

Use this when the Nuwa World workflow is specific to one repository:

```bash
cd /path/to/your-project

mkdir -p .cursor/skills
cp -r /path/to/nuwa-world-api-skill .cursor/skills/nuwa-world-api-skill
```

Cursor will automatically pick up any skill folders under `.cursor/skills/` that contain a `SKILL.md`.

### User-level

Use this when you want the skill available in all projects:

```bash
mkdir -p ~/.cursor/skills
cp -r /path/to/nuwa-world-api-skill ~/.cursor/skills/nuwa-world-api-skill
```

> Do **not** put custom skills in `~/.cursor/skills-cursor/`; that directory is reserved for Cursor’s built‑in skills.

## Repository structure

```text
nuwa-world-api-skill/
├── README.md    # This file: high-level docs & usage
└── SKILL.md     # Required: metadata + instructions for the agent
```

You can optionally add:

- `reference.md` – extended API docs (error codes, advanced options, etc.)
- `examples.md` – example prompts and full request / response transcripts

## How the agent uses this skill

Once installed and with `NUWA_API_KEY` configured:

1. Open a project where this skill is available (project‑level or user‑level).
2. Ask for things like:
   - “Search the web for this face and show me the top URLs.”
   - “Do a deep research pass on 0xajc on X.”
   - “Use the Nuwa World API to summarize this person’s online footprint.”
3. The agent will follow the flows defined in `SKILL.md` (face search upload + poll, or deep research POST) rather than inventing its own protocol.

You generally don’t need to manually “enable” the skill; mentioning Nuwa, the Nuwa World API, face search, or deep research in a context where the skill is installed is enough.

## Customization

To adapt the skill to your own workflows:

- **Change trigger description** – edit the `description` field in `SKILL.md` to better describe what the skill does and when to use it.
- **Extend documentation** – add `reference.md` or `examples.md` and link them from `SKILL.md` for progressive disclosure.
- **Wire into other tools** – if you have additional automation (e.g., scripts wrapping `curl`), document how/when the agent should call them here.

Keep `SKILL.md` reasonably concise; push verbose reference material into separate files and link to them.

## License

Use whichever license your repository adopts; this README does not impose additional terms.
