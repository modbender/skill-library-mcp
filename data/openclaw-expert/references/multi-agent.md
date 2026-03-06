# Multi-Agent-Routing

## Konzept

Ein Gateway kann mehrere Agents hosten, jeder mit eigenem:
- **Workspace** (SOUL.md, AGENTS.md, Memory)
- **agentDir** (Auth-Profile, Sessions)
- **Session-Store** (`~/.openclaw/agents/<agentId>/sessions/`)

### Begriffe
| Begriff | Bedeutung |
|---|---|
| `agentId` | Ein "Gehirn" (Workspace, Auth, Sessions) |
| `accountId` | Ein Channel-Account (z.B. WhatsApp-Nummer "personal" vs "biz") |
| `binding` | Routing-Regel: `(channel, accountId, peer)` → `agentId` |

---

## Konfiguration

```json5
{
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
    },
    list: [
      {
        id: "alex",
        workspace: "~/.openclaw/workspace-alex",
      },
      {
        id: "mia",
        workspace: "~/.openclaw/workspace-mia",
      },
    ],
  },

  bindings: [
    {
      agentId: "alex",
      match: {
        channel: "whatsapp",
        peer: { kind: "direct", id: "+491111111111" },
      },
    },
    {
      agentId: "mia",
      match: {
        channel: "whatsapp",
        peer: { kind: "direct", id: "+492222222222" },
      },
    },
    // Discord: nach Guild-ID routen
    // {
    //   agentId: "work",
    //   match: {
    //     channel: "discord",
    //     guildId: "123456789",
    //   },
    // },
  ],

  channels: {
    whatsapp: {
      dmPolicy: "allowlist",
      allowFrom: ["+491111111111", "+492222222222"],
    },
  },
}
```

---

## Routing-Logik

Bindings sind deterministisch, "most-specific wins":

1. Binding mit allen Match-Feldern (channel + accountId + peer + guildId)
2. Binding mit weniger spezifischen Feldern
3. Fallback: Default-Agent (`agents.list[].default: true`, sonst erster Eintrag)

Bei gleicher Spezifität: Erste Binding in Config-Reihenfolge gewinnt.
Mehrere Match-Felder = AND-Semantik (alle müssen zutreffen).

---

## Wichtige Regeln

1. **Nie agentDir zwischen Agents teilen** → Auth/Session-Kollisionen
2. **Auth-Profile sind per-Agent** — Main-Agent-Credentials werden nicht automatisch geteilt
3. **Skills**: Per-Agent via Workspace `skills/`, shared via `~/.openclaw/skills/`
4. **WhatsApp dmPolicy**: Global pro Account, nicht pro Agent!
5. **Discord/Telegram**: Pro Agent ein eigener Bot nötig
6. **Binding-Upgrade**: Wenn du eine channel-only Binding und dann eine mit accountId hinzufügst,
   wird die bestehende automatisch auf account-scoped upgraded (kein Duplikat)

---

## Setup für Multi-Agent

```bash
# Workspaces erstellen
mkdir -p ~/.openclaw/workspace-alex
mkdir -p ~/.openclaw/workspace-mia

# Workspace-Dateien initialisieren
openclaw setup --workspace ~/.openclaw/workspace-alex
openclaw setup --workspace ~/.openclaw/workspace-mia

# Dann SOUL.md, AGENTS.md etc. in jedem Workspace individuell anpassen
```
