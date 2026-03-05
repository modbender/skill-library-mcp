---
name: firm-acp-bridge
version: 1.0.0
description: >
  Haute disponibilité du bridge ACP et gestion des sessions agents autonomes.
  Comble les gaps C4 (ACP sans persistance), H3 (sessions spawn sans provider env),
  H4 (cron bloqué en sandbox), et H5 (race condition workspace) dans openclaw/openclaw.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 2.0.0
      - "@agentclientprotocol/sdk >= 0.14.0"
tags:
  - acp
  - sessions
  - reliability
  - autonomous-agents
  - persistence
---

# firm-acp-bridge

> ⚠️ Contenu généré par IA — validation humaine requise avant déploiement en production.

## Purpose

Ce skill rend le bridge ACP **résilient aux crashs** et les sessions agents autonomes
**pleinement fonctionnelles** en comblant les gaps découverts dans `openclaw/openclaw`.

**Gaps couverts :**
| Gap | Sévérité | Outil |
|-----|----------|-------|
| C4 — ACP sessions en mémoire uniquement (crash = perte) | CRITICAL | `acp_session_persist/restore` |
| H3 — Sessions spawn/cron sans provider env vars | HIGH | `fleet_session_inject_env` |
| H4 — Cron tools sur denylist sandbox | HIGH | `fleet_cron_schedule` |
| H5 — Race condition shared-workspace read/write | HIGH | `openclaw_workspace_lock` |

## Tools activés

```
acp_session_persist       — persiste run_id → gateway_session_key sur disque (C4)
acp_session_restore       — recharge sessions après crash/restart bridge (C4)
acp_session_list_active   — liste sessions ACP actives et stale (C4)
fleet_session_inject_env  — injecte provider env vars dans sessions non-main (H3)
fleet_cron_schedule       — planifie cron tasks sur session main (H4)
openclaw_workspace_lock   — advisory lock pour éviter les race conditions (H5)
```

## Protocole ACP Persistence (C4)

**Problème :** Si le bridge `openclaw acp` crashe ou est tué (OOM, reboot), tous les
mappings `run_id → gateway_session_key` en mémoire sont perdus. Les IDE integrations
(VS Code, Cursor) se reconnectent silencieusement à de nouvelles sessions.

### Intégration côté bridge (pattern d'appel)

**À chaque création de session ACP**, appeler immédiatement :

```json
{
  "tool": "acp_session_persist",
  "args": {
    "run_id": "<acp_run_id>",
    "gateway_session_key": "<gateway_key>",
    "metadata": {
      "ide": "vscode",
      "workspace": "/path/to/project",
      "created_by": "agent-name"
    }
  }
}
```

**Au démarrage du bridge** (après crash ou restart) :

```json
{
  "tool": "acp_session_restore",
  "args": { "max_age_hours": 24 }
}
```
→ Retourne les sessions récupérables + purge automatique des sessions > 24h stale.

**Pour monitorer :**

```json
{
  "tool": "acp_session_list_active",
  "args": { "include_stale": false }
}
```

### Décision d'architecture — ACP session store

| Option | Décision | Raison |
|--------|----------|--------|
| Redis | ❌ NON | Trop lourd pour single-operator, dépendance externe |
| SQLite | ❌ NON | Overkill pour des clés simples, migration schema |
| JSON file (atomic rename) | ✅ OUI | Zéro dépendance, atomic write (tmp + os.replace), léger |

## Autonomous Session Bootstrap (H3)

**Problème :** Les sessions spawned via `sessions_spawn` ou cron n'ont pas accès aux
env vars des providers configurés (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.).
Tout appel LLM dans une session non-main échoue silencieusement.

### Séquence obligatoire avant sessions_spawn

**Étape 1 — Validation dry_run (vérifier les clés sans envoyer) :**

```json
{
  "tool": "fleet_session_inject_env",
  "args": {
    "env_vars": {
      "ANTHROPIC_API_KEY": "<your_key>",
      "OPENCLAW_MODEL": "claude-3-5-sonnet-20241022"
    },
    "dry_run": true
  }
}
```
→ Vérifie que les clés passent l'allowlist. Si `rejected` non vide, les clés sont invalides.

**Étape 2 — Injection effective avant spawn :**

