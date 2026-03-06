# ngrok-preview Troubleshooting

## 1) `ngrok: command not found`

- Install ngrok from https://ngrok.com/download
- Verify:

```bash
ngrok version
```

## 2) Auth token not configured

- Run:

```bash
ngrok config add-authtoken "$NGROK_AUTHTOKEN"
ngrok config check
```

- Or pass `--auth-token <token>` to `scripts/ngrok_preview.py up`.

## 3) Tunnel URL timeout

Run checks in order:

```bash
python3 scripts/ngrok_preview.py status
ngrok config check
```

Then retry with a longer timeout:

```bash
python3 scripts/ngrok_preview.py up \
  --title "retry" \
  --source <path> \
  --ngrok-timeout-seconds 40
```

## 4) Preview page loads but content is missing

- Confirm source path exists and was copied.
- Re-run with explicit `--source` entries.
- Avoid passing very large directories; include only required files.

## 5) Port conflict or stale processes

Stop the session and clean expired state:

```bash
python3 scripts/ngrok_preview.py down --session-id <id> --delete-session-dir
python3 scripts/ngrok_preview.py cleanup
```

## 6) Security checklist before sending link

- Scope is only current task artifacts.
- TTL is short and explicit in message.
- Session is stopped after task completion.
