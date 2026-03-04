---
name: bitclawden
description: Look up, create, and edit credentials in Bitwarden vault via the bw CLI. Use when asked to store, retrieve, find, or manage passwords, secrets, or credentials.
homepage: https://bitwarden.com/help/cli/
metadata:
  {
    "openclaw":
      {
        "emoji": "🔐",
        "requires": { "bins": ["bw", "jq"], "env": ["BW_SESSION"] },
        "primaryEnv": "BW_SESSION",
        "install":
          [
            {
              "id": "bw-binary",
              "kind": "script",
              "script": "PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]'); [ \"$PLATFORM\" = 'darwin' ] && PLATFORM='macos'; curl -sL \"https://vault.bitwarden.com/download/?app=cli&platform=${PLATFORM}\" -o /tmp/bw.zip && unzip -o /tmp/bw.zip -d ~/.local/bin/ && chmod +x ~/.local/bin/bw && rm /tmp/bw.zip",
              "bins": ["bw"],
              "requires": ["curl", "unzip"],
              "label": "Install Bitwarden CLI to ~/.local/bin",
            },
          ],
      },
  }
---

# Bitwarden CLI

Manage credentials in Bitwarden vault. Follow the official CLI docs — don't guess commands.

## Workflow

1. Verify CLI present: `bw --version`.
2. Check vault status: `bw status`.
3. If locked, tell the user to run `bw unlock` and set `BW_SESSION`.
4. Verify access: `bw status` must show `unlocked` before any vault operation.
5. After creating or editing items, run `bw sync`.

## Lookup

```bash
bw list items --search "query"
bw get item "name"
bw get password "name"
bw get username "name"
bw get totp "name"
bw list items --folderid <folder-id>
bw list folders
```

## Create

```bash
# Login item (type 1=Login, 2=Secure Note, 3=Card, 4=Identity)
echo '{"type":1,"name":"Example","login":{"username":"user@example.com","password":"s3cret","uris":[{"uri":"https://example.com"}]}}' | bw encode | bw create item

# Folder
bw create folder "$(echo '{"name":"Work"}' | bw encode)"
```

## Edit

```bash
bw get item <id> | jq '.login.password = "newpass"' | bw encode | bw edit item <id>
bw get item <id> | jq '.folderId = "<folder-id>"' | bw encode | bw edit item <id>
```

## Generate

```bash
bw generate -ulns --length 24
bw generate --passphrase --words 4 --separator "-"
```

## Guardrails

- Never paste secrets into logs, chat, or code.
- Prefer showing username and site — only reveal passwords if explicitly requested.
- Always generate a strong password with `bw generate` unless the user provides one.
- If a command returns "Vault is locked", stop and ask the user to unlock.
