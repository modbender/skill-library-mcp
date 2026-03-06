---
name: solid-agent-storage
description: Give your AI agent persistent identity (WebID) and personal data storage (Pod) using the Solid Protocol
version: 0.3.9
author: Interition
license: Apache-2.0
metadata:
  openclaw:
    requires:
      env:
        - INTERITION_PASSPHRASE
        - SOLID_SERVER_URL
      bins:
        - node
        - curl
        - jq
    primaryEnv: INTERITION_PASSPHRASE
    install:
      - kind: brew
        formula: jq
        bins: [jq]
    categories:
      - storage
      - identity
      - data
    homepage: https://github.com/masterworrall/agent-interition
---

# Solid Agent Storage

This Skill gives you a **Solid Pod** — a personal data store with a **WebID** (your identity on the web). You can store data, read it back, and share specific resources with other agents.

## When to Use This Skill

- You need to **remember something** across conversations (notes, preferences, learned facts)
- You need to **store structured data** (RDF/Turtle format for linked data, or any content type)
- You need to **share data** with another agent who also has a Pod
- You need a **persistent identity** that other agents or services can verify

## Setup

Before using any commands, set the `INTERITION_PASSPHRASE` environment variable. This passphrase encrypts the Solid server credentials stored on your device (under `~/.interition/agents/`), protecting them at rest in your OpenClaw environment. Use a strong passphrase and keep it secret.

### Running your own Solid server (recommended)

