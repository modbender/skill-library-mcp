# Vexa webhook setup (meeting finished → report)

When a meeting finishes, Vexa can POST to your OpenClaw hooks endpoint. The bundled transform processes the webhook and triggers creation of a basic meeting report.

## Setup

1. **Set Vexa webhook URL** (points to your public OpenClaw hooks endpoint):

   `node skills/vexa/scripts/vexa.mjs user:webhook:set --webhook_url https://your-domain/hooks/vexa`

2. **Add hooks mapping** in `openclaw.json` (under `hooks.mappings`):

   ```json
   {
     "id": "vexa",
     "match": { "path": "vexa" },
     "action": "agent",
     "wakeMode": "now",
     "name": "Vexa meeting report",
     "transform": {
       "module": "skills/vexa/scripts/vexa-transform.mjs"
     }
   }
   ```

3. **Set transformsDir** to your workspace root so the transform path resolves:

   ```json
   "hooks": {
     "transformsDir": "/path/to/your/workspace",
     "mappings": [ ... ]
   }
   ```

## Behavior

- The transform runs when a webhook is received at `POST /hooks/vexa`.
- It processes only "meeting finished" events (skips in-progress, heartbeats).
- On meeting finished: injects a message instructing the agent to run `vexa.mjs report` and enrich the output (summary, entities).
- The transform lives inside the skill (`scripts/vexa-transform.mjs`) so it packs with the skill for ClawHub.

## Webhook requires a public domain

The webhook **cannot be set** without a public URL — Vexa rejects internal URLs (e.g. localhost). The webhook **cannot be validated** end-to-end without a reachable public domain; Vexa must POST to it. If there is no public URL or the tunnel (e.g. cloudflared) is not running, **Claw should be explicit**: *"The webhook can't be set until you have a public URL reachable from the internet. Until then, create reports manually with `vexa.mjs report`."*

## Publishing the webhook (cloudflared tunnel)

To make the webhook reachable, run a cloudflared tunnel pointing at the OpenClaw gateway (port 18789):

1. **Ensure OpenClaw gateway is running** (it serves hooks on 127.0.0.1:18789).

2. **Ensure cloudflared credentials exist** at `~/.cloudflared/<tunnel-id>.json`. If not:
   - `cloudflared tunnel login`
   - `cloudflared tunnel create openclaw-hooks` (or use an existing tunnel)

3. **Run the tunnel** (from workspace root):
   ```bash
   cloudflared tunnel --config cloudflared-config.yml run
   ```
   Config example (`cloudflared-config.yml`):
   ```yaml
   tunnel: <your-tunnel-id>
   credentials-file: ~/.cloudflared/<tunnel-id>.json
   ingress:
     - hostname: openclaw-hooks.vexa.ai
       service: http://127.0.0.1:18789
     - service: http_status:404
   ```

4. **Ensure DNS**: In Cloudflare, add a CNAME for `openclaw-hooks.vexa.ai` → `<tunnel-id>.cfargotunnel.com`.

5. **Set the Vexa webhook URL** (public hostname from your tunnel):
   ```bash
   node skills/vexa/scripts/vexa.mjs user:webhook:set --webhook_url https://openclaw-hooks.vexa.ai/hooks/vexa
   ```

## Mock webhook for local pipeline only

During `--validate-webhook`, if the real webhook was not received (no public URL / tunnel down), the script sends a **mock webhook** to `http://127.0.0.1:<gateway.port>/hooks/vexa`. This validates only the **local pipeline** (transform → report), **not** webhook delivery from Vexa. Use `--send-mock-webhook` standalone to trigger this manually.
