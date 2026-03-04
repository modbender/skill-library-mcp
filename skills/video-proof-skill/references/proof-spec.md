# Proof Spec Reference

## UI Proof Schema (record-proof.js)

```yaml
proof:
  # --- Server startup (optional) ---
  # Omit start_command entirely if the app is already running.
  # Accepts any shell command: npm, python, docker, go, cargo, etc.
  start_command: "npm run dev"
  start_port: 3000                    # Port to poll before recording (default: 3000)
  start_timeout: 30000                # Max ms to wait for server (default: 30000)

  # --- Browser config ---
  base_url: "http://localhost:3000"   # Base for relative goto paths
  viewport:
    width: 1280                       # Default: 1280
    height: 720                       # Default: 720

  # --- Steps (executed sequentially) ---
  steps:
    - goto: "/path"                   # Navigate (relative or absolute URL)
    - click: "text=Button"            # Playwright selector
    - fill:                           # Clear + fill input
        selector: "#email"
        value: "user@example.com"
    - type:                           # Keystroke-by-keystroke input
        selector: "#search"
        text: "query"
    - wait: 2000                      # Pause in milliseconds
    - screenshot: "name"              # Save screenshots/<name>.png
    - scroll: "down"                  # "up" or "down" (500px)
    - assert_visible: "text=Success"  # Fail proof if not visible within 10s
    - assert_url: "/dashboard"        # Fail if URL doesn't contain string

  timeout: 60000                      # Overall proof timeout (default: 60000)
```

## API Proof Schema (api-proof.js)

```yaml
proof:
  start_command: "npm start"          # Optional — same as UI proof
  start_port: 3000
  base_url: "http://localhost:3000"
  timeout: 30000

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

    - method: DELETE
      path: /api/users/1
      assert_status: 204
```

## PRD Integration Template

Copy into any task PRD:

```markdown
## Proof of Work

After implementation, create `proof-spec.yaml` in the task directory:

\`\`\`yaml
proof:
  start_command: "<command to start the app>"
  start_port: <port>
  base_url: "http://localhost:<port>"
  steps:
    - goto: "/<feature-page>"
    - wait: 2000
    - screenshot: "before"
    - click: "text=<feature-action>"
    - wait: 1000
    - assert_visible: "text=<expected-result>"
    - screenshot: "after"
\`\`\`

Then run:
\`\`\`bash
node <skill-dir>/scripts/record-proof.js --spec proof-spec.yaml --output ./proof-artifacts
\`\`\`

Commit the `proof-artifacts/` directory with your changes.
```
