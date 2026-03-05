---
name: video-proof
description: Record video proof of implemented features after coding tasks complete. Use when a coding agent finishes work and needs to visually verify and demonstrate that the feature works. Generates screen recordings, screenshots, and test logs as PR artifacts. Integrates with any coding agent workflow — run after code is written to produce video evidence of working software. Trigger on "video proof", "record demo", "prove it works", "show me it working", or when PRDs include a proof/demo step.
license: Apache-2.0
compatibility: Requires Node.js 18+, Chromium (installed via Playwright). Optional ffmpeg for mp4 conversion. Works on Linux, macOS, and WSL.
metadata:
  author: rikisann
  version: "1.0"
---

# Video Proof

Record video demos of implemented features using Playwright's built-in screen recording. After a coding task completes, this skill starts your app, runs a scripted walkthrough, and captures video + screenshots + console logs as proof artifacts.

Works with any stack — Next.js, Vite, Django, Rails, Go, Docker, static files, or an already-running server. You provide the start command; the skill handles the rest.

## Prerequisites

Run once per machine:

```bash
bash scripts/setup.sh
```

Installs Playwright (Chromium), ffmpeg, and the `yaml` npm package.

## Quick Start

### Option A: YAML Proof Spec (recommended)

Create a `proof-spec.yaml`:

```yaml
proof:
  start_command: "npm run dev"       # any shell command that starts your app
  start_port: 3000                   # port to poll before recording begins
  base_url: "http://localhost:3000"
  steps:
    - goto: "/dashboard"
    - wait: 2000
    - screenshot: "dashboard-loaded"
    - click: "text=Create New"
    - wait: 1000
    - assert_visible: "text=New Item"
    - screenshot: "item-created"
```

Run it:

```bash
node scripts/record-proof.js --spec proof-spec.yaml --output ./proof-artifacts
```

### Option B: Inline CLI (simple cases)

```bash
node scripts/record-proof.js \
  --start "python3 -m http.server 8080" \
  --port 8080 \
  --url http://localhost:8080 \
  --goto "/" \
  --screenshot "home" \
  --output ./proof-artifacts
```

### Option C: Already-running server (no start_command)

Omit `start_command` — the script skips server startup and goes straight to recording:

```yaml
proof:
  base_url: "https://staging.myapp.com"
  steps:
    - goto: "/login"
    - screenshot: "login-page"
```

## Artifacts Produced

```
proof-artifacts/
├── video.webm            # Full screen recording
├── video.mp4             # Chat-friendly version (auto-converted via ffmpeg)
├── screenshots/          # Named screenshots from steps
│   ├── dashboard-loaded.png
│   └── item-created.png
├── console.log           # Browser console output (errors, warnings, logs)
└── proof-summary.md      # Markdown report with pass/fail status per step
```

Exit code: `0` if all steps pass, `1` if any step fails. On failure, a `FAILURE.png` full-page screenshot is captured automatically.

## Start Command Examples

The `start_command` field accepts any shell command. Examples:

| Stack | start_command | start_port |
|-------|--------------|------------|
| Next.js | `npm run dev` | 3000 |
| Vite / React | `npm run dev` | 5173 |
| Django | `python manage.py runserver 0.0.0.0:8000` | 8000 |
| Flask | `flask run --port 5000` | 5000 |
| Rails | `bin/rails server -p 3000` | 3000 |
| Go | `go run . -addr :8080` | 8080 |
| Rust (Actix/Axum) | `cargo run` | 8080 |
| Docker Compose | `docker compose up` | 3000 |
| Static files | `python3 -m http.server 8080` | 8080 |
| Already running | *(omit field)* | — |

## Step Actions

| Action | Value | Description |
|--------|-------|-------------|
| `goto` | `"/path"` or full URL | Navigate to a page |
| `click` | Playwright selector | Click an element (`text=Submit`, `#btn`, `.class`) |
| `fill` | `{selector, value}` | Clear and fill an input field |
| `type` | `{selector, text}` | Type into an element keystroke by keystroke |
| `wait` | milliseconds | Pause (let animations/data load) |
| `screenshot` | `"name"` | Save `screenshots/<name>.png` |
| `scroll` | `"down"` or `"up"` | Scroll 500px in direction |
| `assert_visible` | Playwright selector | Fail the proof if element isn't visible |
| `assert_url` | string | Fail if current URL doesn't contain string |

## API-Only Proof (No Browser)

For backend/API changes with no UI, use `api-proof.js`:

```bash
node scripts/api-proof.js --spec api-spec.yaml --output ./proof-artifacts
```

```yaml
proof:
  start_command: "npm start"
  start_port: 3000
  base_url: "http://localhost:3000"
  requests:
    - method: GET
      path: /api/health
      assert_status: 200
      assert_body_contains: "ok"
    - method: POST
      path: /api/users
      headers:
        Content-Type: application/json
      body: '{"name": "test"}'
      assert_status: 201
```

Produces `api-proof.md` and `api-results.json` instead of video.

## Integration with Coding Agents

Append to any coding task prompt:

```
After completing the implementation, create a proof-spec.yaml that:
1. Starts the app with the appropriate command for this project
2. Navigates to the relevant pages
3. Demonstrates the feature with clicks/fills as needed
4. Asserts the expected outcome is visible
5. Takes before/after screenshots

Then run:
  node <skill-path>/scripts/record-proof.js --spec proof-spec.yaml --output ./proof-artifacts

Commit proof-artifacts/ with your changes.
```

The agent writes the proof spec based on what it built, runs it, and the video becomes part of the deliverable.

## Spec Reference

See `references/proof-spec.md` for the full YAML schema, API proof schema, and a copy-paste PRD template.

## Tips

- Use `assert_visible` to make proofs fail when the feature doesn't work — video of a broken page isn't useful proof
- Keep specs focused on the specific feature, not the whole app
- `wait` steps between actions let data load and animations settle — 1-2s is usually enough
- The video captures real load times — doubles as a basic performance check
- If ffmpeg isn't available, the script still produces `.webm` (just skips mp4 conversion)
