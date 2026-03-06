# NotebookLM CLI Skill (OpenClaw) - VPS Installation Guide

This guide explains how to install and run the `notebooklm-cli-cookies` OpenClaw skill on a generic Linux VPS (Ubuntu/Debian), without any browser/UI on the server.

Skill slug on ClawHub (example): `notebooklm-cli-cookies`

Important security note:
- `notebooklm-auth.json`, `cookies.json`, and `metadata.json` are credentials. Never commit them to git. Never share them publicly.

## What you will achieve

- `nlm` works on the VPS (NotebookLM CLI).
- OpenClaw can query your NotebookLM sources from Telegram.
- You can force execution via Telegram slash command: `/nlm ...`

## 1) Prerequisites on the VPS

You need:
- Linux VPS (Ubuntu/Debian)
- `sudo` access

The bootstrap script will install most dependencies automatically.

## 2) Install the skill from ClawHub

Install ClawHub CLI (pick one):

```bash
npm i -g clawhub
```

or:

```bash
pnpm add -g clawhub
```

Login:

```bash
clawhub login
clawhub whoami
```

Choose your OpenClaw workspace directory, for example:

```text
~/.openclaw/workspace
```

Install the skill into the workspace:

```bash
cd ~/.openclaw/workspace
clawhub install notebooklm-cli-cookies
```

Verify files exist:

```bash
ls -la ./skills/notebooklm-cli-cookies/
ls -la ./skills/notebooklm-cli-cookies/scripts/
```

## 3) Run the one-liner bootstrap (systemd-friendly)

After installation, run the bootstrap shipped inside the skill:

```bash
cd ~/.openclaw/workspace
bash ./skills/notebooklm-cli-cookies/scripts/bootstrap_vps_systemd_one_liner.sh \
  --workdir ~/.openclaw/workspace \
  --user ubuntu \
  --service openclaw-telegram.service \
  --skill-name notebooklm-cli-cookies
```

What the bootstrap does:
- installs `jq`, `pipx`, and Python tooling
- installs `nlm` (`notebooklm-mcp-cli`) with `pipx` first, then safe fallback
- ensures `NOTEBOOKLM_MCP_CLI_PATH` is injected into OpenClaw via `~/.openclaw/openclaw.json`
- sets up a systemd drop-in to auto-inject auth on service start (if you pass `--service`)

Compatibility notes:
- The bootstrap avoids `apt install npm` to prevent `nodejs`/`npm` conflict on NodeSource-based systems.
- On PEP 668 systems (`externally-managed-environment`), it uses `pipx` first and only falls back to `pip --break-system-packages` if required.

## 4) Prepare NotebookLM auth (on a machine with a browser)

NotebookLM requires Google cookies. You must prepare auth on a machine with Chrome:

```bash
nlm login
```

The default profile is stored at:

```text
~/.notebooklm-mcp-cli/profiles/default/
  - cookies.json
  - metadata.json
```

Create one JSON file named `notebooklm-auth.json`:

```json
{
  "cookies": <contents of cookies.json>,
  "metadata": <contents of metadata.json>
}
```

## 5) Copy auth to the VPS (required)

On the VPS, store the file at:

```text
/etc/openclaw/notebooklm-auth.json
```

Set permissions (recommended):

```bash
sudo mkdir -p /etc/openclaw
sudo cp ./notebooklm-auth.json /etc/openclaw/notebooklm-auth.json
sudo chown root:openclaw /etc/openclaw/notebooklm-auth.json
sudo chmod 640 /etc/openclaw/notebooklm-auth.json
```

Then restart your OpenClaw service:

```bash
sudo systemctl restart openclaw-telegram.service
```

## 6) Verify on the VPS

Run as the OpenClaw user (example: `ubuntu`):

```bash
export NOTEBOOKLM_MCP_CLI_PATH="~/.notebooklm-mcp-cli"
nlm login --check
nlm notebook list --json
```

If this works, the NotebookLM side is ready.

## 7) Use from Telegram

These commands force execution via the `nlm` CLI:

```text
/nlm login --check
```

```text
/nlm notebook list --json
```

Create an alias for easier queries (recommended):

```text
/nlm alias set tai_lieu_dien <NOTEBOOK_UUID> --type notebook
```

Query:

```text
/nlm notebook query tai_lieu_dien "What are the rated currents for MCB?"
```

## 8) Troubleshooting

- Skill not visible / bot asks for Browser Control:
  - Check Telegram: `echo $NOTEBOOKLM_MCP_CLI_PATH` must not be empty.
  - Ensure `~/.openclaw/openclaw.json` injects `NOTEBOOKLM_MCP_CLI_PATH`.
  - Restart OpenClaw (new session).
- `nlm notebook get "<title>"` returns null:
  - Use UUID or alias, not the notebook title.
- Auth expires:
  - Re-run `nlm login` on a machine with a browser and replace `/etc/openclaw/notebooklm-auth.json`.