For full control, run your own [Community Solid Server](https://github.com/CommunitySolidServer/CommunitySolidServer) (CSS). The CSS is open-source software maintained by the [Open Data Institute](https://www.theodi.org/).

Set `SOLID_SERVER_URL` to your server's URL:

```bash
export SOLID_SERVER_URL="http://localhost:3000"
```

See the [source repository](https://github.com/masterworrall/agent-interition) for a hardened Docker configuration you can use as a starting point.

### Using a shared Solid server (for multi-agent collaboration)

If your agents need to collaborate with other agents using the Solid Protocol, they need to share the same Solid server. Two public CSS instances are available:

- **https://solidcommunity.net** — operated by the [Open Data Institute](https://www.theodi.org/)
- **https://crawlout.io** — operated by [Interition](https://interition.net), the provider of this Skill

To use a shared server, set `SOLID_SERVER_URL`:

```bash
export SOLID_SERVER_URL="https://crawlout.io"
```

If `SOLID_SERVER_URL` is not set, the Skill defaults to `https://crawlout.io`.

## How Credentials Work

The Solid server issues credentials to prevent anyone other than your agent from accessing its services and data. This is the same trust model as any remote service that requires users to identify themselves and prove they are authorised. When you provision an agent:

1. The CSS **creates** an account, WebID, and Pod for your agent
2. The CSS **issues** client credentials (ID and secret) that your agent uses to authenticate
3. Your agent uses those credentials to obtain **time-limited Bearer tokens** for reading and writing data
4. The CSS **enforces access control** (WAC) on every request — only authorised agents can access protected resources

`INTERITION_PASSPHRASE` is **not** a server credential. It seeds the encryption (AES-256-GCM) of the server-issued credentials stored locally on your device (under `~/.interition/agents/` with `0600` permissions), making them less vulnerable in your OpenClaw environment. The server never sees your passphrase.

## How It Works

This Skill provides **three management scripts** for CSS-specific operations (provisioning, deprovisioning, status) plus a **token helper** for authentication. All standard Solid operations (read, write, delete, share) are done with **curl and a Bearer token** — your Pod is a standard W3C Solid server.

For broader guidance on using Solid servers and the wider Solid ecosystem, refer to [solidproject.org](https://solidproject.org). The full protocol specification is at [Solid Protocol (W3C)](https://solidproject.org/TR/protocol).

### Two-Step Workflow

**Step 1:** Get a token:
```bash
scripts/get-token.sh --agent <name>
```

Output:
```json
{"token": "eyJhbG...", "expiresIn": 600, "serverUrl": "https://crawlout.io", "podUrl": "https://crawlout.io/example-agent/", "webId": "https://crawlout.io/example-agent/profile/card#me"}
```

**Step 2:** Use curl with `Authorization: Bearer $TOKEN` for any Solid operation.

### Token Expiry

Tokens last **600 seconds** (10 minutes). If more than **8 minutes** have elapsed since your last `get-token.sh` call, fetch a new token before making requests.

## Quick Reference

Extract token and URLs:
```bash
TOKEN_JSON=$(scripts/get-token.sh --agent example-agent)
TOKEN=$(echo "$TOKEN_JSON" | jq -r '.token')
POD_URL=$(echo "$TOKEN_JSON" | jq -r '.podUrl')
```

**Read a resource:**
```bash
curl -s -H "Authorization: Bearer $TOKEN" "${POD_URL}memory/notes.ttl"
```

**Write a resource:**
```bash
curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: text/turtle" \
  --data-raw '@prefix schema: <http://schema.org/>.
<#note-1> a schema:Note;
  schema:text "Important finding";
  schema:dateCreated "2024-01-15".' \
  "${POD_URL}memory/notes.ttl"
```

**Delete a resource:**
```bash
curl -s -X DELETE -H "Authorization: Bearer $TOKEN" "${POD_URL}memory/old.ttl"
```

For the full set of operations (containers, PATCH, access control, public access), see `references/solid-http-reference.md`.

## Management Commands

### Provision Identity and Storage

Creates a WebID and Pod for an agent. Run this once per unique agent name.

```bash
scripts/provision.sh --name <agent-name> [--displayName <display-name>]
```

**Example:**
```bash
scripts/provision.sh --name example-agent --displayName "Example Agent"
```

**Output:**
```json
{"status": "ok", "agent": "example-agent", "webId": "https://crawlout.io/example-agent/profile/card#me", "podUrl": "https://crawlout.io/example-agent/"}
```

### Deprovision Identity and Storage

Fully removes an agent's WebID and Pod: deletes its pods, client credentials, WebID links, and password logins from the CSS server, then deletes local credential files.

```bash
scripts/deprovision.sh --name <agent-name>
```

**Example:**
```bash
scripts/deprovision.sh --name example-agent
```

**Output (success):**
```json
{"status": "ok", "agent": "example-agent", "accountDeleted": true, "credentialsDeleted": true}
```

**Output (partial — e.g. server unreachable):**
```json
{"status": "partial", "agent": "example-agent", "accountDeleted": false, "credentialsDeleted": true, "warnings": ["Could not delete CSS account: ..."]}
```

- `status: "ok"` — CSS account fully dismantled and local files deleted
- `status: "partial"` — local files deleted but CSS cleanup failed (see warnings)

If the agent was provisioned before email/password storage was added, CSS cleanup is skipped and a warning explains why.

### Check Status

Lists all provisioned agents and their details.

```bash
scripts/status.sh
```

## Pod Structure

Each agent's Pod has these containers:

| Path | Purpose |
|------|---------|
| `/{name}/memory/` | Private agent memory (notes, learned facts, preferences) |
| `/{name}/shared/` | Resources intended for sharing with other agents |
| `/{name}/conversations/` | Conversation logs and context |

## Turtle Templates

When storing structured data, use Turtle (RDF) format. Here are templates for common patterns:

### A note or memory
```turtle
@prefix schema: <http://schema.org/>.
<#note-1> a schema:Note;
  schema:text "The content of the note";
  schema:dateCreated "2024-01-15".
```

### An agent preference
```turtle
@prefix foaf: <http://xmlns.com/foaf/0.1/>.
@prefix schema: <http://schema.org/>.
<#pref-1> a schema:PropertyValue;
  schema:name "response-style";
  schema:value "concise".
```

### A shared dataset
```turtle
@prefix schema: <http://schema.org/>.
<#dataset-1> a schema:Dataset;
  schema:name "Research Results";
  schema:description "Findings from the analysis task";
  schema:dateModified "2024-01-15".
```

## Error Handling

All management commands output JSON. On error, stderr will contain:
```json
{"error": "description of what went wrong"}
```

Common errors:
- `"No passphrase provided"` — Set `INTERITION_PASSPHRASE` env var
- `"No credentials found"` — Run `provision.sh` first
- `"Invalid passphrase"` — Wrong `INTERITION_PASSPHRASE` value
- `"Token request failed: 401"` — Credentials expired; re-provision the agent's WebID and Pod
- `"HTTP 404"` — Resource doesn't exist at that URL