```json
{
  "tool": "fleet_session_inject_env",
  "args": {
    "env_vars": {
      "ANTHROPIC_API_KEY": "<your_key>",
      "OPENCLAW_MODEL": "claude-3-5-sonnet-20241022"
    },
    "filter_tags": ["engineering", "quality"]
  }
}
```

**Étape 3 — Spawn la session (via Gateway direct) :**

```json
{
  "method": "sessions_spawn",
  "params": {
    "agent": "engineering",
    "reply_session": "main"
  }
}
```

### Clés autorisées (allowlist intégrée)

```
ANTHROPIC_API_KEY | OPENAI_API_KEY | OPENROUTER_API_KEY | GEMINI_API_KEY
OPENCLAW_MODEL | OPENCLAW_PROVIDER | OPENCLAW_MAX_TOKENS
CLAW_MODEL | CLAW_PROVIDER | PROXY_URL | CUSTOM_*
```

Jamais dans les logs — les valeurs sont masquées avec `****{last4}`.

## Cron Outside Sandbox (H4)

**Problème :** `cron` tools sont sur la denylist dans les sessions Docker sandbox.
Tout workflow autonome planifié dans un container non-main est bloqué.

**Solution :** Planifier sur la session `main` (accès hôte) via `fleet_cron_schedule`.

```json
{
  "tool": "fleet_cron_schedule",
  "args": {
    "command": "node scripts/daily-report.js",
    "schedule": "0 9 * * 1-5",
    "session": "main",
    "description": "Daily business report — Monday to Friday 9h"
  }
}
```

**Utiliser `fleet_cron_schedule` quand :**
- ✅ La tâche est un script léger et déterministe
- ✅ La tâche ne nécessite pas d'isolation sécurité
- ✅ La command passe l'allowlist `[a-zA-Z0-9 /._-=]+`

**Utiliser `sessions_spawn` (session non-main) quand :**
- ✅ La tâche implique du code non vérifié / externe
- ✅ Isolation sécurité requise (sandbox Docker)
- ✅ La tâche peut se déclencher ad-hoc (pas planifiée)

## Workspace Locking (H5)

**Problème :** Race condition documentée (#29947) sur shared-workspace read/modify/write.
Plusieurs sessions agent peuvent corrompre la même ressource partagée.

### Pattern acquire / work / release

```json
// 1. Acquérir le lock
{
  "tool": "openclaw_workspace_lock",
  "args": {
    "path": "shared/config.json",
    "action": "acquire",
    "owner": "engineering-session-001",
    "timeout_s": 30
  }
}

// 2. Faire le travail (read → modify → write)
// ... vos opérations sur la ressource ...

// 3. Libérer le lock
{
  "tool": "openclaw_workspace_lock",
  "args": {
    "path": "shared/config.json",
    "action": "release",
    "owner": "engineering-session-001"
  }
}
```

**Vérifier le statut d'un lock :**
```json
{
  "tool": "openclaw_workspace_lock",
  "args": {
    "path": "shared/config.json",
    "action": "status",
    "owner": "any"
  }
}
```

### Règles

- Le lock est **advisory** (pas kernel-level) — tous les agents doivent coopérer
- `timeout_s` max = 300s. Si lock non acquis → `ok: false` + current_owner
- Toujours `release` dans un bloc try/finally pour éviter les locks orphelins
- Un lock expired ne se libère pas automatiquement — utiliser `acp_session_restore` pour purger les owners stale

## Monitoring de santé ACP

Flux de monitoring recommandé (à exécuter périodiquement) :

```
acp_session_list_active → sessions stale > 2h → acp_session_restore(max_age_hours=2) → recheck
```

Si `restored: 0` et `purged > 0` après un intervalle normal → le bridge a crashé et les
sessions ont été perdues → notifier via `firm_export_slack_digest`.

---
*OpenClaw gaps : C4 (ACP in-memory), H3 (#29886 isolated sessions no provider env), H4 (#29921 cron sandbox denylist), H5 (#29947 race condition)*

---

## 💎 Support

Si ce skill vous est utile, vous pouvez soutenir le développement :

**Dogecoin** : `DQBggqFNWsRNTPb6kkiwppnMo1Hm8edfWq`
